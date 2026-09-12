"""Optional image understanding and generation adapters.

Image understanding uses Ollama vision models when configured. Generation is
provider-neutral and uses EDULAB_IMAGE_API_URL when supplied; no fake image is
returned when a provider is unavailable.
"""

import base64
import os
from pathlib import Path

import requests


def inspect_image(file_path, prompt="Describe this educational image and identify useful labels or equations."):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    model = os.getenv("EDULAB_VISION_MODEL", os.getenv("EDULAB_LLM_MODEL", "qwen2.5:0.5b"))
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    response = requests.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "images": [encoded], "stream": False}, timeout=45)
    response.raise_for_status()
    return {"model": model, "description": response.json().get("response", "")}


def generate_image(prompt, size="1024x1024"):
    endpoint = os.getenv("EDULAB_IMAGE_API_URL")
    if not endpoint:
        raise RuntimeError("Image generation is not configured. Set EDULAB_IMAGE_API_URL to a compatible image API.")
    response = requests.post(endpoint, json={"prompt": prompt, "size": size}, timeout=90)
    response.raise_for_status()
    return response.json()
