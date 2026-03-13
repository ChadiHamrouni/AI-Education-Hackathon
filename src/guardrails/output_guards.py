from pydantic import BaseModel
from agents import (
    Agent, Runner, ModelSettings,
    output_guardrail, GuardrailFunctionOutput, RunContextWrapper,
)
from src.config import classifier_model, CLASSIFIER_TEMPERATURE


class ClassifierOutput(BaseModel):
    verdict: bool   # True = harmful/blocked, False = safe/pass
    reason: str


_safety_agent = Agent(
    name="Output Safety Filter",
    instructions=(
        "You are a content safety filter for an educational platform. "
        "Only flag (verdict=true) if the response contains EXPLICITLY harmful content: "
        "step-by-step instructions for violence or weapons, graphic sexual content, "
        "terrorist recruitment, or detailed self-harm methods. "
        "Everything else is safe — educational explanations, math, science, history, "
        "medical topics, security concepts, and web search results about any academic topic. "
        "When in doubt, do NOT flag. Set verdict=false."
    ),
    output_type=ClassifierOutput,
    model_settings=ModelSettings(temperature=CLASSIFIER_TEMPERATURE),
    model=classifier_model,
)


@output_guardrail
async def safe_output_filter(
    ctx: RunContextWrapper,
    _agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    """
    Screens the agent's final response for harmful content before it reaches the user.
    Critical when the agent has web search access — anything can appear in fetched pages.
    """
    result = await Runner.run(_safety_agent, input=output, context=ctx.context)
    classification: ClassifierOutput = result.final_output

    if classification.verdict:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "reason": classification.reason,
                "message": (
                    "The response was blocked because it contained content "
                    "that is not appropriate for an educational setting."
                ),
            },
        )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={"reason": classification.reason},
    )
