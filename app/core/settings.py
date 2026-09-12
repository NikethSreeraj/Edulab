import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parents[1] / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "light",
    "accent": "#2d7dd2",
    "font_scale": 1.0,
    "web_search": True,
    "rag_enabled": True,
    "auto_save": True,
    "pdf_indexing": True,
    "show_tool_tips": True,
}


def load_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def update_settings(changes):
    settings = load_settings()
    settings.update(changes)
    save_settings(settings)
    return settings
