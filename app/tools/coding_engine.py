"""Lightweight coding assistant and local compiler adapter."""

import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANGUAGE_INFO = {
    "python": {"extension": ".py", "compiler": None, "run": True},
    "javascript": {"extension": ".js", "compiler": "node", "run": True},
    "c": {"extension": ".c", "compiler": "gcc", "run": True},
    "cpp": {"extension": ".cpp", "compiler": "g++", "run": True},
    "java": {"extension": ".java", "compiler": "javac", "run": True},
    "html": {"extension": ".html", "compiler": None, "run": False},
}

LANGUAGE_TEMPLATES = {
    "python": "print('Hello, Edulab')\n",
    "javascript": "console.log('Hello, Edulab');\n",
    "c": '#include <stdio.h>\n\nint main(void) {\n    printf("Hello, Edulab\\n");\n    return 0;\n}\n',
    "cpp": '#include <iostream>\n\nint main() {\n    std::cout << "Hello, Edulab\\n";\n    return 0;\n}\n',
    "java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, Edulab");\n    }\n}\n',
    "html": '<!doctype html>\n<html><body><h1>Hello, Edulab</h1></body></html>\n',
}

CODE_LIBRARY = {
    "python": {
        "builtins": ["print", "len", "range", "sum", "min", "max", "enumerate"],
        "libraries": ["math", "statistics", "random", "datetime", "pathlib"],
    },
    "javascript": {
        "builtins": ["console.log", "Array", "Object", "Math", "JSON", "Date"],
        "libraries": ["node:fs", "node:path", "node:http"],
    },
    "c": {"builtins": ["printf", "scanf", "malloc", "free"], "libraries": ["stdio.h", "stdlib.h", "string.h", "math.h"]},
    "cpp": {"builtins": ["std::cout", "std::cin", "std::vector", "std::string"], "libraries": ["iostream", "vector", "string", "algorithm"]},
    "java": {"builtins": ["System.out.println", "String", "Math", "Integer"], "libraries": ["java.util", "java.io", "java.time"]},
    "html": {"builtins": ["<h1>", "<p>", "<button>", "<input>"], "libraries": ["CSS", "JavaScript"]},
}


def language_template(language):
    return LANGUAGE_TEMPLATES.get((language or "python").lower(), "")


def analyze_code(code, language):
    language = (language or "python").lower()
    code = code or ""
    result = {"language": language, "syntax": "valid", "error": None, "line": None, "column": None, "hints": [], "library": CODE_LIBRARY.get(language, {})}
    if language == "python":
        try:
            ast.parse(code)
        except SyntaxError as exc:
            result.update({"syntax": "error", "error": exc.msg, "line": exc.lineno, "column": exc.offset})
            result["hints"].append("Check the highlighted line for missing colons, brackets, or indentation.")
    elif language == "javascript":
        if code.count("{") != code.count("}"):
            result.update({"syntax": "error", "error": "Unbalanced curly braces"})
            result["hints"].append("Make sure every opening brace has a matching closing brace.")
    return result


def explain_code(code, language):
    code = (code or "").strip()
    if not code:
        return "Start with a small example and I will explain it line by line."
    if language == "python":
        analysis = analyze_code(code, language)
        if analysis["syntax"] == "error":
            return f"Python mistake on line {analysis['line']}, column {analysis['column']}: {analysis['error']}. Check brackets, colons, and indentation on that line."
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return f"Python syntax is valid. It contains {len(functions)} function(s): {', '.join(functions) or 'none'}. Trace inputs, transformations, and outputs."
    return f"{language.upper()} code received. Look for the entry point, data types, control flow, and output statements."


def run_code(code, language, timeout=8):
    language = (language or "python").lower()
    if language not in LANGUAGE_INFO:
        raise ValueError(f"Unsupported language: {language}")
    if not (code or "").strip():
        return {"output": "No code entered.", "status": "empty", "explain": explain_code(code, language)}
    if language == "html":
        return {"output": "HTML is ready for browser preview.", "status": "preview", "source": code, "explain": explain_code(code, language)}
    if language == "python":
        ast.parse(code)
    info = LANGUAGE_INFO[language]
    with tempfile.TemporaryDirectory(prefix="edulab-code-") as directory:
        source = Path(directory) / ("Main" + info["extension"] if language == "java" else "main" + info["extension"])
        source.write_text(code, encoding="utf-8")
        if info["compiler"] is None:
            command = [sys.executable, str(source)]
        elif language == "javascript":
            command = [info["compiler"], str(source)]
        else:
            compiler = shutil.which(info["compiler"])
            if not compiler:
                return {"output": f"{language} compiler '{info['compiler']}' is not installed.", "status": "unavailable", "explain": explain_code(code, language)}
            binary = Path(directory) / ("main.exe" if language in {"c", "cpp"} else "Main.class")
            if language == "java":
                compile_result = subprocess.run([compiler, str(source)], capture_output=True, text=True, timeout=timeout, cwd=directory)
                if compile_result.returncode:
                    return {"output": compile_result.stderr or compile_result.stdout, "status": "compile_error", "explain": explain_code(code, language)}
                command = ["java", "-cp", directory, "Main"]
            else:
                compile_result = subprocess.run([compiler, str(source), "-o", str(binary)], capture_output=True, text=True, timeout=timeout, cwd=directory)
                if compile_result.returncode:
                    return {"output": compile_result.stderr or compile_result.stdout, "status": "compile_error", "explain": explain_code(code, language)}
                command = [str(binary)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=directory)
        return {"output": result.stdout or result.stderr or "Program finished without output.", "status": "ok" if result.returncode == 0 else "runtime_error", "explain": explain_code(code, language)}
