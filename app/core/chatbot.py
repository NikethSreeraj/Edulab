import json
import re

from app.core.ai_provider import LocalModelProvider, context_prompt
from app.services.knowledge_store import search_topics
from app.services.web_search import search_web
from app.utils.intent import detect_intent, detect_subject, search_terms


class RAGChatbot:
    def __init__(self, knowledge_base=None, provider=None):
        self.knowledge_base = knowledge_base or []
        self.provider = provider or LocalModelProvider()

    def _knowledge_matches(self, query):
        stored = sorted(search_topics(query), key=lambda item: self._relevance(item, query), reverse=True)[:5]
        if stored:
            return stored
        query_lower = query.lower()
        matches = []
        for item in self.knowledge_base:
            content = " ".join([
                item.get("title", ""), item.get("subject", ""), item.get("summary", ""),
                *item.get("facts", []), *item.get("activities", []),
            ]).lower()
            if query_lower in content or any(term in content for term in query_lower.split()):
                matches.append(item)
        return matches[:3] if matches else self.knowledge_base[:3]

    @staticmethod
    def _relevance(item, query):
        text = " ".join(str(item.get(key, "")) for key in ("title", "unit", "summary", "keywords", "formulas", "facts")).lower()
        terms = search_terms(query)
        return sum(100 if term in str(item.get("title", "")).lower() else 25 if term in text else 0 for term in terms)

    def web_search(self, query, limit=3):
        return search_web(query, limit)

    def _build_context(self, query, app_context=None):
        knowledge = self._knowledge_matches(query)
        context = app_context or {}
        web_requested = bool(re.search(r"\b(latest|today|current|research|web|internet|news)\b", query.lower()))
        web_results = self.web_search(query) if web_requested else []
        return {"intent": detect_intent(query), "subject": detect_subject(query, context), "knowledge": knowledge, "simulator": context.get("simulatorState", {}), "recentChanges": context.get("recentSimulatorChanges", []), "web": web_results}

    def generate_response(self, user_query, include_web_search=True, app_context=None, mode="explain"):
        package = self._build_context(user_query, app_context)
        if not include_web_search:
            package["web"] = []
        mode_instructions = {
            "summarize": "Summarize the supplied material in concise bullet points, then list key terms.",
            "explain": "Explain the idea step by step at the learner's level, using a small example.",
            "solve": "Solve the task step by step. Show formula, substitution, answer, and units where relevant. Point out common mistakes.",
        }
        instruction = mode_instructions.get(mode, mode_instructions["explain"])
        prompt = ("You are EduCore, Edulab's context-aware educational tutor. Answer at school level. "
                  "Use only relevant retrieved data and actual simulator values. Never invent values. "
                  "Do not reveal chain-of-thought. " + instruction + " "
                  f"MODE: {mode}\nUSER: {user_query}\nEDUCORE_CONTEXT: {context_prompt(package)}")
        try:
            generated = self.provider.generate(prompt)
            if generated:
                return generated
        except Exception:
            pass
        return self._fallback_response(user_query, package, mode)

    def _fallback_response(self, user_query, package, mode="explain"):
        query = user_query.strip()
        if not query:
            return "Ask me about a topic, simulator, calculation, document, or study question and I will help explain it."

        topic = query.lower()
        if "math" in topic or "equation" in topic or "algebra" in topic:
            answer = "For mathematics, identify the unknown, choose the relevant formula, substitute carefully, and check the result."
        elif "physics" in topic or "force" in topic or "motion" in topic:
            answer = "For physics, identify the known quantities, choose a model, keep units consistent, and check whether the result is physically reasonable."
        elif "chem" in topic or "ph" in topic or "mole" in topic:
            answer = "For chemistry, identify the species and units first, then use the balanced relationship or concentration formula before calculating."
        else:
            answer = "I can help explain a concept, calculate a result, inspect the current simulator state, search EduCore knowledge, or look up current web information."

        if mode == "summarize":
            answer = "Key points:\n" + answer
        elif mode == "solve":
            answer += "\n\nSolution pattern: identify the known values, select the relevant relationship, substitute with units, then check the result."

        if package.get("web"):
            web_summary = "\n".join(f"- {item.get('title', 'Source')}: {item.get('snippet', '')}" for item in package["web"][:2])
            answer += f"\n\nWeb context:\n{web_summary}"

        if package.get("knowledge"):
            item = package["knowledge"][0]
            answer += f"\n\nEduCore context: {item.get('title', '')}. {item.get('summary', '')}"
        if package.get("simulator"):
            answer += f"\n\nCurrent simulator values: {json.dumps(package['simulator'], ensure_ascii=False)}"

        return answer
