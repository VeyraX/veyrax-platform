from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class Provider(BaseModel):
    id: int
    provider_tag: str
    name: str
    description: str
    logo: str
    created_at: datetime

    class Config:
        table_name = "providers"

class UserOAuthToken(BaseModel):
    user_id: str
    provider_id: int
    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[datetime]
    scopes: str
    raw_token_data: Dict[str, Any]
    created_at: datetime

    class Config:
        table_name = "users_oauth_tokens"