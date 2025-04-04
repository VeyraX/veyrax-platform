import requests
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
import os
import uuid
from datetime import datetime, timedelta
from db.supabase import get_supabase
from fastapi import HTTPException

class VeyraxAuthClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = get_supabase()
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://app.veyrax.com')
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        response = self.supabase.table("providers").select("*").execute()
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
    
    def generate_connection_link(self, provider_tag: str) -> Dict[str, str]:
        provider = self.get_provider_by_tag(provider_tag)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider with tag {provider_tag} not found")
        
        provider_id = provider.get("id")
        if self.is_provider_connected(provider_id):
            raise HTTPException(status_code=400, detail=f"Provider with tag {provider_tag} is already connected")
        
        code = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=60)
        
        data = {
            "code": code,
            "user_id": self.user_id,
            "provider_id": provider_id,
            "expires_at": expires_at.isoformat(),
            "used": False
        }
        
        result = self.supabase.table("user_auth_codes").insert(data).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create auth code")
        
        auth_url = f"{self.frontend_url}/user/{provider_tag}/auth?code={code}"
        
        return {"connection_url": auth_url}
