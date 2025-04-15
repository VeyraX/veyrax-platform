from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, List


class PushMCPRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to parse")
    image_name: str = Field(..., description="Docker image name to be built")
    repository_id: str = Field(..., description="Repository ID for connecting to Veyrax")
    commit_hash: Optional[str] = Field(None, description="Commit hash for deployment")
    
    @validator('repo_url')
    def validatorte_repo_url(cls, v):
        if 'github.com' not in v:
            raise ValueError("Only GitHub repositories are supported")
        return v
    
class PushMCPResponse(BaseModel):
    status: str
    dockerfile: Optional[str] = None
    dockerfile_b64: Optional[str] = None
    github_workflow_url: Optional[str] = None
    message: Optional[str] = None
    deployment_id: Optional[str] = None


class RepositoryMetaRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to parse")
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if 'github.com' not in v:
            raise ValueError("Only GitHub repositories are supported")
        return v

class RepositoryMetaResponse(BaseModel):
    env_variables: Dict[str, str]
    name: Optional[str] = None
    description: Optional[str] = None
    is_local: bool = False

class ExternalMCPServer(BaseModel):
    name: str
    url: Optional[str] = None
    external_url: Optional[str] = None
    short_description: Optional[str] = None
    source_code_url: Optional[str] = None
    github_stars: Optional[int] = None
    package_registry: Optional[str] = None
    package_name: Optional[str] = None
    package_download_count: Optional[int] = None
    EXPERIMENTAL_ai_generated_description: Optional[str] = None

class ExternalMCPResponse(BaseModel):
    servers: List[ExternalMCPServer]
    next: Optional[str] = None
    total_count: int

class DeployMCPRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to deploy")
    image_name: str = Field(..., description="Docker image name to be built")
    repository_id: str = Field(..., description="Repository ID for connecting to Veyrax")
    commit_hash: Optional[str] = Field(None, description="Commit hash for deployment")
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if 'github.com' not in v:
            raise ValueError("Only GitHub repositories are supported")
        return v

class DeployMCPResponse(BaseModel):
    status: str
    dockerfile: Optional[str] = None
    dockerfile_base64: Optional[str] = None
    github_workflow_url: Optional[str] = None
    message: Optional[str] = None