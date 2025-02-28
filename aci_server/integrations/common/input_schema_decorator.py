# decorators.py
import functools
from fastapi import Request, HTTPException
from pydantic import BaseModel
from typing import Type, Optional

def input_schema(schema_class: Type[BaseModel]):
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        wrapper.__schema_class__ = schema_class
        return wrapper
    return decorator

def output_schema(schema_class: Type[BaseModel]):
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        wrapper.__output_schema_class__ = schema_class
        return wrapper
    return decorator

def schema(input_schema_class: Optional[Type[BaseModel]] = None, output_schema_class: Optional[Type[BaseModel]] = None):
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            return await endpoint_func(*args, **kwargs)
        
        if input_schema_class:
            wrapper.__schema_class__ = input_schema_class
        if output_schema_class:
            wrapper.__output_schema_class__ = output_schema_class
        return wrapper
    return decorator
