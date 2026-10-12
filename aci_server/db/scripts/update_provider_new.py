import sys
import os
import json
import asyncio
from pathlib import Path
import argparse
from typing import List, Dict, Any, Optional
import yaml
import datetime
from upstash_vector import Index, Vector

sys.path.append('/app')

from db.supabase import get_supabase
from llm import embed
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

def get_existing_action_scopes(supabase, action_id: str) -> dict:
    """Get existing scope links for an action with their scope_ids"""
    links = supabase.table("provider_action_scopes").select(
        "id, scope_id"
    ).eq("action_id", action_id).execute()
    
    # Get the actual scope_id strings from provider_scopes table
    scope_links = {}
    for link in links.data:
        scope = supabase.table("provider_scopes").select(
            "scope_id"
        ).eq("id", link["scope_id"]).execute()
        if scope.data:
            scope_id_string = scope.data[0]["scope_id"]
            scope_links[scope_id_string] = link["scope_id"]
    
    return scope_links

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
                                        try:
                                            # Handle both string and parsed JSON
                                            if isinstance(example["input_json"], str):
                                                # Try to parse JSON from string
                                                example_entry["input"] = json.loads(example["input_json"])
                                            else:
                                                # Already parsed by YAML loader
                                                example_entry["input"] = example["input_json"]
                                            print(f"Successfully parsed input example for {endpoint_name}")
                                        except json.JSONDecodeError as e:
                                            print(f"Error parsing input JSON for {endpoint_name}: {str(e)}")
                                            # Store as-is if JSON parsing fails
                                            example_entry["input"] = example["input_json"]
                                    
                                    if "output_json" in example:
                                        try:
                                            # Handle both string and parsed JSON
                                            if isinstance(example["output_json"], str):
                                                # Try to parse JSON from string
                                                example_entry["output"] = json.loads(example["output_json"])
                                            else:
                                                # Already parsed by YAML loader
                                                example_entry["output"] = example["output_json"]
                                            print(f"Successfully parsed output example for {endpoint_name}")
                                        except json.JSONDecodeError as e:
                                            print(f"Error parsing output JSON for {endpoint_name}: {str(e)}")
                                            # Store as-is if JSON parsing fails
                                            example_entry["output"] = example["output_json"]
                                    
                                    endpoint_examples.append(example_entry)
                                
                                if endpoint_examples:
                                    example_schemas[endpoint_name] = endpoint_examples
                                    print(f"Added {len(endpoint_examples)} examples for {endpoint_name}")
                                else:
                                    print(f"No examples found for {endpoint_name}")
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
                        
                        input_schema = tool_item.copy()
                        
                        if 'output_schema' in function_data:
                            output_schemas[endpoint_name] = function_data['output_schema']
                            del input_schema['function']['output_schema']
                        
                        if 'examples' in input_schema:
                            del input_schema['examples']
                        
                        input_schemas[endpoint_name] = input_schema
        
        # Add examples to the actions
        for endpoint_name, schemas in input_schemas.items():
            if endpoint_name in example_schemas:
                if 'function' in schemas:
                    schemas['function']['examples'] = example_schemas[endpoint_name]
                    print(f"Attached examples to {endpoint_name}")
        
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

async def add_provider_to_providers_index(provider_id: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Create text representation for embedding
        text = f"{provider_data.get('name', '')}\n"
        if provider_data.get('description'):
            text += f"{provider_data.get('description')}\n"
        if provider_data.get('provider_tag'):
            text += f"{provider_data.get('provider_tag')}\n"
            
        # Generate embedding
        embedding = embed(text)
        
        # Get vector index for Providers
        url = os.getenv("UPSTASH_PROVIDERS_URL")
        token = os.getenv("UPSTASH_PROVIDERS_TOKEN")
        if not url or not token:
            return {"error": "Missing Upstash Vector credentials for Providers index"}
        vector_index = Index(url=url, token=token)
        
        # Check if the provider already exists in the index
        check_result = vector_index.query(
            vector=embedding,
            top_k=1,
            include_metadata=True,
            filter={"id": {"$eq": str(provider_id)}}
        )
        
        if check_result and check_result.matches and len(check_result.matches) > 0:
            return {"success": True, "message": f"Provider {provider_id} already exists in Providers index"}
        
        # Create vector with metadata
        vector = Vector(
            id=str(provider_id),
            vector=embedding,
            metadata={
                "id": str(provider_id),
                "name": provider_data.get('name', ''),
                "description": provider_data.get('description', ''),
                "logo_url": provider_data.get('logo_url', ''),
                "created_at": provider_data.get('created_at', ''),
                "provider_tag": provider_data.get('provider_tag', ''),
                "auth_method": provider_data.get('auth_method', ''),
                "is_enabled": provider_data.get('is_enabled', True)
            }
        )
        
        # Upsert vector to index
        vector_index.upsert(vectors=[vector])
        
        return {"success": True, "message": f"Provider {provider_id} added to Providers index"}
        
    except Exception as e:
        print(f"Error adding provider to Providers index: {str(e)}")
        return {"error": str(e)}

async def create_or_update_provider(provider_data: Dict[str, Any]):
    try:
        supabase = get_supabase()
        
        # Create or update provider
        # Start with all fields from provider_data
        provider_record = provider_data.copy()
        
        # Remove fields that are not columns in the providers table
        if "action_scopes" in provider_record:
            del provider_record["action_scopes"]
        if "scopes" in provider_record:
            del provider_record["scopes"]
        
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
            
        # Add provider to Providers vector index
        provider_record["id"] = provider_id
        index_result = await add_provider_to_providers_index(provider_id, provider_record)
        if "error" in index_result:
            print(f"Warning: {index_result['error']}")
        else:
            print(index_result["message"])
        
        # Create or update scopes
        existing_actions, existing_scopes = get_existing_provider_data(supabase, provider_id)
        
        # Process scopes from the provider data
        scopes_added = 0
        scopes_updated = 0
        
        # Check if provider uses OAuth auth method
        auth_method = provider_data.get("auth_method", "").lower()
        oauth_enabled = auth_method == "oauth"
        
        if "scopes" in provider_data:
            for scope in provider_data["scopes"]:
                scope_id = scope["scope_id"]
                scope_name = scope["scope_name"]
                
                scope_record = {
                    "provider_id": provider_id,
                    "scope_id": scope_id,
                    "scope_name": scope_name
                }
                
                if scope_id in existing_scopes:
                    # Update existing scope
                    supabase.table("provider_scopes").update(scope_record)\
                        .eq("id", existing_scopes[scope_id]).execute()
                    scopes_updated += 1
                    print(f"Updated scope: {scope_name}")
                else:
                    # Create new scope
                    result = supabase.table("provider_scopes").insert(scope_record).execute()
                    # Store the new scope ID for action-scope mapping
                    existing_scopes[scope_id] = result.data[0]["id"]
                    scopes_added += 1
                    print(f"Added scope: {scope_name}")
            
            print(f"\nScopes added: {scopes_added}")
            print(f"Scopes updated: {scopes_updated}")
        
        # Get schemas and examples from integration router
        schemas = get_provider_schemas(provider_data["provider_tag"])
        actions_added = 0
        actions_updated = 0
        
        # Process schemas if available
        if schemas and schemas.get("input_schemas"):
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
            for endpoint_name, schema in schemas["input_schemas"].items():
                action_slug = endpoint_name
                action_name = generate_action_name(action_slug)
                
                action_record = {
                    "provider_id": provider_id,
                    "action_slug": action_slug,
                    "action_name": action_name,
                    "input_schema": schema,
                    "output_schema": schemas["output_schemas"].get(endpoint_name, {}),
                    "examples": schemas["example_schemas"].get(endpoint_name, [])
                }

                if action_slug == 'validate_key':
                    print(f"Skipping action: {action_slug}")
                    continue
                
                if action_slug in existing_actions:
                    action_id = existing_actions[action_slug]
                    supabase.table("provider_actions").update(action_record)\
                        .eq("id", action_id).execute()
                    actions_updated += 1
                    print(f"Updated action: {action_name} with {len(schemas['example_schemas'].get(endpoint_name, []))} examples")
                else:
                    result = supabase.table("provider_actions").insert(action_record).execute()
                    action_id = result.data[0]["id"]
                    existing_actions[action_slug] = action_id
                    actions_added += 1
                    print(f"Added action: {action_name}")
        else:
            print("No schemas found for provider")
        
        # Create actions manually from action_scopes if no schemas available or as a fallback
        if "action_scopes" in provider_data:
            print("\n=== Creating actions from action_scopes ===")
            for action_slug in provider_data["action_scopes"].keys():
                if action_slug not in existing_actions:
                    action_name = generate_action_name(action_slug)
                    
                    action_record = {
                        "provider_id": provider_id,
                        "action_slug": action_slug,
                        "action_name": action_name,
                        "input_schema": {},
                        "output_schema": {},
                        "examples": []
                    }
                    
                    result = supabase.table("provider_actions").insert(action_record).execute()
                    action_id = result.data[0]["id"]
                    existing_actions[action_slug] = action_id
                    actions_added += 1
                    print(f"Added action: {action_name}")
        
        print(f"\nActions added: {actions_added}")
        print(f"Actions updated: {actions_updated}")
        
        # Process action_scopes mapping if provided
        if "action_scopes" in provider_data:
            action_scope_links_added = 0
            
            # Only link actions to scopes if OAuth is enabled
            if oauth_enabled:
                print("\n=== Creating action-scope links for OAuth ===")
                for action_slug, required_scopes in provider_data["action_scopes"].items():
                    if action_slug in existing_actions:
                        action_id = existing_actions[action_slug]
                        
                        # Get existing scope links for this action
                        existing_action_scopes = get_existing_action_scopes(supabase, action_id)
                        
                        # Create links for each scope
                        for scope_id in required_scopes:
                            # Check if the scope exists and if there's already a link for this scope_id string
                            if scope_id in existing_scopes and scope_id not in existing_action_scopes:
                                # Create new link
                                link_record = {
                                    "action_id": action_id,
                                    "scope_id": existing_scopes[scope_id]
                                }
                                supabase.table("provider_action_scopes").insert(link_record).execute()
                                action_scope_links_added += 1
                                print(f"Linked action '{action_slug}' to scope '{scope_id}'")
                    else:
                        print(f"Warning: Action '{action_slug}' not found, cannot link to scopes")
                
                print(f"\nAction-scope links added: {action_scope_links_added}")
            else:
                print("\n=== Skipping action-scope links (OAuth not enabled) ===")
                print("With API Key authentication, all actions are available without scope restrictions.")
        
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