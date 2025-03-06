import os
import supabase
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()   

# 🔹 Replace with your Supabase project details
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

# 🔹 Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# 🔹 Function to get user ID by email
def get_user_by_email(email):
    try:
        response = supabase.auth.admin.list_users()

        if not response:
            print("❌ Error: list_users() did not return any data.")
            return None

        users = response  # This is already a list of User objects
        for user in users:
            if user.email == email:
                print(f"✅ User found: {user.id}")
                return user  # Return full user object

        print("❌ User not found.")
        return None
    except Exception as e:
        print(f"⚠️ Exception fetching user: {str(e)}")
        return None

# 🔹 Function to update user password
def update_user_password(email, new_password):
    user = get_user_by_email(email)

    if not user:
        print("❌ User not found. Cannot update password.")
        return

    user_id = user.id  # Correct way to access the user ID

    try:
        # ✅ Corrected API call (Use attributes)
        response = supabase.auth.admin.update_user_by_id(user_id, attributes={"password": new_password})

        # Debugging output to inspect response
        print("DEBUG: update_user_by_id response:", response)

        if response.user:
            print(f"✅ Password updated successfully for user: {email}")
        else:
            print("❌ Error updating password: No user data in response.")

    except Exception as e:
        print(f"⚠️ Exception updating password: {str(e)}")



# 🔹 Run the function (Replace with actual email & password)
email = os.environ.get("SERVICE_ACCOUNT_EMAIL")
new_password = os.environ.get("SERVICE_ACCOUNT_SECRET")
update_user_password(email, new_password)
