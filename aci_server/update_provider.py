import sys
import os
import json
import asyncio
from pathlib import Path
import argparse
from typing import List, Dict, Any, Optional
import yaml
import datetime

sys.path.append('/app')

from db.supabase import get_supabase
from gpt_generation import generate_prompt
from main import INTEGRATION_ROUTERS, get_router_tools

# System prompt for generating action names
SYSTEM_PROMPT = """
You are an AI specialized in creating clear, concise names for API actions.
Your task is to generate a user-friendly display name for each API action.

RULES:
1. Generate 2-4 words maximum
2. Make it descriptive of what the action does
3. Use Title Case (capitalize each word)
4. Focus on the action's purpose, not technical details
5. Be concise but clear
6. Return ONLY the name, nothing else - no explanation, no quotes, no period.
"""

def normalize_provider_tag(tag):
    """Normalize provider tag for consistent lookup"""
    if "-" in tag:
        return tag.replace("-", "_")
    return tag.replace("_", "-")

def generate_action_name(action_slug: str) -> str:
    """Generate a user-friendly name for an action"""
    try:
        user_prompt = f"""
        Generate a concise, user-friendly display name for this API action:
        Action ID: {action_slug}
        Based on this information, provide a clear, concise 2-4 word name that describes what this action does.
        """
        display_name = generate_prompt(SYSTEM_PROMPT, user_prompt)
        return display_name.strip('"\'').strip()
    except Exception as e:
        print(f"Error generating name for {action_slug}: {str(e)}")
        return action_slug.replace("_", " ").title()

def get_existing_provider_data(supabase, provider_id: str) -> tuple:
    """Get existing actions and scopes for a provider"""
    
    # Get existing actions
    actions = supabase.table("provider_actions").select(
        "id, action_slug, action_name"
    ).eq("provider_id", provider_id).execute()
    
    existing_actions = {
        action["action_slug"]: action["id"]
        for action in actions.data
    }
    
    # Get existing scopes
    scopes = supabase.table("provider_scopes").select(
        "id, scope_id, scope_name"
    ).eq("provider_id", provider_id).execute()
    
    existing_scopes = {
        scope["scope_id"]: scope["id"]
        for scope in scopes.data
    }
    
    return existing_actions, existing_scopes

def get_existing_action_scopes(supabase, action_id: str) -> set:
    """Get existing scope links for an action"""
    links = supabase.table("provider_action_scopes").select(
        "scope_id"
    ).eq("action_id", action_id).execute()
    
    return {link["scope_id"] for link in links.data}

def get_provider_schemas(provider_tag: str) -> Dict[str, Any]:
    """Get all schemas and examples for a provider from the integration router"""
    try:
        router_key = provider_tag
        if router_key not in INTEGRATION_ROUTERS:
            router_key = normalize_provider_tag(provider_tag)
        
        if router_key not in INTEGRATION_ROUTERS:
            print(f"Provider {provider_tag} not found in INTEGRATION_ROUTERS")
            return {}
            
        router = INTEGRATION_ROUTERS[router_key]
        full_tool_spec = get_router_tools(router)
        
        input_schemas = {}
        output_schemas = {}
        example_schemas = {}
        
        # Load examples from YAML
        examples_path = Path('/app/integrations') / provider_tag / "examples.yaml"
        alt_examples_path = Path('/app/integrations') / normalize_provider_tag(provider_tag) / "examples.yaml"
        
        for path in [examples_path, alt_examples_path]:
            if path.exists():
                try:
                    with open(path, "r") as f:
                        examples_data = yaml.safe_load(f)
                    if examples_data and "routes" in examples_data:
                        for route_info in examples_data["routes"]:
                            if "endpoint" in route_info and "examples" in route_info:
                                endpoint_name = route_info["endpoint"].split("/")[-1]
                                endpoint_examples = []
                                
                                for example in route_info["examples"]:
                                    example_entry = {
                                        "scenario": example.get("scenario", ""),
                                        "description": example.get("description", "")
                                    }
                                    
                                    if "input_json" in example:
                                        example_entry["input"] = (
                                            json.loads(example["input_json"])
                                            if isinstance(example["input_json"], str)
                                            else example["input_json"]
                                        )
                                    
                                    if "output_json" in example:
                                        example_entry["output"] = (
                                            json.loads(example["output_json"])
                                            if isinstance(example["output_json"], str)
                                            else example["output_json"]
                                        )
                                    
                                    endpoint_examples.append(example_entry)
                                
                                if endpoint_examples:
                                    example_schemas[endpoint_name] = endpoint_examples
                    break
                except Exception as e:
                    print(f"Error loading examples from {path}: {str(e)}")
        
        # Extract schemas from tool spec
        if isinstance(full_tool_spec, list):
            for tool_item in full_tool_spec:
                if isinstance(tool_item, dict) and 'function' in tool_item:
                    function_data = tool_item['function']
                    
                    if 'name' in function_data:
                        endpoint_name = function_data['name'].split('/')[-1]
                        
                        input_schema = {
                            'type': 'function',
                            'function': function_data.copy()
                        }
                        
                        if 'output_schema' in input_schema['function']:
                            output_schemas[endpoint_name] = input_schema['function']['output_schema']
                            del input_schema['function']['output_schema']
                        
                        if 'examples' in input_schema:
                            del input_schema['examples']
                        
                        input_schemas[endpoint_name] = input_schema
        
        # Get component data
        component_data = None
        for component_path in [
            Path('/app/integrations') / provider_tag / "component.json",
            Path('/app/integrations') / normalize_provider_tag(provider_tag) / "component.json"
        ]:
            if component_path.exists():
                try:
                    with open(component_path, "r") as f:
                        component_data = json.load(f)
                    break
                except Exception as e:
                    print(f"Error loading component data from {component_path}: {str(e)}")
        
        return {
            "input_schemas": input_schemas,
            "output_schemas": output_schemas,
            "example_schemas": example_schemas,
            "component_data": component_data
        }
    except Exception as e:
        print(f"Error getting provider schemas: {str(e)}")
        return {}

async def create_or_update_provider(provider_data: Dict[str, Any]):
    try:
        supabase = get_supabase()
        
        # Create or update provider
        # Start with all fields from provider_data
        provider_record = provider_data.copy()
        
        # Ensure critical fields have expected values
        provider_record["name"] = provider_data["name"]
        provider_record["provider_tag"] = provider_data["provider_tag"]
        provider_record["description"] = provider_data.get("description", "")
        provider_record["auth_method"] = provider_data.get("auth_method", "none")
        provider_record['created_at'] = int(datetime.datetime.now().timestamp())
        
        # Check if provider exists
        existing_provider = supabase.table("providers").select("*")\
            .eq("provider_tag", provider_data["provider_tag"])\
            .execute()
        
        if existing_provider.data:
            provider_id = existing_provider.data[0]["id"]
            provider = supabase.table("providers").update(provider_record)\
                .eq("id", provider_id).execute().data[0]
            print(f"\n=== Updating existing provider: {provider['name']} ===")
        else:
            provider = supabase.table("providers").insert(provider_record).execute().data[0]
            provider_id = provider["id"]
            print(f"\n=== Created new provider: {provider['name']} ===")
        
        # Get schemas and examples from integration router
        schemas = get_provider_schemas(provider_data["provider_tag"])
        
        if schemas:
            update_data = {}
            
            if schemas.get("input_schemas"):
                update_data["input_schema"] = schemas["input_schemas"]
            
            if schemas.get("output_schemas"):
                update_data["output_schema"] = schemas["output_schemas"]
            
            if schemas.get("example_schemas"):
                update_data["example_schema"] = schemas["example_schemas"]
            
            if schemas.get("component_data"):
                update_data["ui_component"] = schemas["component_data"]
            
            if update_data:
                supabase.table("providers").update(update_data)\
                    .eq("id", provider_id).execute()
                print(f"Updated provider schemas: {list(update_data.keys())}")
            
            # Create actions from input schemas
            if schemas.get("input_schemas"):
                existing_actions, existing_scopes = get_existing_provider_data(supabase, provider_id)
                
                actions_added = 0
                actions_updated = 0
                
                for endpoint_name, schema in schemas["input_schemas"].items():
                    action_slug = endpoint_name
                    action_name = generate_action_name(action_slug)
                    
                    action_record = {
                        "provider_id": provider_id,
                        "action_slug": action_slug,
                        "action_name": action_name,
                        "input_schema": schema,
                        "output_schema": schemas["output_schemas"].get(endpoint_name, {})
                    }
                    
                    if action_slug in existing_actions:
                        action_id = existing_actions[action_slug]
                        supabase.table("provider_actions").update(action_record)\
                            .eq("id", action_id).execute()
                        actions_updated += 1
                        print(f"Updated action: {action_name}")
                    else:
                        result = supabase.table("provider_actions").insert(action_record).execute()
                        actions_added += 1
                        print(f"Added action: {action_name}")
                
                print(f"\nActions added: {actions_added}")
                print(f"Actions updated: {actions_updated}")
        else:
            print("No schemas found for provider")
        
    except Exception as e:
        print(f"\nError creating/updating provider: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Create or update provider with schemas')
    parser.add_argument('json_file', help='Path to JSON file with provider data')
    args = parser.parse_args()
    
    try:
        with open(args.json_file, 'r') as f:
            provider_data = json.load(f)
        asyncio.run(create_or_update_provider(provider_data))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 