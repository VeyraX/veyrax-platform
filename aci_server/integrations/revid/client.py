import requests
from typing import Dict, Any, Optional




class RevidAIClient:
    def __init__(self, api_key: str):
        
        base_url = "https://www.revid.ai/api/public/v2"
        headers = {
            "key": api_key,
            "Content-Type": "application/json"
        }

        self.base_url = base_url
        self.headers = headers
        
    def _make_request(self, endpoint: str, data: Dict[str, Any] = None):
        url = f"{self.base_url}/{endpoint}"
        return requests.post(url, headers=self.headers, json=data)

    def create_video(self, creation_params: Dict[str, Any]):
        return self._make_request("render", creation_params)
        
    def get_status(self, project_id: str):
        return requests.get(f"{self.base_url}/status", params={"pid": project_id}, headers=self.headers)
        
    def get_projects(self, limit: int = 10):
        return requests.get(f"{self.base_url}/projects", params={"limit": limit}, headers=self.headers)
        
    def add_to_queue(self, queue_params: Dict[str, Any]):
        return self._make_request("add-to-queue", queue_params)
        
    def publish_now(self, publish_params: Dict[str, Any]):
        return self._make_request("publish-now", publish_params)