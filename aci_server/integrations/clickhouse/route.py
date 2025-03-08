from typing import Dict, Any, Optional
from fastapi import APIRouter, Body, HTTPException, Depends, Request as FastAPIRequest
from pydantic import ValidationError

from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error
from ..common.examples_handler import ExamplesLoader
from ..common.auth import get_user_db_credentials
from .services import ClickHouseService
from .client import ClickHouseClient
from .schema import (
    ApiResponse, ExecuteQueryParams, GetDatabasesParams, GetTablesParams, 
    GetColumnsParams, QueryResponse, DatabasesResponse, 
    TablesResponse, ColumnsResponse, ClickHouseConnectionParams,
    TestConnectionResponse, TestConnectionResult
)

router = APIRouter(prefix="/clickhouse", tags=["clickhouse"])

examples = ExamplesLoader()

async def get_clickhouse_service(request: FastAPIRequest):
    try:
        connection_params = await get_user_db_credentials(request, 'clickhouse')
        
        if 'secure' not in connection_params:
            connection_params['secure'] = True
            
        return ClickHouseService(connection_params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize ClickHouse service: {str(e)}")


@router.post("/execute_query", response_model=ApiResponse)
@schema(input_schema_class=ExecuteQueryParams, output_schema_class=QueryResponse, examples=examples["/clickhouse/execute_query"])
async def execute_query(
    params: Dict[str, Any] = Body(...),
    service: ClickHouseService = Depends(get_clickhouse_service)
):
    try:
        validated_params = ExecuteQueryParams(**params)
        return service.execute_query(validated_params.query, validated_params.limit)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ExecuteQueryParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_tables", response_model=ApiResponse)
@schema(input_schema_class=GetTablesParams, output_schema_class=TablesResponse, examples=examples["/clickhouse/get_tables"])
async def get_tables(
    params: Dict[str, Any] = Body(...),
    service: ClickHouseService = Depends(get_clickhouse_service)
):
    try:
        validated_params = GetTablesParams(**params)
        return service.get_tables()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetTablesParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_columns", response_model=ApiResponse)
@schema(input_schema_class=GetColumnsParams, output_schema_class=ColumnsResponse, examples=examples["/clickhouse/get_columns"])
async def get_columns(
    params: Dict[str, Any] = Body(...),
    service: ClickHouseService = Depends(get_clickhouse_service)
):
    try:
        validated_params = GetColumnsParams(**params)
        return service.get_columns(validated_params.table_name)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetColumnsParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test_connection", response_model=ApiResponse)
@schema(input_schema_class=ClickHouseConnectionParams, output_schema_class=TestConnectionResponse, examples=examples["/clickhouse/test_connection"])
async def test_connection(
    params: Dict[str, Any] = Body(...)
):
    try:
        validated_params = ClickHouseConnectionParams(**params)
        service = ClickHouseService(validated_params.dict())
        return service.test_connection()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'ClickHouseConnectionParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
