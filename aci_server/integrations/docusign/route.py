from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.requests import Request as FastAPIRequest
from typing import Dict, Any
from .schema import (
    CreateEnvelopeParams,
    GetEnvelopeParams,
    GetDocumentParams,
    GetFormDataParams,
    RecipientViewRequest,
    ApiResponse,
    EnvelopeResponse,
    DocumentResponse,
    RecipientViewUrlResponse,
    FormDataResponse
)
from .service import DocuSignService
from .client import DocuSignClient
from ..common.auth import TokenService, DocuSignTokenRefresher
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/docusign", tags=["docusign"])
examples = ExamplesLoader()

async def get_docusign_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'docusign')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await DocuSignTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        access_token = token_data['access_token']
        client = DocuSignClient(access_token)
        apply_error_handler_to_client(client)
        
        # Get account ID from user info
        user_info = client.get_user_info()
        account_id = user_info["accounts"][0]["account_id"]
        
        service = DocuSignService(client, account_id)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize DocuSign service: {str(e)}"
        )

@router.post("/create_envelope", response_model=ApiResponse)
@schema(
    input_schema_class=CreateEnvelopeParams,
    output_schema_class=EnvelopeResponse,
    examples=examples["/docusign/create_envelope"]
)
async def create_envelope(
    params: Dict[str, Any] = Body(...),
    service: DocuSignService = Depends(get_docusign_service)
):
    validated_params = CreateEnvelopeParams(**params)
    return service.create_envelope(validated_params)

@router.post("/get_envelope", response_model=ApiResponse)
@schema(
    input_schema_class=GetEnvelopeParams,
    output_schema_class=EnvelopeResponse,
    examples=examples["/docusign/get_envelope"]
)
async def get_envelope(
    params: Dict[str, Any] = Body(...),
    service: DocuSignService = Depends(get_docusign_service)
):
    validated_params = GetEnvelopeParams(**params)
    return service.get_envelope(validated_params.envelope_id)

@router.post("/get_document", response_model=ApiResponse)
@schema(
    input_schema_class=GetDocumentParams,
    output_schema_class=DocumentResponse,
    examples=examples["/docusign/get_document"]
)
async def get_document(
    params: Dict[str, Any] = Body(...),
    service: DocuSignService = Depends(get_docusign_service)
):
    validated_params = GetDocumentParams(**params)
    return service.get_document(validated_params.envelope_id, validated_params.document_id)

@router.post("/create_view", response_model=ApiResponse)
@schema(
    input_schema_class=RecipientViewRequest,
    output_schema_class=RecipientViewUrlResponse,
    examples=examples["/docusign/create_view"]
)
async def create_recipient_view(
    params: Dict[str, Any] = Body(...),
    service: DocuSignService = Depends(get_docusign_service)
):
    envelope_id = params.pop("envelope_id", None)
    if not envelope_id:
        raise HTTPException(status_code=400, detail="envelope_id is required")
    validated_params = RecipientViewRequest(**params)
    return service.create_recipient_view(envelope_id, validated_params)

@router.post("/get_form", response_model=ApiResponse)
@schema(
    input_schema_class=GetFormDataParams,
    output_schema_class=FormDataResponse,
    examples=examples["/docusign/get_form"]
)
async def get_form_data(
    params: Dict[str, Any] = Body(...),
    service: DocuSignService = Depends(get_docusign_service)
):
    validated_params = GetFormDataParams(**params)
    return service.get_form_data(validated_params.envelope_id)

@router.post("/get_me", response_model=ApiResponse)
async def get_me(
    service: DocuSignService = Depends(get_docusign_service)
):
    return service.get_user_info()

apply_error_handler_to_router(router)
