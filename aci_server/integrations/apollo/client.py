import requests
from typing import Dict, Any, Optional

class ApolloClient:
    BASE_URL = "https://apollo-io-no-cookies-required.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "apollo-io-no-cookies-required.p.rapidapi.com",
            "x-rapidapi-key": api_key,
            "Content-Type": "application/json"
        }

    def search_people(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/search_people",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        print(response.json())
        return response.json()
    
    def search_organizations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/search_organization",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()
    
    def person_details(self, person_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/person_details",
            headers=self.headers,
            params={"person_id": person_id}
        )
        response.raise_for_status()
        return response.json()
    
    def organization_details(self, organization_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/organization_details",
            headers=self.headers,
            params={"organization_id": organization_id}
        )
        response.raise_for_status()
        return response.json()
    
    def search_people_via_url(self, apollo_url: str, page: int = 1) -> Dict[str, Any]:
        data = {
            "url": apollo_url,
            "page": page
        }
        
        response = requests.post(
            f"{self.BASE_URL}/search_people_via_url",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def search_organizations_via_url(self, apollo_url: str, page: int = 1) -> Dict[str, Any]:
        data = {
            "url": apollo_url,
            "page": page
        }
        
        response = requests.post(
            f"{self.BASE_URL}/search_organizations_via_url",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean parameters before sending to API"""
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            cleaned[k] = v
        return cleaned
