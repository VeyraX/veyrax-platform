import inspect
from typing import List, Dict, Any, get_type_hints, Optional, get_origin, get_args, Union, Type
from fastapi import routing
from pydantic import BaseModel
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


def _process_pydantic_model(model_type, strict: bool):
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
            nested_props, rf = _process_pydantic_model(field_type, strict)
            field_info.update({
                "type": "object",
                "properties": nested_props,
                "required": rf,
            })
            if strict:
                field_info["additionalProperties"] = False
        elif get_origin(field_type) in (list, List):
            args = get_args(field_type)
            if args and hasattr(args[0], '__fields__'):
                item_props, rf = _process_pydantic_model(args[0], strict)
                item_schema = {
                    "type": "object",
                    "properties": item_props,
                    "required": rf,
                }
                if strict:
                    item_schema["additionalProperties"] = False
                field_info.update({
                    "type": "array",
                    "items": item_schema
                })
            else:
                subtype = _get_json_type(args[0]) if args else "string"
                field_info.update({
                    "type": "array",
                    "items": {"type": subtype}
                })
        else:
            base_type = _get_json_type(field_type)
            if (is_optional and strict):
                field_info["type"] = ["null", base_type]
            else:
                field_info["type"] = base_type

            if base_type == "object" and strict:
                field_info["additionalProperties"] = False

        if strict:  # in strict mode we add all fields
            required_fields.append(field_name)
        if not strict and not is_optional:  # in non-strict mode we only add required fields
            required_fields.append(field_name)
        
        properties[field_name] = field_info

    return properties, required_fields


def get_route_schema_class(route: routing.APIRouter) -> Optional[Type[BaseModel]]:
    """
    Extract the schema class from a route's endpoint function that
    has been decorated with input_schema.
    
    Args:
        route: A FastAPI route object
        
    Returns:
        The schema class if the route function is decorated with input_schema,
        otherwise None.
    """
    if hasattr(route.endpoint, "__schema_class__"):
        return route.endpoint.__schema_class__
    return None


def get_openai_function_schemas(
    route: routing.APIRouter, 
    strict: bool = False
) -> Dict[str, Any]:
    """
    Generate OpenAI function schema from FastAPI route and optional schema class.
    
    Args:
        route: The FastAPI route
        strict: Whether to enforce strict schema validation
        
    Returns:
        Dict containing the OpenAI function schema
    """
    endpoint_func = route.endpoint
    schema_class = get_route_schema_class(route)
    
    # If schema_class is provided, use it instead of extracting from function signature
    if schema_class:
        properties, required_fields = _process_pydantic_model(schema_class, strict)
        
        parameters_schema = {
            "type": "object",
            "properties": properties,
            "required": required_fields,
        }
        
        if strict:
            parameters_schema["additionalProperties"] = False
    else:
        # Original logic for extracting schema from function signature
        signature = inspect.signature(endpoint_func)
        type_hints = get_type_hints(endpoint_func)

        properties = {}
        param_names = []
        required_fields = []

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
                model_props, rf = _process_pydantic_model(param_type, strict)
                properties[name] = {
                    "type": ["null", "object"] if (is_optional and strict) else "object",
                    "description": f"Parameter: {name}",
                    "properties": model_props,
                    "required": rf,
                }
                if strict:
                    properties[name]["additionalProperties"] = False
            else:
                json_type = _get_json_type(param_type)
                if (strict and is_optional):
                    properties[name] = {"type": ["null", json_type], "description": f"Parameter: {name}"}
                else:
                    properties[name] = {"type": json_type, "description": f"Parameter: {name}"}

            param_names.append(name)

            if strict:
                required_fields.append(name)
            if not strict and not is_optional:
                required_fields.append(name)

        parameters_schema = {
            "type": "object",
            "properties": properties,
            "required": required_fields,
        }
        if strict:
            parameters_schema["additionalProperties"] = False

    # Get route metadata for schema
    route_name = route.name or route.path.split("/")[-1]
    route_description = (endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} {route.path}").strip()
    
    # Construct the tool schema
    tool_schema = {
        "type": "function",
        "function": {
            "name": route_name,
            "description": route_description,
            "parameters": parameters_schema,
            "strict": strict
        }
    }
    
    return tool_schema

# Convenience function to get schema directly from a schema class
def get_openai_schema_from_class(
    name: str, 
    description: str, 
    schema_class: Type[BaseModel], 
    strict: bool = False
) -> Dict[str, Any]:
    """
    Generate OpenAI function schema directly from a Pydantic model class.
    
    Args:
        name: The function name
        description: The function description
        schema_class: Pydantic model class to use for parameters schema
        strict: Whether to enforce strict schema validation
        
    Returns:
        Dict containing the OpenAI function schema
    """
    properties, required_fields = _process_pydantic_model(schema_class, strict)
    
    parameters_schema = {
        "type": "object",
        "properties": properties,
        "required": required_fields,
    }
    
    if strict:
        parameters_schema["additionalProperties"] = False
        
    tool_schema = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters_schema,
            "strict": strict
        }
    }
    
    return tool_schema