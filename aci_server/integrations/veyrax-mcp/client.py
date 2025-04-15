import os
import httpx
from typing import Dict, Any, List, Optional
from upstash_vector import Index, Vector
import json
import uuid
from datetime import datetime, timedelta
import urllib.parse
from fastapi import HTTPException
from db.supabase import get_supabase
from ..common.encryption import encrypt, safe_encrypt, encrypt_with_code

class VeyraxMcpClient:
    def __init__(self, token: Optional[str] = None, user_id: Optional[str] = None):
        self.upstash_url = os.getenv("UPSTASH_EXTERNAL_MCP_URL", "***REMOVED***")
        self.upstash_token = os.getenv("UPSTASH_EXTERNAL_MCP_TOKEN", "")
        self.mcp_api_url = os.getenv("VEYRAX_DEPLOY_API_URL", "https://api.veyrax.com")
        self.token = token
        self.user_id = user_id
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://app.veyrax.com')
        self.supabase = get_supabase()

    def get_vector_index(self) -> Index:
        return Index(url=self.upstash_url, token=self.upstash_token)

    async def search_mcp(self, query: str, limit: int = 10, include_metadata: bool = True) -> List[Dict[str, Any]]:
        try:
            from openai import OpenAI
            openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Generate embedding for query
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            embedding = response.data[0].embedding
            
            # Search vector database
            index = self.get_vector_index()
            results = index.query(
                vector=embedding,
                top_k=limit,
                include_metadata=True  # Всегда включаем метаданные независимо от параметра
            )
            
            return [
                {
                    "id": item.id,
                    "score": item.score,
                    "name": item.metadata.get("name", ""),
                    **item.metadata
                }
                for item in results.matches
            ]
        except Exception as e:
            raise Exception(f"Error searching MCP repositories: {str(e)}")

    async def deploy_mcp(self, repo_url: str, image_name: str, repository_id: str, commit_hash: Optional[str] = None) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                
                payload = {
                    "repo_url": repo_url,
                    "image_name": image_name,
                    "repository_id": repository_id,
                    "commit_hash": commit_hash
                }
                
                response = await client.post(
                    f"{self.mcp_api_url}/mcp_deployment/push-mcp-to-dockerhub",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                error_message = error_detail.get("detail", str(e))
            except:
                error_message = f"Failed to deploy MCP: {str(e)}"
            
            raise Exception(error_message)
        except Exception as e:
            raise Exception(f"Error deploying MCP: {str(e)}")
    
    def generate_connection_link(self, code: str, api_key: str, image_name: str) -> Dict[str, str]:
        if not self.user_id:
            raise HTTPException(status_code=401, detail="User ID is required for this operation")
            
        try:
            connection_id = str(uuid.uuid4())
            
            api_key_str = f"{api_key}:{image_name}"
            
            encrypted_api_key = encrypt_with_code(api_key_str, code)
            
            url_safe_key = urllib.parse.quote(encrypted_api_key)
            
            expires_at = datetime.now() + timedelta(minutes=60)
            
            data = {
                "code": code,
                "user_id": self.user_id,
                "image_name": image_name,
                "expires_at": expires_at.isoformat(),
                "used": False,
                "encrypted_api_key": encrypted_api_key,
                "connection_type": "mcp"
            }
            
            result = self.supabase.table("user_mcp_connection_codes").insert(data).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to create MCP connection code")
            
            auth_url = f"{self.frontend_url}/user/{image_name}/auth?code={code}&api_key={url_safe_key}&type=mcp"
            
            return {"connection_url": auth_url}
            
        except Exception as e:
            raise Exception(f"Error generating connection link: {str(e)}")
