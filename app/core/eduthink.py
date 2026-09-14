from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class EduThinkPlan:
    intent: str
    subject: str
    needs_web: bool
    needs_tool: bool
    tool_hint: str | None


def build_plan(query: str, package: dict[str, Any]) -> EduThinkPlan:
    text = (query or "").lower().strip()
    intent = str(package.get("intent") or "GENERAL")
    subject = str(package.get("subject") or "General")
    needs_web = bool(package.get("web")) or bool(
        re.search(r"\b(latest|today|current|recent|news|internet|research|source)\b", text)
    )
    needs_tool = intent in {"CALCULATE", "FORMULA", "SIMULATOR_STATE", "CODE_HELP"}
    tool_hint = {
        "CALCULATE": "calculator",
        "FORMULA": "formula_sheet",
        "SIMULATOR_STATE": "simulator_state",
        "CODE_HELP": "coding_engine",
    }.get(intent)
    return EduThinkPlan(intent, subject, needs_web, needs_tool, tool_hint)


def build_prompt(query: str, package: dict[str, Any], mode: str = "explain") -> str:
    plan = build_plan(query, package)
    knowledge = package.get("knowledge") or []
    web = package.get("web") or []
    knowledge_text = "\n".join(
        f"- {item.get('title','Untitled')}: {item.get('summary','')}" for item in knowledge[:5]
    ) or "No retrieved knowledge entries."
    web_text = "\n".join(
        f"- {item.get('title','Web result')}: {item.get('snippet','')}" for item in web[:3]
    ) or "No web results."
    return f"""You are EduCore, the educational AI inside Edulab.

Mode: {mode}
Intent: {plan.intent}
Subject: {plan.subject}
Tool hint: {plan.tool_hint or 'none'}

Retrieved knowledge:
{knowledge_text}

Web evidence:
{web_text}

Simulator state:
{package.get('simulator') or 'none'}

User question:
{query}

Answer the actual question first. Prefer supplied evidence and deterministic tool results over guesses. For calculations, show formula, substitution, result, and units when useful. For explanations, use a compact example. Distinguish current/retrieved information from general knowledge. Keep the answer appropriate for a school learner. Do not reveal hidden reasoning.
"""
