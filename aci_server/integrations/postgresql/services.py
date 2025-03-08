import os
from typing import Dict, Any, List, Optional, Union

from .client import PostgreSQLClient
from .schema import (
    QueryResult, TableList, TableInfo, ColumnList, ColumnInfo, ApiResponse, TestConnectionResult
)
from ..common.component_handler import prepare_components_auto, load_components


class PostgreSQLService:
    def __init__(self, client_or_params: Union[PostgreSQLClient, Dict[str, Any]]):
        if isinstance(client_or_params, dict):
            self.client = PostgreSQLClient(client_or_params)
        else:
            self.client = client_or_params
        
        self.components_data = self._load_components()
        self.connection_params = self.client.connection_params.copy()
        if hasattr(self.client, 'schema'):
            self.connection_params['schema'] = self.client.schema

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "postgresql"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def execute_query(self, query: str, params: Optional[List[Any]] = None, limit: Optional[int] = None) -> ApiResponse:
        try:
            if limit is not None:
                if "LIMIT" not in query.upper():
                    query = f"{query} LIMIT {limit}"
            
            results = self.client.execute_query(query, params)
            
            query_result = QueryResult(
                rows=results,
                row_count=len(results),
                query=query
            )
            
            return self.prepare_response(query_result, "PostgreSQLQueryResultTable")
        except Exception as e:
            return ApiResponse(message=f"Error executing query: {str(e)}")

    def get_tables(self) -> ApiResponse:
        try:
            tables_data = self.client.get_tables()
            
            tables = []
            for table_data in tables_data:
                tables.append(TableInfo(
                    table_name=table_data['table_name'],
                    table_type=table_data['table_type'],
                    table_description=table_data['table_description']
                ))
            
            schema = self.client.schema
            
            table_list = TableList(
                tables=tables,
                schema=schema
            )
            
            return self.prepare_response(table_list, "PostgreSQLTableList")
        except Exception as e:
            return ApiResponse(message=f"Error retrieving tables: {str(e)}")

    def get_columns(self, table_name: str) -> ApiResponse:
        try:
            columns_data = self.client.get_columns(table_name)
            
            columns = []
            for column_data in columns_data:
                columns.append(ColumnInfo(
                    column_name=column_data['column_name'],
                    data_type=column_data['data_type'],
                    is_nullable=column_data['is_nullable'],
                    column_default=column_data['column_default'],
                    column_description=column_data['column_description']
                ))
            
            schema = self.client.schema
            
            column_list = ColumnList(
                columns=columns,
                table_name=table_name,
                schema=schema
            )
            
            return self.prepare_response(column_list, "PostgreSQLColumnList")
        except Exception as e:
            return ApiResponse(message=f"Error retrieving columns: {str(e)}")

    def test_connection(self) -> ApiResponse:
        try:
            self.client.execute_query("SELECT 1 as connection_test")
            
            test_result = TestConnectionResult(
                success=True,
                message="Connection successful"
            )
            
            return self.prepare_response(test_result)
        except Exception as e:
            test_result = TestConnectionResult(
                success=False,
                message=f"Connection failed: {str(e)}"
            )
            return ApiResponse(data=test_result)
