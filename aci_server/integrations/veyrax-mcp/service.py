from typing import Dict, Any, List, Optional
import os
from .client import VeyraxMcpClient
from .schema import (
    SearchMCPParams, 
    MCPRepository, 
    MCPRepositoryList,
    DeployMCPParams,
    DeploymentStatus,
    GenerateConnectionLinkParams,
    ConnectionLinkInfo,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class VeyraxMcpService:
    def __init__(self, client: VeyraxMcpClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "veyrax-mcp"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    async def search_mcp(self, params: SearchMCPParams) -> ApiResponse:
        results = await self.client.search_mcp(
            query=params.query,
            limit=params.limit
        )
        
        repositories = []
        for item in results:
            repo = MCPRepository(
                **item
            )
            repositories.append(repo)
        
        repository_list = MCPRepositoryList(repositories=repositories)
        return self.prepare_response(repository_list, "MCPRepositoryList")
    
    async def deploy_mcp(self, params: DeployMCPParams) -> ApiResponse:
        result = await self.client.deploy_mcp(
            repo_url=params.repo_url,
            image_name=params.image_name,
            repository_id=params.repository_id,
            commit_hash=params.commit_hash
        )
        
        deployment_status = DeploymentStatus(**result)
        
        return self.prepare_response(deployment_status, "DeploymentStatus")
        
    def generate_connection_link(self, params: GenerateConnectionLinkParams) -> ApiResponse:
        result = self.client.generate_connection_link(
            code=params.code,
            api_key=params.api_key,
            image_name=params.image_name
        )
        
        connection_info = ConnectionLinkInfo(**result)
        return self.prepare_response(connection_info, "ConnectionLinkInfo")
