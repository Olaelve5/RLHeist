from config import Config
from math import cos, sin

walls = [
    {
        "rect": (0, 0, Config.SCREEN_WIDTH, Config.WALL_WIDTH),  # Top wall
    },
    {
        "rect": (
            0,
            0,
            Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2 - Config.DOOR_WIDTH,
        ),  # Left wall top
    },
    {
        "rect": (
            0,
            Config.SCREEN_HEIGHT // 2 + Config.DOOR_WIDTH,
            Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2 - Config.WALL_WIDTH,
        ),  # Left wall bottom
    },
    {
        "rect": (
            Config.SCREEN_WIDTH - Config.WALL_WIDTH,
            0,
            Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2 - Config.DOOR_WIDTH,
        ),  # Right wall top
    },
    {
        "rect": (
            Config.SCREEN_WIDTH - Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2 + Config.DOOR_WIDTH,
            Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2 - Config.DOOR_WIDTH,
        ),  # Right wall bottom
    },
    {
        "rect": (
            0,
            Config.SCREEN_HEIGHT - Config.WALL_WIDTH,
            Config.SCREEN_WIDTH,
            Config.WALL_WIDTH,
        ),  # Bottom wall
    },
    {
        "rect": (
            Config.WALL_WIDTH + Config.CORRIDOR_WIDTH,
            Config.WALL_WIDTH + Config.CORRIDOR_WIDTH,
            Config.SCREEN_WIDTH // 2 - Config.CORRIDOR_WIDTH * 1.5 - Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2
            - Config.WALL_WIDTH
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal top left wall - top
    },
    {
        "rect": (
            Config.WALL_WIDTH + Config.CORRIDOR_WIDTH,
            Config.SCREEN_HEIGHT // 2
            - Config.MIDDLE_SQUARE_SIZE / 2
            - Config.CORRIDOR_WIDTH * 0.5,
            Config.SCREEN_WIDTH // 2
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.WALL_WIDTH
            - Config.MIDDLE_SQUARE_SIZE / 2,
            Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal top left wall - bottom
    },
    {
        "rect": (
            Config.SCREEN_WIDTH // 2 + Config.CORRIDOR_WIDTH / 2,
            Config.WALL_WIDTH + Config.CORRIDOR_WIDTH,
            Config.SCREEN_WIDTH // 2 - Config.CORRIDOR_WIDTH * 1.5 - Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2
            - Config.WALL_WIDTH
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal top right wall - top
    },
    {
        "rect": (
            Config.SCREEN_WIDTH // 2
            + Config.MIDDLE_SQUARE_SIZE / 2
            + Config.CORRIDOR_WIDTH * 0.5,
            Config.SCREEN_HEIGHT // 2
            - Config.MIDDLE_SQUARE_SIZE / 2
            - Config.CORRIDOR_WIDTH * 0.5,
            Config.SCREEN_WIDTH // 2
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.WALL_WIDTH
            - Config.MIDDLE_SQUARE_SIZE / 2,
            Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal top right wall - bottom
    },
    {
        "rect": (
            Config.WALL_WIDTH + Config.CORRIDOR_WIDTH,
            Config.SCREEN_HEIGHT // 2 + Config.CORRIDOR_WIDTH * 0.5,
            Config.SCREEN_WIDTH // 2
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.WALL_WIDTH
            - Config.MIDDLE_SQUARE_SIZE / 2,
            Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal bottom left wall - top
    },
    {
        "rect": (
            Config.WALL_WIDTH + Config.CORRIDOR_WIDTH,
            Config.SCREEN_HEIGHT // 2
            + Config.CORRIDOR_WIDTH * 0.5
            + Config.MIDDLE_SQUARE_SIZE / 2,
            Config.SCREEN_WIDTH // 2 - Config.CORRIDOR_WIDTH * 1.5 - Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2
            - Config.WALL_WIDTH
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal bottom left wall - bottom
    },
    {
        "rect": (
            Config.SCREEN_WIDTH // 2
            + Config.MIDDLE_SQUARE_SIZE / 2
            + Config.CORRIDOR_WIDTH * 0.5,
            Config.SCREEN_HEIGHT // 2 + Config.CORRIDOR_WIDTH * 0.5,
            Config.SCREEN_WIDTH // 2
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.WALL_WIDTH
            - Config.MIDDLE_SQUARE_SIZE / 2,
            Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal bottom right wall - top
    },
    {
        "rect": (
            Config.SCREEN_WIDTH // 2 + Config.CORRIDOR_WIDTH / 2,
            Config.SCREEN_HEIGHT // 2
            + Config.CORRIDOR_WIDTH * 0.5
            + Config.MIDDLE_SQUARE_SIZE / 2,
            Config.SCREEN_WIDTH // 2 - Config.CORRIDOR_WIDTH * 1.5 - Config.WALL_WIDTH,
            Config.SCREEN_HEIGHT // 2
            - Config.WALL_WIDTH
            - Config.CORRIDOR_WIDTH * 1.5
            - Config.MIDDLE_SQUARE_SIZE / 2,
        ),  # Internal bottom right wall - bottom
    },
]


def create_wall_lines():
    """Create line segments for wall outlines"""
    lines = []

    # For each wall rectangle, create 4 line segments (the outline)
    for wall in walls:
        rect = wall["rect"]
        left, top, width, height = rect

        # Create the 4 edges of the rectangle
        lines.extend(
            [
                ((left, top), (left + width, top)),  # Top edge
                ((left + width, top), (left + width, top + height)),  # Right edge
                ((left + width, top + height), (left, top + height)),  # Bottom edge
                ((left, top + height), (left, top)),  # Left edge
            ]
        )
    
    # Add the gem circle as a line segment
    gem_radius = 30  # Radius of the gem circle
    gem_center = (Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)
    # Create a circle outline by approximating it with line segments
    num_segments = 36  # Number of segments to approximate the circle
    for i in range(num_segments):
        angle1 = (i / num_segments) * 2 * 3.14159  # Full circle in radians
        angle2 = ((i + 1) / num_segments) * 2 * 3.14159
        start_point = (
            gem_center[0] + gem_radius * cos(angle1),
            gem_center[1] + gem_radius * sin(angle1),
        )
        end_point = (
            gem_center[0] + gem_radius * cos(angle2),
            gem_center[1] + gem_radius * sin(angle2),
        )
        lines.append((start_point, end_point))

    return lines


# Generate the wall lines
wall_lines = create_wall_lines()


gem_circle = (
    Config.SCREEN_WIDTH // 2,
    Config.SCREEN_HEIGHT // 2,
    30,  # Radius of the gem circle
)
