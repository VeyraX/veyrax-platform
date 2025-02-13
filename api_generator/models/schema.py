from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ExtractedEndpoint(BaseModel):
    tool_name: str
    url: str
    endpoint: str
    method: str

    created_at: datetime
    updated_at: datetime


class ExtractedEndpointList(BaseModel):
    endpoints: List[ExtractedEndpoint]

    created_at: datetime
    updated_at: datetime


class EndpointGeneratedFile(BaseModel):
    name: str
    content: str


class EndpointGeneratedFiles(BaseModel):
    endpoint: ExtractedEndpoint
    files: List[EndpointGeneratedFile]

    created_at: datetime
    updated_at: datetime
