from typing import Dict, Any, List, Optional, Union
from .client import FalAIClient
from .schema import (
    ModelsParams,
    SearchModelParams,
    SchemaModelParams,
    GenerateParams,
    ResultParams,
    StatusParams,
    CancelParams,
    UploadParams,
    Model,
    ModelList,
    GenerationResult,
    SchemaInfo,
    UploadResult,
    ModelsResponse,
    SchemaResponse,
    GenerateResponse,
    ResultResponse,
    StatusResponse,
    CancelResponse,
    UploadResponse,
    ApiResponse
)
import os
import re
from ..common.component_handler import load_components, prepare_components_auto

class FalAIService:
    def __init__(self, client: FalAIClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            return load_components(current_dir)
        except:
            return []
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "falai"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    async def get_models(self, params: ModelsParams) -> ApiResponse:
        response = await self.client.get_models(
            page=params.page,
            total=params.total,
            max_results=params.max_results
        )
        
        # Convert to model list
        models = [Model(**model) for model in response]
        
        # Apply max_results limit if specified
        if params.max_results and len(models) > params.max_results:
            models = models[:params.max_results]
            
        model_list = ModelList(models=models)
        
        return self.prepare_response(model_list)

    async def search_models(self, params: SearchModelParams) -> ApiResponse:
        response = await self.client.search_models(keywords=params.keywords)
        
        # Convert to model list
        models = [Model(**model) for model in response]
        model_list = ModelList(models=models)
        
        return self.prepare_response(model_list)

    async def get_schema(self, params: SchemaModelParams) -> ApiResponse:
        response = await self.client.get_schema(model_id=params.model_id)
        
        # Convert to schema info
        schema_info = SchemaInfo(**response)
        
        return self.prepare_response(schema_info)

    async def generate(self, params: GenerateParams) -> ApiResponse:
        response = await self.client.generate(
            model=params.model,
            parameters=params.parameters,
            queue=params.queue
        )
        
        generation_result = GenerationResult(**response)
        
        return self.prepare_response(generation_result)

    async def get_result(self, params: ResultParams) -> ApiResponse:
        response = await self.client.get_result(url=params.url)
        
        is_pixverse = False
        if params.url and "pixverse" in params.url.lower():
            is_pixverse = True
            
        if is_pixverse and "result" in response and response["result"] and "video" in response["result"]:
            component_name = "FalAIVideoResult"
        else:
            component_name = self._determine_component(response)
            
        generation_result = GenerationResult(**response)
        
        return self.prepare_response(generation_result, component_name)
    
    def _determine_component(self, response: Dict[str, Any]) -> Optional[str]:
        if "result" in response and response["result"]:
            result = response["result"]
            if "images" in result:
                return "FalAIImageResult"
            elif "video" in result:
                return "FalAIVideoResult"
            elif "audio" in result:
                return "FalAIAudioResult"
        
        if "status" in response:
            if response["status"] == "queued" or response["status"] == "IN_QUEUE":
                return "FalAIQueuedRequest"
            elif response["status"] == "in_progress" or response["status"] == "IN_PROGRESS":
                return "FalAIQueueStatus"
                
        return None

    async def get_status(self, params: StatusParams) -> ApiResponse:
        response = await self.client.get_status(url=params.url)
        
        generation_result = GenerationResult(**response)
        
        return self.prepare_response(generation_result)

    async def cancel_request(self, params: CancelParams) -> ApiResponse:
        response = await self.client.cancel_request(url=params.url)
        
        generation_result = GenerationResult(**response)
        
        return self.prepare_response(generation_result)

    async def upload_file(self, params: UploadParams) -> ApiResponse:
        response = await self.client.upload_file(path=params.path)
        
        upload_result = UploadResult(**response)
        
        return self.prepare_response(upload_result)
