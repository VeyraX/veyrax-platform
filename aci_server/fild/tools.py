from agents import function_tool
import httpx
import os
import json
from typing import Dict, Any, Optional, List, Union
from .schema import (
    BraveWebSearchRequest,
    WebSearchRequest,
    ExtractPageRequest
)


@function_tool
async def web_search(query: str) -> str:
    request = WebSearchRequest(query=query)
    
    tavily_api_key = os.environ.get("TAVILY_API_KEY", "")
    
    search_url = "https://api.tavily.com/search"
    
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": request.query,
        "max_results": request.max_results,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
        "search_depth": "advanced"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            search_url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        response_json = response.json()
        
        results = []
        if "results" in response_json:
            for item in response_json["results"]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })
        
        return json.dumps({
            "query": request.query,
            "results": results
        })


@function_tool
async def extract_page(url: str) -> str:
    request = ExtractPageRequest(url=url)
    
    tavily_api_key = os.environ.get("TAVILY_API_KEY", "")
    
    extract_url = "https://api.tavily.com/extract"
    
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "urls": request.url,
        "include_images": False,
        "extract_depth": "advanced"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            extract_url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        response_json = response.json()
        
        content = ""
        if "results" in response_json and len(response_json["results"]) > 0:
            content = response_json["results"][0].get("raw_content", "")
        
        return json.dumps({
            "url": request.url,
            "content": content
        })

