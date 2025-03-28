import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('/app')

from db.supabase import get_supabase
from dotenv import load_dotenv

# Make sure environment variables are loaded
load_dotenv()

def get_existing_user_actions(supabase, user_id):
    """Helper function to get all existing actions for a user"""
    existing_actions = supabase.table("users_provider_actions").select(
        "action_id"
    ).eq("user_id", user_id).execute()
    
    return {action["action_id"] for action in existing_actions.data}

def migrate_users_provider_actions():
    """
    Populates the users_provider_actions table based on:
    1. OAuth providers: Checking user's OAuth tokens and their scopes against provider_action_scopes
    2. Non-OAuth providers: Adding all provider actions for users who have the provider enabled
    """
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Counter for tracking operations
        total_oauth_actions = 0
        total_non_oauth_actions = 0
        skipped_count = 0
        total_users_processed = 0

        # Track processed users for statistics only
        processed_users = set()

        print("\n=== Starting Migration Process ===\n")

        # Step 1: Process OAuth providers
        print("Processing OAuth providers...")
        
        # Get all OAuth providers
        oauth_providers = supabase.table("providers").select(
            "id, name"
        ).eq("auth_method", "oauth").execute()

        print(f"Found {len(oauth_providers.data)} OAuth providers")

        for provider in oauth_providers.data:
            provider_id = provider["id"]
            provider_name = provider["name"]
            
            print(f"\nProcessing OAuth provider: {provider_name}")
            
            # Get all OAuth tokens for this provider
            oauth_tokens = supabase.table("users_oauth_tokens").select(
                "user_id, scopes"
            ).eq("provider_id", provider_id).execute()
            
            print(f"Found {len(oauth_tokens.data)} users with OAuth tokens for {provider_name}")
            
            for token in oauth_tokens.data:
                user_id = token["user_id"]
                scopes = token["scopes"].split(",") if token["scopes"] else []
                
                if not scopes:
                    print(f"No scopes found for user {user_id} in provider {provider_name}")
                    continue

                # Always get fresh existing actions for the user
                existing_actions = get_existing_user_actions(supabase, user_id)
                
                # Update statistics if this is a new user
                if user_id not in processed_users:
                    processed_users.add(user_id)
                    total_users_processed += 1
                
                # Get provider_scopes IDs for these scope strings
                provider_scopes = supabase.table("provider_scopes").select(
                    "id, scope_id"
                ).eq("provider_id", provider_id).execute()
                
                # Create mapping of scope_id to database id
                scope_id_to_db_id = {
                    scope["scope_id"]: scope["id"] 
                    for scope in provider_scopes.data
                }
                
                # Get matching scope IDs from the database
                matching_scope_ids = [
                    scope_id_to_db_id[scope]
                    for scope in scopes
                    if scope in scope_id_to_db_id
                ]
                
                if not matching_scope_ids:
                    print(f"No matching scope IDs found for user {user_id} scopes in provider {provider_name}")
                    continue
                
                # Collect all new actions for this user's scopes
                new_actions = set()
                
                # Get all actions that these scopes grant access to
                for scope_db_id in matching_scope_ids:
                    action_scopes = supabase.table("provider_action_scopes").select(
                        "action_id"
                    ).eq("scope_id", scope_db_id).execute()
                    
                    for action_scope in action_scopes.data:
                        action_id = action_scope["action_id"]
                        if action_id not in existing_actions:
                            new_actions.add(action_id)
                
                # Add all new actions in bulk
                if new_actions:
                    try:
                        actions_to_add = [
                            {"user_id": user_id, "action_id": action_id}
                            for action_id in new_actions
                        ]
                        supabase.table("users_provider_actions").insert(actions_to_add).execute()
                        total_oauth_actions += len(new_actions)
                        print(f"Added {len(new_actions)} new actions for user {user_id} in {provider_name}")
                    except Exception as e:
                        print(f"Error adding actions for user {user_id} in {provider_name}: {str(e)}")
                        continue
                else:
                    skipped_count += len(existing_actions)

        # Step 2: Process non-OAuth providers
        print("\nProcessing non-OAuth providers...")
        
        # Get all non-OAuth providers
        non_oauth_providers = supabase.table("providers").select(
            "id, name"
        ).neq("auth_method", "oauth").execute()

        print(f"Found {len(non_oauth_providers.data)} non-OAuth providers")

        for provider in non_oauth_providers.data:
            provider_id = provider["id"]
            provider_name = provider["name"]
            
            print(f"\nProcessing non-OAuth provider: {provider_name}")
            
            # Get all users who have this provider enabled
            users_providers = supabase.table("users_providers").select(
                "user_id"
            ).eq("provider_id", provider_id).execute()
            
            if not users_providers.data:
                print(f"No users found for provider {provider_name}")
                continue
                
            print(f"Found {len(users_providers.data)} users for {provider_name}")
                
            # Get all actions for this provider
            provider_actions = supabase.table("provider_actions").select(
                "id"
            ).eq("provider_id", provider_id).execute()
            
            if not provider_actions.data:
                print(f"No actions found for provider {provider_name}")
                continue
            
            print(f"Found {len(provider_actions.data)} actions for {provider_name}")
            
            # For each user with this provider enabled, add all provider actions
            for user_provider in users_providers.data:
                user_id = user_provider["user_id"]
                
                existing_actions = get_existing_user_actions(supabase, user_id)
                
                if user_id not in processed_users:
                    processed_users.add(user_id)
                    total_users_processed += 1
                
                # Collect all new actions for this user
                new_actions = set()
                for action in provider_actions.data:
                    action_id = action["id"]
                    if action_id not in existing_actions:
                        new_actions.add(action_id)
                
                # Add all new actions in bulk
                if new_actions:
                    try:
                        actions_to_add = [
                            {"user_id": user_id, "action_id": action_id}
                            for action_id in new_actions
                        ]
                        supabase.table("users_provider_actions").insert(actions_to_add).execute()
                        total_non_oauth_actions += len(new_actions)
                        print(f"Added {len(new_actions)} new actions for user {user_id} in {provider_name}")
                    except Exception as e:
                        print(f"Error adding actions for user {user_id} in {provider_name}: {str(e)}")
                        continue
                else:
                    skipped_count += len(existing_actions)
        
        print("\n=== Migration Summary ===")
        print(f"Total users processed: {total_users_processed}")
        print(f"Added {total_oauth_actions} actions for OAuth providers")
        print(f"Added {total_non_oauth_actions} actions for non-OAuth providers")
        print(f"Total actions added: {total_oauth_actions + total_non_oauth_actions}")
        print(f"Skipped {skipped_count} existing actions")
        print("Migration complete!")
        
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_users_provider_actions() 