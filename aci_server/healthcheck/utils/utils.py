import os
import requests
from typing import Dict, Any, Tuple

from supabase import create_client, Client


def login_to_supabase() -> Tuple[str, str]:
    """
    Log in to Supabase using email and password to get an access token.
    
    Returns:
        Tuple[str, str]: A tuple containing (access_token, refresh_token)
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_anon_key:
        raise ValueError("Missing Supabase configuration")
    
    email = os.getenv('SERVICE_ACCOUNT_EMAIL')
    password = os.getenv('SERVICE_ACCOUNT_SECRET')
    
    if not email or not password:
        raise ValueError("Missing service account credentials")
    
    # Create Supabase client with anonymous key
    supabase = create_client(supabase_url, supabase_anon_key)
    
    # Log in with email and password
    auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    
    # Extract tokens
    access_token = auth_response.session.access_token
    refresh_token = auth_response.session.refresh_token
    
    return access_token, refresh_token


def check_tools_endpoint() -> Dict[str, Any]:
    """
    Performs a healthcheck by calling the tools endpoint.
    
    Returns:
        Dict[str, Any]: The response from the tools endpoint or error information
    """
    try:
        # Get token from Supabase
        access_token, _ = login_to_supabase()
        
        # Get API URL
        api_url = os.getenv('NEXT_PUBLIC_API_URL')
        if not api_url:
            return {"status": "error", "message": "NEXT_PUBLIC_API_URL not configured"}
        
        # Build full URL
        tools_url = f"{api_url}/tools"
        
        # Make request with token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(tools_url, headers=headers)
        
        # Check response
        if response.status_code == 200:
            return {
                "status": "healthy",
                "statusCode": response.status_code,
                "data": response.json()
            }
        else:
            return {
                "status": "unhealthy",
                "statusCode": response.status_code,
                "message": f"Failed to call tools endpoint: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception during healthcheck: {str(e)}"
        }


def check_calendar_endpoint() -> Dict[str, Any]:
    """
    Performs a healthcheck by calling the Google Calendar endpoint.
    
    Returns:
        Dict[str, Any]: The response from the calendar endpoint or error information
    """
    try:
        # Get token from Supabase
        access_token, _ = login_to_supabase()
        
        # Get API URL
        api_url = os.getenv('NEXT_PUBLIC_API_URL')
        if not api_url:
            return {"status": "error", "message": "NEXT_PUBLIC_API_URL not configured"}
        
        # Build full URL for calendar endpoint
        calendar_url = f"{api_url}/google_calendar/events"
        
        # Make request with token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(calendar_url, headers=headers)
        
        # Check response
        if response.status_code == 200:
            return {
                "status": "healthy",
                "statusCode": response.status_code,
                "data": response.json()
            }
        else:
            return {
                "status": "unhealthy",
                "statusCode": response.status_code,
                "message": f"Failed to call calendar endpoint: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception during calendar healthcheck: {str(e)}"
        }

if __name__ == "__main__":
    # Load environment variables from .env file in project root
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Get project root directory by going up from current file
    root_dir = Path(__file__).resolve().parents[3]
    print(root_dir)
    load_dotenv(root_dir / '.env')

    
    # When run directly, execute the healthcheck and print results
    result = check_calendar_endpoint()
    print(result)