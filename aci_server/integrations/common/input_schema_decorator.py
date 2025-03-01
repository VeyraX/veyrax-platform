# decorators.py
import functools
from fastapi import Request, HTTPException
from pydantic import BaseModel
from typing import Type, Optional, List, Dict, Any


def input_schema(schema_class: Type[BaseModel]):
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        wrapper.__schema_class__ = schema_class
        
        # Add method to access input schema
        def get_input_schema():
            return getattr(wrapper, "__schema_class__", None)
        wrapper.input_schema = get_input_schema
        
        return wrapper
    return decorator

def output_schema(schema_class: Type[BaseModel]):
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        wrapper.__output_schema_class__ = schema_class
        
        # Add method to access output schema
        def get_output_schema():
            return getattr(wrapper, "__output_schema_class__", None)
        wrapper.output_schema = get_output_schema
        
        return wrapper
    return decorator

def schema(
    input_schema_class: Optional[Type[BaseModel]] = None,
    output_schema_class: Optional[Type[BaseModel]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
):
    """
    Decorator that attaches schema classes and a list of examples to an endpoint.
    Each example is a dict with 'input' and 'output' keys, e.g.:
    
    examples=[
        {
            "input": {"name": "Alice", "email": "[email protected]"},
            "output": {"id": "12345", "name": "Alice", "email": "[email protected]"}
        },
        {
            "input": {"name": "Bob",   "email": "[email protected]"},
            "output": {"id": "67890", "name": "Bob",   "email": "[email protected]"}
        }
    ]
    """
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        if input_schema_class:
            wrapper.__schema_class__ = input_schema_class
        
        if output_schema_class:
            wrapper.__output_schema_class__ = output_schema_class
        
        if examples:
            # Attach the examples list, each containing {"input": {...}, "output": {...}}
            wrapper.__examples__ = examples
        
        # Add convenience methods to access schemas and examples
        def get_input_schema():
            return getattr(wrapper, "__schema_class__", None)
        
        def get_output_schema():
            return getattr(wrapper, "__output_schema_class__", None)
        
        def get_examples():
            return getattr(wrapper, "__examples__", None)
        
        wrapper.input_schema = get_input_schema
        wrapper.output_schema = get_output_schema
        wrapper.examples = get_examples
        
        return wrapper
    return decorator
