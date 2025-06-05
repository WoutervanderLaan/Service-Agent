from agents import Agent, WebSearchTool, ModelSettings
from schemas.types import QueryContext

web_search_agent = Agent[QueryContext](
    name="Web Search Agent",
    model="gpt-4.1-mini",
    tools=[
        WebSearchTool(
            search_context_size="medium",
        )
    ],
    model_settings=ModelSettings(tool_choice="required"),
    instructions="""
    #identity

    You are a web search agent.

    #instructions

    - Look up any relevant information related to the app to help resolve the query.
    - Only search and return web results that relate to the app.
    """,
)
