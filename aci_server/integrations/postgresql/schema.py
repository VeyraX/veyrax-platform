from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, RootModel


class ApiResponse(BaseModel):
    data: Optional[Any] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None


# Input schemas
class PostgreSQLConnectionParams(BaseModel):
    host: str = Field(..., description="Database host")
    port: int = Field(5432, description="Database port")
    dbname: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    schema: str = Field("public", description="Database schema")


class ExecuteQueryParams(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    limit: Optional[int] = Field(50, description="Maximum number of rows to return (default: 50)")


class GetTablesParams(BaseModel):
    pass


class GetColumnsParams(BaseModel):
    table_name: str = Field(..., description="Table name")


# Output schemas
class QueryResultRow(RootModel):
    root: Dict[str, Any]


class QueryResult(BaseModel):
    rows: List[Dict[str, Any]]
    row_count: int
    query: str


class TableInfo(BaseModel):
    table_name: str
    table_type: str
    table_description: Optional[str] = None


class TableList(BaseModel):
    tables: List[TableInfo]
    schema: str


class ColumnInfo(BaseModel):
    column_name: str
    data_type: str
    is_nullable: str
    column_default: Optional[str] = None
    column_description: Optional[str] = None


class ColumnList(BaseModel):
    columns: List[ColumnInfo]
    table_name: str
    schema: str


# Response schemas
class QueryResponse(BaseModel):
    data: QueryResult
    message: Optional[str] = None


class TablesResponse(BaseModel):
    data: TableList
    message: Optional[str] = None


class ColumnsResponse(BaseModel):
    data: ColumnList
    message: Optional[str] = None


class TestConnectionResult(BaseModel):
    success: bool
    message: str


class TestConnectionResponse(BaseModel):
    data: TestConnectionResult
    message: Optional[str] = None
