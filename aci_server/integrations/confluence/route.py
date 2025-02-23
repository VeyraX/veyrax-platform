from fastapi import APIRouter, Depends, HTTPException, Query, Request as FastAPIRequest
from typing import Optional
import os
import pickle
from .service import ConfluenceService
from .client import ConfluenceClient
from .schema import (
    SpaceSchema,
    PageSchema,
    PageCreateSchema,
    PageUpdateSchema,
    PaginatedResponseSchema
)
from ..common.auth import TokenService, ConfluenceTokenRefresher

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

@router.get("/spaces", response_model=PaginatedResponseSchema)
async def get_spaces(
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Get all available spaces"""
    return service.get_spaces()

@router.get("/pages", response_model=PaginatedResponseSchema)
async def get_pages(
    space_id: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Get pages with optional filters"""
    return service.get_pages(space_id=space_id, title=title, limit=limit)

@router.get("/pages/{page_id}", response_model=PageSchema)
async def get_page(
    page_id: str,
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Get specific page by ID"""
    return service.get_page(page_id)

@router.post("/pages", response_model=PageSchema)
async def create_page(
    page: PageCreateSchema,
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Create new page"""
    return service.create_page(page)

@router.put("/pages/{page_id}", response_model=PageSchema)
async def update_page(
    page_id: str,
    update: PageUpdateSchema,
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Update existing page"""
    return service.update_page(page_id, update)

@router.get("/content", response_model=PaginatedResponseSchema)
async def search_content(
    cql: Optional[str] = Query(None),
    space_key: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    type: str = Query('page'),
    limit: int = Query(50, le=100),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Search content using CQL or filters"""
    return service.search_content(
        cql=cql,
        space_key=space_key,
        title=title,
        content_type=type,
        limit=limit
    )