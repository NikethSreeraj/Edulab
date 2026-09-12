import math


def projectile_metrics(initial_velocity, angle_degrees, height=0):
    angle = math.radians(angle_degrees)
    vx = initial_velocity * math.cos(angle)
    vy = initial_velocity * math.sin(angle)
    time_to_ground = (vy + math.sqrt(vy ** 2 + 2 * 9.81 * height)) / 9.81
    range_distance = vx * time_to_ground
    max_height = (vy ** 2) / (2 * 9.81) + height
    return {
        "vx": round(vx, 2),
        "vy": round(vy, 2),
        "time": round(time_to_ground, 2),
        "range": round(range_distance, 2),
        "max_height": round(max_height, 2),
    }
