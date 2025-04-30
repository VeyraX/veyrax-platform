from typing import Optional, Dict, Any, List
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
        response = requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json=kwargs
        )

        response.raise_for_status()
        
        return response.json()

    def get_page(self, page_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers
        )

        response.raise_for_status()
        
        return response.json()

    def create_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        
        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=page_data
        )

        response.raise_for_status()
        
        return response.json()

    def create_database(self, database_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/databases",
            headers=self.headers,
            json=database_data
        )

        response.raise_for_status()
        
        return response.json()

    def update_page(self, page_id: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        
        response = requests.patch(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers,
            json=page_data
        )

        response.raise_for_status()
        return response.json()

    def archive_page(self, page_id: str) -> Dict[str, Any]:
        response = requests.patch(  
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers,
            json={"archived": True}
        )

        response.raise_for_status()
        
        return response.json()

    def append_block_children(self, block_id: str, children: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Append blocks to a page or block.
        
        Args:
            block_id: The ID of the block or page
            children: List of block objects to append
            
        Returns:
            API response
        """

        response = requests.patch(
            f"{self.base_url}/blocks/{block_id}/children",
            headers=self.headers,
            json={"children": children}
        )

        response.raise_for_status()
        return response.json()

    def search_pages(self, query="", **kwargs):
        payload = {
            "query": query
        }
        
        if "filter" in kwargs:
            payload["filter"] = kwargs["filter"]
        elif not any(k == "filter" for k in kwargs):
            payload["filter"] = {"property": "object", "value": "page"}
        
        if "sort" in kwargs:
            payload["sort"] = kwargs["sort"]
        elif not any(k == "sort" for k in kwargs):
            payload["sort"] = {
                "direction": "descending",
                "timestamp": "last_edited_time"
            }
        
        if "page_size" in kwargs:
            payload["page_size"] = kwargs["page_size"]
        elif "max_results" in kwargs:
            payload["page_size"] = kwargs["max_results"]
        else:
            payload["page_size"] = 100
        
        if "start_cursor" in kwargs:
            payload["start_cursor"] = kwargs["start_cursor"]
        
        
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        
        return response.json()

    def query_database(self, database_id: str, params: Dict[str, Any]) -> Dict[str, Any]:

        response = requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json=params
        )

        response.raise_for_status()
        
        return response.json()

    def get_block_children(self, block_id: str, **kwargs) -> Dict[str, Any]:
        return requests.get(
            f"{self.base_url}/blocks/{block_id}/children",
            headers=self.headers,
            params=kwargs
        ).json()

    def get_database(self, database_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/databases/{database_id}",
            headers=self.headers
        )

        response.raise_for_status()
        
        return response.json()

    def update_database(self, database_id: str, database_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates a database's title, description, or properties.
        
        Args:
            database_id: The ID of the database to update
            database_data: Dictionary containing updates (title, description, properties)
            
        Returns:
            The updated database object
        """
        response = requests.patch(
            f"{self.base_url}/databases/{database_id}",
            headers=self.headers,
            json=database_data
        )

        response.raise_for_status()
        
        return response.json()

    def get_users(self, **params) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/users",
            headers=self.headers,
            params=params
        )

        response.raise_for_status()
        
        return response.json()

    def get_user(self, user_id: str) -> Dict[str, Any]:

        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=self.headers
        )
        
        
        return response.json()

    