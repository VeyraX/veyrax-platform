from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
import json

from .parse_repo import parse_repository
from .generate_files import generate_dockerfile, extract_env_variables

router = APIRouter(
    prefix="/mcp_deployment",
    tags=["mcp_deployment"],
)

class ParseRepoRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to parse")
    max_files: int = Field(50, description="Maximum number of files to include")
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if 'github.com' not in v:
            raise ValueError("Only GitHub repositories are supported")
        return v
    
    @validator('max_files')
    def validate_max_files(cls, v):
        if v <= 0 or v > 100:
            raise ValueError("Max files must be between 1 and 100")
        return v

class FileContent(BaseModel):
    path: str
    content: str
    truncated: bool = False

class RepositoryInfo(BaseModel):
    url: str
    owner: str
    name: str

class ParseRepoResponse(BaseModel):
    repository: RepositoryInfo
    files: List[FileContent]
    file_count: int
    truncated: bool = False

class GenerateFileRequest(BaseModel):
    context: str = Field(..., description="Repository context for file generation")

class DockerfileResponse(BaseModel):
    dockerfile: str

class EnvVariablesResponse(BaseModel):
    env_variables: Dict[str, str]

class GenerateFromRepoRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to parse")
    max_files: int = Field(50, description="Maximum number of files to include")
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if 'github.com' not in v:
            raise ValueError("Only GitHub repositories are supported")
        return v

@router.post("/parse-repo", response_model=ParseRepoResponse)
async def parse_github_repository(request: ParseRepoRequest = Body(...)):
    try:
        result = parse_repository(
            repo_url=request.repo_url,
            max_files=request.max_files
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse repository: {str(e)}")

@router.post("/generate-dockerfile", response_model=DockerfileResponse)
async def create_dockerfile(request: GenerateFileRequest = Body(...)):
    try:
        dockerfile = generate_dockerfile(request.context)
        return DockerfileResponse(dockerfile=dockerfile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Dockerfile: {str(e)}")

@router.post("/generate-env-variables", response_model=EnvVariablesResponse)
async def create_env_variables(request: GenerateFileRequest = Body(...)):
    try:
        env_variables_json = extract_env_variables(request.context)
        env_variables = json.loads(env_variables_json)
        return EnvVariablesResponse(env_variables=env_variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse environment variables JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate environment variables: {str(e)}")

@router.post("/generate-dockerfile-from-repo", response_model=DockerfileResponse)
async def generate_dockerfile_from_repo(request: GenerateFromRepoRequest = Body(...)):
    try:
        repo_data = parse_repository(
            repo_url=request.repo_url,
            max_files=request.max_files
        )
        
        context = json.dumps(repo_data)
        
        dockerfile = generate_dockerfile(context)
        
        return DockerfileResponse(dockerfile=dockerfile)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Dockerfile: {str(e)}")

@router.post("/generate-env-variables-from-repo", response_model=EnvVariablesResponse)
async def generate_env_variables_from_repo(request: GenerateFromRepoRequest = Body(...)):
    try:
        # Parse repository
        repo_data = parse_repository(
            repo_url=request.repo_url,
            max_files=request.max_files
        )
        
        # Use raw JSON string as context
        context = json.dumps(repo_data)
        
        # Extract environment variables
        env_variables_json = extract_env_variables(context)
        env_variables = json.loads(env_variables_json)
        
        return EnvVariablesResponse(env_variables=env_variables)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse environment variables JSON")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate environment variables: {str(e)}")

