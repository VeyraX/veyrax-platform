import requests
from typing import Dict, Any, Optional

class TwentyFirstDevClient:
    BASE_URL = "https://21st.dev"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "content-type": "application/json",
            "x-api-key": api_key
        }

    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/api/search",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def generate_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/api/prompts",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
