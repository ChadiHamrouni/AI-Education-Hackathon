"""Unguarded versions of all agents — same tools, no guardrails of any kind."""

from agents import Agent, ModelSettings

from src.config import main_model, AGENT_TEMPERATURE
from src.tools.calculate import calculate
from src.tools.convert_units import convert_units
from src.tools.web_search import web_search
from src.agents.computation_agent import COMPUTATION_INSTRUCTIONS
from src.agents.conceptual_agent import CONCEPTUAL_INSTRUCTIONS
from src.agents.triage_agent import TRIAGE_INSTRUCTIONS

unguarded_computation_agent = Agent(
    name="Computation Engine Unguarded",
    instructions=COMPUTATION_INSTRUCTIONS,
    tools=[calculate, convert_units],
    model_settings=ModelSettings(tool_choice="required", temperature=AGENT_TEMPERATURE),
    model=main_model,
)

unguarded_conceptual_agent = Agent(
    name="Conceptual Tutor Unguarded",
    instructions=CONCEPTUAL_INSTRUCTIONS,
    tools=[web_search],
    model_settings=ModelSettings(temperature=AGENT_TEMPERATURE),
    model=main_model,
)

unguarded_triage_agent = Agent(
    name="Physics Tutor Unguarded",
    instructions=TRIAGE_INSTRUCTIONS,
    handoffs=[unguarded_computation_agent, unguarded_conceptual_agent],
    model_settings=ModelSettings(temperature=AGENT_TEMPERATURE),
    model=main_model,
)
