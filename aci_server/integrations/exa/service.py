from typing import Dict, Any, List, Optional
from .client import ExaClient
from .schema import (
    SearchParams,
    ContentsParams,
    FindSimilarParams,
    SearchResponse,
    ContentsResponse,
    FindSimilarResponse,
    ApiResponse
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class ExaService:
    def __init__(self, client: ExaClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "exa"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def search(self, params: SearchParams) -> ApiResponse:
        processed_params = self._process_search_params(params)
        response = self.client.search(processed_params)
        validated = SearchResponse(**response)
        return ApiResponse(data=validated)

    def get_contents(self, params: ContentsParams) -> ApiResponse:
        processed_params = self._process_contents_params(params)
        response = self.client.get_contents(processed_params)
        validated = ContentsResponse(**response)
        return ApiResponse(data=validated)

    def find_similar(self, params: FindSimilarParams) -> ApiResponse:
        processed_params = self._process_similar_params(params)
        response = self.client.find_similar(processed_params)
        validated = FindSimilarResponse(**response)
        return ApiResponse(data=validated)

    def _process_search_params(self, params: SearchParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_contents_params(self, params: ContentsParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)

    def _process_similar_params(self, params: FindSimilarParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)