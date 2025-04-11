from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
import json

from .schema import PushMCPRequest, PushMCPResponse, EnvVariablesRequest, EnvVariablesResponse
from .parse_repo import parse_repository
from .generate_files import generate_dockerfile, extract_env_variables, push_mcp_to_dockerhub

router = APIRouter(
    prefix="/mcp_deployment",
    tags=["mcp_deployment"],
)   

@router.post("/generate-env-variables", response_model=EnvVariablesResponse)
async def create_env_variables(request: EnvVariablesRequest = Body(...)):
    try:
        env_variables_json = extract_env_variables(request.context)
        env_variables = json.loads(env_variables_json)
        return EnvVariablesResponse(env_variables=env_variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse environment variables JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate environment variables: {str(e)}")

@router.post("/push-mcp-to-dockerhub", response_model=PushMCPResponse)
async def push_mcp_dockerhub_endpoint(request: PushMCPRequest = Body(...)):
    try:
        result = await push_mcp_to_dockerhub(
            repo_url=request.repo_url,
            image_name=request.image_name
        )
        
        return PushMCPResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to push MCP to Docker Hub: {str(e)}")

