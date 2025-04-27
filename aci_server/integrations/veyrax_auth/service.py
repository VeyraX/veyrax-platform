from typing import Dict, Any, List, Optional
import os
from .client import VeyraxAuthClient
from .schema import ProviderInfo, ProviderInfoList, GetToolsConnectionStatusResponse, GenerateConnectionLinkResponse, ApiResponse
from ..common.component_handler import load_components, prepare_components_auto

class VeyraxAuthService:
    def __init__(self, client: VeyraxAuthClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "veyrax-auth"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_tools_connection_status(self) -> ApiResponse:
        providers = self.client.get_all_providers()
        user_providers = self.client.get_user_providers()
        connected_provider_ids = {up["provider_id"] for up in user_providers}
        
        mcp_repos = self.client.get_mcp_repositories()
        
        provider_info_list = []
        
        for provider in providers:
            provider_info = ProviderInfo(
                provider_tag=provider["provider_tag"],
                is_connected=provider["id"] in connected_provider_ids,
                type="tool"
            )
            provider_info_list.append(provider_info)
        
        for repo in mcp_repos:
            provider_info = ProviderInfo(
                provider_tag=repo["image_name"],
                is_connected=self.client.is_mcp_connected(repo["id"]),
                type="mcp"
            )
            provider_info_list.append(provider_info)
        
        provider_list = ProviderInfoList(items=provider_info_list)
        return self.prepare_response(provider_list, "provider_status")
    
    def generate_connection_link(self, provider_tag: str, provider_type: str, redirect_url: Optional[str] = None) -> ApiResponse:
        connection_data = self.client.generate_connection_link(provider_tag, provider_type, redirect_url)
        return self.prepare_response(connection_data, "connection_link")
