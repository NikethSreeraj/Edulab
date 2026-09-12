"""Combined Physics, Chemistry, Mathematics (PCM) study actions."""

from app.tools.chemistry_tools import molar_mass, ph_from_concentration, solution_concentration
from app.tools.math_engine import solve_quadratic
from app.tools.physics_engine import electrical_power, projectile_state


PCM_ACTIONS = {
    "quadratic": "Solve ax^2 + bx + c = 0",
    "projectile": "Calculate projectile trajectory points",
    "ohms_law": "Calculate voltage, current, resistance, and power",
    "molar_mass": "Calculate a compound molar mass",
    "molarity": "Calculate solution concentration",
    "ph": "Calculate pH from hydrogen ion concentration",
}


def run_pcm(action, values):
    if action == "quadratic":
        roots = solve_quadratic(float(values["a"]), float(values["b"]), float(values["c"]))
        return {"roots": roots}
    if action == "projectile":
        return projectile_state(values["velocity"], values["angle"], values.get("gravity", 9.81))
    if action == "ohms_law":
        return electrical_power(values.get("voltage"), values.get("current"), values.get("resistance"))
    if action == "molar_mass":
        return {"formula": values["formula"], "molar_mass": molar_mass(values["formula"])}
    if action == "molarity":
        return {"molarity": solution_concentration(values["moles"], values["volume"])}
    if action == "ph":
        return {"ph": ph_from_concentration(values["concentration"])}
    raise ValueError(f"Unknown PCM action: {action}")
