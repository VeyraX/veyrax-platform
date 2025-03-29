from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import (
    IpInfoParams,
    BulkIpInfoParams,
    AsnInfoParams,
    IpInfoResponseSchema,
    BulkIpInfoResponseSchema,
    AsnInfoResponseSchema,
    ApiResponse
)
from .service import IpInfoService
from .client import IpInfoClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os
router = APIRouter(prefix="/ipinfo", tags=["ipinfo"])

examples = ExamplesLoader()

async def get_ipinfo_service(request: Request):
    try:
        # api_token = await validate_provider_api_key(request, "ipinfo")
        api_token = os.environ.get("IPINFO_API_KEY")
        client = IpInfoClient(api_token)
        apply_error_handler_to_client(client)
        service = IpInfoService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize IpInfo service: {str(e)}")

@router.post("/get_ip_info", response_model=ApiResponse)
@schema(
    input_schema_class=IpInfoParams,
    output_schema_class=IpInfoResponseSchema,
    examples=examples["/ipinfo/get_ip_info"]
)
async def get_ip_info(
    params: Dict[str, Any] = Body(...),
    service: IpInfoService = Depends(get_ipinfo_service)
):
    validated_params = IpInfoParams(**params)
    return service.get_ip_info(validated_params)

@router.post("/get_bulk_info", response_model=ApiResponse)
@schema(
    input_schema_class=BulkIpInfoParams,
    output_schema_class=BulkIpInfoResponseSchema,
    examples=examples["/ipinfo/get_bulk_info"]
)
async def get_bulk_info(
    params: Dict[str, Any] = Body(...),
    service: IpInfoService = Depends(get_ipinfo_service)
):
    validated_params = BulkIpInfoParams(**params)
    return service.get_bulk_info(validated_params)

@router.post("/get_asn_info", response_model=ApiResponse)
@schema(
    input_schema_class=AsnInfoParams,
    output_schema_class=AsnInfoResponseSchema,
    examples=examples["/ipinfo/get_asn_info"]
)
async def get_asn_info(
    params: Dict[str, Any] = Body(...),
    service: IpInfoService = Depends(get_ipinfo_service)
):
    validated_params = AsnInfoParams(**params)
    return service.get_asn_info(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_token = params.get("api_token")
        if not api_token:
            return {"valid": False, "message": "API token is required"}
        
        client = IpInfoClient(api_token=api_token)
        # Test the API token with a simple call
        client.get_ip_info()
        return {"valid": True, "message": "API token is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API token: {str(e)}"}

apply_error_handler_to_router(router) 