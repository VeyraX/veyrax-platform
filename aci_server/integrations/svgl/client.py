import requests
from typing import Dict, Any, List, Optional

class SvglClient:
    BASE_URL = "https://api.svgl.app"
    
    def __init__(self):
        self.headers = {
            "Accept": "application/json"
        }

    def get_all_svgs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all SVGs with optional limit"""
        params = {}
        if limit is not None:
            params["limit"] = limit
            
        response = requests.get(
            self.BASE_URL,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_svg_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get SVGs filtered by category"""
        response = requests.get(
            f"{self.BASE_URL}/category/{category}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all available categories with counts"""
        response = requests.get(
            f"{self.BASE_URL}/categories",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def search_svgs(self, query: str) -> List[Dict[str, Any]]:
        """Search SVGs by name"""
        params = {"search": query}
        response = requests.get(
            self.BASE_URL,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
