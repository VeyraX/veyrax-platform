from typing import Optional, Dict, Any
import requests

class NotionClient:
    def __init__(self, auth_token: str):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
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
        return requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=page_data
        ).json()

    def update_page(self, page_id: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        return requests.patch(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers,
            json=page_data
        ).json()

    def archive_page(self, page_id: str) -> Dict[str, Any]:
        return requests.patch(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers,
            json={"archived": True}
        ).json()

    def search_pages(self, **kwargs) -> Dict[str, Any]:
        return requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json=kwargs
        ).json()