from app.tools.calculator import evaluate_expression
from app.tools.chemistry_tools import molar_mass
from app.tools.physics_engine import ResistiveCircuit, ProjectileMotion
from app.tools.math_engine import solve_quadratic
from app.tools.formula_sheet import get_formula_group
from app.core.settings import load_settings

assert abs(float(evaluate_expression("sin(pi/2) + 2")) - 3.0) < 1e-6
assert abs(molar_mass("H2O") - 18.015) < 1e-3
assert ResistiveCircuit([10, 20, 30]).series_resistance() == 60
assert abs(ProjectileMotion(20, 30).range() - 35.41) < 1.0
assert solve_quadratic(1, -3, 2) == (2.0, 1.0)
assert "ohm_law" in get_formula_group("physics")
assert "theme" in load_settings()
print("smoke-ok")
