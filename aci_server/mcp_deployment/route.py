from fastapi import APIRouter, HTTPException, Body, Header, Request, Depends
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
    AppendAllServersResponse,
    StartDeploymentRequest,
    StartDeploymentResponse
)
from .parse_repo import parse_repository
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
        return auth_header.replace("Bearer ", "")
    
    api_key = request.headers.get("VEYRAX_API_KEY")
    if api_key:
        return api_key
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide either Bearer token in Authorization header or VEYRAX_API_KEY header."
    )

@router.post("/generate-repository-meta", response_model=RepositoryMetaResponse)
async def generate_repository_meta_endpoint(request: RepositoryMetaRequest = Body(...)):
    try:
        repo_data = parse_repository(repo_url=request.repo_url)
        
        context = json.dumps(repo_data)
        
        env_variables = extract_env_variables(context)
        
        repo_metadata = extract_repo_metadata(context)
        
        return RepositoryMetaResponse(
            env_variables=env_variables,
            name=repo_metadata.get("name", ""),
            description=repo_metadata.get("description", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate repository metadata: {str(e)}")

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
        
        if "error" in deployment_record:
            print(f"Warning: Failed to create deployment record: {deployment_record['error']}")
        
        result = await push_mcp_to_dockerhub(
            repo_url=push_request.repo_url,
            image_name=push_request.image_name,
            auth_token=auth_token,
            repository_id=push_request.repository_id,
            deployment_id=deployment_record.get('deployment_id')
        )
        
        return PushMCPResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to push MCP to Docker Hub: {str(e)}")

@router.post("/append-all-servers", response_model=AppendAllServersResponse)
async def append_all_servers_endpoint():
    try:
        api_url = "https://api.pulsemcp.com/v0beta/servers"
        added_count = 0
        skipped_count = 0
        no_source_code_count = 0
        supabase = get_supabase()
        
        async with httpx.AsyncClient(
            headers={"User-Agent": "VeyraX/1.0 (https://veyrax.com)"}
        ) as client:
            next_url = api_url
            while next_url:
                response = await client.get(next_url, timeout=30.0)
                
                if response.status_code != 200:
                    error_detail = f"External API error: {response.status_code} - {response.text}"
                    raise HTTPException(status_code=500, detail=error_detail)
                
                data = ExternalMCPResponse.parse_obj(response.json())
                
                for server in data.servers:
                    if not server.source_code_url:
                        no_source_code_count += 1
                        continue
                    
                    result = supabase.table('mcp_repositories').select('*').execute()
                    
                    existing_entry = False
                    for entry in result.data:
                        if entry.get('metadata') and entry['metadata'].get('source_code_url') == server.source_code_url:
                            existing_entry = True
                            break
                    
                    if existing_entry:
                        skipped_count += 1
                    else:
                        supabase.table('external_mcp_repositories').insert({
                            'name': server.name,
                            'metadata': {
                                'source_code_url': server.source_code_url,
                                'url': server.url,
                                'external_url': server.external_url,
                                'short_description': server.short_description,
                                'github_stars': server.github_stars,
                                'package_registry': server.package_registry,
                                'package_name': server.package_name,
                                'package_download_count': server.package_download_count,
                                'ai_generated_description': server.EXPERIMENTAL_ai_generated_description
                            }
                        }).execute()
                        added_count += 1
                
                next_url = data.next
        
        return AppendAllServersResponse(
            total_added=added_count,
            skipped=skipped_count,
            message=f"Successfully processed servers: {added_count} added, {skipped_count} skipped (already exist), {no_source_code_count} skipped (no source_code_url)"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch and store external MCP servers: {str(e)}")

@router.post("/start-deployment", response_model=StartDeploymentResponse)
async def start_deployment_endpoint(
    request: Request,
    start_request: StartDeploymentRequest = Body(...),
    auth_token: str = Depends(get_auth_token)
):
    try:
        user_id = await get_user_from_request(request)
        
        deployment_id = start_request.deployment_id
        
        repo_connect_url = os.environ.get("REPO_CONNECT_URL", "https://api.veyrax.com/repo/connect")
        
        if auth_token.startswith("Bearer "):
            headers = {
                "Content-Type": "application/json",
                "Authorization": auth_token
            }
        else:
            headers = {
                "Content-Type": "application/json",
                "VEYRAX_API_KEY": auth_token
            }
            
        try:
            async with httpx.AsyncClient() as client:
                repo_connect_response = await client.post(
                    repo_connect_url,
                    headers=headers,
                    json={"repository_id": start_request.repository_id, "deployment_id": deployment_id},
                    timeout=10.0
                )
                
                if repo_connect_response.status_code != 200:
                    print(f"Warning: Failed to connect repository: {repo_connect_response.text}")
        except Exception as connect_error:
            print(f"Warning: Error connecting repository: {str(connect_error)}")
            
        result = await update_mcp_deployment_status(
            deployment_id=deployment_id,
            status="building"
        )
        
        if "error" in result:
            return StartDeploymentResponse(
                success=False,
                message=f"Failed to update deployment status: {result['error']}",
                deployment_id=deployment_id
            )
        
        return StartDeploymentResponse(
            success=True,
            message="Deployment started successfully and repository connected",
            deployment_id=deployment_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start deployment: {str(e)}")

