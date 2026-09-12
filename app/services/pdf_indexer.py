import json
from pathlib import Path

INDEX_PATH = Path(__file__).resolve().parents[1] / "data" / "pdf_index.json"


def index_pdf_text(file_path, text):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    if INDEX_PATH.exists():
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as file:
                entries = json.load(file)
        except Exception:
            entries = []

    entries.append({
        "file": str(file_path),
        "text": text[:5000],
    })

    with open(INDEX_PATH, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2)

    return entries


def get_indexed_documents():
    if not INDEX_PATH.exists():
        return []
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []
