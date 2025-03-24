import sys
import os
import json
from pathlib import Path

# Use the same import approach as update_provider.py
sys.path.append('/app')

from db.supabase import get_supabase
from dotenv import load_dotenv

# Make sure environment variables are loaded
load_dotenv()

def migrate_provider_scopes():
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Fetch all providers from the providers table
        response = supabase.table("providers").select("id, name, scopes").execute()
        providers = response.data
        
        print(f"Found {len(providers)} providers")
        
        # Counter for tracking operations
        scope_count = 0
        
        for provider in providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            scopes = provider.get("scopes")
            
            if not scopes:
                print(f"No scopes found for provider: {provider_name}")
                continue
                
            # Convert string to JSON if necessary
            if isinstance(scopes, str):
                try:
                    scopes = json.loads(scopes)
                except json.JSONDecodeError:
                    print(f"Failed to parse scopes JSON for provider: {provider_name}")
                    continue
            
            print(f"Processing {len(scopes)} scopes for provider: {provider_name}")
            
            # Insert each scope into the provider_scopes table
            for scope_item in scopes:
                try:
                    scope_id = scope_item.get("scope")
                    scope_name = scope_item.get("scope_name")
                    
                    if not scope_id or not scope_name:
                        print(f"Missing scope data in item for provider {provider_name}: {scope_item}")
                        continue
                    
                    # Check if this scope already exists in the database
                    existing_scope = supabase.table("provider_scopes").select(
                        "id"
                    ).eq("provider_id", provider_id).eq("scope_id", scope_id).limit(1).execute()
                    
                    if existing_scope.data:
                        print(f"Scope '{scope_name}' already exists for provider '{provider_name}'. Skipping...")
                        continue
                    
                    # Insert into the new table
                    supabase.table("provider_scopes").insert({
                        "scope_id": scope_id,
                        "scope_name": scope_name,
                        "provider_id": provider_id
                    }).execute()
                    
                    scope_count += 1
                    print(f"Added scope: {scope_name} for provider: {provider_name}")
                    
                except Exception as e:
                    print(f"Error adding scope for provider {provider_name}: {str(e)}")
        
        print(f"Migration complete! Added {scope_count} scopes to provider_scopes table")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_provider_scopes()