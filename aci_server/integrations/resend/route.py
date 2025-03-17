from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    SendEmailParams, SendBatchEmailsParams, GetEmailParams, 
    UpdateEmailParams, CancelEmailParams, ApiResponse,
    SendEmailResponse, SendBatchEmailsResponse, GetEmailResponse,
    UpdateEmailResponse, CancelEmailResponse,
    CreateDomainParams, GetDomainParams, VerifyDomainParams,
    UpdateDomainParams, DeleteDomainParams,
    CreateDomainResponse, GetDomainResponse, VerifyDomainResponse,
    UpdateDomainResponse, ListDomainsResponse, DeleteDomainResponse,
    CreateApiKeyParams, DeleteApiKeyParams,
    CreateApiKeyResponse, ListApiKeysResponse, DeleteApiKeyResponse,
    CreateBroadcastParams, GetBroadcastParams, SendBroadcastParams, DeleteBroadcastParams,
    CreateBroadcastResponse, GetBroadcastResponse, SendBroadcastResponse, 
    DeleteBroadcastResponse, ListBroadcastsResponse,
    CreateAudienceParams, GetAudienceParams, DeleteAudienceParams,
    CreateAudienceResponse, GetAudienceResponse, DeleteAudienceResponse, ListAudiencesResponse,
    CreateContactParams, GetContactParams, UpdateContactParams, DeleteContactParams, ListContactsParams,
    CreateContactResponse, GetContactResponse, UpdateContactResponse, DeleteContactResponse, ListContactsResponse
)
from .service import ResendService
from .client import ResendClient
import os
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/resend", tags=["resend"])

examples = ExamplesLoader()  # Will automatically use /integrations/resend directory

async def get_resend_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "resend")
        client = ResendClient(api_key)
        service = ResendService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/send_email", response_model=ApiResponse)
@schema(input_schema_class=SendEmailParams, output_schema_class=SendEmailResponse, examples=examples["/resend/send_email"])
async def send_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = SendEmailParams(**params)
    return service.send_email(validated_params)

@router.post("/send_batch_emails", response_model=ApiResponse)
@schema(input_schema_class=SendBatchEmailsParams, output_schema_class=SendBatchEmailsResponse, examples=examples["/resend/send_batch_emails"])
async def send_batch_emails(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = SendBatchEmailsParams(**params)
    return service.send_batch_emails(validated_params)

@router.post("/get_email", response_model=ApiResponse)
@schema(input_schema_class=GetEmailParams, output_schema_class=GetEmailResponse, examples=examples["/resend/get_email"])
async def get_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = GetEmailParams(**params)
    return service.get_email(validated_params.email_id)

@router.post("/update_email", response_model=ApiResponse)
@schema(input_schema_class=UpdateEmailParams, output_schema_class=UpdateEmailResponse, examples=examples["/resend/update_email"])
async def update_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = UpdateEmailParams(**params)
    return service.update_email(validated_params.email_id, validated_params.scheduled_at)

@router.post("/cancel_email", response_model=ApiResponse)
@schema(input_schema_class=CancelEmailParams, output_schema_class=CancelEmailResponse, examples=examples["/resend/cancel_email"])
async def cancel_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = CancelEmailParams(**params)
    return service.cancel_email(validated_params.email_id)

@router.post("/create_domain", response_model=ApiResponse)
@schema(input_schema_class=CreateDomainParams, output_schema_class=CreateDomainResponse, examples=examples["/resend/create_domain"])
async def create_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = CreateDomainParams(**params)
    return service.create_domain(validated_params)

@router.post("/get_domain", response_model=ApiResponse)
@schema(input_schema_class=GetDomainParams, output_schema_class=GetDomainResponse, examples=examples["/resend/get_domain"])
async def get_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = GetDomainParams(**params)
    return service.get_domain(validated_params.domain_id)

@router.post("/verify_domain", response_model=ApiResponse)
@schema(input_schema_class=VerifyDomainParams, output_schema_class=VerifyDomainResponse, examples=examples["/resend/verify_domain"])
async def verify_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = VerifyDomainParams(**params)
    return service.verify_domain(validated_params.domain_id)

@router.post("/update_domain", response_model=ApiResponse)
@schema(input_schema_class=UpdateDomainParams, output_schema_class=UpdateDomainResponse, examples=examples["/resend/update_domain"])
async def update_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = UpdateDomainParams(**params)
    return service.update_domain(validated_params.domain_id, validated_params)

@router.post("/list_domains", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListDomainsResponse, examples=examples["/resend/list_domains"])
async def list_domains(
    service: ResendService = Depends(get_resend_service)
):
    return service.list_domains()

@router.post("/delete_domain", response_model=ApiResponse)
@schema(input_schema_class=DeleteDomainParams, output_schema_class=DeleteDomainResponse, examples=examples["/resend/delete_domain"])
async def delete_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = DeleteDomainParams(**params)
    return service.delete_domain(validated_params.domain_id)

@router.post("/create_api_key", response_model=ApiResponse)
@schema(input_schema_class=CreateApiKeyParams, output_schema_class=CreateApiKeyResponse, examples=examples["/resend/create_api_key"])
async def create_api_key(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = CreateApiKeyParams(**params)
    return service.create_api_key(validated_params)

@router.post("/list_api_keys", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListApiKeysResponse, examples=examples["/resend/list_api_keys"])
async def list_api_keys(
    service: ResendService = Depends(get_resend_service)
):
    return service.list_api_keys()

@router.post("/delete_api_key", response_model=ApiResponse)
@schema(input_schema_class=DeleteApiKeyParams, output_schema_class=DeleteApiKeyResponse, examples=examples["/resend/delete_api_key"])
async def delete_api_key(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = DeleteApiKeyParams(**params)
    return service.delete_api_key(validated_params.api_key_id)

@router.post("/create_broadcast", response_model=ApiResponse)
@schema(input_schema_class=CreateBroadcastParams, output_schema_class=CreateBroadcastResponse, examples=examples["/resend/create_broadcast"])
async def create_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = CreateBroadcastParams(**params)
    return service.create_broadcast(validated_params)

@router.post("/get_broadcast", response_model=ApiResponse)
@schema(input_schema_class=GetBroadcastParams, output_schema_class=GetBroadcastResponse, examples=examples["/resend/get_broadcast"])
async def get_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = GetBroadcastParams(**params)
    return service.get_broadcast(validated_params.broadcast_id)

@router.post("/send_broadcast", response_model=ApiResponse)
@schema(input_schema_class=SendBroadcastParams, output_schema_class=SendBroadcastResponse, examples=examples["/resend/send_broadcast"])
async def send_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = SendBroadcastParams(**params)
    return service.send_broadcast(validated_params.broadcast_id, validated_params.scheduled_at)

@router.post("/delete_broadcast", response_model=ApiResponse)
@schema(input_schema_class=DeleteBroadcastParams, output_schema_class=DeleteBroadcastResponse, examples=examples["/resend/delete_broadcast"])
async def delete_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = DeleteBroadcastParams(**params)
    return service.delete_broadcast(validated_params.broadcast_id)

@router.post("/list_broadcasts", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListBroadcastsResponse, examples=examples["/resend/list_broadcasts"])
async def list_broadcasts(
    service: ResendService = Depends(get_resend_service)
):
    return service.list_broadcasts()

@router.post("/create_audience", response_model=ApiResponse)
@schema(input_schema_class=CreateAudienceParams, output_schema_class=CreateAudienceResponse, examples=examples["/resend/create_audience"])
async def create_audience(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = CreateAudienceParams(**params)
    return service.create_audience(validated_params)

@router.post("/get_audience", response_model=ApiResponse)
@schema(input_schema_class=GetAudienceParams, output_schema_class=GetAudienceResponse, examples=examples["/resend/get_audience"])
async def get_audience(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = GetAudienceParams(**params)
    return service.get_audience(validated_params.audience_id)

@router.post("/delete_audience", response_model=ApiResponse)
@schema(input_schema_class=DeleteAudienceParams, output_schema_class=DeleteAudienceResponse, examples=examples["/resend/delete_audience"])
async def delete_audience(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = DeleteAudienceParams(**params)
    return service.delete_audience(validated_params.audience_id)

@router.post("/list_audiences", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListAudiencesResponse, examples=examples["/resend/list_audiences"])
async def list_audiences(
    service: ResendService = Depends(get_resend_service)
):
    return service.list_audiences()

@router.post("/create_contact", response_model=ApiResponse)
@schema(input_schema_class=CreateContactParams, output_schema_class=CreateContactResponse, examples=examples["/resend/create_contact"])
async def create_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = CreateContactParams(**params)
    return service.create_contact(validated_params)

@router.post("/get_contact", response_model=ApiResponse)
@schema(input_schema_class=GetContactParams, output_schema_class=GetContactResponse, examples=examples["/resend/get_contact"])
async def get_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = GetContactParams(**params)
    return service.get_contact(validated_params.audience_id, validated_params.contact_id)

@router.post("/update_contact", response_model=ApiResponse)
@schema(input_schema_class=UpdateContactParams, output_schema_class=UpdateContactResponse, examples=examples["/resend/update_contact"])
async def update_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = UpdateContactParams(**params)
    return service.update_contact(validated_params)

@router.post("/delete_contact", response_model=ApiResponse)
@schema(input_schema_class=DeleteContactParams, output_schema_class=DeleteContactResponse, examples=examples["/resend/delete_contact"])
async def delete_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = DeleteContactParams(**params)
    return service.delete_contact(validated_params)

@router.post("/list_contacts", response_model=ApiResponse)
@schema(input_schema_class=ListContactsParams, output_schema_class=ListContactsResponse, examples=examples["/resend/list_contacts"])
async def list_contacts(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    validated_params = ListContactsParams(**params)
    return service.list_contacts(validated_params.audience_id)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = ResendClient(api_key=api_key)
        test_response = client.list_domains()
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)
