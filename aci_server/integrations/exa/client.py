import requests
from typing import Dict, Any, List, Optional

class ExaClient:
    BASE_URL = "https://api.exa.ai"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a search query"""
        response = requests.post(
            f"{self.BASE_URL}/search",
            headers=self.headers,
            json=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_contents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/contents",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def find_similar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find similar content to a given URL"""
        response = requests.post(
            f"{self.BASE_URL}/findSimilar",
            headers=self.headers,
            json=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean parameters before sending to API"""
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, bool):
                cleaned[k] = v
            elif isinstance(v, list):
                cleaned[k] = v
            else:
                cleaned[k] = v
        return cleaned