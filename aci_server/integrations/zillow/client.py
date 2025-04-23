import requests
from typing import Dict, Any, Optional

class ZillowClient:
    BASE_URL = "https://zillow-com1.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "zillow-com1.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }

    def get_property(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/property",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def search_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/propertyExtendedSearch",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_zestimate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/zestimate",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_zestimate_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/zestimateHistory",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_price_and_tax_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/priceAndTaxHistory",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_property_comps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/propertyComps",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_property_value_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/valueEstimate",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_similar_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/similarProperty",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_similar_sales(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/similarSales",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_similar_rentals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/similarForRent",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_market_location(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/marketLocation",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()

    def get_market_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/marketData",
            headers=self.headers,
            params=self._clean_params(params)
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
