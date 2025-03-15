from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
from .schema import SingleRequestParams, ApiResponse, ExecuteRequestParams, ExecuteRequestResponse
from .service import HttpService
from pydantic import ValidationError
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader
from ..common.input_schema_decorator import schema

router = APIRouter(prefix="/http-request", tags=["http-request"])
examples = ExamplesLoader()

@router.post("/execute_request", response_model=ApiResponse)
@schema(input_schema_class=ExecuteRequestParams, 
        output_schema_class=ExecuteRequestResponse, 
        examples=examples["/http-request/execute_request"])
async def execute_request(params: Dict[str, Any] = Body(...)):
    try:
        service = HttpService()
        validated_params = SingleRequestParams(**params)
        return service.execute_single_request(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SingleRequestParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))