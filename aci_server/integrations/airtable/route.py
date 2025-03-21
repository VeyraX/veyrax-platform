from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    ListRecordsParams, GetRecordParams, CreateRecordParams, CreateRecordsParams,
    UpdateRecordParams, UpdateRecordsParams, DeleteRecordParams, DeleteRecordsParams,
    UploadAttachmentParams, SyncCSVParams, CreateFieldParams, UpdateFieldParams,
    CreateTableParams, UpdateTableParams,
    ListRecordsResponse, GetRecordResponse, CreateRecordResponse, CreateRecordsResponse,
    UpdateRecordResponse, UpdateRecordsResponse, DeleteRecordResponse, DeleteRecordsResponse,
    UploadAttachmentResponse, SyncCSVResponse, CreateFieldResponse, UpdateFieldResponse,
    CreateTableResponse, UpdateTableResponse,
    ApiResponse,
    ListBasesParams, GetBaseSchemaParams, CreateBaseParams,
    ListBasesResponse, GetBaseSchemaResponse, CreateBaseResponse,
    ListWebhooksParams, CreateWebhookParams, DeleteWebhookParams, ListWebhookPayloadsParams,
    ListWebhooksResponse, CreateWebhookResponse, DeleteWebhookResponse, ListWebhookPayloadsResponse,
    UserInfo, GetUserInfoResponse
)
from .service import AirtableService
from .client import AirtableClient
from ..common.auth import TokenService, AirtableTokenRefresher
from ..common.input_schema_decorator import schema
from ..common.utils import (
    apply_error_handler_to_service, 
    apply_error_handler_to_router, 
    apply_error_handler_to_client
)
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/airtable", tags=["airtable"])
examples = ExamplesLoader()

async def get_airtable_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'airtable')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await AirtableTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")
        
        access_token = token_data['access_token']
        client = AirtableClient(access_token)
        apply_error_handler_to_client(client)
        service = AirtableService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Airtable service: {str(e)}"
        )

@router.post("/list_records", response_model=ApiResponse)
@schema(
    input_schema_class=ListRecordsParams,
    output_schema_class=ListRecordsResponse,
    examples=examples["/airtable/list_records"]
)
async def list_records(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = ListRecordsParams(**params)
    return service.list_records(validated_params)

@router.post("/get_record", response_model=ApiResponse)
@schema(
    input_schema_class=GetRecordParams,
    output_schema_class=GetRecordResponse,
    examples=examples["/airtable/get_record"]
)
async def get_record(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = GetRecordParams(**params)
    return service.get_record(validated_params)

@router.post("/create_record", response_model=ApiResponse)
@schema(
    input_schema_class=CreateRecordParams,
    output_schema_class=CreateRecordResponse,
    examples=examples["/airtable/create_record"]
)
async def create_record(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = CreateRecordParams(**params)
    return service.create_record(validated_params)

@router.post("/create_records", response_model=ApiResponse)
@schema(
    input_schema_class=CreateRecordsParams,
    output_schema_class=CreateRecordsResponse,
    examples=examples["/airtable/create_records"]
)
async def create_records(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = CreateRecordsParams(**params)
    return service.create_records(validated_params)

@router.post("/update_record", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateRecordParams,
    output_schema_class=UpdateRecordResponse,
    examples=examples["/airtable/update_record"]
)
async def update_record(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = UpdateRecordParams(**params)
    return service.update_record(validated_params)

@router.post("/update_records", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateRecordsParams,
    output_schema_class=UpdateRecordsResponse,
    examples=examples["/airtable/update_records"]
)
async def update_records(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = UpdateRecordsParams(**params)
    return service.update_records(validated_params)

@router.post("/delete_record", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteRecordParams,
    output_schema_class=DeleteRecordResponse,
    examples=examples["/airtable/delete_record"]
)
async def delete_record(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = DeleteRecordParams(**params)
    return service.delete_record(validated_params)

@router.post("/delete_records", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteRecordsParams,
    output_schema_class=DeleteRecordsResponse,
    examples=examples["/airtable/delete_records"]
)
async def delete_records(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = DeleteRecordsParams(**params)
    return service.delete_records(validated_params)

@router.post("/upload_attachment", response_model=ApiResponse)
@schema(
    input_schema_class=UploadAttachmentParams,
    output_schema_class=UploadAttachmentResponse,
    examples=examples["/airtable/upload_attachment"]
)
async def upload_attachment(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = UploadAttachmentParams(**params)
    return service.upload_attachment(validated_params)

@router.post("/sync_csv", response_model=ApiResponse)
@schema(
    input_schema_class=SyncCSVParams,
    output_schema_class=SyncCSVResponse,
    examples=examples["/airtable/sync_csv"]
)
async def sync_csv(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = SyncCSVParams(**params)
    return service.sync_csv(validated_params)

# New field management endpoints
@router.post("/create_field", response_model=ApiResponse)
@schema(
    input_schema_class=CreateFieldParams,
    output_schema_class=CreateFieldResponse,
    examples=examples["/airtable/create_field"]
)
async def create_field(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = CreateFieldParams(**params)
    return service.create_field(validated_params)

@router.post("/update_field", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateFieldParams,
    output_schema_class=UpdateFieldResponse,
    examples=examples["/airtable/update_field"]
)
async def update_field(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = UpdateFieldParams(**params)
    return service.update_field(validated_params)

# Table management endpoints
@router.post("/create_table", response_model=ApiResponse)
@schema(
    input_schema_class=CreateTableParams,
    output_schema_class=CreateTableResponse,
    examples=examples["/airtable/create_table"]
)
async def create_table(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = CreateTableParams(**params)
    return service.create_table(validated_params)

@router.post("/update_table", response_model=ApiResponse)
@schema(
    input_schema_class=UpdateTableParams,
    output_schema_class=UpdateTableResponse,
    examples=examples["/airtable/update_table"]
)
async def update_table(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = UpdateTableParams(**params)
    return service.update_table(validated_params)

# Base management endpoints
@router.post("/list_bases", response_model=ApiResponse)
@schema(
    input_schema_class=ListBasesParams,
    output_schema_class=ListBasesResponse,
    examples=examples["/airtable/list_bases"]
)
async def list_bases(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = ListBasesParams(**params)
    return service.list_bases(validated_params)

@router.post("/get_base_schema", response_model=ApiResponse)
@schema(
    input_schema_class=GetBaseSchemaParams,
    output_schema_class=GetBaseSchemaResponse,
    examples=examples["/airtable/get_base_schema"]
)
async def get_base_schema(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = GetBaseSchemaParams(**params)
    return service.get_base_schema(validated_params)

@router.post("/create_base", response_model=ApiResponse)
@schema(
    input_schema_class=CreateBaseParams,
    output_schema_class=CreateBaseResponse,
    examples=examples["/airtable/create_base"]
)
async def create_base(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = CreateBaseParams(**params)
    return service.create_base(validated_params)

# Webhook management endpoints
@router.post("/list_webhooks", response_model=ApiResponse)
@schema(
    input_schema_class=ListWebhooksParams,
    output_schema_class=ListWebhooksResponse,
    examples=examples["/airtable/list_webhooks"]
)
async def list_webhooks(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = ListWebhooksParams(**params)
    return service.list_webhooks(validated_params)

@router.post("/create_webhook", response_model=ApiResponse)
@schema(
    input_schema_class=CreateWebhookParams,
    output_schema_class=CreateWebhookResponse,
    examples=examples["/airtable/create_webhook"]
)
async def create_webhook(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = CreateWebhookParams(**params)
    return service.create_webhook(validated_params)

@router.post("/delete_webhook", response_model=ApiResponse)
@schema(
    input_schema_class=DeleteWebhookParams,
    output_schema_class=DeleteWebhookResponse,
    examples=examples["/airtable/delete_webhook"]
)
async def delete_webhook(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = DeleteWebhookParams(**params)
    return service.delete_webhook(validated_params)

@router.post("/list_webhook_payloads", response_model=ApiResponse)
@schema(
    input_schema_class=ListWebhookPayloadsParams,
    output_schema_class=ListWebhookPayloadsResponse,
    examples=examples["/airtable/list_webhook_payloads"]
)
async def list_webhook_payloads(
    params: Dict[str, Any] = Body(...),
    service: AirtableService = Depends(get_airtable_service)
):
    validated_params = ListWebhookPayloadsParams(**params)
    return service.list_webhook_payloads(validated_params)

# User info endpoint
@router.post("/get_user_info", response_model=ApiResponse)
@schema(
    output_schema_class=GetUserInfoResponse,
    examples=examples["/airtable/get_user_info"]
)
async def get_user_info(
    service: AirtableService = Depends(get_airtable_service)
):
    return service.get_user_info()

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    service = AirtableService(None)
    return service.validate_key(params)


apply_error_handler_to_router(router)