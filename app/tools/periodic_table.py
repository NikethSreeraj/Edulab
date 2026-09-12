PERIODIC_TABLE = {
    "H": {"number": 1, "mass": 1.008, "group": "Nonmetal"},
    "He": {"number": 2, "mass": 4.0026, "group": "Noble gas"},
    "Li": {"number": 3, "mass": 6.94, "group": "Alkali metal"},
    "Be": {"number": 4, "mass": 9.0122, "group": "Alkaline earth metal"},
    "B": {"number": 5, "mass": 10.81, "group": "Metalloid"},
    "C": {"number": 6, "mass": 12.011, "group": "Nonmetal"},
    "N": {"number": 7, "mass": 14.007, "group": "Nonmetal"},
    "O": {"number": 8, "mass": 15.999, "group": "Nonmetal"},
    "F": {"number": 9, "mass": 18.998, "group": "Halogen"},
    "Ne": {"number": 10, "mass": 20.180, "group": "Noble gas"},
    "Na": {"number": 11, "mass": 22.990, "group": "Alkali metal"},
    "Mg": {"number": 12, "mass": 24.305, "group": "Alkaline earth metal"},
    "Al": {"number": 13, "mass": 26.982, "group": "Metal"},
    "Si": {"number": 14, "mass": 28.085, "group": "Metalloid"},
    "P": {"number": 15, "mass": 30.974, "group": "Nonmetal"},
    "S": {"number": 16, "mass": 32.06, "group": "Nonmetal"},
    "Cl": {"number": 17, "mass": 35.45, "group": "Halogen"},
    "Ar": {"number": 18, "mass": 39.948, "group": "Noble gas"},
    "Ca": {"number": 20, "mass": 40.078, "group": "Alkaline earth metal"},
    "Fe": {"number": 26, "mass": 55.845, "group": "Transition metal"},
    "Cu": {"number": 29, "mass": 63.546, "group": "Transition metal"},
    "Zn": {"number": 30, "mass": 65.38, "group": "Transition metal"},
}


def get_element(symbol):
    symbol = (symbol or "").strip().title()
    if symbol in PERIODIC_TABLE:
        return PERIODIC_TABLE[symbol]
    if symbol.lower() in {key.lower(): value for key, value in PERIODIC_TABLE.items()}:
        lookup = {key.lower(): value for key, value in PERIODIC_TABLE.items()}
        return lookup[symbol.lower()]
    return None
