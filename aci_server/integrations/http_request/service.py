from typing import Optional, Dict, Any
from .client import HttpClient
from .schema import (
    ApiResponse, RequestResponse, SingleRequestParams
)
import os
from ..common.component_handler import load_components, prepare_components_auto
from fastapi import HTTPException
from ..common.utils import apply_error_handler_to_client
class HttpService:
    def __init__(self):
        self.client = HttpClient()
        apply_error_handler_to_client(self.client)
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "http_client"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def execute_single_request(self, params: SingleRequestParams) -> ApiResponse:
        """Execute a single HTTP request"""
        request_data = {
            "name": params.request.name,
            "method": params.request.method,
            "url": params.request.url if isinstance(params.request.url, str) else params.request.url.dict(exclude_none=True),
            "headers": [h.dict(exclude_none=True) for h in params.request.headers] if params.request.headers else [],
            "body": params.request.body.dict(exclude_none=True) if params.request.body else None,
        }

        response = self.client.execute_request(
            request_data=request_data,
            environment=params.environment
        )
        
        request_response = RequestResponse(
            name=params.request.name,
            status=response["status"],
            code=response["code"],
            body=response["data"],
            headers=response["headers"]
        )
        
        return self.prepare_response(request_response, "HttpRequestResponse")