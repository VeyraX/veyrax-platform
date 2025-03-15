import time
from typing import List, Dict, Any, get_type_hints, Optional, get_origin, get_args, Union, Type
from fastapi import routing
import os
import json
from pydantic.fields import PydanticUndefined
from pydantic import BaseModel
from .schema_generation.openai.schema import get_openai_function_schemas
from .schema_generation.openai.validate import validate_tool_schema
import warnings
from pydantic import ValidationError
from db.supabase import get_supabase

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
        
        
        tool_schema = get_openai_function_schemas(route)
        try:
            examples = route.endpoint.examples()
            tool_schema["examples"] = examples
        except Exception as e:
            print(f"Error getting examples for {route.path}: {e}")
            tool_schema["examples"] = []
        
        tools.append(tool_schema)

    return tools


def route_identifier(route: routing.APIRoute) -> str:
    """
    Extract a consistent identifier for a route that can be used to match
    between frontend tool calls and backend route handlers.
    
    Returns the route path, which provides a consistent way to identify routes
    across the application.
    """
    return str(route.path)


def format_validation_error(e: ValidationError, model_name: str = "InputValidation"):
    errors = e.errors()
    schema_info = {
        "errors": errors,
        "valid_schema": {
            "expected_schema": model_name,
            "error_locations": [list(err.get("loc", [])) for err in errors]
        }
    }
    return schema_info


def log_api_call(user_id: str, endpoint: Optional[str] = None, success: Optional[int] = None, error_message: Optional[str] = None):
    try:
        supabase = get_supabase()
        
        api_call_data = {
            "user_id": user_id,
            "endpoint": endpoint,
            "success": success,
            "error_message": error_message
        }
        
        supabase.table("api_calls").insert(api_call_data).execute()
    except Exception as e:
        print(f"Error logging API call: {str(e)}")