#!/usr/bin/env python3
import os
import sys
import asyncio
from typing import Dict, Any, List

# Add app directory to path so we can import modules
sys.path.append('/app')

from db.supabase import get_supabase

# Configuration
OLD_LINKEDIN_ID = "be96ae99-c65a-4e98-b796-729196321ecf"
NEW_PROVIDER_TAG = "linkedin_2"

async def migrate_linkedin():
    """
    Simple LinkedIn migration:
    1. Find all users of old LinkedIn
    2. Add them to new LinkedIn_2 and give them all actions
    3. Delete old LinkedIn provider
    """
    try:
        print("\n=== Starting LinkedIn migration ===")
        supabase = get_supabase()
        
        # Step 1: Get old LinkedIn provider details
        old_provider = supabase.table("providers").select("*").eq("id", OLD_LINKEDIN_ID).execute()
        if not old_provider.data:
            print(f"Error: Old LinkedIn provider with ID {OLD_LINKEDIN_ID} not found")
            return
        
        old_provider_data = old_provider.data[0]
        print(f"Found old LinkedIn provider: {old_provider_data['name']}")
        
        # Step 2: Get new LinkedIn_2 provider
        new_provider = supabase.table("providers").select("*").eq("provider_tag", NEW_PROVIDER_TAG).execute()
        if not new_provider.data:
            print(f"Error: New LinkedIn provider with tag '{NEW_PROVIDER_TAG}' not found")
            print("Please run the update_provider_new.py script first!")
            return
        
        new_provider_id = new_provider.data[0]["id"]
        print(f"Found new LinkedIn provider with ID: {new_provider_id}")
        
        # Step 3: Get all new provider actions
        new_actions = supabase.table("provider_actions").select("*").eq("provider_id", new_provider_id).execute()
        print(f"Found {len(new_actions.data)} actions for the new LinkedIn provider")
        
        # Step 4: Get all users with the old LinkedIn provider
        user_providers = supabase.table("users_providers").select("*").eq("provider_id", OLD_LINKEDIN_ID).execute()
        print(f"Found {len(user_providers.data)} users with the old LinkedIn provider")
        
        # Step 5: Add all users to new provider and give them all actions
        user_provider_count = 0
        user_action_count = 0
        
        for user_provider in user_providers.data:
            user_id = user_provider["user_id"]
            
            # Check if user already has the new provider
            existing = supabase.table("users_providers").select("*")\
                .eq("user_id", user_id)\
                .eq("provider_id", new_provider_id)\
                .execute()
                
            if not existing.data:
                # Create new provider connection 
                new_user_provider = {
                    "user_id": user_id,
                    "provider_id": new_provider_id
                }
                
                result = supabase.table("users_providers").insert(new_user_provider).execute()
                if result.data:
                    user_provider_count += 1
                    print(f"Connected user {user_id} to new LinkedIn provider")
                else:
                    print(f"Failed to connect user {user_id} to new LinkedIn provider")
            
            # Add all actions to the user
            for action in new_actions.data:
                # Check if user already has this action
                existing_action = supabase.table("users_provider_actions").select("*")\
                    .eq("user_id", user_id)\
                    .eq("action_id", action["id"])\
                    .execute()
                
                if not existing_action.data:
                    # Add this action for the user
                    new_user_action = {
                        "user_id": user_id,
                        "action_id": action["id"]
                    }
                    
                    result = supabase.table("users_provider_actions").insert(new_user_action).execute()
                    if result.data:
                        user_action_count += 1
                        if user_action_count % 10 == 0:  # Print status every 10 actions
                            print(f"Added {user_action_count} actions so far...")
        
        print(f"Migration complete! Connected {user_provider_count} users to new provider.")
        print(f"Added {user_action_count} new action connections.")
        
        # Step 6: Delete old LinkedIn provider (this will cascade delete related data)
        print("\n⚠️ About to delete old LinkedIn provider!")
        confirm = input("Type 'DELETE' to confirm deletion of old LinkedIn provider: ")
        
        if confirm == "DELETE":
            # Get all actions to delete them first (to handle foreign key constraints)
            old_actions = supabase.table("provider_actions").select("id").eq("provider_id", OLD_LINKEDIN_ID).execute()
            
            # Delete all user-action connections for old provider actions
            for action in old_actions.data:
                supabase.table("users_provider_actions").delete().eq("action_id", action["id"]).execute()
                print(f"Deleted user connections for action {action['id']}")
            
            # Delete all actions
            supabase.table("provider_actions").delete().eq("provider_id", OLD_LINKEDIN_ID).execute()
            print("Deleted all old LinkedIn actions")
            
            # Delete all user-provider connections
            supabase.table("users_providers").delete().eq("provider_id", OLD_LINKEDIN_ID).execute()
            print("Deleted all old LinkedIn user connections")
            
            # Finally delete the provider itself
            supabase.table("providers").delete().eq("id", OLD_LINKEDIN_ID).execute()
            print("Deleted old LinkedIn provider")
            
            print("\n✅ Migration completed successfully!")
        else:
            print("\nDeletion cancelled. Old LinkedIn provider still exists.")
            print("You can run this script again to delete it later.")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    asyncio.run(migrate_linkedin())

if __name__ == "__main__":
    main() 