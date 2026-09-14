import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".venv", "__pycache__"}


def python_files():
    return sorted(
        path
        for path in PROJECT_ROOT.rglob("*.py")
        if not any(part in EXCLUDED_PARTS for part in path.parts)
        and "tests" not in path.parts
    )


def test_all_python_files_parse():
    errors = []
    for path in python_files():
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            errors.append(f"{path.relative_to(PROJECT_ROOT)}: {exc}")
    assert not errors, "Python syntax errors found:\n" + "\n".join(errors)
