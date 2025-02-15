import uuid
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class SupabaseModel(BaseModel):
    """Base model for all Supabase tables"""
    class Config:
        table_name: str
        primary_key: str = "id"

class Provider(SupabaseModel):
    name: str
    description: str
    logo: str
    
    created_at: int
    updated_at: int

    class Config:
        table_name = "provider"

class UserOAuthToken(SupabaseModel):
    id: UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the OAuth token")
    user_id: UUID = Field(..., description="Supabase user UUID")
    provider_id: UUID = Field(..., description="Reference to the provider table")
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: str
    created_at: int
    updated_at: int

    class Config:
        table_name = "user_oauth_token"
    