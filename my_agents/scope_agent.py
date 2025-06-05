from agents import (
    Agent,
    input_guardrail,
    RunContextWrapper,
    TResponseInputItem,
    Runner,
    GuardrailFunctionOutput,
)
from dataclasses import dataclass
from schemas.types import User


@dataclass
class ScopeOutput:
    is_in_scope: bool
    score: float
    reasoning: str


@input_guardrail
async def scope_guardrail(
    ctx: RunContextWrapper[User], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(scope_agent, input)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_in_scope,
    )


scope_agent = Agent(
    name="Scope Agent",
    model="gpt-4.1-mini",
    output_type=ScopeOutput,
    instructions="""
    #identity

    You are a guardrail agent. Your job is to assess if the query is within the scope of the app and our support team.

    #instructions

    -Add a score (from 0 to 1) to rate the query on relevance and add reasoning tags.
    -Any query that is not about the app is outside our scope.
    """,
)
