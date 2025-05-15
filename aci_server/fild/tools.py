from agents import function_tool
import httpx
import os
from typing import Dict, Any


@function_tool
async def web_search(query: str) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = '***REMOVED***'
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    payload = {
        "q": query,
        "count": 5,
        "offset": 0,
        "country": "US",
        "safesearch": "moderate",
        "spellcheck": True,
        "search_lang": "en",
        "text_decorations": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/brave/web_search",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    

@function_tool
async def find_email(query: str) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    headers = {"VEYRAX_API_KEY": os.environ.get("VEYRAX_API_KEY")}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/find-email/{query}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

