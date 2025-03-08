import os
from typing import Dict, Any, List, Optional, Union

from .client import ClickHouseClient
from .schema import (
    QueryResult, DatabaseList, DatabaseInfo, TableList, TableInfo, 
    ColumnList, ColumnInfo, ApiResponse, TestConnectionResult
)
from ..common.component_handler import prepare_components_auto, load_components


class ClickHouseService:
    def __init__(self, connection_params: Dict[str, Any]):
        self.client = ClickHouseClient(connection_params)
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "clickhouse"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def execute_query(self, query: str, limit: Optional[int] = None) -> ApiResponse:
        try:
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
        except Exception as e:
            return ApiResponse(message=f"Error executing query: {str(e)}")

    def get_tables(self) -> ApiResponse:
        try:
            tables_data = self.client.get_tables()
            
            tables = []
            for table_data in tables_data:
                tables.append(TableInfo(name=table_data['name']))
            
            database = self.client.connection_params.get('database', 'default')
            table_list = TableList(
                tables=tables,
                database=database
            )
            
            return ApiResponse(data=table_list)
        except Exception as e:
            return ApiResponse(message=f"Error retrieving tables: {str(e)}")

    def get_columns(self, table_name: str) -> ApiResponse:
        try:
            columns_data = self.client.get_columns(table_name)
            
            columns = []
            for column_data in columns_data:
                columns.append(ColumnInfo(
                    name=column_data['name'],
                    type=column_data['type'],
                    default_type=column_data.get('default_type'),
                    default_expression=column_data.get('default_expression'),
                    comment=column_data.get('comment'),
                    codec_expression=column_data.get('codec_expression'),
                    ttl_expression=column_data.get('ttl_expression')
                ))
            
            database = self.client.connection_params.get('database', 'default')
            column_list = ColumnList(
                columns=columns,
                table_name=table_name,
                database=database
            )
            
            return ApiResponse(data=column_list)
        except Exception as e:
            return ApiResponse(message=f"Error retrieving columns: {str(e)}")

    def test_connection(self) -> ApiResponse:
        try:
            host = self.client.connection_params.get('host', '')
            port = self.client.connection_params.get('port', '')
            secure = self.client.connection_params.get('secure', False)
            print(f"Testing ClickHouse connection to {host}:{port} (secure={secure})")
            
            result = self.client.execute_query("SELECT 1")
            print(f"Test query successful, result: {result}")
            
            test_result = TestConnectionResult(
                success=True,
                message="Connection successful"
            )
            
            return ApiResponse(data=test_result)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Connection error details: {error_details}")
            
            error_message = str(e)
            if "Query execution failed: " in error_message:
                error_message = error_message.replace("Query execution failed: ", "")
            
            test_result = TestConnectionResult(
                success=False,
                message=error_message
            )
            
            return ApiResponse(data=test_result)
