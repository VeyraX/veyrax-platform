import json
from pathlib import Path
from integrations.common.encryption import encrypt
from db.supabase import get_supabase

supabase = get_supabase()

def load_api_keys_config():
    config_path = Path(__file__).parent / "config" / "migrate_api_keys.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return None

def get_provider_id(provider_tag: str) -> str:
    try:
        result = supabase.table("providers") \
            .select("id") \
            .eq("provider_tag", provider_tag) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        else:
            print(f"Provider not found: {provider_tag}")
            return None
    except Exception as e:
        print(f"Error getting provider ID for {provider_tag}: {str(e)}")
        return None

def migrate_rent_api_keys():
    print("Starting rent_api_keys migration...")
    
    config = load_api_keys_config()
    if not config:
        print("Failed to load configuration")
        return
        
    for provider_data in config["rent_api_keys"]:
        provider_tag = provider_data["provider_tag"]
        api_key = provider_data.get("api_key", "").strip()
        
        if not api_key:
            print(f"Skipping {provider_tag}: API key is empty")
            continue
        
        provider_id = get_provider_id(provider_tag)
        if not provider_id:
            continue
            
        try:
            encrypted_key = encrypt(api_key)
            
            result = supabase.table("rent_api_keys").upsert({
                "provider_id": provider_id,
                "api_key": encrypted_key
            }, on_conflict="provider_id").execute()
            
            print(f"Successfully upserted API key for provider: {provider_tag}")
            
        except Exception as e:
            print(f"Error upserting API key for {provider_tag}: {str(e)}")

if __name__ == "__main__":
    migrate_rent_api_keys() 