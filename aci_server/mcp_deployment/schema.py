from pydantic import BaseModel, validator, Field
from typing import Optional, Dict


class PushMCPRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to parse")
    image_name: str = Field(..., description="Docker image name to be built")
    
    @validator('repo_url')
    def validatorte_repo_url(cls, v):
        if 'github.com' not in v:
            raise ValueError("Only GitHub repositories are supported")
        return v
    
class PushMCPResponse(BaseModel):
    status: str
    dockerfile: Optional[str] = None
    dockerfile_base64: Optional[str] = None
    github_workflow_url: Optional[str] = None
    message: Optional[str] = None
    

class EnvVariablesRequest(BaseModel):
    context: str = Field(..., description="Repository context for file generation")

class EnvVariablesResponse(BaseModel):
    env_variables: Dict[str, str]