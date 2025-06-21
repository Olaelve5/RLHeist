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
import torch

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

    algo = config.build_algo()
    algo.restore(checkpoint_path)

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

        actions = {}
        for agent_id, agent_obs in obs.items():

            policy_id = (
                "thief_policy" if agent_id.startswith("thief") else "guard_policy"
            )

            rl_module = algo.get_module(policy_id)

            obs_tensor = torch.tensor([agent_obs], dtype=torch.float32)
            obs_batch = {"obs": obs_tensor}

            outputs = rl_module.forward_inference(obs_batch)

            action_dist_class = rl_module.get_inference_action_dist_cls()
            action_dist = action_dist_class.from_logits(outputs["action_dist_inputs"])

            action_tensor = action_dist.sample()

            actions[agent_id] = action_tensor.item()

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
