import os
from ray.tune.logger import UnifiedLogger


def custom_logger_creator(config):
    """Creates a UnifiedLogger that saves results in a custom directory."""
    logdir = os.path.join(os.getcwd(), "training_results")
    os.makedirs(logdir, exist_ok=True)
    print(f"📊 Custom logger created. Saving all results to: {logdir}")

    return UnifiedLogger(config, logdir, loggers=None)
