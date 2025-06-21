import pygame
from config import Config
from utils.walls import walls, gem_circle, wall_lines
from light_ray import RayCollection


class Graphics:
    def __init__(
        self,
        render_mode="human",
        screen_width=1200,
        screen_height=1000,
        agent_radius=40,
    ):
        pygame.init()
        self.render_mode = render_mode
        self.screen_width = screen_width
        self.screen_height = screen_height
        if self.render_mode == "human":
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            pygame.display.set_caption("RL Heist")

        self.agent_radius = agent_radius

        # --- Define Colors ---
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 210, 0)
        self.TEAL = (0, 220, 114)  # Guard
        self.ORANGE = (220, 63, 0)  # Thief
        self.BLACK = (8, 8, 8)
        self.WALL_COLOR = (54, 50, 47)
        self.SKY_BLUE = (0, 255, 247)
        self.BLUE_GRAY = (38, 47, 64)
        self.RED = (200, 0, 0)
        self.GREEN = (0, 255, 0)

    def draw(
        self,
        thief_pos,
        guard_pos,
        gem_pos,
        thief_has_gem,
        flashlight_rays=None,
    ):
        if self.render_mode != "human":
            return

        # --- Draw the Field ---
        self.screen.fill(self.BLACK)

        # Draw the flashlight cone
        self.draw_flashlight(flashlight_rays)

        # Draw the guard
        pygame.draw.circle(
            self.screen,
            self.TEAL,
            (int(guard_pos[0]), int(guard_pos[1])),
            self.agent_radius,
        )

        # Draw the thief
        pygame.draw.circle(
            self.screen,
            self.ORANGE,
            (int(thief_pos[0]), int(thief_pos[1])),
            self.agent_radius,
        )

        # Draw the gem circle
        self.draw_gem_circle()

        gem_scaling = 1.0 if not thief_has_gem else 0.7

        # Draw the gem
        pygame.draw.polygon(
            self.screen,
            self.SKY_BLUE,
            [
                (
                    int(gem_pos[0]) - (8 * gem_scaling),
                    int(gem_pos[1]),
                ),
                (
                    int(gem_pos[0]),
                    int(
                        gem_pos[1] - (14 * gem_scaling),
                    ),
                ),
                (
                    int(gem_pos[0] + (8 * gem_scaling)),
                    int(gem_pos[1]),
                ),
                (
                    int(gem_pos[0]),
                    int(gem_pos[1] + (14 * gem_scaling)),
                ),
            ],
        )

        # Draw the walls and doors
        self.draw_walls()
        self.draw_doors()
        # self.draw_wall_lines()

        # Update the display
        pygame.display.flip()

    def draw_walls(self):
        for wall in walls:
            pygame.draw.rect(
                self.screen,
                self.WALL_COLOR,
                wall["rect"],
            )

    def draw_gem_circle(self):
        # Draw the gem circle
        pygame.draw.circle(
            self.screen,
            self.BLUE_GRAY,
            (gem_circle[0], gem_circle[1]),
            gem_circle[2],
        )

    def draw_doors(self):
        # Draw doors on the walls
        door_width = Config.DOOR_WIDTH
        pygame.draw.rect(
            self.screen,
            self.YELLOW,
            (
                0,
                Config.SCREEN_HEIGHT // 2 - door_width,
                Config.WALL_WIDTH,
                door_width * 2,
            ),
        )
        pygame.draw.rect(
            self.screen,
            self.YELLOW,
            (
                Config.SCREEN_WIDTH - Config.WALL_WIDTH,
                Config.SCREEN_HEIGHT // 2 - door_width,
                Config.WALL_WIDTH,
                door_width * 2,
            ),
        )

    def draw_rays(self, ray_collection):
        rays = ray_collection.rays

        for ray in rays:
            start_pos = (int(ray.origin.x), int(ray.origin.y))
            end_point = ray.end_point
            print(f"Ray end point: {end_point}")
            end_pos = (int(end_point.x), int(end_point.y))

            pygame.draw.line(
                self.screen,
                self.RED,
                start_pos,
                end_pos,
                2,
            )

    def draw_flashlight(self, ray_collection: RayCollection):
        vertices = ray_collection.get_light_cone_vertices()
        if not vertices:
            return
        pygame.draw.polygon(
            self.screen,
            self.YELLOW,
            vertices,
        )

    def draw_wall_lines(self):
        """Draw the wall lines on the screen."""
        for line in wall_lines:
            pygame.draw.line(
                self.screen,
                self.WHITE,
                line[0],
                line[1],
                2,
            )

    def draw_end_message(self, text):
        """Draw text on the screen."""
        font_path = "assets/AVENGEANCE MIGHTIEST AVENGER.ttf"
        try:
            font = pygame.font.Font(font_path, 60)
        except FileNotFoundError:
            print(f"Font file not found: {font_path}. Using default font.")
            font = pygame.font.Font(None, 60)

        text_surface = font.render(text, True, self.BLACK)

        subtitle_font = pygame.font.Font(font_path, 30)
        subtitle_surface = subtitle_font.render(
            "Press ENTER to continue or ESC to exit", True, self.BLACK
        )

        # Backround rectangle for the text
        pygame.draw.rect(
            self.screen,
            self.WHITE,
            (
                Config.SCREEN_WIDTH // 2 - text_surface.get_width() // 2 - 40,
                Config.SCREEN_HEIGHT // 2 - text_surface.get_height() // 2 - 50,
                text_surface.get_width() + 80,
                text_surface.get_height() + 100,
            ),
            border_radius=10,
        )

        self.screen.blit(
            text_surface,
            (
                Config.SCREEN_WIDTH // 2 - text_surface.get_width() // 2,
                Config.SCREEN_HEIGHT // 2 - text_surface.get_height() // 2,
            ),
        )

        self.screen.blit(
            subtitle_surface,
            (
                Config.SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2,
                Config.SCREEN_HEIGHT // 2 + text_surface.get_height() // 2 + 10,
            ),
        )

        pygame.display.flip()
