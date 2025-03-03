import inspect
from typing import List, Dict, Any, TypeVar, get_type_hints, Optional, get_origin, get_args, Union, Type, Tuple, Union, Set, Callable
from fastapi import routing
from pydantic import BaseModel
from openai.types.chat import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition
from pydantic import create_model
import openai
from ...route_identifier import route_identifier, route_method

def get_route_schema_class(route: routing.APIRouter) -> Optional[Type[BaseModel]]:
    if hasattr(route.endpoint, "__schema_class__"):
        return route.endpoint.__schema_class__
    return None


def get_route_output_schema_class(route: routing.APIRouter) -> Optional[Type[BaseModel]]:
    if hasattr(route.endpoint, "__output_schema_class__"):
        return route.endpoint.__output_schema_class__
    return None

K = TypeVar("K")


def remove_if_exists(k: K, d: dict[K, Any]) -> None:
    """Removes key `k` from `d` if present."""
    if k in d:
        d.pop(k)

def format_schema_for_strict(schema: Any) -> None:
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


def create_simplified_output_schema(schema_class: Type[BaseModel]) -> Dict[str, Any]:
    schema = schema_class.schema()
    
    simplified = {
        "type": "object",
        "properties": {}
    }
    
    def simplify_schema(schema_part):
        if not isinstance(schema_part, dict):
            return schema_part
            
        result = {}
        
        if "type" in schema_part:
            result["type"] = schema_part["type"]
            
            if schema_part["type"] == "object" and "properties" in schema_part:
                result["properties"] = {}
                for prop_name, prop_schema in schema_part["properties"].items():
                    result["properties"][prop_name] = simplify_schema(prop_schema)
            
            elif schema_part["type"] == "array" and "items" in schema_part:
                result["items"] = simplify_schema(schema_part["items"])
        
        elif any(key in schema_part for key in ["anyOf", "oneOf", "allOf"]):
            for key in ["anyOf", "oneOf", "allOf"]:
                if key in schema_part:
                    if schema_part[key] and len(schema_part[key]) > 0:
                        return simplify_schema(schema_part[key][0])
        
        elif "$ref" in schema_part:
            ref = schema_part["$ref"]
            if ref.startswith("#/$defs/"):
                ref_name = ref.split("/")[-1]
                if "$defs" in schema and ref_name in schema["$defs"]:
                    return simplify_schema(schema["$defs"][ref_name])
        
        return result or schema_part
    
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            simplified["properties"][prop_name] = simplify_schema(prop_schema)
    
    return simplified


def get_openai_function_schemas(
    route: routing.APIRouter
) -> Dict[str, Any]:
    parameters = {}
    endpoint_func = route.endpoint
    input_schema_class = get_route_schema_class(route)
    output_schema_class = get_route_output_schema_class(route)
    
    route_name = route_method(route)
    route_description = (endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} {route.path}").strip()
    
    if input_schema_class:
        schema = openai.pydantic_function_tool(input_schema_class)
        schema['function']['name'] = route_name
        schema['function']['description'] = route_description
        
        if output_schema_class:
            output_schema = create_simplified_output_schema(output_schema_class)
            schema['function']['output_schema'] = output_schema
        
        return schema
    
    else:
        signature = inspect.signature(endpoint_func)
        model_fields = {}

        for param_name, param in signature.parameters.items():
            if param_name == 'service':
                continue
            
            param_type = (
                param.annotation if param.annotation != inspect.Parameter.empty else Any
            )
            if param.default != inspect.Parameter.empty:
                model_fields[param_name] = (param_type, param.default)
            else:
                model_fields[param_name] = (param_type, ...)

            model_name = (
                    "".join(word.capitalize() for word in endpoint_func.__name__.split("_")) + "Model"
                )
            model = create_model(model_name, **model_fields)
            parameters = model.schema()

        schema_dict = {
            "type": "function",
            "function": {
                "name": route_name,
                "description": route_description,
                "parameters": parameters,
            }
        }
        
        if output_schema_class:
            output_schema = create_simplified_output_schema(output_schema_class)
            schema_dict["function"]["output_schema"] = output_schema
        
        return schema_dict

    


if __name__ == "__main__":

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

