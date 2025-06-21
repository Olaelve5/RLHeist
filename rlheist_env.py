from gymnasium import spaces
import numpy as np
from pettingzoo.utils.env import ParallelEnv
from graphics import Graphics
from pygame.math import Vector2
from collision_handler import handle_collisions, handle_gem_collision
from config import Config
from light_ray import RayCollection
from utils.walls import wall_lines


class RLHeistEnv(ParallelEnv):

    def __init__(self, render_mode="human"):
        super().__init__()
        self.render_mode = render_mode

        self.config = Config()

        self.game_outcome_text = None

        self.thief_pos = Vector2(50, self.config.SCREEN_HEIGHT / 2)
        self.last_thief_pos = self.thief_pos.copy()

        self.guard_pos = Vector2(
            self.config.SCREEN_WIDTH / 2, self.config.SCREEN_HEIGHT / 2 + 150
        )
        self.last_guard_pos = self.guard_pos.copy()

        self.thief_vel = Vector2(0, 0)
        self.guard_vel = Vector2(0, 0)
        self.guard_flashlight_angle = 270
        self.thief_sprint_stamina = self.config.AGENT_SPRINT_STAMINA
        self.flashlight_rays = RayCollection(self.guard_pos, ray_count=20)

        # Initialize the gem position and state
        self.thief_has_gem = False
        self.thief_has_recieved_gem_reward = False
        self.thief_is_caught = False
        self.thief_has_escaped = False
        self.gem_pos = Vector2(
            self.config.SCREEN_WIDTH / 2, self.config.SCREEN_HEIGHT / 2
        )
        self.last_gem_pos = self.gem_pos.copy()

        self.graphics = Graphics(
            render_mode=render_mode,
            screen_width=self.config.SCREEN_WIDTH,
            screen_height=self.config.SCREEN_HEIGHT,
            agent_radius=self.config.AGENT_RADIUS,
        )

        self.score = {
            "thief": 0,
            "guard": 0,
        }

        # Define agents
        self.agents = ["thief", "guard"]
        self.possible_agents = self.agents.copy()

        # Action spaces
        # Thief: 0:No-op, 1:Up, 2:Down, 3:Left, 4:Right, 5:Sprint Up, 6: Sprint Down, 7: Sprint Left, 8: Sprint Right
        # Guard: 0:No-op, 1:Up, 2:Down, 3:Left, 4:Right, 5:Rotate Left, 6: Rotate Right
        # Note:
        self.action_spaces = {"thief": spaces.Discrete(9), "guard": spaces.Discrete(7)}
        self.max_episode_steps = 1800 # 30 seconds at 60 FPS
        self.step_counter = 0

        # Define the observation space
        low = np.array(
            [
                -self.config.AGENT_RADIUS,  # My x position
                0,  # My y position
                -self.config.MAX_AGENT_SPRINT_VELOCITY,  # My velocity x
                -self.config.MAX_AGENT_SPRINT_VELOCITY,  # My velocity y
                -self.config.AGENT_RADIUS,  # Opposition x position
                0,  # Opposition y position
                -self.config.MAX_AGENT_SPRINT_VELOCITY,  # Opposition velocity x
                -self.config.MAX_AGENT_SPRINT_VELOCITY,  # Opposition velocity y
                0,  # Gem x position
                0,  # Gem y position
                0,  # Guard flashlight angle
                0,  # Thief sprint stamina
            ],
        )

        high = np.array(
            [
                self.config.SCREEN_WIDTH + self.config.AGENT_RADIUS,  # My x position
                self.config.SCREEN_HEIGHT,  # My y position
                self.config.MAX_AGENT_SPRINT_VELOCITY,  # My x velocity
                self.config.MAX_AGENT_SPRINT_VELOCITY,  # My y velocity
                self.config.SCREEN_WIDTH
                + self.config.AGENT_RADIUS,  # Opposition x position
                self.config.SCREEN_HEIGHT,  # Opposition y position
                self.config.MAX_AGENT_SPRINT_VELOCITY,  # Opposition x velocity
                self.config.MAX_AGENT_SPRINT_VELOCITY,  # Opposition y velocity
                self.config.SCREEN_WIDTH,  # Gem x position
                self.config.SCREEN_HEIGHT,  # Gem y position
                370,  # Guard flashlight angle (0-360 degrees + 10 for safety)
                self.config.AGENT_SPRINT_STAMINA,  # Thief sprint stamina
            ],
            dtype=np.float32,
        )

        self.observation_spaces = {
            agent: spaces.Box(low=low, high=high, shape=(12,), dtype=np.float32)
            for agent in self.agents
        }

    def render(self):
        if self.render_mode == "human":
            self.graphics.draw(
                self.thief_pos,
                self.guard_pos,
                self.gem_pos,
                self.thief_has_gem,
                self.flashlight_rays,
            )

    def reset(self, seed=None, options=None):
        """Reset the environment to its initial state.
        Returns:
            observations: A tuple containing the initial positions of My, Opponent, and the ball.
            infos: Additional information about the environment state.
        """
        self.step_counter = 0

        self.game_outcome_text = None

        self.thief_pos = Vector2(50, self.config.SCREEN_HEIGHT / 2)
        self.last_thief_pos = self.thief_pos.copy()

        self.guard_pos = Vector2(
            self.config.SCREEN_WIDTH / 2, self.config.SCREEN_HEIGHT / 2 + 150
        )
        self.last_guard_pos = self.guard_pos.copy()

        self.thief_vel = Vector2(0, 0)
        self.guard_vel = Vector2(0, 0)
        self.guard_flashlight_angle = 270
        self.thief_sprint_stamina = self.config.AGENT_SPRINT_STAMINA
        self.gem_pos = Vector2(
            self.config.SCREEN_WIDTH / 2, self.config.SCREEN_HEIGHT / 2
        )
        self.last_gem_pos = self.gem_pos.copy()

        self.thief_has_gem = False
        self.thief_has_recieved_gem_reward = False
        self.thief_is_caught = False
        self.thief_has_escaped = False

        observations = self._get_obs()
        infos = self._get_infos()

        return observations, infos

    def _get_obs(self):
        """Return observations as a dictionary for each agent."""

        # Common information
        common_info = np.concatenate(
            [
                np.array(self.gem_pos, dtype=np.float32),
                np.array([self.guard_flashlight_angle], dtype=np.float32),
                np.array([self.thief_sprint_stamina], dtype=np.float32),
            ]
        )

        # Observation for thief
        obs_thief = np.concatenate(
            [
                np.array(self.thief_pos, dtype=np.float32),
                np.array(self.thief_vel, dtype=np.float32),
                np.array(self.guard_pos, dtype=np.float32),
                np.array(self.guard_vel, dtype=np.float32),
                common_info,
            ]
        )

        # Observation for guard
        obs_guard = np.concatenate(
            [
                np.array(self.guard_pos, dtype=np.float32),
                np.array(self.guard_vel, dtype=np.float32),
                np.array(self.thief_pos, dtype=np.float32),
                np.array(self.thief_vel, dtype=np.float32),
                common_info,
            ]
        )

        # clip observations to ensure they are within bounds
        obs_thief = np.clip(
            obs_thief,
            self.observation_spaces["thief"].low,
            self.observation_spaces["thief"].high,
        )
        obs_guard = np.clip(
            obs_guard,
            self.observation_spaces["guard"].low,
            self.observation_spaces["guard"].high,
        )

        return {
            "thief": obs_thief,
            "guard": obs_guard,
        }

    def _get_infos(self):
        """Get additional information about the environment state."""
        return {
            "thief": {
                "has_gem": self.thief_has_gem,
                "has_escaped": self.thief_has_escaped,
                "is_caught": self.thief_is_caught,
            },
            "guard": {
                "flashlight_angle": self.guard_flashlight_angle,
                "is_caught": self.thief_is_caught,
            },
        }

    def observation_space(self, agent):
        """Return the observation space for a given agent."""
        return self.observation_spaces[agent]

    def action_space(self, agent):
        """Return the action space for a given agent."""
        return self.action_spaces[agent]

    def step(self, actions):
        """Perform a step in the environment with the given actions."""
        self.step_counter += 1

        thief_action = actions.get("thief", 0)
        guard_action = actions.get("guard", 0)

        # Update player positions based on actions
        self._handle_actions(
            self.thief_pos, self.thief_vel, thief_action, is_guard=False
        )
        self._handle_actions(
            self.guard_pos, self.guard_vel, guard_action, is_guard=True
        )

        # Handle gem collection
        self.thief_has_gem = handle_gem_collision(
            self.thief_pos, self.config.AGENT_RADIUS, self.gem_pos
        )

        if self.thief_has_gem:
            self.gem_pos = self.thief_pos  # Move gem to thief's position

        # Update the flashlight rays for the guard
        self.flashlight_rays.update(
            new_origin=self.guard_pos,
            new_origin_angle=self.guard_flashlight_angle,
            wall_lines=wall_lines,
        )

        # Check if the thief has escaped with the gem
        # The thief can escape if they have the gem and are at the left or right exit
        self.thief_has_escaped = self.thief_has_gem and (
            self.thief_pos.x < self.config.WALL_WIDTH - self.config.AGENT_RADIUS
            or self.thief_pos.x
            > self.config.SCREEN_WIDTH
            - self.config.WALL_WIDTH
            + self.config.AGENT_RADIUS
        )

        # Check if the thief is caught by the guard's flashlight
        self.thief_is_caught = self.flashlight_rays.is_thief_visible(
            self.thief_pos,
            self.config.AGENT_RADIUS,
            self.guard_flashlight_angle,
            wall_lines,
        )

        # Handle collisions with walls
        self.thief_pos = handle_collisions(
            self.thief_pos, self.config.AGENT_RADIUS, self.thief_has_gem, is_guard=False
        )
        self.guard_pos = handle_collisions(
            self.guard_pos, self.config.AGENT_RADIUS, self.thief_has_gem, is_guard=True
        )

        # Calculate rewards
        rewards = self._calculate_rewards()

        # Update last positions after rewards and actions
        self.last_thief_pos = self.thief_pos.copy()
        self.last_guard_pos = self.guard_pos.copy()
        self.last_gem_pos = self.gem_pos.copy()

        # Check for truncation (episode ends due to time limit)
        truncated = self.step_counter >= self.max_episode_steps

        # Check for termination
        terminated = self.thief_is_caught or self.thief_has_escaped

        # If an episode ends for one agent, it must end for all
        terminations = {agent: terminated for agent in self.agents}
        truncations = {agent: truncated for agent in self.agents}

        if truncated:
            self.game_outcome_text = "Guard wins by time limit!"

        if self.thief_is_caught:
            self.game_outcome_text = "Guard caught the thief!"

        if self.thief_has_escaped:
            self.game_outcome_text = "Thief escaped with the gem!"

        observations = self._get_obs()
        infos = self._get_infos()

        return observations, rewards, terminations, truncations, infos

    def _handle_actions(self, agent_pos, agent_vel, action, is_guard=False):
        """Handles movement, sprinting, and rotation for an agent."""
        if is_guard:
            # Guard can move (1-4) or rotate (5-6)
            if action == 1:
                agent_vel.y -= self.config.AGENT_ACCELERATION
            elif action == 2:
                agent_vel.y += self.config.AGENT_ACCELERATION
            elif action == 3:
                agent_vel.x -= self.config.AGENT_ACCELERATION
            elif action == 4:
                agent_vel.x += self.config.AGENT_ACCELERATION
            elif action == 5:
                self.guard_flashlight_angle = (
                    self.guard_flashlight_angle + self.config.AGENT_ROTATION_SPEED
                ) % 360
            elif action == 6:
                self.guard_flashlight_angle = (
                    self.guard_flashlight_angle - self.config.AGENT_ROTATION_SPEED
                ) % 360

            agent_vel *= self.config.AGENT_FRICTION

            # Limit Guard's velocity
            if agent_vel.length() > self.config.MAX_AGENT_VELOCITY:
                agent_vel.scale_to_length(self.config.MAX_AGENT_VELOCITY)

        else:
            # Thief can move (1-4) or sprint in a direction (5-8)
            is_sprinting = (action >= 5) and (self.thief_sprint_stamina > 0)

            acceleration = (
                self.config.AGENT_SPRINT_ACCELERATION
                if is_sprinting
                else self.config.AGENT_ACCELERATION
            )

            # Determine the maximum velocity based on sprinting status
            max_velocity = (
                self.config.MAX_AGENT_SPRINT_VELOCITY
                if is_sprinting
                else self.config.MAX_AGENT_VELOCITY
            )

            # Handle movement actions
            if action == 1 or action == 5:
                agent_vel.y -= acceleration
            elif action == 2 or action == 6:
                agent_vel.y += acceleration
            elif action == 3 or action == 7:
                agent_vel.x -= acceleration
            elif action == 4 or action == 8:
                agent_vel.x += acceleration
            else:
                agent_vel *= self.config.AGENT_FRICTION

            # Handle stamina recharge/cost
            if is_sprinting:
                self.thief_sprint_stamina -= 1
            else:
                if action < 5:
                    self.thief_sprint_stamina = min(
                        self.thief_sprint_stamina + 0.1,
                        self.config.AGENT_SPRINT_STAMINA,
                    )

            # Limit Thief's velocity
            if agent_vel.length() > max_velocity:
                agent_vel.scale_to_length(max_velocity)

            # Ensure the thief's sprint stamina does not go below zero
            self.thief_sprint_stamina = max(self.thief_sprint_stamina, 0)

        # Update the agent's position
        agent_pos += agent_vel

    def _calculate_rewards(self):
        """Calculate rewards for each player."""
        rewards = {agent: 0.0 for agent in self.agents}

        # Time penalty
        rewards["thief"] -= 0.005

        if self.thief_is_caught:
            rewards["thief"] = -10.0
            rewards["guard"] = 10.0
            print("🚨 Thief caught by the guard!")
            return rewards

        # Check if the thief escapes with the gem
        if self.thief_has_gem and self.thief_has_escaped:
            rewards["thief"] = 10.0
            rewards["guard"] = -10.0
            print("🚪 Thief escaped with the gem!")
            return rewards

        if self.thief_has_gem and not self.thief_has_recieved_gem_reward:
            rewards["thief"] += 4.0
            rewards["guard"] -= 4.0
            print("💎 Thief caught the gem!")
            self.thief_has_recieved_gem_reward = True

        if self.step_counter >= self.max_episode_steps:
            rewards["thief"] = -2.0
            rewards["guard"] = 2.0
            return rewards

        # Check if guard comes closer to the thief
        last_distance = self.last_guard_pos.distance_to(self.last_thief_pos)
        current_distance = self.guard_pos.distance_to(self.thief_pos)
        if current_distance < last_distance:
            rewards["guard"] += 0.005

        # Check if the theif moves closer to the gem
        last_gem_distance = self.last_thief_pos.distance_to(self.last_gem_pos)
        current_gem_distance = self.thief_pos.distance_to(self.gem_pos)
        if (current_gem_distance < last_gem_distance) and not self.thief_has_gem:
            rewards["thief"] += 0.005

        # Check if the thief moves closer to an exit if they have the gem
        left_exit_location = Vector2(
            self.config.WALL_WIDTH + self.config.AGENT_RADIUS,
            self.config.SCREEN_HEIGHT / 2,
        )
        right_exit_location = Vector2(
            self.config.SCREEN_WIDTH
            - self.config.WALL_WIDTH
            - self.config.AGENT_RADIUS,
            self.config.SCREEN_HEIGHT / 2,
        )
        if self.thief_has_gem:
            last_smallest_exit_distance = min(
                self.last_thief_pos.distance_to(left_exit_location),
                self.last_thief_pos.distance_to(right_exit_location),
            )
            current_smallest_exit_distance = min(
                self.thief_pos.distance_to(left_exit_location),
                self.thief_pos.distance_to(right_exit_location),
            )
            if current_smallest_exit_distance < last_smallest_exit_distance:
                rewards["thief"] += 0.005
            

        return rewards
