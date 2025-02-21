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
        payload = {
            "query": query,
            "filter": kwargs.get("filter", {"property": "object", "value": "page"}),
            "sort": kwargs.get("sort", {
                "direction": "descending",
                "timestamp": "last_edited_time"
            }),
            "page_size": kwargs.get("max_results", 100)
        }
        
        if kwargs.get("start_cursor"):
            payload["start_cursor"] = kwargs["start_cursor"]
            
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json=payload
        ).json()
        return response

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
        return requests.get(
            f"{self.base_url}/databases/{database_id}",
            headers=self.headers
        ).json()