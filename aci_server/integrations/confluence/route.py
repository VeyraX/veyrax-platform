from fastapi import APIRouter, Depends, HTTPException, Body, Request as FastAPIRequest
from typing import Optional, Dict, Any
import os
import pickle
from .service import ConfluenceService
from .client import ConfluenceClient
from .schema import (
    PageFilters,
    ApiResponse,
    GetSpacesParams,
    GetPagesParams,
    GetPageParams,
    CreatePageParams,
    UpdatePageParams,
    SearchContentParams,
    DeletePageParams,
    SpacesResponse,
    PagesResponse,
    PageResponse,
    CreatePageResponse,
    UpdatePageResponse,
    SearchContentResponse,
    DeletePageResponse
)
from ..common.auth import TokenService, ConfluenceTokenRefresher
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/confluence", tags=["confluence"])

examples = ExamplesLoader()

async def get_confluence_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'confluence')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await ConfluenceTokenRefresher.refresh(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = ConfluenceClient(token_data['access_token'])
        service = ConfluenceService(client)
        
        apply_error_handler_to_service(service)
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to initialize Confluence service: {str(e)}"
        )


@router.post("/get_spaces", response_model=ApiResponse)
@schema(input_schema_class=GetSpacesParams, output_schema_class=SpacesResponse, examples=examples["/confluence/spaces"])
async def get_spaces(
    params: Dict[str, Any] = Body({}),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = GetSpacesParams(**params)
    return service.get_spaces()
    

@router.post("/get_pages", response_model=ApiResponse)
@schema(input_schema_class=GetPagesParams, output_schema_class=PagesResponse, examples=examples["/confluence/pages"])
async def get_pages(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = GetPagesParams(**params)
    filters = PageFilters(**validated_params.filters.dict() if validated_params.filters else {})
    return service.get_pages(filters=filters)

@router.post("/get_page", response_model=ApiResponse)
@schema(input_schema_class=GetPageParams, output_schema_class=PageResponse, examples=examples["/confluence/get_page"])
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = GetPageParams(**params)
    return service.get_page(validated_params.page_id)

@router.post("/create_page", response_model=ApiResponse)
@schema(input_schema_class=CreatePageParams, output_schema_class=CreatePageResponse, examples=examples["/confluence/create_page"])
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = CreatePageParams(**params)
    return service.create_page(validated_params.page)

@router.post("/update_page", response_model=ApiResponse)
@schema(input_schema_class=UpdatePageParams, output_schema_class=UpdatePageResponse, examples=examples["/confluence/update_page"])
async def update_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = UpdatePageParams(**params)
    return service.update_page(validated_params.page_id, validated_params.update)

@router.post("/search_content", response_model=ApiResponse)
@schema(input_schema_class=SearchContentParams, output_schema_class=SearchContentResponse, examples=examples["/confluence/search"])
async def search_content(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = SearchContentParams(**params)
    return service.search_content(
        cql=validated_params.cql,
        space_key=validated_params.space_key,
        title=validated_params.title,
        content_type=validated_params.type,
        limit=validated_params.limit
    )

@router.post("/delete_page", response_model=ApiResponse)
@schema(input_schema_class=DeletePageParams, output_schema_class=DeletePageResponse, examples=examples["/confluence/delete_page"])
async def delete_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    validated_params = DeletePageParams(**params)
    return service.delete_page(validated_params.page_id)

apply_error_handler_to_router(router)