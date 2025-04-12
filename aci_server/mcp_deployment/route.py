from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
import json
import httpx

from .schema import (
    PushMCPRequest, 
    PushMCPResponse, 
    RepositoryMetaRequest, 
    RepositoryMetaResponse,
    ExternalMCPResponse,
    AppendAllServersResponse
)
from .parse_repo import parse_repository
from .generate_files import (
    push_mcp_to_dockerhub,
    extract_repo_metadata,
    extract_env_variables
)
from db.supabase import get_supabase

router = APIRouter(
    prefix="/mcp_deployment",
    tags=["mcp_deployment"],
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
async def push_mcp_dockerhub_endpoint(request: PushMCPRequest = Body(...)):
    try:
        result = await push_mcp_to_dockerhub(
            repo_url=request.repo_url,
            image_name=request.image_name
        )
        
        return PushMCPResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to push MCP to Docker Hub: {str(e)}")

@router.post("/append-all-servers", response_model=AppendAllServersResponse)
async def append_all_servers_endpoint():
    """
    Fetches all MCP servers from the external API and stores them in Supabase.
    Performs deduplication based on source_code_url in the metadata field.
    Servers without source_code_url are skipped.
    """
    try:
        api_url = "https://api.pulsemcp.com/v0beta/servers"
        added_count = 0
        skipped_count = 0
        no_source_code_count = 0
        supabase = get_supabase()
        
        # Set up HTTP client with user agent
        async with httpx.AsyncClient(
            headers={"User-Agent": "VeyraX/1.0 (https://veyrax.com)"}
        ) as client:
            # Process pagination
            next_url = api_url
            while next_url:
                response = await client.get(next_url, timeout=30.0)
                
                if response.status_code != 200:
                    error_detail = f"External API error: {response.status_code} - {response.text}"
                    raise HTTPException(status_code=500, detail=error_detail)
                
                data = ExternalMCPResponse.parse_obj(response.json())
                
                for server in data.servers:
                    # Пропускаем сервера без source_code_url
                    if not server.source_code_url:
                        no_source_code_count += 1
                        continue
                    
                    # Проверяем существование записи с таким source_code_url в metadata
                    result = supabase.table('mcp_repositories').select('*').execute()
                    
                    existing_entry = False
                    for entry in result.data:
                        if entry.get('metadata') and entry['metadata'].get('source_code_url') == server.source_code_url:
                            existing_entry = True
                            break
                    
                    if existing_entry:
                        # Server already exists, skip it
                        skipped_count += 1
                    else:
                        # Insert new server
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
                
                # Check if there's a next page
                next_url = data.next
        
        return AppendAllServersResponse(
            total_added=added_count,
            skipped=skipped_count,
            message=f"Successfully processed servers: {added_count} added, {skipped_count} skipped (already exist), {no_source_code_count} skipped (no source_code_url)"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch and store external MCP servers: {str(e)}")

