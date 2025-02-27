from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Optional, Dict, Any, List, Union
from .schema import (
    DatabaseList, PageList, Page, Database, PageCreate, PageUpdate, 
    DatabaseFilters, PageFilters, SearchResult, ApiResponse,
    ListDatabasesParams, GetDatabaseParams, ListDatabasePagesParams,
    QueryDatabaseParams, CreatePageParams, GetPageParams,
    UpdatePageParams, SearchParams
)
from .service import NotionService
from .client import NotionClient
import os
from ..common.auth import TokenService
from ..common.input_schema_decorator import input_schema
from pydantic import ValidationError

router = APIRouter(prefix="/notion", tags=["notion"])

async def get_notion_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'notion')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await TokenService.refresh_token(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = NotionClient(token_data['access_token'])
        return NotionService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Notion service: {str(e)}")

@router.post("/list_databases", response_model=ApiResponse)
@input_schema(schema_class=ListDatabasesParams)
async def list_databases(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = ListDatabasesParams(**params)
        return service.list_databases(
            start_cursor=validated_params.start_cursor, 
            max_results=validated_params.max_results
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_database", response_model=ApiResponse)
@input_schema(schema_class=GetDatabaseParams)
async def get_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = GetDatabaseParams(**params)
        return service.get_database(validated_params.database_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_database_pages", response_model=ApiResponse)
@input_schema(schema_class=ListDatabasePagesParams)
async def list_database_pages(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = ListDatabasePagesParams(**params)
        return service.list_pages(
            validated_params.database_id, 
            start_cursor=validated_params.start_cursor, 
            filters=validated_params.filters
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query_database", response_model=ApiResponse)
@input_schema(schema_class=QueryDatabaseParams)
async def query_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = QueryDatabaseParams(**params)
        return service.query_database(
            validated_params.database_id, 
            filter_data=validated_params.filter, 
            sorts=validated_params.sorts, 
            start_cursor=validated_params.start_cursor, 
            page_size=validated_params.page_size
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_page", response_model=ApiResponse)
@input_schema(schema_class=CreatePageParams)
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = CreatePageParams(**params)
        return service.create_page(validated_params.page)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_page", response_model=ApiResponse)
@input_schema(schema_class=GetPageParams)
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = GetPageParams(**params)
        return service.get_page(validated_params.page_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_page", response_model=ApiResponse)
@input_schema(schema_class=UpdatePageParams)
async def update_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = UpdatePageParams(**params)
        return service.update_page(
            validated_params.page_id, 
            validated_params.page_update
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=ApiResponse)
@input_schema(schema_class=SearchParams)
async def search(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = SearchParams(**params)
        
        filters = PageFilters(
            query=validated_params.query,
            sort_direction=validated_params.sort_direction,
            max_results=validated_params.page_size
        )
        
        return service.search(
            filters=filters, 
            start_cursor=validated_params.start_cursor
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))