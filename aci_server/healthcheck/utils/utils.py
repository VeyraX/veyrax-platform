import os
import requests
from typing import Dict, Any, Tuple, Optional
from supabase import create_client, Client


def login_to_supabase() -> Tuple[str, str]:
    """
    Logs in to Supabase using service account credentials and returns the access and refresh tokens.
    
    Returns:
        Tuple[str, str]: A tuple containing (access_token, refresh_token)
    
    Raises:
        ValueError: If required environment variables are missing.
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    if not supabase_url or not supabase_anon_key:
        raise ValueError("Missing Supabase configuration (SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY)")

    email = os.getenv('SERVICE_ACCOUNT_EMAIL')
    password = os.getenv('SERVICE_ACCOUNT_SECRET')
    if not email or not password:
        raise ValueError("Missing service account credentials (SERVICE_ACCOUNT_EMAIL or SERVICE_ACCOUNT_SECRET)")

    # Create Supabase client using the anonymous key
    supabase: Client = create_client(supabase_url, supabase_anon_key)

    # Authenticate with email and password
    auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    access_token = auth_response.session.access_token
    refresh_token = auth_response.session.refresh_token

    return access_token, refresh_token


def _make_healthcheck_request(
    endpoint: str, 
    method: str = "GET", 
    data: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Helper function to make an authenticated HTTP request to a given endpoint.
    
    Args:
        endpoint (str): The endpoint path (e.g., "/tools" or "/google_calendar/events")
        method (str): The HTTP method to use ("GET", "POST", etc.). Defaults to "GET".
        data (Optional[dict]): The payload to send in case of POST/PUT requests.
    
    Returns:
        Dict[str, Any]: The healthcheck result, including status and data or error message.
    """
    try:
        access_token, _ = login_to_supabase()

        api_url = os.getenv('NEXT_PUBLIC_API_URL')
        if not api_url:
            return {"status": "error", "message": "NEXT_PUBLIC_API_URL not configured"}

        full_url = f"{api_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Choose the right request method
        method = method.upper()
        if method == "GET":
            response = requests.get(full_url, headers=headers)
        elif method == "POST":
            response = requests.post(full_url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(full_url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(full_url, headers=headers)
        else:
            return {"status": "error", "message": f"HTTP method {method} not supported."}

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
                "message": f"Failed to call endpoint: {response.text}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception during healthcheck: {str(e)}"
        }


def check_tools_endpoint() -> Dict[str, Any]:
    """
    Performs a healthcheck by calling the /tools endpoint.
    
    Returns:
        Dict[str, Any]: The response from the tools endpoint or error information.
    """
    return _make_healthcheck_request("/tools")


def check_calendar_endpoint() -> Dict[str, Any]:
    """
    Performs a healthcheck by calling the /google_calendar/events endpoint.
    
    Returns:
        Dict[str, Any]: The response from the calendar endpoint or error information.
    """
    return _make_healthcheck_request("/google_calendar/list_events", method="POST")


if __name__ == "__main__":
    # Load environment variables from .env file in project root
    from dotenv import load_dotenv
    from pathlib import Path

    # Assume the project root is three directories up from this file
    root_dir = Path(__file__).resolve().parents[3]
    print(f"Loading environment variables from: {root_dir / '.env'}")
    load_dotenv(root_dir / '.env')

    # Execute the calendar endpoint healthcheck and print the results
    result = check_calendar_endpoint()
    print(result)
