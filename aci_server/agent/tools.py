from agents import function_tool
import httpx
import os
from typing import Dict, Any

_API_KEY = None

def set_api_key(api_key: str):
    global _API_KEY
    _API_KEY = api_key

@function_tool
async def get_flow_by_id(flow_id: str) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "http://localhost:8000")
    headers = {"VEYRAX_API_KEY": _API_KEY}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/flow/get-flow/{flow_id}",
            headers=headers
        )   
        response.raise_for_status()
        return response.json()

@function_tool
async def get_available_tools() -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "http://localhost:8000")
    headers = {"VEYRAX_API_KEY": _API_KEY}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/get-tools",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@function_tool
async def tool_call(tool: str, method: str, params_json: str) -> Dict[str, Any]:
    base_url = os.environ.get("API_URL", "http://localhost:8000")
    headers = {"VEYRAX_API_KEY": _API_KEY}
    
    import json
    
    try:
        if params_json:
            params = json.loads(params_json)
        else:
            params = {}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON for params"}
    
    payload = {
        "tool": tool,
        "method": method,
        "params": params
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{base_url}/tool-execute",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            error_detail = f"Timeout error after {e.timeout} seconds; {e.__dict__}"
            print(error_detail)
            return {"error": error_detail}
        except Exception as e:
            error_detail = f"API error: {str(e)} {e.__dict__}"
            print(error_detail)
            return {"error": error_detail}
    
    