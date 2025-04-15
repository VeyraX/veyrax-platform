from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

# Search MCP Models
class SearchMCPParams(BaseModel):
    query: str = Field(..., description="Search query for finding MCP repositories")
    limit: Optional[int] = Field(10, description="Maximum number of results to return")

class MCPRepository(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    external_url: Optional[str] = None
    github_stars: Optional[int] = None
    package_name: Optional[str] = None
    source_code_url: Optional[str] = None
    package_registry: Optional[str] = None
    short_description: Optional[str] = None
    package_download_count: Optional[int] = None
    ai_generated_description: Optional[str] = None
    score: Optional[float] = None

class MCPRepositoryList(BaseModel):
    repositories: List[MCPRepository]

class SearchMCPResponse(BaseModel):
    data: MCPRepositoryList

# Deploy MCP Models
class DeployMCPParams(BaseModel):
    repo_url: str = Field(..., description="URL of the repository to deploy")
    image_name: str = Field(..., description="Name for the Docker image")
    repository_id: str = Field(..., description="ID of the repository in the database")
    commit_hash: Optional[str] = Field(None, description="Commit hash to deploy")

class DeploymentStatus(BaseModel):
    image_name: str
    status: str
    repository_id: str
    deployment_id: str

class DeployMCPResponse(BaseModel):
    data: DeploymentStatus

# Connection Models
class GenerateConnectionLinkParams(BaseModel):
    code: str = Field(..., description="Code for linking the connection")
    api_key: str = Field(..., description="API key for authentication")
    image_name: str = Field(..., description="Name of the MCP Docker image")

class ConnectionLinkInfo(BaseModel):
    connection_url: str

class GenerateConnectionLinkResponse(BaseModel):
    data: ConnectionLinkInfo

# API Response
class ApiResponse(BaseModel):
    data: Union[MCPRepositoryList, DeploymentStatus, ConnectionLinkInfo]
    component: Optional[Dict[str, Any]] = None
