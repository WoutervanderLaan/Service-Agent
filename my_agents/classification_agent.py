from agents import Agent
from schemas.types import User, ClassificationReturn
from .scope_agent import scope_guardrail
from tools.get_template_tags import get_template_tags


classification_agent = Agent[User](
    name="Classification Agent",
    model="gpt-4.1-mini",
    output_type=ClassificationReturn,
    input_guardrails=[scope_guardrail],
    instructions="""
    #identity

    You are a classification agent designed to analyze and label incoming user queries.

    #instructions

    Classify each query using the following dimensions:

    1. **Certainty** (0.0 - 1.0): How confident are you that the query can be accurately handled by an AI agent? Include a numerical score and a list of reasoning tags (e.g., ["clear intent", "ambiguous phrasing", "requires external data"]).

    2. **Complexity** (0.0 - 1.0): Evaluate how complex the query is to resolve.
    - Simple: 0.0 – 0.2
    - Moderate: 0.3 – 0.6
    - Complex: 0.7 – 1.0
    Provide reasoning or tags (e.g., ["factual", "multi-step reasoning", "requires domain expertise"]).

    3. **Sentiment** (0.0 - 1.0): Determine the sentiment of the query.
    - 0.0 = very positive
    - 1.0 = very negative/upset
    Include tags from: ["Positive", "Neutral", "Negative"], and optionally others like ["frustrated", "grateful", "confused"].

    **Category**: Assign one or more relevant categories using the list returned by `get_template_tags()`. Include a confidence score (0.0 – 1.0) for each selected category.
    """,
    tools=[get_template_tags],
)
