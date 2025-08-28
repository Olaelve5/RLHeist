from utils.walls import walls_level_1, gem_circle, walls_level_2, walls_level_3
from config import Config
from pygame.math import Vector2
from light_ray import Ray


def handle_collisions(
    agent_pos, agent_radius, thief_has_gem=False, is_guard=False, map_level=1
):

    current_pos = Vector2(agent_pos.x, agent_pos.y)

    walls = []
    if map_level == 1:
        walls = walls_level_1
    elif map_level == 2:
        walls = walls_level_2
    elif map_level == 3:
        walls = walls_level_3

    for wall in walls:
        rect = wall["rect"]
        left, top, width, height = rect

        # Check if agent collides with this wall
        if (
            current_pos.x + agent_radius > left
            and current_pos.x - agent_radius < left + width
            and current_pos.y + agent_radius > top
            and current_pos.y - agent_radius < top + height
        ):
            # Calculate overlap distances
            overlap_left = (current_pos.x + agent_radius) - left
            overlap_right = (left + width) - (current_pos.x - agent_radius)
            overlap_top = (current_pos.y + agent_radius) - top
            overlap_bottom = (top + height) - (current_pos.y - agent_radius)

            # Find the smallest overlap (closest wall edge)
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            # Push agent out in the direction of smallest overlap
            if min_overlap == overlap_left:
                # Push left
                current_pos.x = left - agent_radius
            elif min_overlap == overlap_right:
                # Push right
                current_pos.x = left + width + agent_radius
            elif min_overlap == overlap_top:
                # Push up
                current_pos.y = top - agent_radius
            elif min_overlap == overlap_bottom:
                # Push down
                current_pos.y = top + height + agent_radius

    # Handle gem circle collision
    gem_vector = Vector2(gem_circle[0], gem_circle[1])
    if current_pos.distance_to(gem_vector) < gem_circle[2] + agent_radius:
        # Push agent out of the gem circle
        direction = (current_pos - gem_vector).normalize()
        current_pos = gem_vector + direction * (gem_circle[2] + agent_radius)

    # Ensure the thief can't leave unless he has the gem
    if not thief_has_gem or is_guard:
        if agent_pos.x < Config.WALL_WIDTH + agent_radius:
            current_pos.x = Config.WALL_WIDTH + agent_radius
        elif agent_pos.x > Config.SCREEN_WIDTH - Config.WALL_WIDTH - agent_radius:
            current_pos.x = Config.SCREEN_WIDTH - Config.WALL_WIDTH - agent_radius

    return current_pos


def handle_gem_collision(agent_pos, agent_radius, gem_pos):
    current_pos = Vector2(agent_pos.x, agent_pos.y)
    gem_vector = Vector2(gem_pos[0], gem_pos[1])

    take_radius = gem_circle[2] + 2

    # Check if agent is in range to take the gem
    if current_pos.distance_to(gem_vector) < agent_radius + take_radius:
        return True
    return False
