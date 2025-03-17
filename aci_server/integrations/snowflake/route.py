from typing import Dict, Any, Optional
from fastapi import APIRouter, Body, HTTPException, Depends, Request as FastAPIRequest
from pydantic import ValidationError

from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_user_db_credentials
from .services import SnowflakeService
from .client import SnowflakeClient
from .schema import (
    ApiResponse, ExecuteQueryParams, GetTablesParams, 
    GetColumnsParams, GetTableInfoParams, QueryResponse, 
    TablesResponse, ColumnsResponse, TableInfoResponse,
    TestConnectionResponse, TestConnectionResult, SnowflakeConnectionParams
)

router = APIRouter(prefix="/snowflake", tags=["snowflake"])

examples = ExamplesLoader()

async def get_snowflake_service(request: FastAPIRequest):
    try:
        connection_params = await get_user_db_credentials(request, 'snowflake')
        service = SnowflakeService(connection_params)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Snowflake service: {str(e)}")


@router.post("/execute_query", response_model=ApiResponse)
@schema(input_schema_class=ExecuteQueryParams, output_schema_class=QueryResponse, examples=examples["/snowflake/execute_query"])
async def execute_query(
    params: Dict[str, Any] = Body(...),
    service: SnowflakeService = Depends(get_snowflake_service)
):
    validated_params = ExecuteQueryParams(**params)
    return service.execute_query(validated_params.query, validated_params.limit)


@router.post("/get_tables", response_model=ApiResponse)
@schema(input_schema_class=GetTablesParams, output_schema_class=TablesResponse, examples=examples["/snowflake/get_tables"])
async def get_tables(
    params: Dict[str, Any] = Body(...),
    service: SnowflakeService = Depends(get_snowflake_service)
):
    validated_params = GetTablesParams(**params)
    return service.get_tables()


@router.post("/get_columns", response_model=ApiResponse)
@schema(input_schema_class=GetColumnsParams, output_schema_class=ColumnsResponse, examples=examples["/snowflake/get_columns"])
async def get_columns(
    params: Dict[str, Any] = Body(...),
    service: SnowflakeService = Depends(get_snowflake_service)
):
    validated_params = GetColumnsParams(**params)
    return service.get_columns(validated_params.table_name)


@router.post("/test_connection", response_model=ApiResponse)
@schema(input_schema_class=SnowflakeConnectionParams, output_schema_class=TestConnectionResponse, examples=examples["/snowflake/test_connection"])
async def test_connection(
    params: Dict[str, Any] = Body(...)
):
    try:
        validated_params = SnowflakeConnectionParams(**params)
        service = SnowflakeService(validated_params.dict())
        apply_error_handler_to_service(service)
        return service.test_connection()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'SnowflakeConnectionParams'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

apply_error_handler_to_router(router)
