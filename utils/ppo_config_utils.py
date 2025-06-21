from ray.rllib.algorithms.ppo import PPOConfig


def get_ppo_config(obs_space_thief, act_space_thief, obs_space_guard, act_space_guard):

    config = (
        PPOConfig()
        .environment(
            env="RLHeistEnv",
        )
        .multi_agent(
            policies={
                "thief_policy": (None, obs_space_thief, act_space_thief, {}),
                "guard_policy": (None, obs_space_guard, act_space_guard, {}),
            },
            policy_mapping_fn=lambda agent_id, episode, **kwargs: (
                "thief_policy" if agent_id.startswith("thief") else "guard_policy"
            ),
            policies_to_train=["thief_policy", "guard_policy"],
        )
        .training(
            lr=2e-4,
            train_batch_size=8192*2, 
            minibatch_size=256,
            num_epochs=8,
            gamma=0.99,
            model={
                "fcnet_hiddens": [256, 256],
                "fcnet_activation": "relu",
            },
            entropy_coeff=0.001,
            clip_param=0.2,
            vf_clip_param=10.0,
        )
        .resources(num_gpus=0)
    )

    return config
