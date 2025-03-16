from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
from .schema import SingleRequestParams, ApiResponse, ExecuteRequestParams, ExecuteRequestResponse
from .service import HttpService
from pydantic import ValidationError
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader
from ..common.input_schema_decorator import schema

router = APIRouter(prefix="/http-request", tags=["http-request"])
examples = ExamplesLoader()

def get_http_service():
    service = HttpService()
    apply_error_handler_to_service(service)
    return service

@router.post("/execute_request", response_model=ApiResponse)
@schema(input_schema_class=ExecuteRequestParams, 
        output_schema_class=ExecuteRequestResponse, 
        examples=examples["/http-request/execute_request"])
async def execute_request(params: Dict[str, Any] = Body(...)):
    service = get_http_service()
    validated_params = SingleRequestParams(**params)
    return service.execute_single_request(validated_params)

apply_error_handler_to_router(router)