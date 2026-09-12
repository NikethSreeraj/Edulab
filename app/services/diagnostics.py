"""Runtime diagnostics for the Edulab task-manager style panel."""

import ast
import time
from pathlib import Path

from app.services.knowledge_store import get_store_summary

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def scan_project():
    files = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file() or any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        item = {
            "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "size": path.stat().st_size,
            "status": "ready",
            "detail": "",
        }
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"))
                item["detail"] = "Python syntax OK"
            except (OSError, SyntaxError) as exc:
                item["status"] = "error"
                item["detail"] = str(exc)
        files.append(item)
    return files


def get_diagnostics():
    files = scan_project()
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": files,
        "file_count": len(files),
        "errors": sum(item["status"] == "error" for item in files),
        "knowledge": get_store_summary(),
        "accessed": ["app/ui/web_app.py", "app/services/knowledge_store.py", "app/core/chatbot.py"],
        "note": "Access tracking is process-local; this panel reports the files scanned and core files used by the web app.",
    }
