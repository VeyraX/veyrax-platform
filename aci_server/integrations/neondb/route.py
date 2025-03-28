from typing import Dict, Any
from fastapi import APIRouter, Body, HTTPException, Depends, Request as FastAPIRequest

from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader
from ..postgresql.services import PostgreSQLService
from ..postgresql.schema import (
    ApiResponse, ExecuteQueryParams, GetTablesParams, GetColumnsParams, 
    QueryResponse, TablesResponse, ColumnsResponse, PostgreSQLConnectionParams,
    TestConnectionResponse
)
from ..common.auth import get_user_db_credentials

router = APIRouter(prefix="/neondb", tags=["neondb"])

examples = ExamplesLoader()

async def get_neondb_service(request: FastAPIRequest):
    try:
        connection_params = await get_user_db_credentials(request, 'neondb')
        service = PostgreSQLService(connection_params)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize NeonDB service: {str(e)}")

@router.post("/execute_query", response_model=ApiResponse)
@schema(input_schema_class=ExecuteQueryParams, output_schema_class=QueryResponse, examples=examples["/neondb/execute_query"])
async def execute_query(
    params: Dict[str, Any] = Body(...),
    service: PostgreSQLService = Depends(get_neondb_service)
):
    validated_params = ExecuteQueryParams(**params)
    return service.execute_query(validated_params.query, validated_params.limit)

@router.post("/get_tables", response_model=ApiResponse)
@schema(input_schema_class=GetTablesParams, output_schema_class=TablesResponse, examples=examples["/neondb/get_tables"])
async def get_tables(
    params: Dict[str, Any] = Body(...),
    service: PostgreSQLService = Depends(get_neondb_service)
):
    validated_params = GetTablesParams(**params)
    return service.get_tables()

@router.post("/get_columns", response_model=ApiResponse)
@schema(input_schema_class=GetColumnsParams, output_schema_class=ColumnsResponse, examples=examples["/neondb/get_columns"])
async def get_columns(
    params: Dict[str, Any] = Body(...),
    service: PostgreSQLService = Depends(get_neondb_service)
):
    validated_params = GetColumnsParams(**params)
    return service.get_columns(validated_params.table_name)

@router.post("/test_connection", response_model=ApiResponse)
@schema(input_schema_class=PostgreSQLConnectionParams, output_schema_class=TestConnectionResponse, examples=examples["/neondb/test_connection"])
async def test_connection(
    params: Dict[str, Any] = Body(...)
):
    try:
        validated_params = PostgreSQLConnectionParams(**params)
        service = PostgreSQLService(validated_params.dict())
        apply_error_handler_to_service(service)
        return service.test_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

apply_error_handler_to_router(router)
