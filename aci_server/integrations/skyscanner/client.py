import requests
from typing import Dict, Any

class SkyscannerClient:
    BASE_URL = "https://sky-scanner3.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "sky-scanner3.p.rapidapi.com",
            "x-rapidapi-key": api_key,
            "Content-Type": "application/json"
        }
    
    def search_everywhere(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for flights to all destinations from a specific location.
        
        Args:
            params: Search parameters including fromEntityId
            
        Returns:
            Dictionary containing search results with destinations and prices
        """
        url = f"{self.BASE_URL}/flights/search-everywhere"
        
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
        
    def get_flight_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/detail"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
        
    def get_price_calendar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/price-calendar"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def get_price_calendar_return(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/price-calendar-return"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def get_cheapest_one_way(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/flights/cheapest-one-way"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def search_hotels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/hotels/search"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def get_hotel_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/hotels/detail"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def get_hotel_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/hotels/prices"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()
    
    def get_hotel_reviews(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/hotels/reviews"
        
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            url,
            headers=self.headers,
            params=cleaned_params
        )
        response.raise_for_status()
        return response.json()