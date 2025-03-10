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
)
from .service import NotionService
from .client import NotionClient
from ..common.auth import TokenService
from ..common.input_schema_decorator import schema
from pydantic import ValidationError
from ..common.utils import format_validation_error
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
        return NotionService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Notion service: {str(e)}")

@router.post("/list_databases", response_model=ApiResponse)
@schema(input_schema_class=ListDatabasesParams, output_schema_class=ListDatabasesResponse, examples=examples["/notion/list_databases"])
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
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListDatabasesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_database", response_model=ApiResponse)
@schema(input_schema_class=GetDatabaseParams, output_schema_class=GetDatabaseResponse, examples=examples["/notion/get_database"])
async def get_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = GetDatabaseParams(**params)
        return service.get_database(validated_params.database_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetDatabaseParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_database_pages", response_model=ApiResponse)
@schema(input_schema_class=ListDatabasePagesParams, output_schema_class=ListDatabasePagesResponse, examples=examples["/notion/list_database_pages"])
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
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ListDatabasePagesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query_database", response_model=ApiResponse)
@schema(input_schema_class=QueryDatabaseParams, output_schema_class=QueryDatabaseResponse, examples=examples["/notion/query_database"])
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
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'QueryDatabaseParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_page", response_model=ApiResponse)
@schema(input_schema_class=CreatePageParams, output_schema_class=CreatePageResponse, examples=examples["/notion/create_page"])
async def create_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
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

@router.post("/create_database", response_model=ApiResponse)
@schema(input_schema_class=CreateDatabaseParams, output_schema_class=CreateDatabaseResponse)
async def create_database(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = CreateDatabaseParams(**params)
        return service.create_database(validated_params.database)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'CreateDatabaseParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_page", response_model=ApiResponse)
@schema(input_schema_class=GetPageParams, output_schema_class=GetPageResponse, examples=examples["/notion/get_page"])
async def get_page(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
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

@router.post("/update_page", response_model=ApiResponse)
@schema(input_schema_class=UpdatePageParams, output_schema_class=UpdatePageResponse, examples=examples["/notion/update_page"])
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
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'UpdatePageParams'))
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=ApiResponse)
@schema(input_schema_class=SearchParams, output_schema_class=SearchResponse, examples=examples["/notion/search"])
async def search(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = SearchParams(**params)
        return service.search(
            filters=PageFilters(
                query=validated_params.query,
                sort_direction=validated_params.sort_direction
            ),
            start_cursor=validated_params.start_cursor
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SearchParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/append_block_children", response_model=ApiResponse)
@schema(input_schema_class=AppendBlockChildrenParams, output_schema_class=AppendBlockChildrenResponse, examples=examples["/notion/append_block_children"])
async def append_block_children(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = AppendBlockChildrenParams(**params)
        return service.append_block_children(validated_params.block_id, validated_params.children)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'AppendBlockChildrenParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_users", response_model=ApiResponse)
@schema(input_schema_class=GetUsersParams, output_schema_class=GetUsersResponse)#, examples=examples["/notion/get_users"] if "/notion/get_users" in examples else None)
async def get_users(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = GetUsersParams(**params)
        return service.get_users(validated_params.start_cursor, validated_params.page_size)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetUsersParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_user", response_model=ApiResponse)
@schema(input_schema_class=GetUserParams, output_schema_class=GetUserResponse)#, examples=examples["/notion/get_user"] if "/notion/get_user" in examples else None)
async def get_user(
    params: Dict[str, Any] = Body(...),
    service: NotionService = Depends(get_notion_service)
):
    try:
        validated_params = GetUserParams(**params)
        return service.get_user(validated_params.user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetUserParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))