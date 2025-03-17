import requests
from typing import Dict, Any, List, Optional

class PostmanClient:
    BASE_URL = "https://api.getpostman.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._initialize_client()

    def _initialize_client(self):
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def get_collections(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/collections",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_collection(self, collection_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/collections/{collection_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def update_collection(self, collection_id: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/collections/{collection_id}",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def delete_collection(self, collection_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/collections/{collection_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def create_collection(self, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/collections",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_environments(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/environments",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_environment(self, environment_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/environments/{environment_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def create_environment(self, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/environments",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def update_environment(self, environment_id: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/environments/{environment_id}",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def delete_environment(self, environment_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/environments/{environment_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def fork_collection(self, collection_id: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/collections/fork/{collection_id}",
            headers=self.headers,
            json=data or {},
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_workspaces(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/workspaces",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def get_workspace(self, workspace_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/workspaces/{workspace_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def create_workspace(self, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/workspaces",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def update_workspace(self, workspace_id: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.put(
            f"{self.BASE_URL}/workspaces/{workspace_id}",
            headers=self.headers,
            json=data,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def delete_workspace(self, workspace_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.BASE_URL}/workspaces/{workspace_id}",
            headers=self.headers,
            params=self._clean_params(params or {})
        )
        response.raise_for_status()
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, bool):
                cleaned[k] = str(v).lower()
            elif isinstance(v, list):
                cleaned[k] = ",".join(map(str, v))
            else:
                cleaned[k] = v
        return cleaned
