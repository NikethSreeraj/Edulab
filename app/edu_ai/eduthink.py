"""EduThink: lightweight orchestration and response-quality layer for EduCore."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ThoughtPlan:
    """Structured plan used internally; it never exposes private reasoning."""

    intent: str
    subject: str
    mode: str
    tools: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class EduThink:
    """Plan tool usage and validate an educational answer without chain-of-thought."""

    WEB_TERMS = {"latest", "today", "current", "news", "research", "internet", "web"}

    def plan(self, query: str, intent: str = "GENERAL", subject: str = "General", mode: str = "explain", context=None) -> ThoughtPlan:
        text = (query or "").lower()
        tools = []
        if intent == "CALCULATE" or any(token in text for token in ("calculate", "compute", "evaluate")):
            tools.append("calculator")
        if intent == "FORMULA" or "formula" in text or "equation" in text:
            tools.append("formula_sheet")
        if intent == "SIMULATOR_STATE":
            tools.append("simulator")
        if intent == "CODE_HELP" or any(token in text for token in ("python", "javascript", "java", "c++", "compile", "code")):
            tools.append("coding_engine")
        if self.WEB_TERMS.intersection(set(text.split())):
            tools.append("web_search")
        return ThoughtPlan(intent=intent, subject=subject, mode=mode, tools=tools, context=context or {})

    @staticmethod
    def validate(answer: str) -> str:
        """Apply cheap output hygiene while preserving the model's answer."""
        text = (answer or "").strip()
        if not text:
            return "I couldn't generate a response. Try asking the question in a little more detail."
        # Avoid accidentally presenting hidden-reasoning labels to the learner.
        for marker in ("chain of thought:", "hidden reasoning:", "private reasoning:"):
            if marker in text.lower():
                return "I can provide the result and a clear explanation, but not private reasoning."
        return text
