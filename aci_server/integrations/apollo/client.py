import requests
from typing import Dict, Any

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
        query_params = self._clean_params(params)
        response = requests.get(
            f"{self.BASE_URL}/search_people",
            headers=self.headers,
            params=query_params
        )
        response.raise_for_status()
        return response.json()
        
    def search_people_by_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        data = self._clean_params(params)
        response = requests.post(
            f"{self.BASE_URL}/search_people_via_url",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def search_organizations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_params = self._clean_params(params)
        response = requests.get(
            f"{self.BASE_URL}/search_organization",
            headers=self.headers,
            params=query_params
        )
        response.raise_for_status()
        return response.json()
        
    def search_organizations_by_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        data = self._clean_params(params)
        response = requests.post(
            f"{self.BASE_URL}/search_organizations_via_url",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_person_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_params = self._clean_params(params)
        response = requests.get(
            f"{self.BASE_URL}/person_details",
            headers=self.headers,
            params=query_params
        )
        response.raise_for_status()
        return response.json()

    def get_organization_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_params = self._clean_params(params)
        response = requests.get(
            f"{self.BASE_URL}/organization_details",
            headers=self.headers,
            params=query_params
        )
        response.raise_for_status()
        return response.json()

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        for k, v in params.items():
            if v is None:
                continue
            cleaned[k] = v
        return cleaned
