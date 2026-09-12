import math
import re

from app.tools.periodic_table import PERIODIC_TABLE


def molar_mass(formula):
    counts = parse_formula(formula)
    return round(sum(PERIODIC_TABLE[symbol]["mass"] * count for symbol, count in counts.items()), 3)


def parse_formula(formula):
    """Return element counts for formulas such as Al2(SO4)3."""
    tokens = re.findall(r"([A-Z][a-z]?|\(|\)|\d+)", (formula or "").strip())
    if not tokens or "".join(tokens) != (formula or "").strip():
        raise ValueError("Invalid chemical formula.")
    stack = [{}]
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "(":
            stack.append({})
        elif token == ")":
            if len(stack) == 1:
                raise ValueError("Unmatched closing parenthesis.")
            group = stack.pop()
            multiplier = int(tokens[index + 1]) if index + 1 < len(tokens) and tokens[index + 1].isdigit() else 1
            if multiplier != 1:
                index += 1
            for symbol, count in group.items():
                stack[-1][symbol] = stack[-1].get(symbol, 0) + count * multiplier
        elif token.isdigit():
            raise ValueError("A count must follow an element or closing parenthesis.")
        else:
            if token not in PERIODIC_TABLE:
                raise ValueError(f"Unsupported element: {token}")
            multiplier = int(tokens[index + 1]) if index + 1 < len(tokens) and tokens[index + 1].isdigit() else 1
            if multiplier != 1:
                index += 1
            stack[-1][token] = stack[-1].get(token, 0) + multiplier
        index += 1
    if len(stack) != 1:
        raise ValueError("Unclosed parenthesis.")
    return stack[0]


def solution_concentration(moles, volume_litres):
    volume_litres = float(volume_litres)
    if volume_litres <= 0:
        raise ValueError("Volume must be positive.")
    return round(float(moles) / volume_litres, 6)


def ph_from_concentration(concentration):
    concentration = float(concentration)
    if concentration <= 0:
        raise ValueError("Hydrogen ion concentration must be positive.")
    return round(-math.log10(concentration), 6)


def percent_composition(formula, target_element):
    mass_total = molar_mass(formula)
    target = molar_mass(target_element)
    return round((target / mass_total) * 100, 2)


def ideal_gas_law(pressure, volume, moles, temperature):
    gas_constant = 0.082057
    return round((pressure * volume) / (moles * temperature), 4)
