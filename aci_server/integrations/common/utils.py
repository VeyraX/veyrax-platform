from typing import List, Dict, Any, get_type_hints, Optional, get_origin, get_args, Union
from fastapi import routing
from pydantic.fields import PydanticUndefined
from .schema_generation.openai.schema import get_openai_function_schemas
from .schema_generation.openai.validate import validate_tool_schema
import warnings

def get_router_tools(router: routing.APIRouter) -> List[Dict[str, Any]]:
    """
    Generate a simplified set of OpenAI function schemas from FastAPI routes,
    applying strict mode: all parameters are 'required'. We now accurately handle
    optional fields by checking if a default is provided or if the annotation includes `None`.
    """
    tools = []

    for route in router.routes:
        # Skip the /tools endpoint
        if route.path.endswith("/tools"):
            continue
        tool_schema = get_openai_function_schemas(route, strict=True)

        tools.append(tool_schema)

    return tools
