from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ExtractedEndpoint(BaseModel):
    tool_name: str
    url: str
    endpoint: str
    method: str

class ExtractedEndpointList(BaseModel):
    endpoints: List[ExtractedEndpoint]

class EndpointGeneratedFile(BaseModel):
    name: str
    content: str

class EndpointGeneratedFilesList(BaseModel):
    files: List[EndpointGeneratedFile]

class EndpointGeneratedFiles(BaseModel):
    endpoint: ExtractedEndpoint
    files: EndpointGeneratedFilesList