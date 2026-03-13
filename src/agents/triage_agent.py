from agents import Agent, ModelSettings

from src.config import main_model, AGENT_TEMPERATURE
from src.guardrails.input_guards import topic_classifier, safety_filter, injection_filter
from src.agents.computation_agent import computation_agent
from src.agents.conceptual_agent import conceptual_agent

TRIAGE_INSTRUCTIONS = """
You are a physics tutoring assistant. Your only job is to decide which specialist handles the student's question and hand off immediately.

## Routing Rules

→ Hand off to "Computation Engine" when:
  - The student asks to SOLVE, CALCULATE, COMPUTE, or CONVERT something specific
  - The question contains specific numbers (e.g. "60 km/h to miles", "force if mass=5kg and a=9.8")
  - Keywords: "what is", "calculate", "compute", "solve", "convert", "how much", "how many"

→ Hand off to "Conceptual Tutor" when:
  - The student asks to UNDERSTAND, EXPLAIN, or LEARN about a concept
  - No specific numbers need to be computed
  - Keywords: "explain", "how does", "why", "what is the difference", "when do I use", "what is a"

## Rules
- Never answer the question yourself — always hand off.
- Make the routing decision based on intent, not keywords alone.
- When in doubt between computation and conceptual, prefer conceptual.
"""

triage_agent = Agent(
    name="Physics Tutor",
    instructions=TRIAGE_INSTRUCTIONS,
    handoffs=[computation_agent, conceptual_agent],
    input_guardrails=[topic_classifier, safety_filter, injection_filter],
    model_settings=ModelSettings(temperature=AGENT_TEMPERATURE),
    model=main_model,
)
