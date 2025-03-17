from typing import Dict, Any
from fastapi import APIRouter, Body, HTTPException, Depends, Request as FastAPIRequest
from pydantic import ValidationError

from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader
from .services import PostgreSQLService
from .client import PostgreSQLClient
from .schema import (
    ApiResponse, ExecuteQueryParams, GetTablesParams, GetColumnsParams,
    QueryResponse, TablesResponse, ColumnsResponse, PostgreSQLConnectionParams,
    TestConnectionResponse, TestConnectionResult
)
from ..common.auth import get_user_db_credentials

router = APIRouter(prefix="/postgresql", tags=["postgresql"])

examples = ExamplesLoader()

async def get_postgresql_service(request: FastAPIRequest):
    try:
        connection_params = await get_user_db_credentials(request, 'postgresql')
        service = PostgreSQLService(connection_params)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize PostgreSQL service: {str(e)}")

@router.post("/execute_query", response_model=ApiResponse)
@schema(input_schema_class=ExecuteQueryParams, output_schema_class=QueryResponse, examples=examples["/postgresql/execute_query"])
async def execute_query(
    params: Dict[str, Any] = Body(...),
    service: PostgreSQLService = Depends(get_postgresql_service)
):
    validated_params = ExecuteQueryParams(**params)
    return service.execute_query(validated_params.query, validated_params.limit)

@router.post("/get_tables", response_model=ApiResponse)
@schema(input_schema_class=GetTablesParams, output_schema_class=TablesResponse, examples=examples["/postgresql/get_tables"])
async def get_tables(
    params: Dict[str, Any] = Body(...),
    service: PostgreSQLService = Depends(get_postgresql_service)
):
    validated_params = GetTablesParams(**params)
    return service.get_tables()

@router.post("/get_columns", response_model=ApiResponse)
@schema(input_schema_class=GetColumnsParams, output_schema_class=ColumnsResponse, examples=examples["/postgresql/get_columns"])
async def get_columns(
    params: Dict[str, Any] = Body(...),
    service: PostgreSQLService = Depends(get_postgresql_service)
):
    validated_params = GetColumnsParams(**params)
    return service.get_columns(validated_params.table_name)

@router.post("/test_connection", response_model=ApiResponse)
@schema(input_schema_class=PostgreSQLConnectionParams, output_schema_class=TestConnectionResponse, examples=examples["/postgresql/test_connection"])
async def test_connection(
    params: Dict[str, Any] = Body(...)
):
    try:
        validated_params = PostgreSQLConnectionParams(**params)
        service = PostgreSQLService(validated_params.dict())
        apply_error_handler_to_service(service)
        return service.test_connection()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'PostgreSQLConnectionParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

apply_error_handler_to_router(router)
