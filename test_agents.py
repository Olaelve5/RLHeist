from rlheist_env import RLHeistEnv
import pygame
from utils.human_input_utils import get_human_action
import ray
import numpy as np
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from utils.list_models_utils import choose_model
from utils.ppo_config_utils import get_ppo_config
import warnings

# Ignore deprecation warnings from RLlib
# clutters output - messy because of new api changes
warnings.filterwarnings("ignore", category=DeprecationWarning)


def env_creator(env_config):
    """Create and return the wrapped environment"""
    base_env = RLHeistEnv(render_mode=None)
    return ParallelPettingZooEnv(base_env)


def launch_game(checkpoint_path: str):
    ray.init(local_mode=True, ignore_reinit_error=True)

    register_env("RLHeistEnv", env_creator)

    temp_env = env_creator({})
    obs_space_thief = temp_env.observation_space["thief"]
    act_space_thief = temp_env.action_space["thief"]
    obs_space_guard = temp_env.observation_space["guard"]
    act_space_guard = temp_env.action_space["guard"]
    temp_env.close()

    config = get_ppo_config(
        obs_space_thief=obs_space_thief,
        act_space_thief=act_space_thief,
        obs_space_guard=obs_space_guard,
        act_space_guard=act_space_guard,
    )

    config.env_runners(num_env_runners=0)
    config.environment(render_env=True)
    algo = config.build_algo()
    algo.restore(checkpoint_path)

    # Get the specific RLModules for each policy
    thief_module = algo.get_module("thief_policy")
    guard_module = algo.get_module("guard_policy")

    # Create rendering environment
    env = RLHeistEnv(render_mode="human")
    obs, info = env.reset()

    running = True
    clock = pygame.time.Clock()
    episode_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Get actions for each agent
        thief_obs_batch = np.array([obs["thief"]])
        guard_obs_batch = np.array([obs["guard"]])

        # Get actions from each module using the new API
        thief_action_dist = thief_module.forward_inference({"obs": thief_obs_batch})
        guard_action_dist = guard_module.forward_inference({"obs": guard_obs_batch})

        # Extract the action from the resulting dictionary
        thief_action = thief_action_dist['actions'][0]
        guard_action = guard_action_dist['actions'][0]

        # Combine actions into a dictionary for the environment
        actions = {
            "thief": thief_action,
            "guard": guard_action,
        }

        # Step environment
        obs, rewards, terminations, truncations, infos = env.step(actions)

        # Check for episode end
        if any(terminations.values()) or any(truncations.values()):
            waiting_for_input = True
            while waiting_for_input:
                env.graphics.draw_end_message(env.game_outcome_text)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_input = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            waiting_for_input = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                            waiting_for_input = False
            episode_count += 1
            print(f"\n--- Episode {episode_count} ended! ---")
            obs, info = env.reset()

        env.render()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    checkpoint_path = choose_model()

    if not checkpoint_path:
        print("No checkpoint selected. Exiting.")
        exit(0)

    print(f"💾 Loading checkpoint from path: {checkpoint_path}")

    launch_game(checkpoint_path)
