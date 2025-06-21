from config import Config
import math
from pygame.math import Vector2
from utils.math_utils import get_line_intersection


class Ray:
    def __init__(self, origin, angle):
        self.origin = origin
        self.angle = angle
        self.length = Config.FLASHLIGHT_DISTANCE
        self.end_point = self._calculate_max_endpoint()

    def _calculate_max_endpoint(self):
        """Calculate the end point of the ray based on origin, angle, and length."""
        angle_rad = math.radians(self.angle)
        end_x = self.origin.x + self.length * math.cos(angle_rad)
        end_y = self.origin.y + self.length * math.sin(angle_rad)
        return Vector2(end_x, end_y)

    def set_end_point(self, end_point):
        """Set the end point of the ray directly."""
        self.end_point = end_point
        self.length = self.origin.distance_to(end_point)

    def reset(self):
        """Resets the ray to its maximum length and default endpoint."""
        self.length = Config.FLASHLIGHT_DISTANCE
        self.end_point = self._calculate_max_endpoint()


class RayCollection:
    def __init__(self, origin, ray_count=30):
        self.origin = origin
        self.rays = self.create_rays(ray_count)

    def create_rays(self, ray_count, origin_angle=0):
        rays = []
        angle_increment = Config.FLASHLIGHT_FOV / ray_count
        for i in range(ray_count):
            angle = -Config.FLASHLIGHT_FOV / 2 + i * angle_increment
            rays.append(Ray(self.origin, angle))
        return rays

    # This is now the main "controller" method for the collection.
    def update(self, new_origin, new_origin_angle, wall_lines):
        """
        Updates the origin and angle of all rays and handles their collisions.
        """
        self.origin = new_origin

        angle_increment = Config.FLASHLIGHT_FOV / (len(self.rays) - 1)
        start_angle = new_origin_angle - Config.FLASHLIGHT_FOV / 2

        for i, ray in enumerate(self.rays):
            # Update each ray's position and angle
            ray.origin = new_origin
            ray.angle = start_angle + i * angle_increment

            # Reset the ray to its max length before checking collisions
            ray.reset()

            # Find the closest collision point for this specific ray
            closest_point = self._find_closest_intersection(ray, wall_lines)

            # If a collision was found, update the ray's endpoint
            if closest_point:
                ray.set_end_point(closest_point)

    def _find_closest_intersection(self, ray: Ray, wall_lines: list):
        """
        Checks a single ray against all walls and returns the closest hit point.
        """
        closest_intersection = None
        min_distance = float("inf")

        for wall_line in wall_lines:
            intersection_point = get_line_intersection(
                (ray.origin, ray.end_point), wall_line
            )

            if intersection_point:
                distance = ray.origin.distance_to(intersection_point)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = intersection_point

        return closest_intersection

    def get_light_cone_vertices(self):
        """Returns a list of points for drawing the light cone polygon."""
        # The first vertex is the light source itself
        vertices = [self.origin]
        # The rest are the endpoints of all the rays
        for ray in self.rays:
            vertices.append(ray.end_point)
        return vertices

    def is_thief_visible(self, thief_pos, agent_radius, guard_angle, wall_lines):
        vector_to_thief = thief_pos - self.origin
        distance_to_thief = vector_to_thief.length()

        if distance_to_thief > Config.FLASHLIGHT_DISTANCE + agent_radius:
            return False  # Thief is too far away

        guard_forward_vector = Vector2()
        guard_forward_vector.from_polar((1, guard_angle))
        vector_to_thief_normalized = vector_to_thief.normalize()
        dot_product = guard_forward_vector.dot(vector_to_thief_normalized)
        fov_cosine_threshold = math.cos(math.radians(Config.FLASHLIGHT_FOV / 2))

        if dot_product < fov_cosine_threshold:
            return False  # Thief is outside the flashlight's field of view

        line_of_sight = (self.origin, thief_pos)
        for wall_line in wall_lines:
            intersection = get_line_intersection(line_of_sight, wall_line)
            if intersection:
                # If there's an intersection, the thief is not visible
                return False

        return True
