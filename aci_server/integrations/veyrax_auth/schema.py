from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class ProviderInfo(BaseModel):
    provider_tag: str
    is_connected: bool
    type: Optional[str] = None

class ProviderInfoList(BaseModel):
    items: List[ProviderInfo]

class GetToolsConnectionStatusParams(BaseModel):
    pass

class GetToolsConnectionStatusResponse(BaseModel):
    data: ProviderInfoList

class GenerateConnectionLinkParams(BaseModel):
    provider_tag: str = Field(..., description="Provider tag to connect")
    type: str = Field(..., description="Type of provider (tool or mcp)")
    redirect_url: Optional[str] = Field(None, description="Optional URL to redirect to after successful connection")

class GenerateConnectionLinkResponse(BaseModel):
    data: Dict[str, str]

class ApiResponse(BaseModel):
    data: Union[ProviderInfoList, GenerateConnectionLinkResponse, GetToolsConnectionStatusResponse, Dict[str, str]]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None, 
        description="UI components configuration for rendering results"
    )
