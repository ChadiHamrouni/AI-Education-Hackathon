from agents import Agent, ModelSettings
from src.config import get_model
from src.tools import all_math_tools
from src.guardrails.output_guards import tool_use_enforcement, safe_output_filter

COMPUTATION_INSTRUCTIONS = """
You are a math computation engine for a teaching assistant.
Your sole job: compute the answer using the provided tools, then explain the result clearly.

## Rules
- You MUST call a tool for every computation. No mental math. No estimates.
- After the tool returns a result, show it to the student and explain what it means.
- Keep explanations concise — one paragraph maximum.
- Do not explain theory or concepts. If the student wants theory, they will ask separately.

## Available Tools
- add(a, b), subtract(a, b), multiply(a, b), divide(a, b) — arithmetic
- derivative(expression, variable) — symbolic differentiation via SymPy
- integral(expression, variable) — symbolic integration via SymPy
""".strip()


computation_agent = Agent(
    name="Computation Engine",
    instructions=COMPUTATION_INSTRUCTIONS,
    tools=all_math_tools,
    # Hard API-level constraint: the model cannot produce a response without calling a tool.
    # This is not a prompt suggestion — the API will reject a plain-text response.
    model_settings=ModelSettings(tool_choice="required"),
    output_guardrails=[tool_use_enforcement, safe_output_filter],
    model=get_model(),
)
