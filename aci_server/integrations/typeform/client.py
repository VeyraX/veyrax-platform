from typing import Dict, Any, Optional, List, Union
import requests
from requests.exceptions import RequestException

class TypeformClient:
    """Client for interacting with the Typeform API."""
    
    BASE_URL = "https://api.typeform.com"
    
    def __init__(self, access_token: str):
        """Initialize the Typeform client with authentication.
        
        Args:
            access_token (str): The Typeform API access token
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                      data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Typeform API.
        
        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint path
            params (Dict[str, Any], optional): Query parameters
            data (Dict[str, Any], optional): Request body data
            
        Returns:
            Dict[str, Any]: Response from the API
            
        Raises:
            RequestException: If the request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )
        response.raise_for_status()
        
        # For successful DELETE requests, return empty dict
        if method == "DELETE" and response.status_code == 204:
            return {}
            
        # For successful requests with content
        if response.content:
            return response.json()
        return {}

    
    # Workspace endpoints
    
    def get_account_workspaces(self, account_id: str, search: Optional[str] = None, 
                              page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve all workspaces in a specific account.
        
        Args:
            account_id (str): ID of the account
            search (str, optional): Filter results by name
            page (int, optional): Page number for pagination
            page_size (int, optional): Number of results per page
            
        Returns:
            Dict[str, Any]: List of workspaces and pagination info
        """
        params = {}
        if search:
            params["search"] = search
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("GET", f"/accounts/{account_id}/workspaces", params=params)
    
    def create_account_workspace(self, account_id: str, name: str) -> Dict[str, Any]:
        """Create a workspace in a specific account.
        
        Args:
            account_id (str): ID of the account
            name (str): Name of the new workspace
            
        Returns:
            Dict[str, Any]: Created workspace details
        """
        data = {"name": name}
        return self._make_request("POST", f"/accounts/{account_id}/workspaces", data=data)
    
    def get_workspaces(self, search: Optional[str] = None, 
                      page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve all workspaces the user has access to across all accounts.
        
        Args:
            search (str, optional): Filter results by name
            page (int, optional): Page number for pagination
            page_size (int, optional): Number of results per page
            
        Returns:
            Dict[str, Any]: List of workspaces and pagination info
        """
        params = {}
        if search:
            params["search"] = search
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("GET", "/workspaces", params=params)
    
    def create_workspace(self, name: str) -> Dict[str, Any]:
        """Create a workspace in the account where the user is owner.
        
        Args:
            name (str): Name of the new workspace
            
        Returns:
            Dict[str, Any]: Created workspace details
        """
        data = {"name": name}
        return self._make_request("POST", "/workspaces", data=data)
    
    def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Delete a workspace.
        
        Args:
            workspace_id (str): ID of the workspace to delete
            
        Returns:
            Dict[str, Any]: Empty dict for successful deletion
        """
        return self._make_request("DELETE", f"/workspaces/{workspace_id}")
    
    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Retrieve a specific workspace.
        
        Args:
            workspace_id (str): ID of the workspace
            
        Returns:
            Dict[str, Any]: Workspace details
        """
        return self._make_request("GET", f"/workspaces/{workspace_id}")
    
    def update_workspace(self, workspace_id: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update a workspace using JSON Patch operations.
        
        Args:
            workspace_id (str): ID of the workspace to update
            operations (List[Dict[str, Any]]): List of patch operations to apply
            
        Returns:
            Dict[str, Any]: Empty dict for successful update
        """
        return self._make_request("PATCH", f"/workspaces/{workspace_id}", data=operations)
    
    # Form endpoints
    
    def get_forms(self, search: Optional[str] = None, page: Optional[int] = None,
                 page_size: Optional[int] = None, workspace_id: Optional[str] = None,
                 sort_by: Optional[str] = None, order_by: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve all forms in your Typeform account.
        
        Args:
            search (str, optional): Filter results by name
            page (int, optional): Page number for pagination
            page_size (int, optional): Number of results per page
            workspace_id (str, optional): Filter forms by workspace
            sort_by (str, optional): Field to sort by (created_at or last_updated_at)
            order_by (str, optional): Sort order (asc or desc)
            
        Returns:
            Dict[str, Any]: List of forms and pagination info
        """
        params = {}
        if search:
            params["search"] = search
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
        if workspace_id:
            params["workspace_id"] = workspace_id
        if sort_by:
            params["sort_by"] = sort_by
        if order_by:
            params["order_by"] = order_by
            
        return self._make_request("GET", "/forms", params=params)
    
    def create_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new form.
        
        Args:
            form_data (Dict[str, Any]): Complete form definition including title, fields, etc.
            
        Returns:
            Dict[str, Any]: Created form details
        """
        return self._make_request("POST", "/forms", data=form_data)
    
    def delete_form(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/forms/{form_id}")
    
    def get_form(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}")
    
    def update_form_patch(self, form_id: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/forms/{form_id}", data=operations)
    
    def update_form(self, form_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"/forms/{form_id}", data=form_data)
    
    def get_form_messages(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}/messages")
    
    def update_form_messages(self, form_id: str, messages: Dict[str, str]) -> Dict[str, Any]:
        return self._make_request("PUT", f"/forms/{form_id}/messages", data=messages)
    
    def get_translation_payload(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}/translations/main")
    
    def get_translation_statuses(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}/translations/status")
    
    def delete_form_translation(self, form_id: str, language: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/forms/{form_id}/translations/{language}")
    
    def get_form_translation(self, form_id: str, language: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}/translations/{language}")
    
    def update_form_translation(self, form_id: str, language: str, translation_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"/forms/{form_id}/translations/{language}", data=translation_data)
    
    def auto_translate_form(self, form_id: str, language: str) -> Dict[str, Any]:
        return self._make_request("POST", f"/forms/{form_id}/translations/{language}/auto")
    
    # Image endpoints
    
    def get_images(self) -> List[Dict[str, Any]]:
        return self._make_request("GET", "/images")
    
    def delete_image(self, image_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/images/{image_id}")
    
    def get_image(self, image_id: str, json_response: bool = True) -> Dict[str, Any]:
        headers = self.headers.copy()
        if json_response:
            headers["Accept"] = "application/json"
            
        url = f"{self.BASE_URL}/images/{image_id}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if json_response:
            return response.json()
        else:
            return {"content": response.content, "media_type": response.headers.get("Content-Type")}

    
    def get_background_image(self, image_id: str, size: str, json_response: bool = True) -> Dict[str, Any]:
        headers = self.headers.copy()
        if json_response:
            headers["Accept"] = "application/json"
            
        url = f"{self.BASE_URL}/images/{image_id}/background/{size}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if json_response:
            return response.json()
        else:
            return {"content": response.content, "media_type": response.headers.get("Content-Type")}
                
    
    def get_choice_image(self, image_id: str, size: str, json_response: bool = True) -> Dict[str, Any]:
        headers = self.headers.copy()
        if json_response:
            headers["Accept"] = "application/json"
            
        url = f"{self.BASE_URL}/images/{image_id}/choice/{size}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if json_response:
            return response.json()
        else:
            return {"content": response.content, "media_type": response.headers.get("Content-Type")}
                
    def get_image_by_size(self, image_id: str, size: str, json_response: bool = True) -> Dict[str, Any]:
        headers = self.headers.copy()
        if json_response:
            headers["Accept"] = "application/json"
            
        url = f"{self.BASE_URL}/images/{image_id}/image/{size}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if json_response:
            return response.json()
        else:
            return {"content": response.content, "media_type": response.headers.get("Content-Type")}
                
    
    def get_themes(self, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("GET", "/themes", params=params)
    
    def create_theme(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/themes", data=theme_data)
    
    def delete_theme(self, theme_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/themes/{theme_id}")
    
    def get_theme(self, theme_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/themes/{theme_id}")
    
    def update_theme_partial(self, theme_id: str, theme_updates: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/themes/{theme_id}", data=theme_updates)
    
    def update_theme_full(self, theme_id: str, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"/themes/{theme_id}", data=theme_data)
    
    
    def delete_responses(self, form_id: str, response_ids: List[str]) -> Dict[str, Any]:
        data = {
            "included_response_ids": response_ids
        }
        return self._make_request("DELETE", f"/forms/{form_id}/responses", data=data)
    
    def get_responses(self, form_id: str, page_size: Optional[int] = None, 
                     since: Optional[str] = None, until: Optional[str] = None,
                     after: Optional[str] = None, before: Optional[str] = None,
                     included_response_ids: Optional[List[str]] = None,
                     excluded_response_ids: Optional[List[str]] = None,
                     response_type: Optional[List[str]] = None,
                     completed: Optional[bool] = None,
                     sort: Optional[str] = None,
                     query: Optional[str] = None,
                     fields: Optional[List[str]] = None,
                     answered_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        params = {}
        if page_size:
            params["page_size"] = page_size
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if included_response_ids:
            params["included_response_ids"] = ",".join(included_response_ids)
        if excluded_response_ids:
            params["excluded_response_ids"] = ",".join(excluded_response_ids)
        if response_type:
            params["response_type"] = ",".join(response_type)
        if completed is not None:
            params["completed"] = str(completed).lower()
        if sort:
            params["sort"] = sort
        if query:
            params["query"] = query
        if fields:
            params["fields"] = ",".join(fields)
        if answered_fields:
            params["answered_fields"] = ",".join(answered_fields)
            
        return self._make_request("GET", f"/forms/{form_id}/responses", params=params)
    
    def download_form_files(self, form_id: str) -> bytes:
        url = f"{self.BASE_URL}/forms/{form_id}/responses/files"
    
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.content
                
    
    def get_response_file(self, form_id: str, response_id: str, field_id: str, 
                         filename: str, inline: bool = False) -> bytes:
        params = {}
        if inline:
            params["inline"] = "true"
            
        url = f"{self.BASE_URL}/forms/{form_id}/responses/{response_id}/fields/{field_id}/files/{filename}"
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.content
                
    
    def get_form_insights(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/insights/{form_id}/summary")
    
    # Webhook endpoints
    
    def get_webhooks(self, form_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}/webhooks")
    
    def get_webhook(self, form_id: str, tag: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/forms/{form_id}/webhooks/{tag}")
    
    def create_or_update_webhook(self, form_id: str, tag: str, 
                               webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"/forms/{form_id}/webhooks/{tag}", data=webhook_data)
    
    def delete_webhook(self, form_id: str, tag: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/forms/{form_id}/webhooks/{tag}")