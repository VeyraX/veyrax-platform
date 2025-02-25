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
    ApiResponse
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

@router.post("/spaces", response_model=ApiResponse)
async def get_spaces(
    params: Dict[str, Any] = Body({}),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Get all available spaces"""
    try:
        return service.get_spaces()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pages", response_model=ApiResponse)
async def get_pages(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Get pages with optional filters"""
    try:
        filters_data = params.get('filters', {})
        filters = PageFilters(**filters_data)
        return service.get_pages(filters=filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_page", response_model=ApiResponse)
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Get specific page by ID"""
    try:
        page_id = params.get('page_id')
        if not page_id:
            raise HTTPException(status_code=400, detail="page_id is required")
        return service.get_page(page_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_page", response_model=ApiResponse)
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Create new page"""
    try:
        page_data = params.get('page', params)
        page = PageCreateSchema(**page_data)
        return service.create_page(page)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_page", response_model=ApiResponse)
async def update_page(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Update existing page"""
    try:
        page_id = params.get('page_id')
        if not page_id:
            raise HTTPException(status_code=400, detail="page_id is required")
        
        update_data = params.get('update', {})
        update = PageUpdateSchema(**update_data)
        return service.update_page(page_id, update)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=ApiResponse)
async def search_content(
    params: Dict[str, Any] = Body(...),
    service: ConfluenceService = Depends(get_confluence_service)
):
    """Search content using CQL or filters"""
    try:
        cql = params.get('cql')
        space_key = params.get('space_key')
        title = params.get('title')
        content_type = params.get('type', 'page')
        limit = params.get('limit', 50)
        
        return service.search_content(
            cql=cql,
            space_key=space_key,
            title=title,
            content_type=content_type,
            limit=limit
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))