import requests
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

class SkyscannerClient:
    BASE_URL = "https://sky-scanner3.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "sky-scanner3.p.rapidapi.com",
            "x-rapidapi-key": api_key,
            "Content-Type": "application/json"
        }

    def search_one_way(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/search-one-way"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def search_roundtrip(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/search-roundtrip"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def search_multi_city(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/search-multi-city"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.post(
            url,
            headers=self.headers,
            json=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def flight_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/detail"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def price_calendar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/price-calendar"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def price_calendar_return(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/price-calendar-return"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def cheapest_one_way(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/cheapest-one-way"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()

    def search_hotels(self, params: Dict[str, Any], max_attempts: int = 5, poll_interval: int = 2) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/hotels/search"
        
        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        response = requests.get(f"{url}?{query_string}", headers=self.headers)
        response.raise_for_status()
        result = response.json()
        
        response = requests.get(f"{url}?{query_string}", headers=self.headers)
        response.raise_for_status()
        result = response.json()
        
        return result

    def hotel_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/hotels/detail"

        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        response = requests.get(f"{url}?{query_string}", headers=self.headers)
        response.raise_for_status()
        
        return response.json()

    def hotel_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get pricing information for a specific hotel
        
        Args:
            params: Dictionary containing the hotel ID, check-in/check-out dates, and optional parameters
            
        Returns:
            Hotel prices response
        """
        url = f"{self.BASE_URL}/hotels/prices"
        
        # Include specific headers if cookie is provided
        headers = self.headers.copy()
        if "cookie" in params and params["cookie"]:
            headers["cookie"] = params["cookie"]
            # Remove cookie from params as it's not a query parameter
            cookie = params.pop("cookie")
        
        # Make the request
        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        response = requests.get(f"{url}?{query_string}", headers=headers)
        response.raise_for_status()
        
        return response.json()

    def hotel_reviews(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get reviews for a specific hotel
        
        Args:
            params: Dictionary containing the hotel ID and optional filtering/sorting parameters
            
        Returns:
            Hotel reviews response
        """
        url = f"{self.BASE_URL}/hotels/reviews"
        
        # Include specific headers if cookie is provided
        headers = self.headers.copy()
        if "cookie" in params and params["cookie"]:
            headers["cookie"] = params["cookie"]
            # Remove cookie from params as it's not a query parameter
            cookie = params.pop("cookie")
        
        # Make the request
        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        response = requests.get(f"{url}?{query_string}", headers=headers)
        response.raise_for_status()
        
        return response.json()
