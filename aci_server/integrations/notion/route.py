from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest
from typing import Optional, Dict, Any
from .schema import (
    DatabaseList, Database, PageList, Page, 
    PageCreate, PageUpdate, PageFilters, DatabaseProperties, ListPagesRequest
)
from .service import NotionService
from .client import NotionClient
from ..common.auth import TokenService
import os

router = APIRouter(prefix="/notion", tags=["notion"])

async def get_notion_service(request: FastAPIRequest):
    token_data = await TokenService.get_user_token(request, 'notion')
    
    client = NotionClient(token_data['access_token'])
    return NotionService(client)

@router.get("/databases", response_model=DatabaseList)
async def list_databases(
    start_cursor: Optional[str] = None,
    max_results: Optional[int] = None,
    service: NotionService = Depends(get_notion_service)
):
    return service.list_databases(start_cursor, max_results)

@router.post("/databases/{database_id}/pages", response_model=PageList)
async def list_pages(
    database_id: str,
    request_body: ListPagesRequest,
    service: NotionService = Depends(get_notion_service)
):
    filters = PageFilters(
        filter=request_body.filter,
        sorts=request_body.sorts,
        page_size=request_body.page_size
    )
    return service.list_pages(
        database_id,
        request_body.start_cursor,
        filters
    )

@router.get("/pages/{page_id}", response_model=Page)
async def get_page(
    page_id: str,
    service: NotionService = Depends(get_notion_service)
):
    return service.get_page(page_id)

@router.post("/pages", response_model=Page)
async def create_page(
    page_data: PageCreate,
    service: NotionService = Depends(get_notion_service)
):
    return service.create_page(page_data)

@router.patch("/pages/{page_id}", response_model=Page)
async def update_page(
    page_id: str,
    page_data: PageUpdate,
    service: NotionService = Depends(get_notion_service)
):
    return service.update_page(page_id, page_data)

@router.delete("/pages/{page_id}", response_model=Page)
async def archive_page(
    page_id: str,
    service: NotionService = Depends(get_notion_service)
):
    return service.archive_page(page_id)

@router.get("/search", response_model=PageList)
async def search_pages(
    query: str,
    start_cursor: Optional[str] = None,
    max_results: Optional[int] = 100,
    sort_direction: Optional[str] = "descending",
    service: NotionService = Depends(get_notion_service)
):
    result = service.search_pages(
        query=query,
        start_cursor=start_cursor,
        page_size=max_results,
        sort_direction=sort_direction
    )
    return result

@router.get("/databases/{database_id}", response_model=DatabaseProperties)
async def get_database_properties(
    database_id: str,
    service: NotionService = Depends(get_notion_service)
):
    """Get database properties including its schema"""
    return service.get_database_properties(database_id)

@router.post("/databases/{database_id}/query", response_model=PageList)
async def query_database(
    database_id: str,
    query_params: PageFilters,
    service: NotionService = Depends(get_notion_service)
):
    """Execute a complex query against a Notion database"""
    return service.query_database(database_id, query_params)