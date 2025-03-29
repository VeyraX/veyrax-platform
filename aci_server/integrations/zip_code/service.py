from typing import Dict, Any, Union, List, Optional
from .client import ZipCodeClient
from .schema import ZipCodeRequest, CityRequest, ZipCodeResponse, ApiResponse
import os
from ..common.component_handler import load_components, prepare_components_auto
import json
from requests.exceptions import HTTPError

class ZipCodeService:
    def __init__(self, client: ZipCodeClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: ZipCodeResponse, component_name: str = None) -> ApiResponse:
        tool_name = "zip_code"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
        
    def get_by_zipcode(self, request: ZipCodeRequest) -> ApiResponse:
        response = self.client.get_by_zipcode(request.country, request.postal_code)
        
        if not response:
            raise ValueError("Empty response received from Zippopotam API")
            
        zip_code_response = ZipCodeResponse(**response)
        return self.prepare_response(zip_code_response, "ZipCodeResponseView")
        
    def get_by_city(self, request: CityRequest) -> ApiResponse:
        response = self.client.get_by_city(request.country, request.state, request.city)
        
        if not response:
            raise ValueError("Empty response received from Zippopotam API")
            
        zip_code_response = ZipCodeResponse(**response)
        return self.prepare_response(zip_code_response, "ZipCodeResponseView") 