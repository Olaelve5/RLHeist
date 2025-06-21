import ray
from ray.rllib.algorithms.ppo import PPO
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from rlheist_env import RLHeistEnv
import os
import warnings
from utils.ppo_config_utils import get_ppo_config
from utils.custom_logger_creator import custom_logger_creator

warnings.filterwarnings("ignore", category=DeprecationWarning)


def env_creator(env_config):
    """Create and return the wrapped environment"""
    base_env = RLHeistEnv(render_mode=None)
    return ParallelPettingZooEnv(base_env)


def train_agents():
    """Function to train agents using RLlib."""
    ray.init(
        local_mode=True,
        ignore_reinit_error=True,
    )

    register_env("RLHeistEnv", env_creator)

    models_dir = os.path.join(os.getcwd(), "policies_checkpoints")
    os.makedirs(models_dir, exist_ok=True)

    # Get observation and action spaces
    temp_env = env_creator({})
    obs_space_thief = temp_env.observation_space["thief"]
    act_space_thief = temp_env.action_space["thief"]
    obs_space_guard = temp_env.observation_space["guard"]
    act_space_guard = temp_env.action_space["guard"]
    temp_env.close()  # Clean up

    config = get_ppo_config(
        obs_space_thief=obs_space_thief,
        act_space_thief=act_space_thief,
        obs_space_guard=obs_space_guard,
        act_space_guard=act_space_guard,
    )

    config.env_runners(num_env_runners=4)

    algo = PPO(config=config, logger_creator=custom_logger_creator)

    print("🚀 Starting training...")
    for i in range(300):
        print(f"\n\n=== Training iteration {i + 1} ===")

        result = algo.train()

        # ✅ CORRECT - Use these keys from your result structure:
        episode_reward_mean = result.get("env_runners", {}).get(
            "episode_reward_mean", 0
        )

        # Individual policy rewards:
        policy_rewards = result.get("env_runners", {}).get("policy_reward_mean", {})
        thief_reward = policy_rewards.get("thief_policy", 0)
        guard_reward = policy_rewards.get("guard_policy", 0)

        # Episode length:
        episode_length = result.get("env_runners", {}).get("episode_len_mean", 0)

        print(f"Iter {i + 1}:")
        print(f"  📊 Overall reward: {episode_reward_mean:.3f}")
        print(f"  📏 Episode length: {episode_length:.1f}")
        print(f"  🔴 Thief reward: {thief_reward:.3f}")
        print(f"  🔵 Guard reward: {guard_reward:.3f}")

        save_frequency = 20

        if (i + 1) % save_frequency == 0:
            # Create a proper subdirectory for each checkpoint
            checkpoint_name = f"RLHeist_checkpoint_iteration_{i + 1:03d}"
            checkpoint_path = os.path.join(models_dir, checkpoint_name)

            checkpoint_result = algo.save(checkpoint_path)
            print(f"  💾 Checkpoint saved: {checkpoint_result.checkpoint.path}")

    print("\n🎉 Training completed successfully!")

    ray.shutdown()


if __name__ == "__main__":
    train_agents()
