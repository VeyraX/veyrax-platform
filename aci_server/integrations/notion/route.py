from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import (
    PageFilters, ApiResponse,
    ListDatabasesParams, GetDatabaseParams, ListDatabasePagesParams,
    QueryDatabaseParams, CreatePageParams, GetPageParams,
    UpdatePageParams, SearchParams,
    ListDatabasesResponse, GetDatabaseResponse, ListDatabasePagesResponse,
    QueryDatabaseResponse, CreatePageResponse, GetPageResponse,
    UpdatePageResponse, SearchResponse, CreateDatabaseParams, CreateDatabaseResponse,
    AppendBlockChildrenParams, AppendBlockChildrenResponse, CreatePageWithDatabaseParams,
    GetUsersParams, GetUsersResponse, GetUserParams, GetUserResponse,
    AppendMediaParams, AppendMediaResponse, UpdateDatabaseParams, UpdateDatabaseResponse,
)
from .service import NotionService
from .client import NotionClient
from ..common.auth import TokenService
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader



router = APIRouter(prefix="/notion", tags=["notion"])

examples = ExamplesLoader()

async def get_notion_service(request: FastAPIRequest):
    try:
        token_data = await TokenService.get_user_token(request, 'notion')
        
        if TokenService.is_token_expired(token_data):
            try:
                token_data = await TokenService.refresh_token(request, token_data)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        client = NotionClient(token_data['access_token'])
        apply_error_handler_to_client(client)
        service = NotionService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Notion service: {str(e)}")

@router.post("/list_databases", response_model=ApiResponse)
@schema(input_schema_class=ListDatabasesParams, output_schema_class=ListDatabasesResponse, examples=examples["/notion/list_databases"])
async def list_databases(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = ListDatabasesParams(**params)
    return service.list_databases(
        start_cursor=validated_params.start_cursor, 
        max_results=validated_params.max_results
    )

@router.post("/get_database", response_model=ApiResponse)
@schema(input_schema_class=GetDatabaseParams, output_schema_class=GetDatabaseResponse, examples=examples["/notion/get_database"])
async def get_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = GetDatabaseParams(**params)
    return service.get_database(validated_params.database_id)

@router.post("/list_database_pages", response_model=ApiResponse)
@schema(input_schema_class=ListDatabasePagesParams, output_schema_class=ListDatabasePagesResponse, examples=examples["/notion/list_database_pages"])
async def list_database_pages(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = ListDatabasePagesParams(**params)
    return service.list_pages(
        validated_params.database_id, 
        start_cursor=validated_params.start_cursor, 
        filters=validated_params.filters
    )

@router.post("/query_database", response_model=ApiResponse)
@schema(input_schema_class=QueryDatabaseParams, output_schema_class=QueryDatabaseResponse, examples=examples["/notion/query_database"])
async def query_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = QueryDatabaseParams(**params)
    return service.query_database(
        validated_params.database_id, 
        filter_data=validated_params.filter, 
        sorts=validated_params.sorts, 
        start_cursor=validated_params.start_cursor, 
        page_size=validated_params.page_size
    )

@router.post("/create_page", response_model=ApiResponse)
@schema(input_schema_class=CreatePageParams, output_schema_class=CreatePageResponse, examples=examples["/notion/create_page"])
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = CreatePageParams(**params)
    return service.create_page(validated_params.page)

@router.post("/create_database", response_model=ApiResponse)
@schema(input_schema_class=CreateDatabaseParams, output_schema_class=CreateDatabaseResponse)
async def create_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = CreateDatabaseParams(**params)
    return service.create_database(validated_params.database)

@router.post("/update_database", response_model=ApiResponse)
@schema(input_schema_class=UpdateDatabaseParams, output_schema_class=UpdateDatabaseResponse)
async def update_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = UpdateDatabaseParams(**params)
    return service.update_database(
        validated_params.database_id, 
        validated_params.database_update
    )

@router.post("/get_page", response_model=ApiResponse)
@schema(input_schema_class=GetPageParams, output_schema_class=GetPageResponse, examples=examples["/notion/get_page"])
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = GetPageParams(**params)
    return service.get_page(validated_params.page_id)

@router.post("/update_page", response_model=ApiResponse)
@schema(input_schema_class=UpdatePageParams, output_schema_class=UpdatePageResponse, examples=examples["/notion/update_page"])
async def update_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = UpdatePageParams(**params)
    return service.update_page(
        validated_params.page_id, 
        validated_params.page_update
    )

@router.post("/search", response_model=ApiResponse)
@schema(input_schema_class=SearchParams, output_schema_class=SearchResponse, examples=examples["/notion/search"])
async def search(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = SearchParams(**params)
    return service.search(
        filters=PageFilters(
            query=validated_params.query,
            sort_direction=validated_params.sort_direction,
            max_results=validated_params.page_size
        ),
        start_cursor=validated_params.start_cursor
    )

@router.post("/append_block_children", response_model=ApiResponse)
@schema(input_schema_class=AppendBlockChildrenParams, output_schema_class=AppendBlockChildrenResponse, examples=examples["/notion/append_block_children"])
async def append_block_children(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = AppendBlockChildrenParams(**params)
    return service.append_block_children(validated_params.block_id, validated_params.children)

@router.post("/append_media", response_model=ApiResponse)
@schema(input_schema_class=AppendMediaParams, output_schema_class=AppendMediaResponse, examples=examples["/notion/append_media"])
async def append_media(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = AppendMediaParams(**params)
    return service.append_media(
        validated_params.block_id,
        validated_params.media_type,
        validated_params.url,
        validated_params.caption,
        validated_params.name
    )

@router.post("/create_page_with_database", response_model=ApiResponse)
@schema(input_schema_class=CreatePageWithDatabaseParams, output_schema_class=CreatePageResponse)
async def create_page_with_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = CreatePageWithDatabaseParams(**params)
    return service.create_page_with_database(validated_params.page, validated_params.database)

@router.post("/get_users", response_model=ApiResponse)
@schema(input_schema_class=GetUsersParams, output_schema_class=GetUsersResponse)
async def get_users(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = GetUsersParams(**params)
    return service.get_users(validated_params.start_cursor, validated_params.page_size)

@router.post("/get_user", response_model=ApiResponse)
@schema(input_schema_class=GetUserParams, output_schema_class=GetUserResponse)
async def get_user(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    validated_params = GetUserParams(**params)
    return service.get_user(validated_params.user_id)

@router.post("/debug_append_block_children", response_model=Dict[str, Any])
async def debug_append_block_children(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    """
    Debug endpoint to examine how blocks are serialized before sending to Notion API.
    Does not actually make the API call, just returns the serialized children for inspection.
    """
    try:
        # Extract the same parameters as the real endpoint
        block_id = params.get("block_id", "")
        children = params.get("children", [])
        
        # Process blocks through serializer but don't send to API
        serializable_children = []
        for child in children:
            serialized_child = service._serialize_block(child)
            serializable_children.append(serialized_child)
            
        # Return both original and serialized for comparison
        return {
            "status": "debug_only",
            "original_params": params,
            "serialized_children": serializable_children,
            "notion_api_payload": {"children": serializable_children}
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

apply_error_handler_to_router(router)