"""Persistent educational knowledge store used by search, RAG, and the UI."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
KNOWLEDGE_PATH = DATA_DIR / "knowledge.json"
USER_DATA_PATH = DATA_DIR / "user_data.json"

SEED_KNOWLEDGE = {
    "version": 1,
    "topics": [
        {
            "id": "physics-kinematics",
            "subject": "Physics",
            "unit": "Mechanics",
            "title": "Kinematics",
            "summary": "Describes motion using displacement, velocity, acceleration, and time.",
            "formulas": ["v = u + at", "s = ut + 1/2 at^2", "v^2 = u^2 + 2as"],
            "facts": ["Acceleration is the rate of change of velocity.", "SI units are metre, second, and metre per second squared."],
            "keywords": ["motion", "velocity", "acceleration", "kinematics"]
        },
        {
            "id": "physics-dynamics",
            "subject": "Physics",
            "unit": "Mechanics",
            "title": "Newton's Laws",
            "summary": "Newton's laws connect force, mass, acceleration, and momentum.",
            "formulas": ["F = ma", "p = mv", "W = Fs cos(theta)"],
            "facts": ["Forces are vectors and are measured in newtons.", "The net force determines acceleration."],
            "keywords": ["force", "mass", "newton", "momentum", "work"]
        },
        {
            "id": "physics-energy",
            "subject": "Physics",
            "unit": "Energy",
            "title": "Work, Energy and Power",
            "summary": "Energy is transferred by work and the rate of transfer is power.",
            "formulas": ["KE = 1/2 mv^2", "PE = mgh", "P = W/t"],
            "facts": ["Energy is measured in joules.", "Power is measured in watts."],
            "keywords": ["energy", "kinetic", "potential", "power", "joule"]
        },
        {
            "id": "physics-electricity",
            "subject": "Physics",
            "unit": "Electricity",
            "title": "Circuits and Ohm's Law",
            "summary": "Voltage, current, and resistance describe simple electrical circuits.",
            "formulas": ["V = IR", "P = VI", "R_series = R1 + R2", "1/R_parallel = 1/R1 + 1/R2"],
            "facts": ["Current is charge flow per second.", "Resistance is measured in ohms."],
            "keywords": ["voltage", "current", "resistance", "circuit", "ohm"]
        },
        {
            "id": "physics-waves",
            "subject": "Physics",
            "unit": "Waves",
            "title": "Waves and Sound",
            "summary": "Waves transfer energy and are described by frequency, wavelength, and speed.",
            "formulas": ["v = f lambda", "T = 1/f", "I = P/A"],
            "facts": ["Frequency is measured in hertz.", "Sound needs a medium to travel."],
            "keywords": ["wave", "sound", "frequency", "wavelength", "amplitude"]
        },
        {
            "id": "chemistry-matter",
            "subject": "Chemistry",
            "unit": "Matter",
            "title": "Atoms and the Periodic Table",
            "summary": "Atoms contain protons, neutrons, and electrons arranged into energy levels.",
            "formulas": ["A = Z + N", "charge = protons - electrons"],
            "facts": ["Atomic number is the number of protons.", "Isotopes have the same proton count but different neutron counts."],
            "keywords": ["atom", "proton", "neutron", "electron", "periodic"]
        },
        {
            "id": "chemistry-stoichiometry",
            "subject": "Chemistry",
            "unit": "Reactions",
            "title": "Stoichiometry",
            "summary": "Balanced equations provide mole ratios for quantitative chemical calculations.",
            "formulas": ["n = m/M", "C = n/V", "% yield = actual/theoretical x 100"],
            "facts": ["Equations must conserve each element.", "The limiting reagent determines the maximum product."],
            "keywords": ["mole", "mass", "molar", "stoichiometry", "reaction"]
        },
        {
            "id": "chemistry-solutions",
            "subject": "Chemistry",
            "unit": "Solutions",
            "title": "Solutions and Concentration",
            "summary": "Concentration describes how much solute is present in a given amount of solution.",
            "formulas": ["M = n/V", "C1V1 = C2V2", "m = n/kg solvent"],
            "facts": ["Molarity uses litres of solution.", "Dilution changes concentration but not solute moles."],
            "keywords": ["molarity", "molality", "dilution", "solution", "concentration"]
        },
        {
            "id": "chemistry-acids",
            "subject": "Chemistry",
            "unit": "Acids and Bases",
            "title": "Acids, Bases and pH",
            "summary": "The pH scale describes hydrogen ion concentration in aqueous solutions.",
            "formulas": ["pH = -log10[H+ ]", "pOH = -log10[OH-]", "pH + pOH = 14"],
            "facts": ["At 25 C, pH 7 is neutral.", "A one-unit pH change represents a tenfold concentration change."],
            "keywords": ["acid", "base", "ph", "neutralization", "buffer"]
        },
        {
            "id": "math-algebra",
            "subject": "Mathematics",
            "unit": "Algebra",
            "title": "Algebra and Quadratics",
            "summary": "Algebra uses symbols and rules to represent relationships and solve unknowns.",
            "formulas": ["x = (-b +/- sqrt(b^2 - 4ac))/(2a)", "(a+b)^2 = a^2 + 2ab + b^2"],
            "facts": ["The discriminant classifies the roots of a quadratic.", "Always check solutions in the original equation."],
            "keywords": ["algebra", "quadratic", "equation", "roots", "factor"]
        },
        {
            "id": "math-functions",
            "subject": "Mathematics",
            "unit": "Functions",
            "title": "Functions and Graphs",
            "summary": "A function maps each allowed input to exactly one output.",
            "formulas": ["slope = (y2-y1)/(x2-x1)", "y = mx + c", "distance = sqrt((x2-x1)^2 + (y2-y1)^2)"],
            "facts": ["The domain contains valid inputs.", "The range contains resulting outputs."],
            "keywords": ["function", "graph", "slope", "line", "domain", "range"]
        },
        {
            "id": "math-calculus",
            "subject": "Mathematics",
            "unit": "Calculus",
            "title": "Derivatives and Integrals",
            "summary": "Derivatives measure instantaneous change and integrals accumulate quantities.",
            "formulas": ["d/dx x^n = nx^(n-1)", "integral x^n dx = x^(n+1)/(n+1) + C", "integral_a^b f(x) dx = F(b)-F(a)"],
            "facts": ["A derivative is the slope of a curve.", "A definite integral represents signed area."],
            "keywords": ["calculus", "derivative", "integral", "limit", "area"]
        },
        {
            "id": "math-statistics",
            "subject": "Mathematics",
            "unit": "Statistics",
            "title": "Probability and Statistics",
            "summary": "Statistics summarizes data while probability models uncertain events.",
            "formulas": ["mean = sum(x)/n", "P(A or B) = P(A)+P(B)-P(A and B)", "z = (x-mu)/sigma"],
            "facts": ["The median is less sensitive to outliers than the mean.", "Probability lies between zero and one."],
            "keywords": ["probability", "statistics", "mean", "median", "normal", "data"]
        }
    ]
}


def _read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except (OSError, ValueError):
        return default


def ensure_store():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not KNOWLEDGE_PATH.exists():
        KNOWLEDGE_PATH.write_text(json.dumps(SEED_KNOWLEDGE, indent=2), encoding="utf-8")
    if not USER_DATA_PATH.exists():
        USER_DATA_PATH.write_text(json.dumps({"notes": [], "saved_files": []}, indent=2), encoding="utf-8")


def get_topics():
    ensure_store()
    return _read_json(KNOWLEDGE_PATH, SEED_KNOWLEDGE).get("topics", [])


def search_topics(query="", subject="all"):
    query_terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 1]
    results = []
    for topic in get_topics():
        if subject != "all" and topic.get("subject") != subject:
            continue
        haystack = " ".join(str(topic.get(key, "")) for key in ("title", "unit", "summary", "keywords", "formulas", "facts")).lower()
        score = sum(haystack.count(term) for term in query_terms)
        if not query_terms or score:
            results.append({**topic, "score": score})
    return sorted(results, key=lambda item: (-item["score"], item.get("title", "")))


def store_user_data(changes):
    ensure_store()
    data = _read_json(USER_DATA_PATH, {"notes": [], "saved_files": []})
    data.update(changes)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    USER_DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def get_store_summary():
    topics = get_topics()
    return {
        "topics": len(topics),
        "formulas": sum(len(item.get("formulas", [])) for item in topics),
        "facts": sum(len(item.get("facts", [])) for item in topics),
        "subjects": sorted({item.get("subject") for item in topics}),
        "knowledge_file": str(KNOWLEDGE_PATH),
    }
