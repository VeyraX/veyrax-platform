import os
import json
from typing import Dict, Any, List, Union, Optional


def wrap_component_with_tool(component: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'tool_wrapper.json'), 'r') as file:
        tool_wrapper = json.load(file)
    
    return {
        "name": "ToolWrapper",
        "props": {
            "toolName": tool_name,
            "children": component
        },
        "jsx": tool_wrapper["component"]["jsx"]
    }

def load_components(integration_dir: str) -> List[Dict[str, Any]]:
    with open(os.path.join(integration_dir, 'component.json'), 'r') as file:
        components = json.load(file)
        return components if isinstance(components, list) else [components]

def find_component(components: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    for component in components:
        if component["name"] == name:
            return component
    return None

def create_component(component_def: Dict[str, Any], data: Any) -> Dict[str, Any]:
    data_dict = data.dict() if hasattr(data, 'dict') else data
    
    for key, value in data_dict.items():
        if hasattr(value, 'isoformat'):
            data_dict[key] = value.isoformat()
    
    return {
        "name": component_def["name"],
        "props": {"data": data_dict},
        "jsx": component_def["component"]["jsx"]
    }

def prepare_components_auto(data: Any, component_name: str, components: List[Dict[str, Any]],
                           tool_name: str) -> Optional[Dict[str, Any]]:
    if not component_name:
        return None
        
    component_def = find_component(components, component_name)
    if not component_def:
        return None
    
    if hasattr(data, 'items') and data.items:
        component_list = [create_component(component_def, item) for item in data.items()]
        return wrap_component_with_tool(component_list, tool_name)
    
    elif isinstance(data, list):
        component_list = [create_component(component_def, item) for item in data]
        return wrap_component_with_tool(component_list, tool_name)
    
    else:
        component = create_component(component_def, data)
        return wrap_component_with_tool(component, tool_name)

