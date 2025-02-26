from typing import Dict, Any, Union, List, Optional
from .client import PerplexityClient
from .schema import CompletionRequest, CompletionResponse, ApiResponse
import os
from ..common.component_handler import load_components, prepare_components_auto

class PerplexityService:
    def __init__(self, client: PerplexityClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: CompletionResponse, component_name: str = None) -> ApiResponse:
        tool_name = "perplexity"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
        
    def create_completion(self, request: CompletionRequest) -> ApiResponse:
        response = self.client.create_completion(**request.model_dump())
        completion_response = CompletionResponse(**response)
        return self.prepare_response(completion_response, "PerplexityResponseView")