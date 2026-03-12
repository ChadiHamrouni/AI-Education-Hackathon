import sympy
from agents import function_tool, RunContextWrapper
from src.guardrails.output_guards import MathRunContext


@function_tool
def derivative(ctx: RunContextWrapper[MathRunContext], expression: str, variable: str = "x") -> str:
    """Compute the symbolic derivative of a mathematical expression.
    Use this tool for any differentiation operation.

    Args:
        expression: The mathematical expression to differentiate (e.g. "x**3 + 2*x").
        variable: The variable to differentiate with respect to (default "x").
    """
    try:
        var = sympy.Symbol(variable)
        expr = sympy.sympify(expression)
        result = sympy.diff(expr, var)
        output = f"d/d{variable}({expression}) = {result}"
        if isinstance(ctx.context, MathRunContext):
            ctx.context.record_call("derivative", output)
        return output
    except (sympy.SympifyError, TypeError) as e:
        return f"Error: Could not parse expression '{expression}'. {e}"


@function_tool
def integral(ctx: RunContextWrapper[MathRunContext], expression: str, variable: str = "x") -> str:
    """Compute the symbolic indefinite integral of a mathematical expression.
    Use this tool for any integration operation.

    Args:
        expression: The mathematical expression to integrate (e.g. "x**2 + 3*x").
        variable: The variable to integrate with respect to (default "x").
    """
    try:
        var = sympy.Symbol(variable)
        expr = sympy.sympify(expression)
        result = sympy.integrate(expr, var)
        output = f"∫({expression}) d{variable} = {result} + C"
        if isinstance(ctx.context, MathRunContext):
            ctx.context.record_call("integral", output)
        return output
    except (sympy.SympifyError, TypeError) as e:
        return f"Error: Could not parse expression '{expression}'. {e}"
