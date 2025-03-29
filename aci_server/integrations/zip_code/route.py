from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import ZipCodeRequest, CityRequest, ApiResponse, ZipCodeResponseSchema
from .service import ZipCodeService
from .client import ZipCodeClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from pydantic import ValidationError
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader
import os
from requests import HTTPError

router = APIRouter(prefix="/zip_code", tags=["zip_code"])

examples = ExamplesLoader() 

async def get_zipcode_service(request: Request):
    try:
        # This API doesn't require authentication, so we're not validating a provider API key
        client = ZipCodeClient()
        apply_error_handler_to_client(client)
        service = ZipCodeService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize ZipCode service: {str(e)}")

@router.post("/get_by_zipcode", response_model=ApiResponse)
@schema(input_schema_class=ZipCodeRequest, output_schema_class=ZipCodeResponseSchema, examples=examples["/zip_code/get_by_zipcode"])
async def get_by_zipcode(
    params: Dict[str, Any] = Body(...),
    service: ZipCodeService = Depends(get_zipcode_service)
):
    validated_params = ZipCodeRequest(**params)
    return service.get_by_zipcode(validated_params)

@router.post("/get_by_city", response_model=ApiResponse)
@schema(input_schema_class=CityRequest, output_schema_class=ZipCodeResponseSchema, examples=examples["/zip_code/get_by_city"])
async def get_by_city(
    params: Dict[str, Any] = Body(...),
    service: ZipCodeService = Depends(get_zipcode_service)
):
    validated_params = CityRequest(**params)
    return service.get_by_city(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        # Since this API doesn't require an API key, we'll always return valid
        return {"valid": True, "message": "No API key required for Zippopotam"}
    except Exception as e:
        return {"valid": False, "message": f"Error: {str(e)}"}

apply_error_handler_to_router(router) 