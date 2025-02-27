from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

class ScopeItem(BaseModel):
    scope: str
    scope_name: str

class Provider(BaseModel):
    id: UUID
    name: str
    description: str
    logo_url: str
    created_at: int
    provider_tag: str
    auth_method: str
    has_index_capability: bool
    scopes: Optional[List[ScopeItem]] = None
    is_enabled: bool
    ui_component: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None