"""Provider abstraction for EduCore's optional AI backend."""

import json
import os

import requests


class AIProvider:
    def generate(self, prompt, model=None):
        raise NotImplementedError


class LocalModelProvider(AIProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model_or_default()

    def generate(self, prompt, model=None):
        response = requests.post(f"{self.base_url}/api/generate", json={"model": model or self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.25}}, timeout=45)
        response.raise_for_status()
        return response.json().get("response", "").strip()


def model_or_default():
    return os.getenv("EDULAB_LLM_MODEL", "qwen2.5:0.5b")


def context_prompt(context):
    return json.dumps(context, ensure_ascii=False, default=str)
