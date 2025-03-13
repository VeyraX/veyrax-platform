import requests
from typing import Dict, Any, List, Optional

class TavilyClient:
    BASE_URL = "https://api.tavily.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a search query using Tavily Search API"""
        response = requests.post(
            f"{self.BASE_URL}/search",
            headers=self.headers,
            json=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def extract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract web page content from one or more URLs using Tavily Extract API"""
        response = requests.post(
            f"{self.BASE_URL}/extract",
            headers=self.headers,
            json=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare parameters for API request"""
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, bool):
                cleaned[k] = v  # Tavily accepts booleans as-is
            elif isinstance(v, list):
                # Tavily accepts both string and list for URLs
                if k == "urls" and len(v) == 1:
                    cleaned[k] = v[0]
                else:
                    cleaned[k] = v
            else:
                cleaned[k] = v
        return cleaned 