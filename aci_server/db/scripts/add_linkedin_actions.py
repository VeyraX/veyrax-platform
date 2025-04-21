#!/usr/bin/env python3
import os
import sys
import asyncio
from typing import Dict, Any, List

# Add app directory to path so we can import modules
sys.path.append('/app')

from db.supabase import get_supabase

# Configuration
PROVIDER_TAG = "linkedin"

async def add_linkedin_actions():
    """
    Add new LinkedIn actions to all users:
    1. Find the LinkedIn provider
    2. Get all users with LinkedIn enabled
    3. Get all actions for LinkedIn
    4. Add any missing actions to all users
    """
    try:
        print("\n=== Starting LinkedIn actions update ===")
        supabase = get_supabase()
        
        # Step 1: Get LinkedIn provider
        provider = supabase.table("providers").select("*").eq("provider_tag", PROVIDER_TAG).execute()
        if not provider.data:
            print(f"Error: LinkedIn provider with tag '{PROVIDER_TAG}' not found")
            return
        
        provider_id = provider.data[0]["id"]
        print(f"Found LinkedIn provider with ID: {provider_id}")
        
        # Step 2: Get all actions for the LinkedIn provider
        actions = supabase.table("provider_actions").select("*").eq("provider_id", provider_id).execute()
        print(f"Found {len(actions.data)} actions for the LinkedIn provider")
        
        # Get the newly added actions (can customize this based on action_slug if needed)
        new_action_slugs = ["get_job_details", "search_jobs", "search_locations"]  # These are the ones we just added
        new_actions = [action for action in actions.data if action["action_slug"] in new_action_slugs]
        
        if not new_actions:
            print("Error: Couldn't find any of the new actions we added")
            return
            
        print(f"Found {len(new_actions)} new actions to add to users")
        for action in new_actions:
            print(f"  - {action['action_name']} ({action['action_slug']})")
        
        # Step 3: Get all users with the LinkedIn provider
        user_providers = supabase.table("users_providers").select("*").eq("provider_id", provider_id).execute()
        print(f"Found {len(user_providers.data)} users with the LinkedIn provider")
        
        # Step 4: Add all new actions to these users
        total_added = 0
        
        for user_provider in user_providers.data:
            user_id = user_provider["user_id"]
            
            for action in new_actions:
                action_id = action["id"]
                
                # Check if user already has this action
                existing_action = supabase.table("users_provider_actions").select("*")\
                    .eq("user_id", user_id)\
                    .eq("action_id", action_id)\
                    .execute()
                
                if not existing_action.data:
                    # Add this action for the user
                    new_user_action = {
                        "user_id": user_id,
                        "action_id": action_id
                    }
                    
                    result = supabase.table("users_provider_actions").insert(new_user_action).execute()
                    if result.data:
                        total_added += 1
                        if total_added % 10 == 0:  # Print status every 10 actions
                            print(f"Added {total_added} action connections so far...")
        
        print(f"\n✅ Update complete! Added {total_added} new action connections to users.")
        
    except Exception as e:
        print(f"Error during update: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    asyncio.run(add_linkedin_actions())

if __name__ == "__main__":
    main() 