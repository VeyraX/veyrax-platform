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
from ..common.utils import format_validation_error

router = APIRouter(prefix="/resend", tags=["resend"])

async def get_resend_service(request: FastAPIRequest):
    try:
        api_key = await validate_provider_api_key(request, "resend")
        client = ResendClient(api_key)
        return ResendService(client)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.post("/send_email", response_model=ApiResponse)
@schema(input_schema_class=SendEmailParams, output_schema_class=SendEmailResponse)
async def send_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = SendEmailParams(**params)
        return service.send_email(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SendEmailParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_batch_emails", response_model=ApiResponse)
@schema(input_schema_class=SendBatchEmailsParams, output_schema_class=SendBatchEmailsResponse)
async def send_batch_emails(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = SendBatchEmailsParams(**params)
        return service.send_batch_emails(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SendBatchEmailsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_email", response_model=ApiResponse)
@schema(input_schema_class=GetEmailParams, output_schema_class=GetEmailResponse)
async def get_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = GetEmailParams(**params)
        return service.get_email(validated_params.email_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetEmailParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_email", response_model=ApiResponse)
@schema(input_schema_class=UpdateEmailParams, output_schema_class=UpdateEmailResponse)
async def update_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = UpdateEmailParams(**params)
        return service.update_email(validated_params.email_id, validated_params.scheduled_at)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateEmailParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel_email", response_model=ApiResponse)
@schema(input_schema_class=CancelEmailParams, output_schema_class=CancelEmailResponse)
async def cancel_email(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = CancelEmailParams(**params)
        return service.cancel_email(validated_params.email_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CancelEmailParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_domain", response_model=ApiResponse)
@schema(input_schema_class=CreateDomainParams, output_schema_class=CreateDomainResponse)
async def create_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = CreateDomainParams(**params)
        return service.create_domain(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateDomainParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_domain", response_model=ApiResponse)
@schema(input_schema_class=GetDomainParams, output_schema_class=GetDomainResponse)
async def get_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = GetDomainParams(**params)
        return service.get_domain(validated_params.domain_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetDomainParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify_domain", response_model=ApiResponse)
@schema(input_schema_class=VerifyDomainParams, output_schema_class=VerifyDomainResponse)
async def verify_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = VerifyDomainParams(**params)
        return service.verify_domain(validated_params.domain_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'VerifyDomainParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_domain", response_model=ApiResponse)
@schema(input_schema_class=UpdateDomainParams, output_schema_class=UpdateDomainResponse)
async def update_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = UpdateDomainParams(**params)
        return service.update_domain(validated_params.domain_id, validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateDomainParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_domains", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListDomainsResponse)
async def list_domains(
    service: ResendService = Depends(get_resend_service)
):
    try:
        return service.list_domains()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_domain", response_model=ApiResponse)
@schema(input_schema_class=DeleteDomainParams, output_schema_class=DeleteDomainResponse)
async def delete_domain(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = DeleteDomainParams(**params)
        return service.delete_domain(validated_params.domain_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteDomainParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_api_key", response_model=ApiResponse)
@schema(input_schema_class=CreateApiKeyParams, output_schema_class=CreateApiKeyResponse)
async def create_api_key(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = CreateApiKeyParams(**params)
        return service.create_api_key(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateApiKeyParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_api_keys", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListApiKeysResponse)
async def list_api_keys(
    service: ResendService = Depends(get_resend_service)
):
    try:
        return service.list_api_keys()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_api_key", response_model=ApiResponse)
@schema(input_schema_class=DeleteApiKeyParams, output_schema_class=DeleteApiKeyResponse)
async def delete_api_key(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = DeleteApiKeyParams(**params)
        return service.delete_api_key(validated_params.api_key_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteApiKeyParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_broadcast", response_model=ApiResponse)
@schema(input_schema_class=CreateBroadcastParams, output_schema_class=CreateBroadcastResponse)
async def create_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = CreateBroadcastParams(**params)
        return service.create_broadcast(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateBroadcastParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_broadcast", response_model=ApiResponse)
@schema(input_schema_class=GetBroadcastParams, output_schema_class=GetBroadcastResponse)
async def get_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = GetBroadcastParams(**params)
        return service.get_broadcast(validated_params.broadcast_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetBroadcastParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_broadcast", response_model=ApiResponse)
@schema(input_schema_class=SendBroadcastParams, output_schema_class=SendBroadcastResponse)
async def send_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = SendBroadcastParams(**params)
        return service.send_broadcast(validated_params.broadcast_id, validated_params.scheduled_at)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SendBroadcastParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_broadcast", response_model=ApiResponse)
@schema(input_schema_class=DeleteBroadcastParams, output_schema_class=DeleteBroadcastResponse)
async def delete_broadcast(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = DeleteBroadcastParams(**params)
        return service.delete_broadcast(validated_params.broadcast_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteBroadcastParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_broadcasts", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListBroadcastsResponse)
async def list_broadcasts(
    service: ResendService = Depends(get_resend_service)
):
    try:
        return service.list_broadcasts()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_audience", response_model=ApiResponse)
@schema(input_schema_class=CreateAudienceParams, output_schema_class=CreateAudienceResponse)
async def create_audience(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = CreateAudienceParams(**params)
        return service.create_audience(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateAudienceParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_audience", response_model=ApiResponse)
@schema(input_schema_class=GetAudienceParams, output_schema_class=GetAudienceResponse)
async def get_audience(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = GetAudienceParams(**params)
        return service.get_audience(validated_params.audience_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetAudienceParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_audience", response_model=ApiResponse)
@schema(input_schema_class=DeleteAudienceParams, output_schema_class=DeleteAudienceResponse)
async def delete_audience(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = DeleteAudienceParams(**params)
        return service.delete_audience(validated_params.audience_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteAudienceParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_audiences", response_model=ApiResponse)
@schema(input_schema_class=None, output_schema_class=ListAudiencesResponse)
async def list_audiences(
    service: ResendService = Depends(get_resend_service)
):
    try:
        return service.list_audiences()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_contact", response_model=ApiResponse)
@schema(input_schema_class=CreateContactParams, output_schema_class=CreateContactResponse)
async def create_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = CreateContactParams(**params)
        return service.create_contact(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateContactParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_contact", response_model=ApiResponse)
@schema(input_schema_class=GetContactParams, output_schema_class=GetContactResponse)
async def get_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = GetContactParams(**params)
        return service.get_contact(validated_params.audience_id, validated_params.contact_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetContactParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_contact", response_model=ApiResponse)
@schema(input_schema_class=UpdateContactParams, output_schema_class=UpdateContactResponse)
async def update_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = UpdateContactParams(**params)
        return service.update_contact(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdateContactParams'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_contact", response_model=ApiResponse)
@schema(input_schema_class=DeleteContactParams, output_schema_class=DeleteContactResponse)
async def delete_contact(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = DeleteContactParams(**params)
        return service.delete_contact(validated_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeleteContactParams'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_contacts", response_model=ApiResponse)
@schema(input_schema_class=ListContactsParams, output_schema_class=ListContactsResponse)
async def list_contacts(
    params: Dict[str, Any] = Body(...),
    service: ResendService = Depends(get_resend_service)
):
    try:
        validated_params = ListContactsParams(**params)
        return service.list_contacts(validated_params.audience_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListContactsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
