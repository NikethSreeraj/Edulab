"""Small graph-data analysis utility for tutor explanations."""


def analyze_graph(points):
    points = [{"x": float(point["x"]), "y": float(point["y"])} for point in (points or [])]
    if not points:
        raise ValueError("No graph points supplied.")
    maximum = max(points, key=lambda point: point["y"])
    minimum = min(points, key=lambda point: point["y"])
    slope = None
    if len(points) > 1 and points[-1]["x"] != points[0]["x"]:
        slope = (points[-1]["y"] - points[0]["y"]) / (points[-1]["x"] - points[0]["x"])
    return {"count": len(points), "maximum": maximum, "minimum": minimum, "overallSlope": slope}
