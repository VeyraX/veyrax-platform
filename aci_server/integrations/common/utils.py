import time
from typing import List, Dict, Any, get_type_hints, Optional, get_origin, get_args, Union, Type, Callable
from fastapi import routing, HTTPException, APIRouter
import os
import json
from pydantic.fields import PydanticUndefined
from pydantic import BaseModel
from .schema_generation.openai.schema import get_openai_function_schemas
from .schema_generation.openai.validate import validate_tool_schema
import warnings
from pydantic import ValidationError
from db.supabase import get_supabase
import requests
import functools
import traceback

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

def handle_api_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            try:
                return {"data": e.response.json(), "component": None}
            except:
                return {"data": {"error": e.response.text or str(e)}, "component": None}
        except Exception as e:
            return {"data": {"error": str(e)}, "component": None}
    
    return wrapper

def apply_error_handler_to_router(router: APIRouter):
    def route_error_handler(endpoint):
        @functools.wraps(endpoint)
        async def wrapper(*args, **kwargs):
            try:
                return await endpoint(*args, **kwargs)
            except ValidationError as e:
                errors = e.errors()
                error_details = []
                
                field_errors = {}
                
                for error in errors:
                    loc = error.get("loc", [])
                    if loc and len(loc) > 0:
                        field_name = loc[0]
                        if field_name not in field_errors:
                            field_errors[field_name] = []
                        field_errors[field_name].append(error.get("msg", ""))
                
                for field, messages in field_errors.items():
                    field_message = f"{field}: {'; '.join(messages)}"
                    error_details.append(field_message)
                
                error_message = ". ".join(error_details)
                
                return {
                    "data": {
                        "status": "error",
                        "message": f"Validation error: {error_message}",
                        "validation_errors": field_errors
                    },
                    "component": None
                }
                
            except HTTPException as e:
                return {
                    "data": {
                        "status": "error",
                        "message": e.detail
                    },
                    "component": None
                }
                
            except Exception as e:
                if not isinstance(e, requests.exceptions.HTTPError):
                    traceback.print_exc()
                    return {
                        "data": {
                            "status": "error",
                            "message": f"Unexpected error: {str(e)}"
                        },
                        "component": None
                    }
                raise
        
        return wrapper
    
    for route in router.routes:
        if isinstance(route, routing.APIRoute):
            original_endpoint = route.endpoint
            route.endpoint = route_error_handler(original_endpoint)

def apply_error_handler_to_service(service):
    for method_name in dir(service):
        if not method_name.startswith('_') and callable(getattr(service, method_name)):
            original_method = getattr(service, method_name)
            if hasattr(original_method, '__self__') and original_method.__self__ is service:
                setattr(service, method_name, handle_api_error(original_method))
    
    return service