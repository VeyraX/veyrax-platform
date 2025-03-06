from typing import Optional, Dict, Any
import requests

class NotionClient:
    def __init__(self, auth_token: str):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def list_databases(self, **kwargs) -> Dict[str, Any]:
        return requests.get(
            f"{self.base_url}/databases",
            headers=self.headers,
            params=kwargs
        ).json()

    def list_pages(self, database_id: str, **kwargs) -> Dict[str, Any]:
        return requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json=kwargs
        ).json()

    def get_page(self, page_id: str) -> Dict[str, Any]:
        return requests.get(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers
        ).json()

    def create_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        
        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=page_data
        )
        
        return response.json()

    def update_page(self, page_id: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        
        response = requests.patch(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers,
            json=page_data
        )
        
        return response.json()

    def archive_page(self, page_id: str) -> Dict[str, Any]:
        return requests.patch(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers,
            json={"archived": True}
        ).json()

    def search_pages(self, query="", **kwargs):
        # Build the payload with appropriate defaults
        payload = {
            "query": query
        }
        
        # Only set default filter if none provided
        if "filter" in kwargs:
            payload["filter"] = kwargs["filter"]
        elif not any(k == "filter" for k in kwargs):
            payload["filter"] = {"property": "object", "value": "page"}
        
        # Only set default sort if none provided
        if "sort" in kwargs:
            payload["sort"] = kwargs["sort"]
        elif not any(k == "sort" for k in kwargs):
            payload["sort"] = {
                "direction": "descending",
                "timestamp": "last_edited_time"
            }
        
        # Handle page_size directly
        if "page_size" in kwargs:
            payload["page_size"] = kwargs["page_size"]
        # For backward compatibility
        elif "max_results" in kwargs:
            payload["page_size"] = kwargs["max_results"]
        else:
            payload["page_size"] = 100
        
        # Add start_cursor if provided
        if "start_cursor" in kwargs:
            payload["start_cursor"] = kwargs["start_cursor"]
        
        # For debugging
        print(f"Sending to Notion API: {payload}")
        
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json=payload
        )
        
        # For debugging: log the raw response
        print(f"Notion API status: {response.status_code}")
        
        return response.json()

    def query_database(self, database_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json=params
        ).json()

    def get_block_children(self, block_id: str, **kwargs) -> Dict[str, Any]:
        """Get children blocks for a given block ID"""
        return requests.get(
            f"{self.base_url}/blocks/{block_id}/children",
            headers=self.headers,
            params=kwargs
        ).json()

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get database metadata including its property schema"""
        response = requests.get(
            f"{self.base_url}/databases/{database_id}",
            headers=self.headers
        )
        return response.json()

    