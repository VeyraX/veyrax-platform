import sys
import os
import json
from pathlib import Path
import time
import re

# Add the app directory to the Python path
sys.path.append('/app')

from db.supabase import get_supabase
from dotenv import load_dotenv
from gpt_generation import generate_prompt

# Make sure environment variables are loaded
load_dotenv()

# System prompt for GPT remains the same
SYSTEM_PROMPT = """
You are an AI specialized in matching API actions with their required OAuth scopes.
Your task is to determine which OAuth scopes can be used for a specific API action.

Given an action name and a list of available scopes for the API, determine which scopes can provide access to this action.

KEY UNDERSTANDING:
1. A single OAuth scope often provides access to multiple different actions
2. For example, 'gmail.modify' scope might allow: reading emails, modifying emails, deleting emails, etc.
3. Some actions might be accessible through multiple scopes (e.g., a 'read' action might be accessible through both 'read' and 'modify' scopes)

RULES:
1. Return ONLY the scope IDs (not names) that can be used for the action
2. Return the answer as a plain JSON array of scope_ids, without any markdown code blocks, backticks or extra formatting
3. Consider that:
   - Read operations can be performed with read scopes OR broader scopes like modify/write
   - Write operations need write scopes or equivalent
   - Consider the hierarchy of permissions (e.g., full access includes read/write)
4. Include ALL scopes that could potentially grant access to the action
5. Scopes ALWAYS should be there, no way that a scope is not applicable to an action.

Examples again: 
Todoist: create_project — scope that will fit: data:read_write
Vercel: create_project, list_projects — scope that will fit: projects
Gmail: send_message — scope that will fit: gmail.modify, gmail.send
Outlook: send_message — scope that will fit: Mail.Read, Mail.Send
Notion: get_user — scope that will fit: read_pages, read_databases, write_pages, write_databases
Asana: create_subtask — scope that will fit: full_access

And the same, if Asana has only full_access, then it should be full_access and should work for all actions.

For example full access means that you can read, write, delete, modify, etc.

Please make sure that actions will include all possible scopes that can be used to perform the action (if read action - write usually will fit). Make logical sense.

Think step by step.

VERY IMPORTANT: Do not include any Markdown formatting, code blocks, or backticks in your response. Just return the raw JSON array.
"""

def get_applicable_scopes(action_name, action_slug, available_scopes):
    """Determine which scopes apply to a specific action"""
    
    # Format scopes for the prompt
    scopes_formatted = []
    for scope in available_scopes:
        scopes_formatted.append({
            "scope_id": scope["scope_id"], 
            "scope_name": scope["scope_name"]
        })
    
    # Create a prompt for GPT
    user_prompt = f"""
    Action display name: {action_name}
    Action technical name: {action_slug}
    
    Available OAuth scopes for this provider:
    {json.dumps(scopes_formatted, indent=2)}
    
    Based on the action name and available scopes, list ALL scope_ids that could potentially be used to perform this action.
    
    IMPORTANT: Return ONLY a plain JSON array of scope_ids without any markdown formatting, code blocks, or backticks.
    Bad example: ```json ["scope1", "scope2"] ```
    Good example: ["scope1", "scope2"]
    """

    # Generate applicable scopes
    try:
        response = generate_prompt(SYSTEM_PROMPT, user_prompt)
        
        # Clean the response - remove any backticks, markdown code blocks or 'json' tags
        clean_response = re.sub(r'```json\s*|\s*```|`', '', response).strip()
        
        # Parse the response as JSON
        try:
            scope_ids = json.loads(clean_response)
            if not isinstance(scope_ids, list):
                print(f"Warning: Invalid response format for {action_name}. Expected list, got: {type(scope_ids)}")
                return []
            return scope_ids
        except json.JSONDecodeError:
            # Handle case where response isn't valid JSON
            print(f"Warning: Couldn't parse GPT response for {action_name}: {clean_response}")
            
            # Try to extract scope IDs by looking for a pattern like ["scope1", "scope2"]
            match = re.search(r'\[(.*?)\]', clean_response)
            if match:
                content = match.group(1)
                items = content.split(',')
                scope_ids = [item.strip().strip('"\'') for item in items if item.strip()]
                return scope_ids
            
            return []
            
    except Exception as e:
        print(f"Error getting applicable scopes for {action_name}: {str(e)}")
        return []

def process_action_scopes():
    """Link actions to their applicable scopes"""
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Get table structure
        print("Checking table structures...")
        try:
            provider_scopes_sample = supabase.table("provider_scopes").select("*").limit(1).execute()
            if provider_scopes_sample.data:
                print(f"provider_scopes sample: {provider_scopes_sample.data[0]}")
            
            provider_action_scopes_sample = supabase.table("provider_action_scopes").select("*").limit(1).execute()
            if provider_action_scopes_sample.data:
                print(f"provider_action_scopes sample: {provider_action_scopes_sample.data[0]}")
        except Exception as e:
            print(f"Error checking table structure: {str(e)}")
        
        # Get only OAuth providers
        providers_response = supabase.table("providers").select(
            "id, name, auth_method"
        ).eq("auth_method", "oauth").execute()
        
        providers = providers_response.data
        
        print(f"Found {len(providers)} OAuth providers to process")
        total_links = 0
        skipped_links = 0
        
        # Process each OAuth provider
        for provider in providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            
            # Get all scopes for this provider with their database IDs
            scopes_response = supabase.table("provider_scopes").select(
                "id, scope_id, scope_name, provider_id"
            ).eq("provider_id", provider_id).execute()
            
            provider_scopes = scopes_response.data
            
            if not provider_scopes:
                print(f"No scopes found for OAuth provider: {provider_name}")
                continue
                
            print(f"Processing {len(provider_scopes)} scopes for OAuth provider: {provider_name}")
            
            # Get all actions for this provider
            actions_response = supabase.table("provider_actions").select(
                "id, action_name, action_slug, provider_id"
            ).eq("provider_id", provider_id).execute()
            
            provider_actions = actions_response.data
            
            if not provider_actions:
                print(f"No actions found for OAuth provider: {provider_name}")
                continue
                
            print(f"Processing {len(provider_actions)} actions for OAuth provider: {provider_name}")
            
            # Create a mapping of scope_id string to database ID
            scope_id_to_db_id = {}
            for scope in provider_scopes:
                scope_id_to_db_id[scope["scope_id"]] = scope["id"]
            
            # Process each action
            for action in provider_actions:
                action_id = action["id"]  # This is the database ID
                action_name = action["action_name"]
                action_slug = action.get("action_slug", action_name)
                
                # Get applicable scopes for this action
                applicable_scope_ids = get_applicable_scopes(action_name, action_slug, provider_scopes)
                
                if not applicable_scope_ids:
                    print(f"No applicable scopes found for action: {action_name}")
                    continue
                    
                print(f"Found {len(applicable_scope_ids)} applicable scopes for action: {action_name}")
                
                # Link action to each applicable scope
                for scope_id in applicable_scope_ids:
                    # Get the database ID for this scope
                    if scope_id not in scope_id_to_db_id:
                        print(f"Warning: Scope {scope_id} not found in database for provider {provider_name}")
                        continue
                    
                    db_scope_id = scope_id_to_db_id[scope_id]
                    
                    try:
                        # Check if link already exists
                        existing_link = supabase.table("provider_action_scopes").select("*")\
                            .eq("scope_id", db_scope_id)\
                            .eq("action_id", action_id)\
                            .execute()
                            
                        if existing_link.data:
                            print(f"Link already exists between scope {scope_id} and action {action_name}")
                            skipped_links += 1
                            continue
                            
                        # Create link in provider_action_scopes table using database IDs
                        supabase.table("provider_action_scopes").insert({
                            "scope_id": db_scope_id,
                            "action_id": action_id
                        }).execute()
                        
                        total_links += 1
                        print(f"Linked action '{action_name}' to scope '{scope_id}'")
                    except Exception as e:
                        print(f"Error linking scope {scope_id} to action {action_name}: {str(e)}")
                
                # Slight delay to avoid rate limits
                time.sleep(0.1)
        
        print(f"Linking complete! Created {total_links} action-scope links for OAuth providers")
        print(f"Skipped {skipped_links} existing links")
        
    except Exception as e:
        print(f"Error during action-scope linking: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Call the main processing function
    process_action_scopes()