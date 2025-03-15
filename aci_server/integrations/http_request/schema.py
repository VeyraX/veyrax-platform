from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class RequestHeader(BaseModel):
    key: str = Field(..., description="Header name")
    value: str = Field(..., description="Header value")
    disabled: Optional[bool] = Field(False, description="Whether the header is disabled")

class RequestBody(BaseModel):
    mode: str = Field(..., description="Body mode (raw, urlencoded, formdata)")
    raw: Optional[str] = Field(None, description="Raw body content")
    urlencoded: Optional[List[Dict[str, Any]]] = Field(None, description="URL encoded form data")
    formdata: Optional[List[Dict[str, Any]]] = Field(None, description="Multipart form data")

class RequestUrl(BaseModel):
    raw: str = Field(..., description="Raw URL")
    protocol: Optional[str] = Field(None, description="URL protocol (http, https)")
    host: Optional[List[str]] = Field(None, description="URL host parts")
    path: Optional[List[str]] = Field(None, description="URL path parts")

class RequestData(BaseModel):
    name: str = Field(..., description="Request name")
    method: str = Field(..., description="HTTP method")
    url: Union[str, RequestUrl] = Field(..., description="Request URL")
    headers: Optional[List[RequestHeader]] = Field(None, description="Request headers")
    body: Optional[RequestBody] = Field(None, description="Request body")

class SingleRequestParams(BaseModel):
    request: RequestData = Field(..., description="Request configuration")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")

class RequestResponse(BaseModel):
    name: str = Field(..., description="Request name")
    status: str = Field(..., description="Response status")
    code: int = Field(..., description="Response status code")
    body: Any = Field(..., description="Response body")
    headers: Dict[str, str] = Field(..., description="Response headers")

# Input/Output schema classes for routes
class ExecuteRequestParams(BaseModel):
    request: RequestData
    environment: Optional[Dict[str, str]] = None

class ExecuteRequestResponse(BaseModel):
    data: RequestResponse
    component: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    data: RequestResponse
    component: Optional[Dict[str, Any]] = None