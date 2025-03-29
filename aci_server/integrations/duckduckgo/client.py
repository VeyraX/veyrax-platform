import requests
from typing import Dict, Any

class DuckDuckGoClient:
    BASE_URL = "https://api.duckduckgo.com"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        }

    def search(self, query: str) -> Dict[str, Any]:
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "no_redirect": 1,
            "t": "aci_client"
        }
        
        response = requests.get(
            self.BASE_URL, 
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def fetch_content(self, url: str) -> Dict[str, Any]:
        response = requests.get(
            url,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return {
            "url": url,
            "html": response.text,
            "status_code": response.status_code
        }
