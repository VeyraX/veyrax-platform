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
        
        # Fetch all actions with examples and output_schema
        response = supabase.table("providers_actions").select("id, action_name, examples, output_schema").execute()
        
        actions = response.data
        print(f"Found {len(actions)} actions to process")
        
        # Process each action
        count = 0
        for action in actions:
            try:
                action_id = action["id"]
                action_slug = action["action_name"]
                examples = action.get("examples", [])
                output_schema = action.get("output_schema", {})
                
                # Generate display name based on examples and output schema
                new_action_name = generate_action_display_name(action_slug, examples, output_schema)
                
                print(f"{action_slug} → {new_action_name}")
                
                # Update the action_name field directly
                supabase.table("providers_actions").update({
                    "action_name": new_action_name
                }).eq("id", action_id).execute()
                
                count += 1
                if count % 10 == 0:
                    print(f"Processed {count}/{len(actions)} actions")
                
                # Slight delay to avoid rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing action {action.get('action_name', 'unknown')}: {str(e)}")
        
        print("Name generation complete!")
        
    except Exception as e:
        print(f"Error during name generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Call the main processing function
    process_actions()