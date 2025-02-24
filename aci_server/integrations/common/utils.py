import inspect
from typing import List, Dict, Any
from fastapi import routing
import os
import json

def _get_json_type(type_):
    """Helper function to convert Python/Pydantic types to JSON schema types"""
    type_str = str(type_).lower()
    if "int" in type_str:
        return "integer"
    elif "float" in type_str or "decimal" in type_str:
        return "number"
    elif "bool" in type_str:
        return "boolean"
    elif "dict" in type_str or "mapping" in type_str:
        return "object"
    elif "list" in type_str or "sequence" in type_str:
        return "array"
    return "string"


def get_router_tools(router: routing.APIRouter) -> List[Dict[str, Any]]:
    """
    Generate a list of OpenAI function-calling schemas from the routes defined in a FastAPI APIRouter.
    """
    tools = []

    for route in router.routes:
        # Skip the /tools endpoint itself (if present)
        if route.path.endswith("/tools"):
            continue

        endpoint_func = route.endpoint
        signature = inspect.signature(endpoint_func)
        
        # Build JSON schema properties for function parameters
        properties = {}
        required = []

        for name, param in signature.parameters.items():
            # Skip dependencies or "service" injection
            if name == 'service':
                continue

            param_type = param.annotation
            if hasattr(param_type, '__fields__'):
                model_properties = {}
                model_required = []

                for field_name, field in param_type.__fields__.items():
                    model_properties[field_name] = {
                        "type": _get_json_type(field.annotation),
                        "description": field.description or f"Field: {field_name}",
                    }
                    # Instead of checking field.required, we check if the default is Ellipsis
                    if field.default is Ellipsis:
                        model_required.append(field_name)
                
                properties[name] = {
                    "type": "object",
                    "description": f"Parameter: {name}",
                    "properties": model_properties,
                    "required": model_required,
                    "additionalProperties": False,
                }
                if param.default == inspect.Parameter.empty:
                    required.append(name)
                continue
            
            # For non-Pydantic parameters, perform basic type inference
            param_type_str = str(param.annotation)
            param_type_str = (
                param_type_str
                .replace('typing.Optional[', '')
                .replace('typing.', '')
                .replace(']', '')
                .replace("<class '", '')
                .replace("'>", '')
            )
            json_type = _get_json_type(param_type_str)

            properties[name] = {
                "type": json_type,
                "description": f"Parameter: {name}",
            }

            if param.default == inspect.Parameter.empty:
                required.append(name)

        # Infer function name and description
        method_name = route.name or route.path.split("/")[-1]
        docstring = endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} request to {route.path}"

        # Construct the OpenAI function-calling schema for this route
        tool = {
            "type": "function",
            "function": {
                "name": method_name,
                "description": docstring.strip(),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required if required else [],
                    "additionalProperties": False,
                },
                "strict": True
            }
        }

        tools.append(tool)

    return tools

def wrap_component_with_tool(component: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'tool_wrapper.json'), 'r') as file:
        tool_wrapper = json.load(file)
    
    return {
        "name": "ToolWrapper",
        "props": {
            "toolName": tool_name,
            "children": component
        },
        "jsx": tool_wrapper["component"]["jsx"]
    }
