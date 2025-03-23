from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    ApiResponse, GetDocumentParams, CreateDocumentParams,
    BatchUpdateParams, InsertTextParams, ReplaceAllTextParams,
    SearchTextParams, ListDocumentsParams, GetDocumentResponse,
    CreateDocumentResponse, BatchUpdateResponse, InsertTextResponse,
    ReplaceAllTextResponse, SearchTextResponse, ListDocumentsResponse,
    GetDocumentContentParams, GetDocumentContentResponse
)
from .service import GoogleDocsService
from .client import GoogleDocsClient
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from ..common.auth import TokenService, GoogleTokenRefresher
from ..common.input_schema_decorator import schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/google_docs", tags=["google_docs"])

examples = ExamplesLoader()

async def get_docs_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'google-docs')
        print(f"token data: {token_data}")
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await GoogleTokenRefresher.refresh(request, token_data)
                print(f"new token data: {token_data}")
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
            
        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=token_data['scopes'].split(',')
        )
        
        client = GoogleDocsClient(creds)
        apply_error_handler_to_client(client)
        service = GoogleDocsService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Docs service: {str(e)}")


@router.post("/get_document", response_model=ApiResponse)
@schema(input_schema_class=GetDocumentParams, output_schema_class=GetDocumentResponse, examples=examples["/google_docs/get_document"])
async def get_document(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = GetDocumentParams(**params)
    return service.get_document(validated_params.document_id)

@router.post("/create_document", response_model=ApiResponse)
@schema(input_schema_class=CreateDocumentParams, output_schema_class=CreateDocumentResponse, examples=examples["/google_docs/create_document"])
async def create_document(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = CreateDocumentParams(**params)
    return service.create_document(validated_params.title)

@router.post("/batch_update", response_model=ApiResponse)
@schema(input_schema_class=BatchUpdateParams, output_schema_class=BatchUpdateResponse, examples=examples["/google_docs/batch_update"])
async def batch_update(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = BatchUpdateParams(**params)
    return service.batch_update(validated_params.document_id, validated_params.requests)

@router.post("/insert_text", response_model=ApiResponse)
@schema(input_schema_class=InsertTextParams, output_schema_class=InsertTextResponse, examples=examples["/google_docs/insert_text"])
async def insert_text(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = InsertTextParams(**params)
    return service.insert_text(
        validated_params.document_id, 
        validated_params.location_index, 
        validated_params.text
    )

@router.post("/replace_all_text", response_model=ApiResponse)
@schema(input_schema_class=ReplaceAllTextParams, output_schema_class=ReplaceAllTextResponse, examples=examples["/google_docs/replace_all_text"])
async def replace_all_text(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = ReplaceAllTextParams(**params)
    return service.replace_all_text(
        validated_params.document_id, 
        validated_params.text_to_replace, 
        validated_params.replace_text
    )

@router.post("/search_text", response_model=ApiResponse)
@schema(input_schema_class=SearchTextParams, output_schema_class=SearchTextResponse, examples=examples["/google_docs/search_text"])
async def search_text(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = SearchTextParams(**params)
    return service.search_text(
        validated_params.document_id, 
        validated_params.search_term,
        validated_params.case_sensitive
    )

@router.post("/get_document_content", response_model=ApiResponse)
@schema(input_schema_class=GetDocumentContentParams, output_schema_class=GetDocumentContentResponse, examples=examples["/google_docs/get_document_content"])
async def get_document_content(
    params: Dict[str, Any] = Body(...),
    service: GoogleDocsService = Depends(get_docs_service)
):
    validated_params = GetDocumentContentParams(**params)
    return service.get_document_content(validated_params.document_id)


apply_error_handler_to_router(router)