from fastapi import APIRouter, Body, Depends
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SearchMCPParams,
    DeployMCPParams,
    GenerateConnectionLinkParams,
    ApiResponse,
    SearchMCPResponse,
    DeployMCPResponse,
    GenerateConnectionLinkResponse
)
from .service import VeyraxMcpService
from .client import VeyraxMcpClient
from ..common.auth import get_user_from_request
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/veyrax-mcp", tags=["veyrax-mcp"])
examples = ExamplesLoader()

async def get_veyrax_mcp_service(request: FastAPIRequest):
    try:
        # Get the user's access token
        user_id = await get_user_from_request(request)
        
        # Get authentication token from request header
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
        
        # Initialize client and service
        client = VeyraxMcpClient(token=token, user_id=user_id)
        apply_error_handler_to_client(client)
        
        service = VeyraxMcpService(client)
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise Exception(f"Failed to initialize Veyrax MCP service: {str(e)}")

@router.post("/search_mcp", response_model=ApiResponse)
@schema(
    input_schema_class=SearchMCPParams,
    output_schema_class=SearchMCPResponse,
    examples=examples.get("/veyrax-mcp/search_mcp", [])
)
async def search_mcp(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMcpService = Depends(get_veyrax_mcp_service)
):
    validated_params = SearchMCPParams(**params)
    return await service.search_mcp(validated_params)

@router.post("/deploy_mcp", response_model=ApiResponse)
@schema(
    input_schema_class=DeployMCPParams,
    output_schema_class=DeployMCPResponse,
    examples=examples.get("/veyrax-mcp/deploy_mcp", [])
)
async def deploy_mcp(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMcpService = Depends(get_veyrax_mcp_service)
):
    validated_params = DeployMCPParams(**params)
    return await service.deploy_mcp(validated_params)

@router.post("/generate_connection_link", response_model=ApiResponse)
@schema(
    input_schema_class=GenerateConnectionLinkParams,
    output_schema_class=GenerateConnectionLinkResponse,
    examples=examples.get("/veyrax-mcp/generate_connection_link", [])
)
async def generate_connection_link(
    params: Dict[str, Any] = Body(...),
    service: VeyraxMcpService = Depends(get_veyrax_mcp_service)
):
    validated_params = GenerateConnectionLinkParams(**params)
    return service.generate_connection_link(validated_params)

apply_error_handler_to_router(router)
