from agents import Agent, FileSearchTool, ModelSettings
from schemas.types import QueryContext

vector_db_agent = Agent[QueryContext](
    name="Vector DB Agent",
    model="gpt-4.1-mini",
    tools=[
        FileSearchTool(
            vector_store_ids=["vs_682f995dc75c8191983c6d29f7ebbc69"], max_num_results=5
        )
    ],
    model_settings=ModelSettings(tool_choice="required"),
    instructions="""
    #identity

    You are a context retrieval agent.

    #instructions

    - Look up relevant context in files to help contextualise the query.
    """,
)
