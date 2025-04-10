import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase connection details
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SERVICE_ROLE_KEY:
    print("❌ Error: Missing Supabase credentials in environment variables.")
    print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

def list_all_users():
    """Fetch all users from Supabase and display them in a simple format."""
    try:
        response = supabase.auth.admin.list_users()
        
        if not response:
            print("❌ No users found or error retrieving users.")
            return
        
        # Print header
        print("\n{:<36} {:<30} {:<25} {:<25} {:<10} {:<10}".format(
            "ID", "Email", "Created At", "Last Sign In", "Confirmed", "Banned"))
        print("-" * 140)
        
        # Print user data
        for user in response:
            print("{:<36} {:<30} {:<25} {:<25} {:<10} {:<10}".format(
                user.id,
                user.email if user.email else "N/A",
                user.created_at if user.created_at else "N/A",
                user.last_sign_in_at if user.last_sign_in_at else "N/A",
                "Yes" if user.confirmed_at else "No",
                "Yes" if user.banned_until else "No"
            ))
        
        print(f"\nTotal users: {len(response)}")
        
    except Exception as e:
        print(f"⚠️ Error listing users: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_all_users() 