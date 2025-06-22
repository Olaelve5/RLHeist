from config import Config
import random
from pygame.math import Vector2


def get_agent_start_pos(config: Config, agent_id, random_level=0):
    if not agent_id.startswith("thief") and not agent_id.startswith("guard"):
        raise ValueError(
            f"Invalid agent_id: {agent_id}. Must start with 'thief' or 'guard'."
        )

    if random_level == 0:
        if agent_id.startswith("thief"):
            return config.THIEF_DEFAULT_START_POS
        else:
            return config.GUARD_DEFAULT_START_POS
    elif random_level == 1:
        if agent_id.startswith("thief"):
            return random.choice(config.THIEF_RANDOM_START_POSITIONS)
        else:
            return random.choice(config.GUARD_RANDOM_START_POSITIONS)
    elif random_level == 2:
        if agent_id.startswith("thief"):
            variant = random.choice([1, 2])
            if variant == 1:
                return Vector2(
                    random.choice([50, config.SCREEN_WIDTH - 50]),
                    random.randint(50, config.SCREEN_HEIGHT - 50),
                )
            else:
                return Vector2(
                    random.randint(50, config.SCREEN_WIDTH - 50),
                    random.choice([50, config.SCREEN_HEIGHT - 50]),
                )
        else:
            variant = random.choice([1, 2])
            if variant == 1:
                return Vector2(
                    random.randint(
                        config.SCREEN_WIDTH // 2 - 150, config.SCREEN_WIDTH // 2 + 150
                    ),
                    random.choice(
                        [config.SCREEN_HEIGHT // 2 - 150, config.SCREEN_HEIGHT // 2 + 150]
                    ),
                )
            else:
                return Vector2(
                    random.choice(
                        [config.SCREEN_WIDTH // 2 + 150, config.SCREEN_WIDTH // 2 - 150]
                    ),
                    random.randint(
                        config.SCREEN_HEIGHT // 2 - 150, config.SCREEN_HEIGHT // 2 + 150
                    ),
                )

    else:
        raise ValueError(f"Invalid random_level: {random_level}. Must be 0, 1, or 2.")
