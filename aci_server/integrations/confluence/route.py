from fastapi import APIRouter, Depends, HTTPException, Body, Request as FastAPIRequest
from typing import Optional, Dict, Any
import os
import pickle
from .service import ConfluenceService
from .client import ConfluenceClient
from .schema import (
    SpaceSchema,
    PageSchema,
    PageCreateSchema,
    PageUpdateSchema,
    PaginatedResponseSchema,
    PageFilters,
    ApiResponse,
    GetSpacesParams,
    GetPagesParams,
    GetPageParams,
    CreatePageParams,
    UpdatePageParams,
    SearchContentParams,
    DeletePageParams,
    SpaceList,
    PageList,
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
from pydantic import ValidationError
from ..common.utils import format_validation_error

router = APIRouter(prefix="/confluence", tags=["confluence"])

async def get_confluence_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'confluence')
    
    if TokenService.is_token_expired(token_data):
        try:
            token_data = await ConfluenceTokenRefresher.refresh(request, token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
    
    client = ConfluenceClient(token_data['access_token'])
    return ConfluenceService(client)

@router.post("/get_spaces", response_model=ApiResponse)
@schema(input_schema_class=GetSpacesParams, output_schema_class=SpacesResponse)
async def get_spaces(
    params: Dict[str, Any] = Body({}),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = GetSpacesParams(**params)
        return service.get_spaces()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetSpacesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_pages", response_model=ApiResponse)
@schema(input_schema_class=GetPagesParams, output_schema_class=PagesResponse)
async def get_pages(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = GetPagesParams(**params)
        filters = PageFilters(**validated_params.filters.dict() if validated_params.filters else {})
        return service.get_pages(filters=filters)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetPagesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_page", response_model=ApiResponse)
@schema(input_schema_class=GetPageParams, output_schema_class=PageResponse)
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = GetPageParams(**params)
        return service.get_page(validated_params.page_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetPageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_page", response_model=ApiResponse)
@schema(input_schema_class=CreatePageParams, output_schema_class=CreatePageResponse)
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = CreatePageParams(**params)
        return service.create_page(validated_params.page)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreatePageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_page", response_model=ApiResponse)
@schema(input_schema_class=UpdatePageParams, output_schema_class=UpdatePageResponse)
async def update_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = UpdatePageParams(**params)
        return service.update_page(validated_params.page_id, validated_params.update)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdatePageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_content", response_model=ApiResponse)
@schema(input_schema_class=SearchContentParams, output_schema_class=SearchContentResponse)
async def search_content(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = SearchContentParams(**params)
        return service.search_content(
            cql=validated_params.cql,
            space_key=validated_params.space_key,
            title=validated_params.title,
            content_type=validated_params.type,
            limit=validated_params.limit
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchContentParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_page", response_model=ApiResponse)
@schema(input_schema_class=DeletePageParams, output_schema_class=DeletePageResponse)
async def delete_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    try:
        validated_params = DeletePageParams(**params)
        return service.delete_page(validated_params.page_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'DeletePageParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))