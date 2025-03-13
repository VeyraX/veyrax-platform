from typing import Optional, Dict, Any, List, Union
from .client import TavilyClient
from .schema import (
    SearchParams,
    ExtractParams,
    SearchResponse,
    ExtractResponse,
    ApiResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class TavilyService:
    def __init__(self, client: TavilyClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "tavily"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def search(self, params: SearchParams) -> ApiResponse:
        """Perform a search using Tavily Search API"""
        params_dict = params.model_dump(exclude_none=True)
        
        # API call
        response = self.client.search(params_dict)
        
        # Validate and process response
        validated_response = SearchResponse(**response)
        
        # Determine appropriate component based on response content
        component_name = self._determine_search_component(validated_response)
        
        return self.prepare_response(validated_response, component_name)

    def extract(self, params: ExtractParams) -> ApiResponse:
        """Extract web page content using Tavily Extract API"""
        params_dict = params.model_dump(exclude_none=True)
        
        # Convert single string URL to string (not list) for API
        if isinstance(params_dict.get('urls', []), list) and len(params_dict.get('urls', [])) == 1:
            params_dict['urls'] = params_dict['urls'][0]
        
        # API call
        response = self.client.extract(params_dict)
        
        # Validate and process response
        validated_response = ExtractResponse(**response)
        
        return self.prepare_response(validated_response, "TavilyExtractCard")
        
    def _determine_search_component(self, response: SearchResponse) -> str:
        """Determine which component to use based on response content"""
        if response.images and len(response.images) > 0:
            return "TavilySearchWithImagesCard"
        elif response.answer:
            return "TavilySearchWithAnswerCard"
        else:
            return "TavilySearchCard" 