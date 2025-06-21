import pygame


def get_human_action(player_id):
    """Get action input from human player."""
    keys = pygame.key.get_pressed()
    action = 0  # Default action (no movement)

    if player_id == "thief":
        if keys[pygame.K_w]:
            action = 1  # Move up
        elif keys[pygame.K_s]:
            action = 2  # Move down
        elif keys[pygame.K_a]:
            action = 3  # Move left
        elif keys[pygame.K_d]:
            action = 4  # Move right
        elif keys[pygame.K_1]:
            action = 5
        elif keys[pygame.K_2]:
            action = 6
        elif keys[pygame.K_3]:
            action = 7
        elif keys[pygame.K_4]:
            action = 8

    elif player_id == "guard":
        if keys[pygame.K_UP]:
            action = 1  # Move up
        elif keys[pygame.K_DOWN]:
            action = 2  # Move down
        elif keys[pygame.K_LEFT]:
            action = 3  # Move left
        elif keys[pygame.K_RIGHT]:
            action = 4  # Move right
        elif keys[pygame.K_PERIOD]:
            action = 5  # Rotate right
        elif keys[pygame.K_MINUS]:
            action = 6  # Rotate left

    return action
