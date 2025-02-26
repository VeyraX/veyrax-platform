import inspect
from typing import List, Dict, Any, TypeVar, get_type_hints, Optional, get_origin, get_args, Union, Type, Tuple, Union, Set, Callable
from fastapi import routing
from pydantic import BaseModel
from openai.types.chat import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition
from pydantic import create_model
import openai


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
    schema = model_type.schema()
    format_schema_for_strict(schema)
    return schema


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

K = TypeVar("K")


def remove_if_exists(k: K, d: dict[K, Any]) -> None:
    """Removes key `k` from `d` if present."""
    if k in d:
        d.pop(k)

def format_schema_for_strict(schema: Any) -> None:
    """
    Recursively set additionalProperties to False and replace
    oneOf and allOf with anyOf, required for OpenAI structured outputs.
    Additionally, remove all defaults and set all fields to required.
    This may not be equivalent to the original schema.
    """
    if isinstance(schema, dict):
        if "type" in schema and schema["type"] == "object":
            schema["additionalProperties"] = False

            if "properties" in schema:
                properties = schema["properties"]
                all_properties = list(properties.keys())
                for k, v in properties.items():
                    if "default" in v:
                        if k == "request":
                            v["enum"] = [v["default"]]

                        v.pop("default")
                schema["required"] = all_properties
            else:
                schema["properties"] = {}
                schema["required"] = []

        anyOf = (
            schema.get("oneOf", []) + schema.get("allOf", []) + schema.get("anyOf", [])
        )
        if "allOf" in schema or "oneOf" in schema or "anyOf" in schema:
            schema["anyOf"] = anyOf

        remove_if_exists("allOf", schema)
        remove_if_exists("oneOf", schema)

        for v in schema.values():
            format_schema_for_strict(v)
    elif isinstance(schema, list):
        for v in schema:
            format_schema_for_strict(v)




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

    
    # Get route metadata for schema
    route_name = f"{route.path}" # route.name or route.path.split("/")[-1]
    route_description = (endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} {route.path}").strip()
    
    # If schema_class is provided, use it instead of extracting from function signature
    if schema_class:
        schema = openai.pydantic_function_tool(schema_class)
        schema['function']['name'] = route_name
        schema['function']['description'] = route_description

        return schema
        
    else:
        # Original logic for extracting schema from function signature
        signature = inspect.signature(endpoint_func)
        model_fields = {}

        for param_name, param in signature.parameters.items():
            if param_name == 'service':
                continue
            
            # Get the type hint
            param_type = (
                param.annotation if param.annotation != inspect.Parameter.empty else Any
            )
            # Check if the parameter has a default value
            if param.default != inspect.Parameter.empty:
                model_fields[param_name] = (param_type, param.default)
            else:
                model_fields[param_name] = (param_type, ...)

            model_name = (
                    "".join(word.capitalize() for word in endpoint_func.__name__.split("_")) + "Model"
                )
            model = create_model(model_name, **model_fields)
            parameters = model.schema()

            
    
        
    # Construct the tool schema
    schema = ChatCompletionToolParam(
        function=FunctionDefinition(
            name=route_name,
            description=route_description,
            parameters=parameters,
        ),
        type="function",
    )

    
    return schema

    


if __name__ == "__main__":

    ## Debugging

    class Basic(BaseModel):
        A: str  # Required string
        B: Optional[int] = None  # Optional integer
        C: float  # Required float
        D: bool  # Required boolean
        E: Optional[bytes] = None  # Optional bytes
        F: List[int]  # Required list of integers
        G: Optional[List[str]] = None  # Optional list of strings
        H: Dict[str, float]  # Required dictionary with string keys and float values
        I: Optional[Dict[int, str]] = None  # Optional dictionary with integer keys and string values
        J: Set[str]  # Required set of strings
        K: Optional[Set[int]] = None  # Optional set of integers
        L: Tuple[int, str, float]  # Required tuple with specific types
        M: Optional[Tuple[bool, ...]] = None  # Optional tuple with variable-length booleans
        N: Union[int, str]  # Required union (int or str)
        O: Optional[Union[float, bool]] = None  # Optional union (float or bool)

    def f(a: Basic):
        pass

    # parameters = _process_pydantic_model(Basic, strict=True)        
    # print(parameters)

