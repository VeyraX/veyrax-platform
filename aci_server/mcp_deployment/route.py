from fastapi import APIRouter, HTTPException, Body, Header, Request, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
import json
import httpx
import os

from .schema import (
    PushMCPRequest, 
    PushMCPResponse, 
    RepositoryMetaRequest, 
    RepositoryMetaResponse,
    ExternalMCPResponse,
    DeploymentStatusUpdate
)
from .parse_repo import parse_repository, check_dockerfile_exists
from .generate_files import (
    push_mcp_to_dockerhub,
    extract_repo_metadata,
    extract_env_variables
)
from db.supabase import get_supabase
from integrations.common.auth import get_user_from_request
from .queries import create_mcp_deployment_record, update_mcp_deployment_status

router = APIRouter(
    prefix="/mcp_deployment",
    tags=["mcp_deployment"],
)   

async def get_auth_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header
    
    api_key = request.headers.get("VEYRAX_API_KEY")
    if api_key:
        return api_key
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide either Bearer token in Authorization header or VEYRAX_API_KEY header."
    )

@router.post("/generate-repository-meta", response_model=RepositoryMetaResponse)
async def generate_repository_meta_endpoint(
    request: RepositoryMetaRequest = Body(...),
    is_local: bool = Query(False, description="Flag indicating if the environment variables are for local development")
):
    try:
        try:
            repo_data = parse_repository(repo_url=request.repo_url)
        except Exception as repo_error:
            error_msg = f"Failed to parse repository: {str(repo_error)}"
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Check for Dockerfile but don't throw error
        dockerfile_exists = True
        try:
            dockerfile_exists = check_dockerfile_exists(repo_data.get("files", []))
        except Exception as docker_error:
            error_msg = f"Error checking for Dockerfile: {str(docker_error)}"
            raise HTTPException(status_code=500, detail=error_msg)
        
        try:
            context = json.dumps(repo_data)
            env_variables = extract_env_variables(context, is_local=is_local)
        except Exception as env_error:
            error_msg = f"Failed to extract environment variables: {str(env_error)}"
            raise HTTPException(status_code=500, detail=error_msg)
        
        try:
            repo_metadata = extract_repo_metadata(context)
        except Exception as meta_error:
            error_msg = f"Failed to extract repository metadata: {str(meta_error)}"
            raise HTTPException(status_code=500, detail=error_msg)
            
        return RepositoryMetaResponse(
            env_variables=env_variables,
            name=repo_metadata.get("name", ""),
            description=repo_metadata.get("description", ""),
            is_local=is_local,
            dockerfile_exists=dockerfile_exists
        )
    except HTTPException as e:
        raise
    except Exception as e:
        error_msg = f"Failed to generate repository metadata: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/push-mcp-to-dockerhub", response_model=PushMCPResponse)
async def push_mcp_dockerhub_endpoint(
    request: Request,
    push_request: PushMCPRequest = Body(...),
    auth_token: str = Depends(get_auth_token)
):
    try:
        user_id = await get_user_from_request(request)
        deployment_record = await create_mcp_deployment_record(
            repository_id=push_request.repository_id,
            commit_hash=push_request.commit_hash,
            status="started"
        )
        
        result = await push_mcp_to_dockerhub(
            repo_url=push_request.repo_url,
            image_name=push_request.image_name,
            auth_token=auth_token,
            repository_id=push_request.repository_id,
            deployment_id=deployment_record.get('deployment_id'),
            commit_hash=push_request.commit_hash
        )
  
        return PushMCPResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to push MCP to Docker Hub: {str(e)}")

@router.post("/update-deployment-status", response_model=Dict[str, Any])
async def update_deployment_status_endpoint(
    request: DeploymentStatusUpdate = Body(...),
    auth_token: str = Depends(get_auth_token)
):
    try:
        # Update the deployment status in the database
        result = await update_mcp_deployment_status(
            deployment_id=request.deployment_id,
            status=request.status,
            build_logs=request.build_logs
        )
        
        return {
            "success": True,
            "deployment_id": request.deployment_id,
            "status": request.status
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to update deployment status: {str(e)}"
        )

