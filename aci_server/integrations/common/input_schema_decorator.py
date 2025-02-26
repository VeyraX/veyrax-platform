# decorators.py
import functools
from fastapi import Request, HTTPException
from pydantic import BaseModel
from typing import Type

def input_schema(schema_class: Type[BaseModel]):
    """
    A decorator that adds schema class to the endpoint function.
    """
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        # Store the schema class as an attribute of the wrapped function
        wrapper.__schema_class__ = schema_class
        return wrapper
    return decorator
