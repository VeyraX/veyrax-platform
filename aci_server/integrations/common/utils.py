from fastapi import routing
from typing import Dict, Any
import inspect

def get_router_tools(router: routing.APIRouter, tool_name: str) -> Dict[str, Any]:
    tools = {}
    
    for route in router.routes:
        if route.path.endswith("/tools"):
            continue
            
        endpoint_func = route.endpoint
        signature = inspect.signature(endpoint_func)
        
        properties = {}
        required = []
        
        for name, param in signature.parameters.items():
            if name in ['service', 'filters']:
                continue
                
            param_type = str(param.annotation)
            param_type = param_type.replace('typing.Optional[', '').replace(']', '')
            param_type = param_type.replace('typing.', '')
            param_type = param_type.replace("<class '", '').replace("'>", '')
            
            json_type = "string"
            if "int" in param_type.lower():
                json_type = "integer"
            elif "float" in param_type.lower() or "decimal" in param_type.lower():
                json_type = "number"
            elif "bool" in param_type.lower():
                json_type = "boolean"
            
            properties[name] = {
                "type": json_type,
                "description": f"Parameter: {name}"
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(name)
        
        method_name = route.name or route.path.split("/")[-1]
        docstring = endpoint_func.__doc__ or f"Handle {list(route.methods)[0]} request to {route.path}"
        
        tools[method_name] = {
            "tool_name": tool_name,
            "method_name": method_name,
            "description": docstring.strip(),
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required if required else None
            }
        }
    
    return tools