import requests
from typing import Dict, Any, List, Optional

class BraveClient:
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }

    def web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a web search"""
        response = requests.get(
            f"{self.BASE_URL}/web/search",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def image_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform an image search"""
        response = requests.get(
            f"{self.BASE_URL}/images/search",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def video_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a video search"""
        response = requests.get(
            f"{self.BASE_URL}/videos/search",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def news_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a news search"""
        response = requests.get(
            f"{self.BASE_URL}/news/search",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert boolean values to lowercase strings"""
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