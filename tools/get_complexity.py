from agents import RunContextWrapper, function_tool
from schemas.types import QueryContext


@function_tool
def get_complexity(ctx: RunContextWrapper[QueryContext]):
    """
    Get the complexity score of the query context.
    Args:
        ctx (RunContextWrapper[QueryContext]): The context of the query.
    Returns:
        int: The complexity score of the query context.
    """
    
    return ctx.context.complexity.score
