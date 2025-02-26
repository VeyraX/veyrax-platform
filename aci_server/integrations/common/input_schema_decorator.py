# decorators.py
import functools
from fastapi import Request, HTTPException
from pydantic import BaseModel
from typing import Type

def input_schema(schema_class: Type[BaseModel]):
    """
    A decorator that reads the request body from FastAPIRequest,
    validates it against the given Pydantic model, and then
    injects the validated data into the route function as `params`.
    """
    def decorator(endpoint_func):
        @functools.wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            # Try to find a FastAPIRequest among *args or **kwargs
            # (depending on how FastAPI has injected the parameters).
            request: Request = None
            
            # If you rely on the function signature being (request, ...) 
            # or (*args, request=...), you can detect it here:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request", None)

            if not request:
                raise HTTPException(status_code=400, detail="Request object not found.")

            # Parse JSON from the request
            body = await request.json()
            
            # Validate using the provided Pydantic model
            try:
                validated_data = schema_class(**body)
            except Exception as e:
                # If validation fails, raise an HTTPException
                raise HTTPException(status_code=422, detail=str(e))
            
            # Override 'params' in kwargs with the validated data
            kwargs["params"] = validated_data
            
            return await endpoint_func(*args, **kwargs)
        
        # Store the schema class as an attribute of the wrapped function
        wrapper.__schema_class__ = schema_class
        return wrapper
    return decorator
