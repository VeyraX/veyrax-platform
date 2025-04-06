import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlencode


class GoogleMapsClient:
    BASE_URL = "https://maps.googleapis.com/maps/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def geocode(self, address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/geocode/json"
        params = {
            "address": address,
            "key": self.api_key
        }
        return self._make_request(url, params)
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": self.api_key
        }
        return self._make_request(url, params)
    
    def search_places(self, query: str, location: Optional[Tuple[float, float]] = None, radius: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/place/textsearch/json"
        params = {
            "query": query,
            "key": self.api_key
        }
        
        if location:
            params["location"] = f"{location[0]},{location[1]}"
        
        if radius:
            params["radius"] = radius
            
        return self._make_request(url, params)
    
    def place_details(self, place_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/place/details/json"
        params = {
            "place_id": place_id,
            "key": self.api_key
        }
        return self._make_request(url, params)
    
    def distance_matrix(self, origins: List[str], destinations: List[str], mode: str = "driving") -> Dict[str, Any]:
        url = f"{self.BASE_URL}/distancematrix/json"
        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": mode,
            "key": self.api_key
        }
        return self._make_request(url, params)
    
    def elevation(self, locations: List[Tuple[float, float]]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/elevation/json"
        location_str = "|".join([f"{lat},{lng}" for lat, lng in locations])
        params = {
            "locations": location_str,
            "key": self.api_key
        }
        return self._make_request(url, params)
    
    def directions(self, origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
        url = f"{self.BASE_URL}/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": self.api_key
        }
        return self._make_request(url, params)
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
