import requests
from typing import Dict, Any
from requests.exceptions import HTTPError

class ZipCodeClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key  # API key not required for this service
        self.base_url = "http://api.zippopotam.us"
        
    def get_by_zipcode(self, country: str, postal_code: str) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/{country}/{postal_code}"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    
    def get_by_city(self, country: str, state: str, city: str) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/{country}/{state}/{city}"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json() 