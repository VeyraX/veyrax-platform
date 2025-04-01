import httpx
import os
import mimetypes
from typing import Dict, Any, Optional, Union

class FalAIClient:
    BASE_URL = "https://fal.ai/api"
    QUEUE_URL = "https://queue.fal.run"
    DIRECT_URL = "https://fal.run"
    REST_URL = "https://rest.alpha.fal.ai"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Key {api_key}"}
    
    async def get_models(self, page: Optional[int] = None, total: Optional[int] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/models"
        
        params = {}
        if page is not None:
            params["page"] = page
        if total is not None:
            params["total"] = total
            
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            # If max_results is specified and smaller than the total results, limit the results
            if max_results is not None and len(result) > max_results:
                result = result[:max_results]
                
            return result
    
    async def search_models(self, keywords: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/models"
        params = {"keywords": keywords}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_schema(self, model_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/openapi/queue/openapi.json"
        params = {"endpoint_id": model_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def generate(self, model: str, parameters: Dict[str, Any], queue: bool = False) -> Dict[str, Any]:
        if queue:
            url = f"{self.QUEUE_URL}/{model}"
        else:
            url = f"{self.DIRECT_URL}/{model}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                json=parameters, 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_result(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_status(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def cancel_request(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def upload_file(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        filename = os.path.basename(path)
        file_size = os.path.getsize(path)
        
        content_type = mimetypes.guess_type(path)[0]
        if not content_type:
            content_type = "application/octet-stream"
        
        initiate_url = f"{self.REST_URL}/storage/upload/initiate"
        params = {"storage_type": "fal-cdn-v3"}
        initiate_payload = {
            "content_type": content_type,
            "file_name": filename
        }
        
        async with httpx.AsyncClient() as client:
            # Initiate upload
            initiate_response = await client.post(
                initiate_url,
                params=params,
                json=initiate_payload,
                headers=self.headers
            )
            initiate_response.raise_for_status()
            initiate_data = initiate_response.json()
            
            # Get upload URL and file URL
            file_url = initiate_data["file_url"]
            upload_url = initiate_data["upload_url"]
            
            # Read and upload file
            with open(path, "rb") as file:
                file_content = file.read()
                
                upload_response = await client.put(
                    upload_url,
                    content=file_content,
                    headers={"Content-Type": content_type}
                )
                upload_response.raise_for_status()
            
            return {
                "file_url": file_url,
                "file_name": filename,
                "file_size": file_size,
                "content_type": content_type
            }
