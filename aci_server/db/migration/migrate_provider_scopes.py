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
        supabase = get_supabase()
        response = supabase.table("providers").select("id, name, scopes").execute()
        providers = response.data
        
        print(f"Found {len(providers)} providers")
        
        scope_count = 0
        skipped_count = 0
        
        for provider in providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            scopes = provider.get("scopes")
            
            if not scopes:
                print(f"No scopes found for provider: {provider_name}")
                continue

            if isinstance(scopes, str):
                try:
                    scopes = json.loads(scopes)
                except json.JSONDecodeError:
                    print(f"Failed to parse scopes JSON for provider: {provider_name}")
                    continue
            
            print(f"Processing {len(scopes)} scopes for provider: {provider_name}")
            
            for scope_item in scopes:
                try:
                    scope_id = scope_item.get("scope")
                    scope_name = scope_item.get("scope_name")
                    
                    if not scope_id or not scope_name:
                        print(f"Missing scope data in item for provider {provider_name}: {scope_item}")
                        continue
                    
                    existing_scope = supabase.table("provider_scopes").select("*").eq("provider_id", provider_id).eq("scope_id", scope_id).execute()
                    
                    if existing_scope.data:
                        print(f"Skipping existing scope: {scope_name} ({scope_id}) for provider: {provider_name}")
                        skipped_count += 1
                        continue
                    
                    supabase.table("provider_scopes").insert({
                        "scope_id": scope_id,
                        "scope_name": scope_name,
                        "provider_id": provider_id
                    }).execute()
                    
                    scope_count += 1
                    print(f"Added scope: {scope_name} for provider: {provider_name}")
                    
                except Exception as e:
                    print(f"Error adding scope for provider {provider_name}: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        print(f"Migration complete! Added {scope_count} scopes to provider_scopes table")
        print(f"Skipped {skipped_count} existing scopes")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_provider_scopes()