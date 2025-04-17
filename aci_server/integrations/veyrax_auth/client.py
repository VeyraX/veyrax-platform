import requests
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
import os
import uuid
from datetime import datetime, timedelta
from db.supabase import get_supabase
from fastapi import HTTPException
from ..common.encryption import encrypt, safe_encrypt, encrypt_with_code
import urllib.parse
import hashlib

class VeyraxAuthClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = get_supabase()
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://app.veyrax.com')
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        response = self.supabase.table("providers").select("*").eq("is_enabled", True).execute()
        return response.data

    def get_user_providers(self) -> List[Dict[str, Any]]:
        response = self.supabase.table("users_providers").select("*").eq("user_id", self.user_id).execute()
        return response.data
    
    def get_provider_by_id(self, provider_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("providers").select("*").eq("id", provider_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_provider_by_tag(self, provider_tag: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("providers").select("*").eq("provider_tag", provider_tag).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def is_provider_connected(self, provider_id: str) -> bool:
        response = self.supabase.table("users_providers").select("*").eq("user_id", self.user_id).eq("provider_id", provider_id).execute()
        return len(response.data) > 0
    
    def get_user_mcp_connections(self) -> List[Dict[str, Any]]:
        response = self.supabase.table("users_mcp").select("*").eq("user_id", self.user_id).execute()
        return response.data
    
    def is_mcp_connected(self, repo_id: str) -> bool:
        response = self.supabase.table("users_mcp").select("*").eq("user_id", self.user_id).eq("repo_id", repo_id).eq("status", "connected").execute()
        return len(response.data) > 0
    
    def get_mcp_repositories(self) -> List[Dict[str, Any]]:
        response = self.supabase.table("mcp_repositories").select("*").eq("is_approved", True).execute()
        return response.data
    
    def get_mcp_repository_by_image_name(self, image_name: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("mcp_repositories").select("*").eq("image_name", image_name).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_user_connected_repo_ids(self) -> List[str]:
        response = self.supabase.table("users_mcp").select("repo_id").eq("user_id", self.user_id).eq("status", "connected").execute()
        if not response.data:
            return []
        return [item["repo_id"] for item in response.data]
    
    def get_user_mcp_image_names(self) -> List[str]:
        repo_ids = self.get_user_connected_repo_ids()
        
        if not repo_ids:
            return []
        
        response = self.supabase.table("mcp_repositories").select("image_name").in_("id", repo_ids).execute()
        if not response.data:
            return []
        
        return [repo["image_name"] for repo in response.data]
    
    def generate_connection_link(self, provider_tag: str, provider_type: str) -> Dict[str, str]:
        code = str(uuid.uuid4())
        encrypted_user_id = encrypt_with_code(self.user_id, code)
        
        if provider_type == "mcp":
            repo = self.get_mcp_repository_by_image_name(provider_tag)
            if not repo:
                raise HTTPException(status_code=404, detail=f"MCP repository with image name {provider_tag} not found")
            
            repo_id = repo.get("id")
            if self.is_mcp_connected(repo_id):
                raise HTTPException(status_code=400, detail=f"MCP with image name {provider_tag} is already connected")
            
            api_key_str = f"{encrypted_user_id}:{repo_id}:{code}"
            encrypted_api_key = safe_encrypt(api_key_str)
            url_safe_key = urllib.parse.quote(encrypted_api_key)
            
            expires_at = datetime.now() + timedelta(minutes=60)
            
            data = {
                "code": code,
                "user_id": self.user_id,
                "repo_id": repo_id,
                "expires_at": expires_at.isoformat(),
                "used": False,
                "encrypted_api_key": encrypted_api_key,
                "type": "mcp"
            }
            
            result = self.supabase.table("user_auth_codes").insert(data).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to create auth code")
            
            auth_url = f"{self.frontend_url}/user/{provider_tag}/auth?code={code}&api_key={url_safe_key}&type=mcp"
            
        else:
            provider = self.get_provider_by_tag(provider_tag)
            if not provider:
                raise HTTPException(status_code=404, detail=f"Provider with tag {provider_tag} not found")
            
            provider_id = provider.get("id")
            if self.is_provider_connected(provider_id):
                raise HTTPException(status_code=400, detail=f"Provider with tag {provider_tag} is already connected")
            
            api_key_str = f"{encrypted_user_id}:{provider_id}:{code}"
            encrypted_api_key = safe_encrypt(api_key_str)
            url_safe_key = urllib.parse.quote(encrypted_api_key)
            
            expires_at = datetime.now() + timedelta(minutes=60)
            
            data = {
                "code": code,
                "user_id": self.user_id,
                "provider_id": provider_id,
                "expires_at": expires_at.isoformat(),
                "used": False,
                "encrypted_api_key": encrypted_api_key,
                "type": "tool"
            }
            
            result = self.supabase.table("user_auth_codes").insert(data).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Failed to create auth code")
            
            auth_url = f"{self.frontend_url}/user/{provider_tag}/auth?code={code}&api_key={url_safe_key}"
        
        return {"connection_url": auth_url}
