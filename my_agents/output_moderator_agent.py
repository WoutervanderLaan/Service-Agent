from schemas.types import QueryContext
from dataclasses import dataclass
from agents import (
    Agent,
    output_guardrail,
    RunContextWrapper,
    Runner,
    GuardrailFunctionOutput,
)


@dataclass
class ModerationOutput:
    is_safe: bool
    reasoning: str


@output_guardrail
async def output_moderation_guardrail(
    ctx: RunContextWrapper[QueryContext],
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_moderator_agent, output)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_safe,
    )


output_moderator_agent = Agent[QueryContext](
    name="Output Moderator Agent",
    model="gpt-4.1-mini",
    instructions="""
    #identity

    You are a content moderation agent.

    #instructions

    - Check if the output contains any sensitive data.
    - Make sure the output does not contain inapporpriate language.
    - Check if the output is relevant to the user query.
    - Check if the output is relevant in the context of the app.
    """,
    output_type=ModerationOutput,
)
