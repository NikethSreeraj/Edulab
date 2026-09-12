import math


def evaluate_expression(expression):
    expression = (expression or "").strip()
    if not expression:
        raise ValueError("Enter an expression to calculate.")

    safe_symbols = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log10,
        "ln": math.log,
        "sqrt": math.sqrt,
        "pi": math.pi,
        "e": math.e,
    }
    allowed = "0123456789+-*/().,%^_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
    for char in expression:
        if char not in allowed:
            raise ValueError(f"Unsupported character: {char}")

    expression = expression.replace("^", "**")
    expression = expression.replace("π", "pi")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("sin(", "sin(")
    expression = expression.replace("cos(", "cos(")
    expression = expression.replace("tan(", "tan(")

    try:
        result = eval(expression, {"__builtins__": {}}, safe_symbols)
        return float(result) if isinstance(result, float) else result
    except Exception as exc:
        raise ValueError(f"Could not evaluate expression: {exc}") from exc
