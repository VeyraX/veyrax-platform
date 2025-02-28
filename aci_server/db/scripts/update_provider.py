import sys
import os
import json
import asyncio
from pathlib import Path
import inspect

sys.path.append('/app')

from db.supabase import get_supabase
from main import INTEGRATION_ROUTERS, get_router_tools
from integrations.common.schema_generation.openai.schema import get_route_schema_class, get_route_output_schema_class

def normalize_provider_tag(tag):
    if "-" in tag:
        return tag.replace("-", "_")
    return tag.replace("_", "-")

async def update_provider_data():
    supabase = get_supabase()
    
    response = supabase.table("providers").select("*").execute()
    providers = response.data
    
    for provider in providers:
        provider_tag = provider["provider_tag"]
        router_key = provider_tag
        
        if router_key not in INTEGRATION_ROUTERS:
            router_key = normalize_provider_tag(provider_tag)
        
        if router_key in INTEGRATION_ROUTERS:
            try:
                router = INTEGRATION_ROUTERS[router_key]
                full_tool_spec = get_router_tools(router)
                
                print(f"Full tool spec for {provider['name']}:")
                print(json.dumps(full_tool_spec, indent=2)[:500] + "...") 
                
                input_schemas = {}
                output_schemas = {}
                
                print(f"Checking routes for {provider['name']}...")
                
                if isinstance(full_tool_spec, list):
                    for tool_item in full_tool_spec:
                        if isinstance(tool_item, dict) and 'function' in tool_item:
                            function_data = tool_item['function']
                            
                            if 'name' in function_data:
                                full_path = function_data['name']
                                endpoint_name = full_path.split('/')[-1]
                                
                                print(f"  Processing tool spec for endpoint: {endpoint_name}")
                                
                                input_schema = tool_item.copy()
                                
                                if 'output_schema' in function_data:
                                    output_schema = function_data['output_schema']
                                    output_schemas[endpoint_name] = output_schema
                                    
                                    input_schema['function'] = function_data.copy()
                                    del input_schema['function']['output_schema']
                                    
                                    print(f"  Extracted output schema from tool spec for {endpoint_name}")
                                
                                input_schemas[endpoint_name] = input_schema
                                print(f"  Added input schema for {endpoint_name}")
                
                for route in router.routes:
                    route_path = route.path
                    endpoint_name = route_path.split('/')[-1]
                    
                    print(f"  Checking endpoint route: {endpoint_name}")
                    
                    if hasattr(route.endpoint, "__output_schema_class__"):
                        try:
                            output_schema_class = getattr(route.endpoint, "__output_schema_class__")
                            print(f"  Output schema class: {output_schema_class}")
                            
                            if output_schema_class is not None:
                                print(f"  Output schema class type: {type(output_schema_class)}")
                                
                                if hasattr(output_schema_class, "model_json_schema"):
                                    schema_dict = output_schema_class.model_json_schema()
                                    
                                    if endpoint_name not in output_schemas:
                                        output_schemas[endpoint_name] = schema_dict
                                        print(f"  Added output schema from class for {endpoint_name}")
                                else:
                                    print(f"  No model_json_schema method found on {output_schema_class}")
                        except Exception as e:
                            print(f"  Error accessing output schema class: {str(e)}")
                
                print(f"Found {len(input_schemas)} input schemas and {len(output_schemas)} output schemas for {provider['name']}")
                
                if not input_schemas:
                    print(f"WARNING: Input schemas is empty for {provider['name']}!")
                    print(f"Original tool_spec structure: {type(full_tool_spec)}")
                    if isinstance(full_tool_spec, list):
                        print(f"Tool spec length: {len(full_tool_spec)}")
                        if len(full_tool_spec) > 0:
                            print(f"First item type: {type(full_tool_spec[0])}")
                
                component_data = None
                possible_paths = [
                    Path('/app/integrations') / provider_tag / "component.json",
                    Path('/app/integrations') / normalize_provider_tag(provider_tag) / "component.json"
                ]
                
                for component_path in possible_paths:
                    print(f"Checking path: {component_path}")
                    if component_path.exists():
                        try:
                            with open(component_path, "r") as f:
                                component_data = json.load(f)
                            print(f"Loaded component.json for {provider['name']} from {component_path}")
                            break
                        except Exception as e:
                            print(f"Error loading component.json for {provider['name']} from {component_path}: {str(e)}")
                
                if not component_data:
                    print(f"No component.json found for {provider['name']}")
                
                update_data = {}
                
                if input_schemas:
                    update_data["input_schema"] = input_schemas
                
                if output_schemas:
                    update_data["output_schema"] = output_schemas
                
                if component_data:
                    update_data["ui_component"] = component_data
                
                if update_data:
                    supabase.table("providers").update(update_data).eq("id", provider["id"]).execute()
                    print(f"Updated provider {provider['name']} with data: {list(update_data.keys())}")
                else:
                    print(f"No data to update for provider {provider['name']}")
                
            except Exception as e:
                print(f"Error updating provider {provider['name']}: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Provider {provider['name']} with tag {provider_tag} not found in INTEGRATION_ROUTERS")

if __name__ == "__main__":
    asyncio.run(update_provider_data())