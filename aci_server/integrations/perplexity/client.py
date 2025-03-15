import requests
from typing import Dict, Any
from requests.exceptions import HTTPError

class PerplexityClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    def create_completion(self, **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.base_url, json=kwargs, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            raise HTTPError(f"Perplexity API Error: {error_message}") from e
        return response.json()