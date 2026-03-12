"""
Output Guardrails
=================
These guardrails run on the agent's final response AFTER it is generated.

Key insight from the SDK:
  - RunContextWrapper does NOT expose run items or tool call history.
  - The right way to track tool calls is via a shared context object
    passed to Runner.run(), which tool functions populate directly.

We define a RunContext dataclass that travels with the run and is
mutated by tool wrappers, giving guardrails clean, reliable access
to what was (or wasn't) computed.
"""

from dataclasses import dataclass, field
from openai import AsyncOpenAI
from agents import output_guardrail, GuardrailFunctionOutput, RunContextWrapper, Agent
from src.config import BASE_URL, CLASSIFIER_MODEL

_client = AsyncOpenAI(base_url=BASE_URL, api_key="ollama")

@dataclass
class MathRunContext:
    """
    Shared context passed to Runner.run(context=...).
    Tools populate this as they are called, giving guardrails
    a reliable record of what was actually computed.
    """
    tool_calls: list[dict] = field(default_factory=list)

    def record_call(self, tool_name: str, result: str) -> None:
        self.tool_calls.append({"tool": tool_name, "result": result})

    @property
    def was_tool_called(self) -> bool:
        return len(self.tool_calls) > 0


# ---------------------------------------------------------------------------
# Layer 2: Tool Use Enforcement
# ---------------------------------------------------------------------------

@output_guardrail
async def tool_use_enforcement(
    ctx: RunContextWrapper[MathRunContext],
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    """
    The Contract: if the agent's response contains a math result, a tool MUST have been called.

    This is the difference between a suggestion (system prompt) and a law (guardrail).
    The system prompt says 'please use tools'. The guardrail enforces it.
    """
    math_context: MathRunContext | None = ctx.context if isinstance(ctx.context, MathRunContext) else None

    # If no shared context is available, we cannot enforce — pass through.
    if math_context is None:
        return GuardrailFunctionOutput(
            tripwire_triggered=False,
            output_info={"reason": "No MathRunContext — skipping enforcement"},
        )

    if math_context.was_tool_called:
        return GuardrailFunctionOutput(
            tripwire_triggered=False,
            output_info={
                "reason": "Tool was called — response is computation-backed",
                "tools_used": [c["tool"] for c in math_context.tool_calls],
            },
        )

    # No tool was called. Block the response.
    return GuardrailFunctionOutput(
        tripwire_triggered=True,
        output_info={
            "reason": "Math answer without tool call",
            "message": (
                "The agent attempted to answer without using a computation tool. "
                "This response has been blocked to protect the learner from "
                "potentially incorrect information."
            ),
        },
    )


# ---------------------------------------------------------------------------
# Layer 3: Safe Output Filter
# ---------------------------------------------------------------------------

@output_guardrail
async def safe_output_filter(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    """
    Screens the agent's final response for harmful content before it reaches the user.
    Critical when the agent has web search access — anything can appear in fetched pages.

    Blocks: graphic violence, terrorism/extremism, explicit sexual content, self-harm instructions.
    Passes: all legitimate educational content, even on sensitive academic topics.
    """
    response = await _client.chat.completions.create(
        model=CLASSIFIER_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a content safety filter for an educational platform. "
                    "Only reply YES if the response contains EXPLICITLY harmful content: "
                    "step-by-step instructions for violence or weapons, graphic sexual content, "
                    "terrorist recruitment, or detailed self-harm methods. "
                    "Everything else is safe — educational explanations, math, science, history, "
                    "medical topics, security concepts, and web search results about any academic topic. "
                    "When in doubt, reply NO. "
                    "Reply with exactly one word: YES if explicitly harmful, NO if safe."
                ),
            },
            {"role": "user", "content": output},
        ],
        max_tokens=10,
        temperature=0,
    )
    verdict = (response.choices[0].message.content or "").strip().lower()

    if verdict.startswith("yes"):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "reason": "Harmful content detected in agent response",
                "message": (
                    "The response was blocked because it contained content "
                    "that is not appropriate for an educational setting."
                ),
            },
        )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={"reason": "Output is safe"},
    )
