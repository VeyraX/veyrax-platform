from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    GetFormsParams, GetFormParams, GetFormResponsesParams,
    CreateWebhookParams, GetWorkspacesParams,
    GetFormsResponse, GetFormResponse, GetFormResponsesResponse,
    CreateWebhookResponse, GetWebhooksResponse, GetWorkspacesResponse,
    ApiResponse,
    CreateFormParams, UpdateFormParams, DeleteFormParams,
    DeleteWebhookParams, CreateWorkspaceParams,
    CreateFormResponse, UpdateFormResponse, DeleteFormResponse,
    DeleteWebhookResponse, CreateWorkspaceResponse
)
from .service import TypeformService
from .client import TypeformClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/typeform", tags=["typeform"])
examples = ExamplesLoader()

async def get_typeform_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "typeform")
        client = TypeformClient(api_key)
        apply_error_handler_to_client(client)
        service = TypeformService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Typeform service: {str(e)}"
        )

@router.post("/get_forms", response_model=ApiResponse)
@schema(
    input_schema_class=GetFormsParams,
    output_schema_class=GetFormsResponse,
    examples=examples["/typeform/get_forms"]
)
async def get_forms(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = GetFormsParams(**params)
    return service.get_forms(validated_params)

@router.post("/get_form", response_model=ApiResponse)
@schema(
    input_schema_class=GetFormParams,
    output_schema_class=GetFormResponse,
    examples=examples["/typeform/get_form"]
)
async def get_form(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = GetFormParams(**params)
    return service.get_form(validated_params)

@router.post("/get_form_responses", response_model=ApiResponse)
@schema(
    input_schema_class=GetFormResponsesParams,
    output_schema_class=GetFormResponsesResponse,
    examples=examples["/typeform/get_form_responses"]
)
async def get_form_responses(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = GetFormResponsesParams(**params)
    return service.get_form_responses(validated_params)

@router.post("/get_webhooks", response_model=ApiResponse)
@schema(
    input_schema_class=GetFormParams,
    output_schema_class=GetWebhooksResponse,
    examples=examples["/typeform/get_webhooks"]
)
async def get_webhooks(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = GetFormParams(**params)
    return service.get_webhooks(validated_params.form_id)

@router.post("/create_webhook", response_model=ApiResponse)
@schema(
    input_schema_class=CreateWebhookParams,
    output_schema_class=CreateWebhookResponse,
        examples=examples["/typeform/create_webhook"]
)
async def create_webhook(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = CreateWebhookParams(**params)
    return service.create_webhook(validated_params)

@router.post("/get_workspaces", response_model=ApiResponse)
@schema(
    input_schema_class=GetWorkspacesParams,
    output_schema_class=GetWorkspacesResponse,
    examples=examples["/typeform/get_workspaces"]
)
async def get_workspaces(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = GetWorkspacesParams(**params)
    return service.get_workspaces(validated_params)

@router.post("/create_form", response_model=ApiResponse)
@schema(
    input_schema_class=CreateFormParams,
    output_schema_class=CreateFormResponse,
    examples=examples["/typeform/create_form"]
)
async def create_form(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = CreateFormParams(**params)
    return service.create_form(validated_params)

@router.post("/update_form", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateFormParams,
    output_schema_class=UpdateFormResponse,
    examples=examples["/typeform/update_form"]
)
async def update_form(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = UpdateFormParams(**params)
    return service.update_form(validated_params)

@router.post("/delete_form", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteFormParams,
    output_schema_class=DeleteFormResponse,
    examples=examples["/typeform/delete_form"]
)
async def delete_form(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = DeleteFormParams(**params)
    return service.delete_form(validated_params)

@router.post("/delete_webhook", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteWebhookParams,
    output_schema_class=DeleteWebhookResponse,
    examples=examples["/typeform/delete_webhook"]
)
async def delete_webhook(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = DeleteWebhookParams(**params)
    return service.delete_webhook(validated_params)

@router.post("/create_workspace", response_model=ApiResponse)
@schema(
    input_schema_class=CreateWorkspaceParams,
    output_schema_class=CreateWorkspaceResponse,
    examples=examples["/typeform/create_workspace"]
)
async def create_workspace(
    params: Dict[str, Any] = Body(...),
    service: TypeformService = Depends(get_typeform_service)
):
    validated_params = CreateWorkspaceParams(**params)
    return service.create_workspace(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = TypeformClient(access_token=api_key)
        
        test_response = client.get_forms(page_size=1)
        
        if isinstance(test_response, dict) and "items" in test_response:
            return {"valid": True, "message": "API key is valid"}
        return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}
    

apply_error_handler_to_router(router)