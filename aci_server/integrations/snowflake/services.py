import os
from typing import Dict, Any, List, Optional, Union

from .client import SnowflakeClient
from .schema import (
    QueryResult, TableList, TableInfo, ColumnList, 
    ColumnInfo, DetailedTableInfo, ApiResponse, TestConnectionResult
)
from ..common.component_handler import prepare_components_auto, load_components


class SnowflakeService:
    def __init__(self, connection_params: Dict[str, Any]):
        self.client = SnowflakeClient(connection_params)
        self.connection_params = connection_params
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "snowflake"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def execute_query(self, query: str, limit: Optional[int] = None) -> ApiResponse:
        if limit is not None:
            if "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"
        
        results = self.client.execute_query(query)
        
        query_result = QueryResult(
            rows=results,
            row_count=len(results),
            query=query
        )
        
        return ApiResponse(data=query_result)

    def get_tables(self) -> ApiResponse:
        tables_data = self.client.get_tables()
        database = self.connection_params.get('database')
        schema = self.connection_params.get('schema')
        
        tables = []
        for table_data in tables_data:
            created_on = table_data.get("created_on")
            if created_on and not isinstance(created_on, str):
                created_on = str(created_on)
            
            tables.append(TableInfo(
                name=table_data.get("name"),
                database=database or table_data.get("database_name"),
                schema=schema or table_data.get("schema_name"),
                kind=table_data.get("kind"),
                created_on=created_on,
                comment=table_data.get("comment")
            ))
        
        table_list = TableList(
            tables=tables,
            database=database,
            schema=schema
        )
        
        return ApiResponse(data=table_list)

    def get_columns(self, table_name: str) -> ApiResponse:
        columns_data = self.client.get_columns(table_name)
        database = self.connection_params.get('database')
        schema = self.connection_params.get('schema')
        
        columns = []
        for column_data in columns_data:
            columns.append(ColumnInfo(
                name=column_data.get("name"),
                type=column_data.get("type"),
                kind=column_data.get("kind"),
                null=column_data.get("null") == "Y",
                default=column_data.get("default"),
                primary_key=column_data.get("primary_key") == "Y",
                unique_key=column_data.get("unique_key") == "Y",
                comment=column_data.get("comment")
            ))
        
        column_list = ColumnList(
            columns=columns,
            table_name=table_name,
            database=database,
            schema=schema
        )
        
        return ApiResponse(data=column_list)

    def test_connection(self) -> ApiResponse:
        try:
            self.client.execute_query("SELECT 1 as connection_test")
            
            test_result = TestConnectionResult(
                success=True,
                message="Connection successful"
            )
            
            return ApiResponse(data=test_result)
        except Exception as e:
            test_result = TestConnectionResult(
                success=False,
                message=f"Connection failed: {str(e)}"
            )
            return ApiResponse(data=test_result)
