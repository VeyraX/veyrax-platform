from agents import function_tool
import httpx
import os
from typing import Dict, Any, Optional, List
from .schema import (
    BraveWebSearchRequest,
)


@function_tool
async def web_search(query: str) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "https://veyraxapp.com")
    veyrax_api_key = os.environ.get("VEYRAX_API_KEY")
    headers = {"VEYRAX_API_KEY": veyrax_api_key}
    
    request_data = BraveWebSearchRequest(q=query)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/brave/web_search",
            headers=headers,
            json=request_data.dict()
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json

