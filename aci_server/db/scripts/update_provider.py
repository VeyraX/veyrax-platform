import sys
import os
import json
import asyncio
from pathlib import Path

sys.path.append('/app')

from db.supabase import get_supabase
from main import INTEGRATION_ROUTERS, get_router_tools

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
                tool_spec = get_router_tools(router)
                
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
                
                update_data = {
                    "input_schema": tool_spec
                }
                
                if component_data:
                    update_data["ui_component"] = component_data
                
                supabase.table("providers").update(update_data).eq("id", provider["id"]).execute()
                
                print(f"Updated provider {provider['name']} with tool specification and UI component data")
                
            except Exception as e:
                print(f"Error updating provider {provider['name']}: {str(e)}")
        else:
            print(f"Provider {provider['name']} with tag {provider_tag} not found in INTEGRATION_ROUTERS")

if __name__ == "__main__":
    asyncio.run(update_provider_data())