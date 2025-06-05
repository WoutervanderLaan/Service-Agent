from agents import function_tool, RunContextWrapper
from schemas.types import QueryContext
from typing import Set
import json

@function_tool
def get_template_tags(ctx: RunContextWrapper[QueryContext]) -> list[str]:
    """
    Get the template tags associated with the email templates.
    Args:
        ctx (RunContextWrapper[User | QueryContext]): The context of the query.
    Returns:
        list[str]: A list of existing template tags.
    """
    
    tags: set[str] = set("other")
    
    with open(f"assets/templates_email.json", "r") as f:
        templates = json.load(f)

        for template in templates:
            for tag in template["tags"]:
                tags.add(tag)
        
        return list(tags)
    

    