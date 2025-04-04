from typing import Dict, Any
from fastapi import APIRouter, Body, HTTPException, Depends, Request as FastAPIRequest

from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_user_from_request
from .service import VeyraxAuthService
from .client import VeyraxAuthClient
from .schema import (
    GetToolsConnectionStatusParams, GetToolsConnectionStatusResponse,
    GenerateConnectionLinkParams, GenerateConnectionLinkResponse,
    ApiResponse
)

router = APIRouter(prefix="/veyrax_auth", tags=["veyrax_auth"])

examples = ExamplesLoader()

async def get_veyrax_auth_service(request: FastAPIRequest):
    try:
        user_id = await get_user_from_request(request)
        client = VeyraxAuthClient(user_id)
        apply_error_handler_to_client(client)
        service = VeyraxAuthService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Veyrax Auth service: {str(e)}")

@router.post("/get_tools_connection_status", response_model=ApiResponse)
@schema(input_schema_class=GetToolsConnectionStatusParams, output_schema_class=GetToolsConnectionStatusResponse, examples=examples["/veyrax_auth/get_tools_connection_status"])
async def get_tools_connection_status(
    params: Dict[str, Any] = Body(...),
    service: VeyraxAuthService = Depends(get_veyrax_auth_service)
):
    validated_params = GetToolsConnectionStatusParams(**params)
    return service.get_tools_connection_status()

@router.post("/generate_connection_link", response_model=ApiResponse)
@schema(input_schema_class=GenerateConnectionLinkParams, output_schema_class=GenerateConnectionLinkResponse, examples=examples["/veyrax_auth/generate_connection_link"])
async def generate_connection_link(
    params: Dict[str, Any] = Body(...),
    service: VeyraxAuthService = Depends(get_veyrax_auth_service)
):
    validated_params = GenerateConnectionLinkParams(**params)
    return service.generate_connection_link(provider_tag=validated_params.provider_tag)

apply_error_handler_to_router(router)
