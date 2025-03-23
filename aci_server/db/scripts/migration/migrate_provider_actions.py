import sys
import os
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('/app')

from db.supabase import get_supabase
from dotenv import load_dotenv

# Make sure environment variables are loaded
load_dotenv()

def migrate_provider_actions():
    """
    Creates action records from provider data with the correct structure:
    - Each action has its own input_schema, output_schema, and examples
    - UI components are linked to actions through their related_endpoints
    """
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Fetch all providers with their schemas
        response = supabase.table("providers").select(
            "id, name, logo_url, input_schema, output_schema, ui_component, example_schema"
        ).execute()
        providers = response.data
        
        print(f"Found {len(providers)} providers")
        
        # Counter for tracking operations
        action_count = 0
        
        for provider in providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            logo_url = provider["logo_url"]
            
            # Parse JSON strings if needed
            for field_name in ['input_schema', 'output_schema', 'ui_component', 'example_schema']:
                field_value = provider.get(field_name)
                if isinstance(field_value, str):
                    try:
                        provider[field_name] = json.loads(field_value)
                    except (json.JSONDecodeError, TypeError):
                        print(f"Failed to parse {field_name} JSON for provider: {provider_name}")
                        provider[field_name] = {}
                elif field_value is None:
                    provider[field_name] = {}
            
            # Get the parsed data
            input_schema = provider["input_schema"] or {}
            output_schema = provider["output_schema"] or {}
            ui_component = provider["ui_component"] or {}
            example_schema = provider["example_schema"] or {}
            
            print(f"Processing actions for provider: {provider_name}")
            print(f"- Input schema keys: {list(input_schema.keys())}")
            
            # Get UI component to endpoint mapping
            component_to_endpoints = {}
            endpoint_to_component = {}
            
            # Handle different UI component formats
            if isinstance(ui_component, dict):
                for component_name, component_data in ui_component.items():
                    if isinstance(component_data, dict) and "related_endpoints" in component_data:
                        endpoints = component_data.get("related_endpoints", [])
                        component_to_endpoints[component_name] = endpoints
                        
                        for endpoint in endpoints:
                            endpoint_to_component[endpoint] = {
                                "component_name": component_name,
                                "component_data": component_data
                            }
            elif isinstance(ui_component, list):
                # If it's a list, try to find component data with related_endpoints
                for component_item in ui_component:
                    if isinstance(component_item, dict):
                        # Look for component name and related_endpoints
                        component_name = component_item.get("name", "UnknownComponent")
                        related_endpoints = component_item.get("related_endpoints", [])
                        
                        if related_endpoints:
                            component_to_endpoints[component_name] = related_endpoints
                            
                            for endpoint in related_endpoints:
                                endpoint_to_component[endpoint] = {
                                    "component_name": component_name,
                                    "component_data": component_item
                                }
            
            # Process each action slug
            for action_slug in input_schema.keys():
                try:
                    # Skip validation_key actions
                    if action_slug == "validate_key":
                        continue
                        
                    # Get the specific schemas for this action
                    action_input_schema = input_schema.get(action_slug, {})
                    action_output_schema = output_schema.get(action_slug, {})
                    action_examples = example_schema.get(action_slug, [])
                    
                    # Calculate a stable ID using MD5 hash
                    import hashlib
                    action_id = hashlib.md5(f"{provider_id}:{action_slug}".encode()).hexdigest()
                    
                    # Get component for this action
                    action_component = None
                    if action_slug in endpoint_to_component:
                        component_info = endpoint_to_component[action_slug]
                        action_component = {
                            component_info["component_name"]: component_info["component_data"]
                        }
                    
                    # Create the action record - without provider_tag
                    action_data = {
                        "provider_id": provider_id,
                        "action_slug": action_slug,
                        "input_schema": action_input_schema,
                        "output_schema": action_output_schema, 
                        "ui_component": action_component,
                        "examples": action_examples
                    }
                    
                    # Log the action data structure (for debugging)
                    print(f"Adding action: {action_slug} for provider: {provider_name}")
                    
                    # Insert into the providers_actions table
                    supabase.table("providers_actions").insert(action_data).execute()
                    
                    action_count += 1
                    print(f"Successfully added action: {action_slug} for provider: {provider_name}")
                    
                except Exception as e:
                    print(f"Error adding action {action_slug} for provider {provider_name}: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        print(f"Migration complete! Added {action_count} actions to providers_actions table")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_provider_actions()