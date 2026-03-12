from agents import function_tool, RunContextWrapper
from src.guardrails.output_guards import MathRunContext


@function_tool
def add(ctx: RunContextWrapper[MathRunContext], a: float, b: float) -> str:
    """Add two numbers together. Use this tool for any addition operation.

    Args:
        a: The first number.
        b: The second number.
    """
    result = a + b
    output = f"add({a}, {b}) = {result}"
    if isinstance(ctx.context, MathRunContext):
        ctx.context.record_call("add", output)
    return output


@function_tool
def subtract(ctx: RunContextWrapper[MathRunContext], a: float, b: float) -> str:
    """Subtract the second number from the first. Use this tool for any subtraction operation.

    Args:
        a: The number to subtract from.
        b: The number to subtract.
    """
    result = a - b
    output = f"subtract({a}, {b}) = {result}"
    if isinstance(ctx.context, MathRunContext):
        ctx.context.record_call("subtract", output)
    return output


@function_tool
def multiply(ctx: RunContextWrapper[MathRunContext], a: float, b: float) -> str:
    """Multiply two numbers together. Use this tool for any multiplication operation.

    Args:
        a: The first number.
        b: The second number.
    """
    result = a * b
    output = f"multiply({a}, {b}) = {result}"
    if isinstance(ctx.context, MathRunContext):
        ctx.context.record_call("multiply", output)
    return output


@function_tool
def divide(ctx: RunContextWrapper[MathRunContext], a: float, b: float) -> str:
    """Divide the first number by the second. Use this tool for any division operation.

    Args:
        a: The dividend (number to be divided).
        b: The divisor (number to divide by). Must not be zero.
    """
    if b == 0:
        return "Error: Division by zero is undefined."
    result = a / b
    output = f"divide({a}, {b}) = {result}"
    if isinstance(ctx.context, MathRunContext):
        ctx.context.record_call("divide", output)
    return output
