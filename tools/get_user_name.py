from agents import function_tool, RunContextWrapper
from schemas.types import User, QueryContext


@function_tool
def get_user_name(ctx: RunContextWrapper[User | QueryContext]):
    """
    Get the user name from the context.
    Args:
        ctx (RunContextWrapper[User | QueryContext]): The context of the query.
    Returns:
        str: The user name."""

    if isinstance(ctx.context, User):
        return ctx.context.name

    if isinstance(ctx.context, QueryContext) and not ctx.context.user is None:
        return ctx.context.user.name
