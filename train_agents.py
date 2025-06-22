import ray
from ray.rllib.algorithms.ppo import PPO
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from rlheist_env import RLHeistEnv
import os
import warnings
from utils.ppo_config_utils import get_ppo_config
from utils.custom_logger_creator import custom_logger_creator
from utils.checkpoint_utils import get_latest_checkpoint

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

    # Restore from the latest checkpoint if available
    latest_checkpoint = get_latest_checkpoint()
    if latest_checkpoint:
        print(f"🔄 Restoring from checkpoint: {latest_checkpoint}")
        iteration_number = int(latest_checkpoint.split("iteration_")[-1].split(".")[0])
        algo.restore(latest_checkpoint)
    else:
        iteration_number = 0
        print("🔄 No checkpoint found, starting fresh training.")

    print("🚀 Starting training...")
    for i in range(200):
        current_iteration = iteration_number + i + 1

        print(f"\n\n=== Training iteration {current_iteration} ===")

        result = algo.train()

        # Safely get the env_runners dictionary
        env_runners_data = result.get("env_runners", {})

        # Extract the metrics using the new paths
        episode_reward = env_runners_data.get("episode_return_mean", 0)
        episode_length = env_runners_data.get("episode_len_mean", 0)

        # Get the dictionary of module rewards
        module_rewards = env_runners_data.get("module_episode_returns_mean", {})
        thief_reward = module_rewards.get("thief_policy", 0)
        guard_reward = module_rewards.get("guard_policy", 0)

        print(f"Iter {current_iteration}:")
        print(f"  📊 Overall reward: {episode_reward:.3f}")
        print(f"  📏 Episode length: {episode_length:.1f}")
        print(f"  🔴 Thief reward: {thief_reward:.3f}")
        print(f"  🔵 Guard reward: {guard_reward:.3f}")

        save_frequency = 25

        if (current_iteration) % save_frequency == 0:
            # Create a proper subdirectory for each checkpoint
            checkpoint_name = f"RLHeist_checkpoint_iteration_{current_iteration:03d}"
            checkpoint_path = os.path.join(models_dir, checkpoint_name)

            checkpoint_result = algo.save(checkpoint_path)
            print(f"  💾 Checkpoint saved: {checkpoint_result.checkpoint.path}")

    print("\n🎉 Training completed successfully!")

    ray.shutdown()


if __name__ == "__main__":
    train_agents()
