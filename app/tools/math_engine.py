import math


def solve_quadratic(a, b, c):
    if a == 0:
        if b == 0:
            return None
        return (round(-c / b, 4),)
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return None
    root1 = (-b + math.sqrt(discriminant)) / (2 * a)
    root2 = (-b - math.sqrt(discriminant)) / (2 * a)
    return (round(root1, 4), round(root2, 4))


def derivative_polynomial(coefficients, x):
    # coefficients in descending degree order: ax^2 + bx + c -> [a, b, c]
    total = 0.0
    degree = len(coefficients) - 1
    for index, coeff in enumerate(coefficients[:-1]):
        power = degree - index
        total += coeff * power * (x ** (power - 1))
    return round(total, 4)


def matrix_determinant(matrix):
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("A 2x2 matrix is required.")
    a, b = matrix[0]
    c, d = matrix[1]
    return a * d - b * c


def solve_linear_system_2x2(a, b, c, d, e, f):
    """Solve ax + by = e and cx + dy = f."""
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("The system has no unique solution.")
    return {
        "x": round((e * d - b * f) / determinant, 6),
        "y": round((a * f - e * c) / determinant, 6),
    }


def descriptive_statistics(values):
    values = [float(value) for value in values]
    if not values:
        raise ValueError("At least one number is required.")
    ordered = sorted(values)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return {"count": len(values), "mean": round(mean, 6), "median": round(median, 6), "min": min(values), "max": max(values), "population_stddev": round(math.sqrt(variance), 6)}


def triangle_metrics(a, b, c):
    sides = [float(a), float(b), float(c)]
    if min(sides) <= 0 or sum(sides) <= 2 * max(sides):
        raise ValueError("The three sides do not form a triangle.")
    semi = sum(sides) / 2
    area = math.sqrt(semi * (semi - sides[0]) * (semi - sides[1]) * (semi - sides[2]))
    return {"perimeter": round(sum(sides), 6), "area": round(area, 6)}
