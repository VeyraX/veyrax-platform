import sys
import os
import json
import asyncio
from pathlib import Path
import inspect
import yaml

sys.path.append('/app')

from db.supabase import get_supabase
from main import INTEGRATION_ROUTERS, get_router_tools
from integrations.common.schema_generation.openai.schema import get_route_schema_class, get_route_output_schema_class

def normalize_provider_tag(tag):
    if "-" in tag:
        return tag.replace("-", "_")
    return tag.replace("_", "-")

async def update_provider_data(provider_tag_filter=None):
    supabase = get_supabase()
    
    query = supabase.table("providers").select("*")
    if provider_tag_filter:
        query = query.eq("provider_tag", provider_tag_filter)
    
    response = query.execute()
    providers = response.data

    if provider_tag_filter and not providers:
        print(f"No provider found with tag: {provider_tag_filter}")
        return

    for provider in providers:
        provider_tag = provider["provider_tag"]
        print(f"Updating provider {provider['name']} with tag {provider_tag}")
        router_key = provider_tag
        
        if router_key not in INTEGRATION_ROUTERS:
            router_key = normalize_provider_tag(provider_tag)
        
        if router_key in INTEGRATION_ROUTERS:
            try:
                router = INTEGRATION_ROUTERS[router_key]
                print(f"Router: {router}")
                full_tool_spec = get_router_tools(router)
                
                print(f"Full tool spec for {provider['name']}:")
                print(json.dumps(full_tool_spec, indent=2)[:500] + "...") 
                
                input_schemas = {}
                output_schemas = {}
                example_schemas = {}
                
                print(f"Checking routes for {provider['name']}...")
                
                examples_path = Path('/app/integrations') / provider_tag / "examples.yaml"
                alt_examples_path = Path('/app/integrations') / normalize_provider_tag(provider_tag) / "examples.yaml"
                
                examples_data = None
                for path in [examples_path, alt_examples_path]:
                    print(f"Checking for examples at: {path}")
                    if path.exists():
                        try:
                            with open(path, "r") as f:
                                examples_data = yaml.safe_load(f)
                            print(f"Loaded examples.yaml for {provider['name']} from {path}")
                            break
                        except Exception as e:
                            print(f"Error loading examples.yaml for {provider['name']} from {path}: {str(e)}")
                
                if examples_data and "routes" in examples_data:
                    for route_info in examples_data["routes"]:
                        if "endpoint" in route_info and "examples" in route_info:
                            endpoint_name = route_info["endpoint"].split("/")[-1]
                            print(f"  Processing examples for endpoint: {endpoint_name}")
                            
                            endpoint_examples = []
                            for example in route_info["examples"]:
                                try:
                                    example_entry = {
                                        "scenario": example.get("scenario", ""),
                                        "description": example.get("description", "")
                                    }
                                    
                                    if "input_json" in example:
                                        if isinstance(example["input_json"], str):
                                            example_entry["input"] = json.loads(example["input_json"])
                                        else:
                                            example_entry["input"] = example["input_json"]
                                    
                                    if "output_json" in example:
                                        if isinstance(example["output_json"], str):
                                            example_entry["output"] = json.loads(example["output_json"])
                                        else:
                                            example_entry["output"] = example["output_json"]
                                    
                                    endpoint_examples.append(example_entry)
                                    print(f"    Added example: {example.get('scenario', 'Unnamed')}")
                                except Exception as e:
                                    print(f"    Error processing example: {str(e)}")
                            
                            if endpoint_examples:
                                example_schemas[endpoint_name] = endpoint_examples
                
                if isinstance(full_tool_spec, list):
                    for tool_item in full_tool_spec:
                        if isinstance(tool_item, dict) and 'function' in tool_item:
                            function_data = tool_item['function']
                            
                            if 'name' in function_data:
                                full_path = function_data['name']
                                endpoint_name = full_path.split('/')[-1]
                                
                                print(f"  Processing tool spec for endpoint: {endpoint_name}")
                                
                                input_schema = {
                                    'type': 'function',
                                    'function': function_data.copy()
                                }
                                
                                if 'output_schema' in input_schema['function']:
                                    output_schema = input_schema['function']['output_schema']
                                    output_schemas[endpoint_name] = output_schema
                                    del input_schema['function']['output_schema']
                                    print(f"  Extracted output schema from tool spec for {endpoint_name}")
                                
                                if 'examples' in input_schema:
                                    del input_schema['examples']
                                
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
                
                print(f"Found {len(input_schemas)} input schemas, {len(output_schemas)} output schemas, and {len(example_schemas)} example schemas for {provider['name']}")
                
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
                
                if example_schemas:
                    update_data["example_schema"] = example_schemas
                
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
    tag_filter = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(update_provider_data(tag_filter))