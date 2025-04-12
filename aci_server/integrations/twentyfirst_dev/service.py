from typing import Dict, Any, Optional
import os
from .client import TwentyFirstDevClient
from .schema import (
    SearchParams,
    GeneratePromptParams,
    SearchResultsList,
    GeneratePromptResponse,
    ApiResponse,
    SearchResponse,
    PromptResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class TwentyFirstDevService:
    def __init__(self, client: TwentyFirstDevClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "twentyfirst_dev"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def search(self, params: SearchParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search(processed_params)
        validated_data = SearchResultsList(**response)
        return self.prepare_response(validated_data, "SearchResults")
    
    def generate_prompt(self, params: GeneratePromptParams) -> ApiResponse:
        processed_params = self._process_prompt_params(params)
        response = self.client.generate_prompt(processed_params)
        validated_data = GeneratePromptResponse(**response)
        return self.prepare_response(validated_data, "GeneratedPrompt")
    
    def _process_search_params(self, params: SearchParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
    
    def _process_prompt_params(self, params: GeneratePromptParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
