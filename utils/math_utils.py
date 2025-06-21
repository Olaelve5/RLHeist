from pygame.math import Vector2


def get_line_intersection(line1, line2):
    """Calculates the intersection point of two line segments"""
    p1, p2 = line1
    p3, p4 = line2

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    # Calculate the denominator
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    # Check if lines are parallel (denominator is zero)
    if denominator == 0:
        return None

    # Calculate the numerators for t and u
    t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
    u_num = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))

    # Calculate t and u
    t = t_num / denominator
    u = u_num / denominator

    # Check if the intersection point is within both line segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculate the intersection point
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return Vector2(ix, iy)

    # No intersection within the segments
    return None
