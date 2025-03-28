import sys
import os
import json
from pathlib import Path
import time

# Add the app directory to the Python path
sys.path.append('/app')

from db.supabase import get_supabase
from dotenv import load_dotenv
from gpt_generation import generate_prompt

# Make sure environment variables are loaded
load_dotenv()

# System prompt for GPT to generate concise, descriptive action names
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

def should_skip_action(action):
    action_name = action.get("action_name")
    action_slug = action.get("action_slug")
    
    # If action_name is None or empty, we should generate it
    if not action_name:
        return False, None
        
    # If action_name looks like a raw slug (contains underscores or is all lowercase)
    if "_" in action_name or action_name.islower():
        return False, None
        
    # If action_name is already properly formatted (Title Case, no underscores)
    words = action_name.split()
    if all(word[0].isupper() for word in words if word):
        return True, "already has proper name format"
    
    return False, None

def generate_action_display_name(action_slug, examples, output_schema):
    """Generate a user-friendly name for an action based on examples and schema"""
    
    # Create a descriptive prompt
    user_prompt = f"""
    Generate a concise, user-friendly display name for this API action:

    Action ID: {action_slug}

    Examples:
    {json.dumps(examples, indent=2)[:500]}

    Based on this information, provide a clear, concise 2-4 word name that describes what this action does.
    """

    # Generate name
    try:
        display_name = generate_prompt(SYSTEM_PROMPT, user_prompt)
        # Clean up any quotes or extra characters
        display_name = display_name.strip('"\'').strip()
        return display_name
    except Exception as e:
        print(f"Error generating name for {action_slug}: {str(e)}")
        return action_slug.replace("_", " ").title()

def process_actions():
    """Generate display names for all actions in the database"""
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Get all providers first
        providers_response = supabase.table("providers").select("id, name").execute()
        providers = providers_response.data
        
        print(f"Found {len(providers)} providers to process")
        
        total_processed = 0
        total_skipped = 0
        
        for provider in providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            
            print(f"\nProcessing provider: {provider_name}")
            
            # Fetch all actions for this provider
            response = supabase.table("provider_actions").select(
                "id, action_name, action_slug, examples, output_schema"
            ).eq("provider_id", provider_id).execute()
            
            actions = response.data
            print(f"Found {len(actions)} actions for provider {provider_name}")
            
            # Track existing names for this provider to avoid duplicates
            existing_names = set()
            
            # Process each action
            provider_processed = 0
            provider_skipped = 0
            
            for action in actions:
                try:
                    action_id = action["id"]
                    action_slug = action.get("action_slug") or action.get("action_name")
                    current_name = action.get("action_name")
                    
                    # Check if we should skip this action
                    should_skip, reason = should_skip_action(action)
                    if should_skip:
                        print(f"Skipping {action_slug} - {reason}")
                        provider_skipped += 1
                        # Add current name to existing names to prevent duplicates
                        if current_name:
                            existing_names.add(current_name.lower())
                        continue
                    
                    examples = action.get("examples", [])
                    output_schema = action.get("output_schema", {})
                    
                    # Generate display name based on examples and output schema
                    new_action_name = generate_action_display_name(action_slug, examples, output_schema)
                    
                    # Check for duplicates (case insensitive)
                    new_name_lower = new_action_name.lower()
                    if new_name_lower in existing_names:
                        print(f"Warning: Duplicate name '{new_action_name}' for {action_slug}, keeping original name")
                        provider_skipped += 1
                        continue
                    
                    print(f"{action_slug} → {new_action_name}")
                    
                    # Update the action_name field
                    supabase.table("provider_actions").update({
                        "action_name": new_action_name
                    }).eq("id", action_id).execute()
                    
                    # Add to existing names to prevent future duplicates
                    existing_names.add(new_name_lower)
                    
                    provider_processed += 1
                    if provider_processed % 10 == 0:
                        print(f"Processed {provider_processed}/{len(actions)} actions for {provider_name}")
                    
                    # Slight delay to avoid rate limits
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error processing action {action.get('action_name', 'unknown')}: {str(e)}")
            
            total_processed += provider_processed
            total_skipped += provider_skipped
            print(f"Completed processing {provider_processed} actions for {provider_name}")
            print(f"Skipped {provider_skipped} actions for {provider_name}")
        
        print("\nName generation complete!")
        print(f"Total processed: {total_processed}")
        print(f"Total skipped: {total_skipped}")
        
    except Exception as e:
        print(f"Error during name generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Call the main processing function
    process_actions()