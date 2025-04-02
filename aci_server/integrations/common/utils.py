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
import sentry_sdk
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def get_router_tools(router: routing.APIRouter) -> List[Dict[str, Any]]:
    tools = []

    for route in router.routes:
        if route.path.endswith("/tools"):
            continue
        
        try:
            tool_schema = get_openai_function_schemas(route)
            try:
                examples = route.endpoint.examples()
                tool_schema["examples"] = examples
            except Exception as e:
                if "validate_key" not in route.path: 
                    print(f"Error getting examples for {route.path}: {e}")
                tool_schema["examples"] = []
            
            tools.append(tool_schema)
        except Exception as e:
            print(f"Error generating schema for {route.path}: {str(e)}")
            # Continue with other routes instead of failing completely

    return tools


def route_identifier(route: routing.APIRoute) -> str:
    return str(route.path)


def format_validation_error_response(errors, error_source="input"):
    field_errors = {}
    
    for error in errors:
        loc = error.get("loc", [])
        if not loc:
            continue
            
        if len(loc) > 1:
            field_name = ".".join(str(item) for item in loc)
        else:
            field_name = str(loc[0])
            
        if field_name not in field_errors:
            field_errors[field_name] = []
        field_errors[field_name].append(error.get("msg", ""))
    
    error_details = []
    for field, messages in field_errors.items():
        field_message = f"{field}: {'; '.join(messages)}"
        error_details.append(field_message)
    
    error_message = ". ".join(error_details)
    
    type_label = "Input" if error_source == "input" else "Output"
    error_code = "VALIDATION_INPUT_ERROR" if error_source == "input" else "VALIDATION_OUTPUT_ERROR"
    
    return {
        "data": {
            "status": "error",
            "message": f"{type_label} validation error: {error_message}",
            "validation_errors": field_errors,
            "error_code": error_code
        },
        "component": None
    }


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
            response = func(*args, **kwargs)
            return response
        except HTTPException as e:
            raise e
        except requests.exceptions.HTTPError as e:
            if not hasattr(e, 'response'):
                raise ClientUnknowError(
                    message=str(e),
                    errors={
                        "status": "error",
                        "message": str(e),
                        "error_code": "API_UNKNOWN_ERROR"
                    }
                )
            try:
                error_data = e.response.json()
                error_message = str(e)
                if 'errorMessages' in error_data and error_data['errorMessages']:
                    error_message = error_data['errorMessages'][0]
                elif isinstance(error_data, dict):
                    if "error" in error_data:
                        error_message = error_data["error"]
                    elif "message" in error_data:
                        error_message = error_data["message"]
            except:
                error_message = e.response.text or str(e)
            
            raise ClientNonCriticalError(
                message=error_message,
                errors={
                    "status": "error",
                    "message": error_message,
                    "status_code": e.response.status_code,
                    "error_code": f"API_HTTP_ERROR_{e.response.status_code}"
                }
            )
        except ValidationError as e:
            error_detail = format_validation_error_response(e.errors(), "input")
            raise ClientNonCriticalError(
                message=f"Input validation error in API client: {str(e)}",
                errors=error_detail["data"]
            )
        except Exception as e:
            print(f"[handle_api_error] Unexpected Error in {func.__name__}:", str(e))
            print(traceback.format_exc())
            
            raise ClientUnknowError(
                message=str(e),
                errors={
                    "status": "error",
                    "message": f"Unexpected error in API client: {str(e)}",
                    "error_code": "API_UNKNOWN_ERROR"
                }
            )
    
    return wrapper


class ServiceValidationError(Exception):
    def __init__(self, message: str, errors: dict):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

    def to_http_exception(self):
        return HTTPException(
            status_code=422, 
            detail=format_validation_error_response(self.errors, "output")
        )


class ClientNonCriticalError(Exception):
    def __init__(self, message: str, errors: dict):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class ClientUnknowError(Exception):
    def __init__(self, message: str, errors: dict):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


def apply_error_handler_to_router(router: APIRouter):
    def route_error_handler(endpoint):
        @functools.wraps(endpoint)
        async def wrapper(*args, **kwargs):
            try:
                try:
                    endpoint_response = await endpoint(*args, **kwargs)
                except ValidationError as e:
                    print("[route_error_handler] Input ValidationError: ", e)
                    
                    error_detail = format_validation_error_response(e.errors(), "input")
                    raise HTTPException(status_code=422, detail=error_detail)
                
                try:
                    return endpoint_response
                except ValidationError as e:
                    error_detail = format_validation_error_response(e.errors(), "output")
                    raise HTTPException(status_code=422, detail=error_detail)
                    
            except HTTPException as e:
                raise
                
            except ServiceValidationError as e:
                raise e.to_http_exception()
                
            except Exception as e:
                if not isinstance(e, requests.exceptions.HTTPError):
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail={
                        "data": {
                            "status": "error",
                            "message": f"Unexpected error: {str(e)}",
                            "error_code": "INTERNAL_SERVER_ERROR"
                        },
                        "component": None
                    })
                raise
        
        return wrapper
    
    for route in router.routes:
        if isinstance(route, routing.APIRoute):
            original_endpoint = route.endpoint
            route.endpoint = route_error_handler(original_endpoint)


def handle_service_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except requests.exceptions.HTTPError as e:
            try:
                error_response = e.response.json()
                raise HTTPException(status_code=e.response.status_code, detail={"data": error_response, "component": None})
            except:
                raise HTTPException(status_code=e.response.status_code or 500, detail={
                    "data": {
                        "status": "error", 
                        "message": e.response.text or str(e),
                        "error_code": "HTTP_REQUEST_ERROR"
                    }, 
                    "component": None
                })
        
        except ClientNonCriticalError as e:
            raise HTTPException(status_code=400, detail={
                "data": {
                    "status": "error", 
                    "message": e.message, 
                    "errors": e.errors,
                    "error_code": "CLIENT_ERROR"
                }, 
                "component": None
            })

        except ValidationError as e:
            sentry_sdk.capture_exception(e)
            
            error_detail = format_validation_error_response(e.errors(), "output")
            raise HTTPException(status_code=422, detail=error_detail)

        except Exception as e:
            print(f"[handle_service_error] Unexpected Error in {func.__name__}:", str(e))
            print(traceback.format_exc())
            
            raise HTTPException(status_code=500, detail={
                "data": {
                    "status": "error", 
                    "message": f"Internal server error: {str(e)}",
                    "error_code": "INTERNAL_SERVER_ERROR" 
                }, 
                "component": None
            })
    return wrapper


def apply_error_handler_to_service(service):
    for method_name in dir(service):
        if not method_name.startswith('_') and callable(getattr(service, method_name)):
            original_method = getattr(service, method_name)
            if hasattr(original_method, '__self__') and original_method.__self__ is service:
                setattr(service, method_name, handle_service_error(original_method))
    
    return service


def apply_error_handler_to_client(client):
    for method_name in dir(client):
        if not method_name.startswith('_') and callable(getattr(client, method_name)):
            original_method = getattr(client, method_name)
            if hasattr(original_method, '__self__') and original_method.__self__ is client:
                setattr(client, method_name, handle_api_error(original_method))
    return client


def get_user_flows_actions(user_id: str, flow_id: str = None):
    try:
        supabase = get_supabase()
        
        query = supabase.from_('user_actions_flows_view') \
            .select('*') \
            .eq('user_id', user_id)
            
        if flow_id:
            query = query.eq('flow_id', flow_id)
            
        result = query.execute()
        
        if not result.data:
            return []
        
        flows_map = {}
        
        for row in result.data:
            flow_id = row.get('flow_id')
            
            if flow_id not in flows_map:
                flows_map[flow_id] = {
                    "id": flow_id,
                    "name": row.get('flow_name'),
                    "plain_description": row.get('flow_plain_description'),
                    "available_actions": []
                }
            
            action = {
                "provider_slug": row.get('provider_slug'),
                "action_slug": row.get('action_slug'),
                "input_schema": row.get('input_schema'),
                "output_schema": row.get('output_schema')
            }
            
            flows_map[flow_id]["available_actions"].append(action)
        
        if flow_id:
            return flows_map.get(flow_id)
            
        return list(flows_map.values())
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}


def get_user_tools_from_actions(user_id: str):
    try:
        supabase = get_supabase()
        
        result = supabase.from_('user_actions_view') \
            .select('*') \
            .eq('user_id', user_id) \
            .execute()
            
        if not result.data:
            return {}
            
        user_tools = {}
        
        for row in result.data:
            provider_name = row.get('provider_tag')
            action_name = row.get('action_slug')
            input_schema = row.get('input_schema')
            
            if not provider_name or not action_name or not input_schema:
                continue
                
            if provider_name not in user_tools:
                user_tools[provider_name] = {}
                
            action_schema = {
                "type": "function",
                "function": {
                    "name": action_name,
                    **input_schema
                }
            }
            
            user_tools[provider_name][action_name] = action_schema
            
        return user_tools
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}
    

def get_user_flows(user_id: str):
    try:
        supabase = get_supabase()
        
        result = supabase.from_('user_flows') \
            .select('id, name') \
            .eq('user_id', user_id) \
            .execute()
            
        if not result.data:
            return []
            
        return result.data
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}
    

