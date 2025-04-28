import requests
from typing import Dict, Any, Optional, List
from fastapi import HTTPException

class YelpClient:
    BASE_URL = "https://yelp-business-api.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "yelp-business-api.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }

    def search_businesses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for businesses based on location, search term, and other filters.
        """
        response = requests.get(
            f"{self.BASE_URL}/search",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_business_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information about one or more businesses.
        Can be queried by business_url or business_ids.
        """
        response = requests.get(
            f"{self.BASE_URL}/each",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_business_reviews(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get reviews for a specific business.
        Requires business_url or business_id and optional reviews_per_page parameter.
        """
        response = requests.get(
            f"{self.BASE_URL}/reviews",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_business_menus(self, business_id: str) -> Dict[str, Any]:
        """
        Get menu information for a specific business by ID.
        """
        params = {"business_id": business_id}
        response = requests.get(
            f"{self.BASE_URL}/get_menus",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json() 