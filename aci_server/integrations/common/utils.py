from fastapi import routing
from typing import Dict, Any
import inspect

def get_router_tools(router: routing.APIRouter) -> Dict[str, Any]:
    methods = {}
    
    for route in router.routes:
        if route.path.endswith("/tools"):
            continue
            
        endpoint_func = route.endpoint
        signature = inspect.signature(endpoint_func)
        
        properties = {}
        required = []
        
        for name, param in signature.parameters.items():
            if name == 'service':
                continue
                
            param_type = param.annotation
            if hasattr(param_type, '__fields__'): 
                properties[name] = {
                    "type": "object",
                    "description": f"Parameter: {name}",
                    "properties": {
                        field_name: {
                            "type": _get_json_type(field.annotation),
                            "description": field.description or f"Field: {field_name}"
                        }
                        for field_name, field in param_type.__fields__.items()
                    }
                }
                continue
            
            param_type = str(param.annotation)
            param_type = param_type.replace('typing.Optional[', '').replace(']', '')
            param_type = param_type.replace('typing.', '')
            param_type = param_type.replace("<class '", '').replace("'>", '')
            
            properties[name] = {
                "type": _get_json_type(param_type),
                "description": f"Parameter: {name}"
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(name)
        
        method_name = route.name or route.path.split("/")[-1]
        docstring = endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} request to {route.path}"
        
        methods[method_name] = {
            "description": docstring.strip(),
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required if required else None
            }
        }

    return methods

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