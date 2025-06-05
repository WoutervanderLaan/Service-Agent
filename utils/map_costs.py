from my_agents.classification_agent import classification_agent
from my_agents.non_relevance_agent import non_relevance_agent
from my_agents.low_complexity_response_agent import low_complexity_response_agent
from my_agents.high_complexity_response_agent import high_complexity_response_agent
from my_agents.quality_assurance_agent import quality_assurance_agent
from agents import Usage


AGENT_MODEL_MAP = {
    classification_agent.name: (classification_agent.model),
    non_relevance_agent.name: non_relevance_agent.model,
    low_complexity_response_agent.name: low_complexity_response_agent.model,
    high_complexity_response_agent.name: high_complexity_response_agent.model,
    quality_assurance_agent.name: quality_assurance_agent.model,
}

# per 1M tokens
MODEL_COST_MAP = {
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
}


def map_costs(usage: Usage, model_name: str) -> float:
    llm = AGENT_MODEL_MAP.get(model_name, None)

    if not llm:
        return 0

    costs = MODEL_COST_MAP.get(str(llm))

    if not costs:
        return 0

    input_costs = costs["input"] / 1000000 * usage.input_tokens
    output_costs = costs["output"] / 100000 * usage.output_tokens

    return input_costs + output_costs
