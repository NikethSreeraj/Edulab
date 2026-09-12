"""Deterministic intent and subject signals used before an LLM call."""

import re

INTENTS = {
    "SIMULATOR_STATE": ("current", "value", "state", "changed", "increase", "decrease", "graph"),
    "CALCULATE": ("calculate", "solve", "what is", "find", "compute"),
    "FORMULA": ("formula", "equation", "law"),
    "PRACTICE": ("practice", "quiz", "question", "test me"),
    "HINT": ("hint", "clue", "without answer"),
    "CODE_HELP": ("code", "python", "java", "c++", "javascript", "error", "program"),
    "DOCUMENT_QUESTION": ("document", "pdf", "uploaded", "textbook", "file"),
    "EXPLAIN": ("why", "explain", "how", "meaning", "understand"),
}

SUBJECTS = {
    "physics": ("physics", "force", "motion", "velocity", "circuit", "wave", "projectile"),
    "chemistry": ("chemistry", "molar", "mole", "ph", "acid", "base", "atom", "reaction"),
    "mathematics": ("math", "equation", "algebra", "calculus", "matrix", "probability", "quadratic"),
    "coding": ("code", "python", "java", "javascript", "c++", "compiler"),
}


def detect_intent(message):
    text = (message or "").lower()
    for intent, terms in INTENTS.items():
        if any(term in text for term in terms):
            return intent
    return "GENERAL"


def detect_subject(message, context=None):
    text = (message or "").lower()
    for subject, terms in SUBJECTS.items():
        if any(term in text for term in terms):
            return subject.title()
    context = context or {}
    return context.get("currentSubject") or "General"


def search_terms(message):
    return [term for term in re.findall(r"[a-zA-Z0-9+.-]+", (message or "").lower()) if len(term) > 1]
