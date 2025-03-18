from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    SaveDocumentParams,
    ListDocumentsParams,
    UpdateDocumentParams,
    DeleteDocumentParams,
    ApiResponse
)
from .service import ReadwiseService
from .client import ReadwiseClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/readwise", tags=["readwise"])
examples = ExamplesLoader()

async def get_readwise_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "readwise")
        client = ReadwiseClient(api_key)
        service = ReadwiseService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        print(f"Error initializing Readwise service: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Readwise service: {str(e)}"
        )

@router.post("/save", response_model=ApiResponse)
@schema(
    input_schema_class=SaveDocumentParams,
    output_schema_class=ApiResponse,
    examples=examples["/readwise/save"]
)
async def save_document(
    params: Dict[str, Any] = Body(...),
    service: ReadwiseService = Depends(get_readwise_service)
):
    validated_params = SaveDocumentParams(**params)
    return service.save_document(validated_params)

@router.post("/list", response_model=ApiResponse)
@schema(
    input_schema_class=ListDocumentsParams,
    output_schema_class=ApiResponse,
    examples=examples["/readwise/list"]
)
async def list_documents(
    params: Dict[str, Any] = Body(...),
    service: ReadwiseService = Depends(get_readwise_service)
):
    validated_params = ListDocumentsParams(**params)
    return service.list_documents(validated_params)

@router.post("/update", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateDocumentParams,
    output_schema_class=ApiResponse,
    examples=examples["/readwise/update"]
)
async def update_document(
    params: Dict[str, Any] = Body(...),
    service: ReadwiseService = Depends(get_readwise_service)
):
    validated_params = UpdateDocumentParams(**params)
    return service.update_document(validated_params.document_id, validated_params)

@router.post("/delete", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteDocumentParams,
    output_schema_class=ApiResponse,
    examples=examples["/readwise/delete"]
)
async def delete_document(
    params: Dict[str, Any] = Body(...),
    service: ReadwiseService = Depends(get_readwise_service)
):
    validated_params = DeleteDocumentParams(**params)
    return service.delete_document(validated_params.document_id)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = ReadwiseClient(api_key=api_key)
        is_valid = client.validate_token()
        if is_valid:
            return {"valid": True, "message": "API key is valid"}
        else:
            return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router)
