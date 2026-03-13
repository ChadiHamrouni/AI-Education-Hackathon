from agents import function_tool

@function_tool
def calculate(operation: str, a: float, b: float) -> str:
    """Perform a basic arithmetic operation on two numbers.

    operation: one of 'add', 'subtract', 'multiply', 'divide'
    Use this for ALL numerical computations — never compute mentally.
    """
    op = operation.lower().strip()
    if op == "add":
        return f"{a} + {b} = {a + b}"
    elif op == "subtract":
        return f"{a} - {b} = {a - b}"
    elif op == "multiply":
        return f"{a} * {b} = {a * b}"
    elif op == "divide":
        if b == 0:
            return "Cannot divide by zero."
        return f"{a} / {b} = {a / b}"
    else:
        return f"Unknown operation '{operation}'. Use: add, subtract, multiply, divide."
