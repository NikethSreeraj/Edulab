import math


class ResistiveCircuit:
    def __init__(self, resistors):
        self.resistors = [float(value) for value in resistors]
        if any(value < 0 for value in self.resistors):
            raise ValueError("Resistance cannot be negative.")

    def series_resistance(self):
        return sum(self.resistors)

    def parallel_resistance(self):
        total = sum(1 / r for r in self.resistors if r != 0)
        return 1 / total if total else 0

    def voltage_divider(self, input_voltage, resistor_index):
        total = self.series_resistance()
        if total == 0:
            return 0
        return input_voltage * (self.resistors[resistor_index] / total)


class ProjectileMotion:
    def __init__(self, velocity, angle_deg, gravity=9.81):
        self.velocity = velocity
        self.angle = math.radians(angle_deg)
        self.gravity = gravity

    def time_of_flight(self):
        return (2 * self.velocity * math.sin(self.angle)) / self.gravity

    def range(self):
        return (self.velocity ** 2 * math.sin(2 * self.angle)) / self.gravity

    def max_height(self):
        return (self.velocity ** 2 * math.sin(self.angle) ** 2) / (2 * self.gravity)


class MotionEquations:
    def __init__(self, initial_velocity, acceleration, time):
        self.u = initial_velocity
        self.a = acceleration
        self.t = time

    def final_velocity(self):
        return self.u + self.a * self.t

    def displacement(self):
        return self.u * self.t + 0.5 * self.a * self.t ** 2

    def average_velocity(self):
        return (self.u + self.final_velocity()) / 2


def projectile_state(velocity, angle_deg, gravity=9.81, samples=21):
    """Return calculated values and points for a lightweight browser chart."""
    motion = ProjectileMotion(float(velocity), float(angle_deg), float(gravity))
    duration = motion.time_of_flight()
    points = []
    for index in range(max(2, int(samples))):
        time = duration * index / (max(2, int(samples)) - 1)
        radians = motion.angle
        points.append({
            "t": round(time, 4),
            "x": round(motion.velocity * math.cos(radians) * time, 4),
            "y": round(motion.velocity * math.sin(radians) * time - 0.5 * motion.gravity * time ** 2, 4),
        })
    return {"time": round(duration, 6), "range": round(motion.range(), 6), "max_height": round(motion.max_height(), 6), "points": points}


def free_fall(height, gravity=9.81):
    height = float(height)
    gravity = float(gravity)
    if height < 0 or gravity <= 0:
        raise ValueError("Height must be non-negative and gravity must be positive.")
    return {"time": math.sqrt(2 * height / gravity), "impact_speed": math.sqrt(2 * gravity * height)}


def electrical_power(voltage=None, current=None, resistance=None):
    values = {"voltage": voltage, "current": current, "resistance": resistance}
    known = {key: float(value) for key, value in values.items() if value is not None}
    if len(known) != 2:
        raise ValueError("Provide exactly two of voltage, current, and resistance.")
    if voltage is None:
        voltage = current * resistance
    elif current is None:
        current = voltage / resistance
    else:
        resistance = voltage / current
    return {"voltage": float(voltage), "current": float(current), "resistance": float(resistance), "power": float(voltage * current)}
