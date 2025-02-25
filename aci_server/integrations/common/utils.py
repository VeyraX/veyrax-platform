import inspect
from typing import List, Dict, Any, get_type_hints, Optional, get_origin, get_args, Union
from fastapi import routing
from pydantic.fields import PydanticUndefined

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


def _process_pydantic_model(model_type):
    """
    Process a Pydantic model. A field is required (non-optional) if:
    1. It has no default value (default is PydanticUndefined) and no default_factory
    2. Its type is not Optional[...]
    """
    properties = {}
    required_fields = []

    if not hasattr(model_type, '__fields__'):
        return properties, required_fields

    for field_name, field in model_type.__fields__.items():
        field_type = field.annotation
        origin = get_origin(field_type) or field_type
        args = get_args(field_type)

        # A field is optional if either:
        # 1. It has a default value or default_factory
        has_default = field.default is not PydanticUndefined
        has_factory = field.default_factory is not None
        # 2. Its type is Optional[...] or Union[..., None]
        is_optional_type = (
            origin is Union and type(None) in args
        )

        is_optional = has_default or has_factory or is_optional_type

        # Basic field info
        field_info = {
            "description": field.description or f"Field: {field_name}"
            # "description": f"{field.default, has_default, has_factory, is_optional_type, is_optional}"
        }

        # Handle nested Pydantic models
        if hasattr(field_type, '__fields__'):
            nested_props, _ = _process_pydantic_model(field_type)
            field_info.update({
                "type": "object",
                "properties": nested_props,
                "required": list(nested_props.keys()),
                "additionalProperties": False
            })
        elif get_origin(field_type) in (list, List):
            args = get_args(field_type)
            if args and hasattr(args[0], '__fields__'):
                item_props, _ = _process_pydantic_model(args[0])
                field_info.update({
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": item_props,
                        "required": list(item_props.keys()),
                        "additionalProperties": False
                    }
                })
            else:
                subtype = _get_json_type(args[0]) if args else "string"
                field_info.update({
                    "type": "array",
                    "items": {"type": subtype}
                })
        else:
            base_type = _get_json_type(field_type)
            if is_optional:
                field_info["type"] = ["null", base_type]
            else:
                field_info["type"] = base_type

        required_fields.append(field_name)
        properties[field_name] = field_info

    return properties, required_fields


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

        endpoint_func = route.endpoint
        signature = inspect.signature(endpoint_func)
        type_hints = get_type_hints(endpoint_func)

        properties = {}
        param_names = []

        for name, param in signature.parameters.items():
            if name == 'service':
                continue

            param_type = type_hints.get(name, param.annotation)
            origin = get_origin(param_type) or param_type
            args = get_args(param_type)

            # Updated is_optional check
            has_default = (param.default is not inspect.Parameter.empty)
            includes_none = (origin is Union and type(None) in args)

            is_optional = has_default or includes_none

            # If it's a Pydantic model
            if hasattr(param_type, '__fields__'):
                model_props, _ = _process_pydantic_model(param_type)
                properties[name] = {
                    "type": ["null", "object"] if is_optional else "object",
                    "description": f"Parameter: {name}",
                    "properties": model_props,
                    "required": list(model_props.keys()),
                    "additionalProperties": False
                }
            else:
                json_type = _get_json_type(param_type)
                if is_optional:
                    properties[name] = {"type": ["null", json_type], "description": f"Parameter: {name}"}
                else:
                    properties[name] = {"type": json_type, "description": f"Parameter: {name}"}

            param_names.append(name)

        tool_schema = {
            "type": "function",
            "function": {
                "name": route.name or route.path.split("/")[-1],
                "description": (endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} {route.path}").strip(),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": param_names,
                    "additionalProperties": False,
                },
                "strict": True
            }
        }
        tools.append(tool_schema)

    return tools
