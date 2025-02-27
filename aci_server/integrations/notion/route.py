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

router = APIRouter(prefix="/notion", tags=["notion"])

async def get_notion_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'notion')
    
    if TokenService.is_token_expired(token_data):
        try:
            token_data = await TokenService.refresh_token(request, token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
    
    client = NotionClient(token_data['access_token'])
    return NotionService(client)

@router.post("/list_databases", response_model=ApiResponse)
@input_schema(schema_class=ListDatabasesParams)
async def list_databases(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        start_cursor = params.get('start_cursor')
        max_results = params.get('max_results', 100)
        
        return service.list_databases(start_cursor=start_cursor, max_results=max_results)
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
        database_id = params.get('database_id')
        if not database_id:
            raise HTTPException(status_code=400, detail="database_id is required")
            
        return service.get_database(database_id)
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
        database_id = params.get('database_id')
        if not database_id:
            raise HTTPException(status_code=400, detail="database_id is required")
            
        filters_data = params.get('filters', {})
        start_cursor = params.get('start_cursor')
        
        filters = DatabaseFilters(**filters_data)
        return service.list_pages(database_id, start_cursor=start_cursor, filters=filters)
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
        database_id = params.get('database_id')
        if not database_id:
            raise HTTPException(status_code=400, detail="database_id is required")
            
        filter_data = params.get('filter', {})
        sorts = params.get('sorts', [])
        start_cursor = params.get('start_cursor')
        page_size = params.get('page_size', 100)
        
        return service.query_database(
            database_id, 
            filter_data=filter_data, 
            sorts=sorts, 
            start_cursor=start_cursor, 
            page_size=page_size
        )
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
        page_data = params.get('page', params)
        page = PageCreate(**page_data)
        return service.create_page(page)
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
        page_id = params.get('page_id')
        if not page_id:
            raise HTTPException(status_code=400, detail="page_id is required")
            
        return service.get_page(page_id)
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
        page_id = params.get('page_id')
        if not page_id:
            raise HTTPException(status_code=400, detail="page_id is required")
            
        page_data = params.get('page_update', {})
        page_update = PageUpdate(**page_data)
        return service.update_page(page_id, page_update)
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
        query = params.get('query', '')
        start_cursor = params.get('start_cursor')
        page_size = params.get('page_size', 100)
        sort_direction = params.get('sort_direction')
        
        filters = PageFilters(
            query=query,
            sort_direction=sort_direction,
            max_results=page_size
        )
        
        return service.search(filters=filters, start_cursor=start_cursor)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))