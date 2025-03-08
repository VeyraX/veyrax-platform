from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    data: Optional[Any] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None


class SnowflakeConnectionParams(BaseModel):
    account: str = Field(..., description="Snowflake account identifier")
    user: str = Field(..., description="Snowflake username")
    password: str = Field(..., description="Snowflake password")
    warehouse: Optional[str] = Field(None, description="Snowflake warehouse")
    database: Optional[str] = Field(None, description="Database name")
    schema: Optional[str] = Field(None, description="Schema name")
    role: Optional[str] = Field(None, description="Snowflake role")


class ExecuteQueryParams(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for parameterized queries")
    limit: Optional[int] = Field(50, description="Maximum number of rows to return (default: 50)")


class GetTablesParams(BaseModel):
    pass 


class GetColumnsParams(BaseModel):
    table_name: str = Field(..., description="Table name")


class GetTableInfoParams(BaseModel):
    table_name: str = Field(..., description="Table name")


# Output schemas
class QueryResult(BaseModel):
    rows: List[Dict[str, Any]]
    row_count: int
    query: str


class TableInfo(BaseModel):
    name: str
    database: Optional[str] = None
    schema: Optional[str] = None
    kind: Optional[str] = None
    created_on: Optional[str] = None
    comment: Optional[str] = None


class TableList(BaseModel):
    tables: List[TableInfo]
    database: Optional[str] = None
    schema: Optional[str] = None


class ColumnInfo(BaseModel):
    name: str
    type: str
    kind: Optional[str] = None
    null: Optional[bool] = None
    default: Optional[str] = None
    primary_key: Optional[bool] = None
    unique_key: Optional[bool] = None
    comment: Optional[str] = None


class ColumnList(BaseModel):
    columns: List[ColumnInfo]
    table_name: str
    database: Optional[str] = None
    schema: Optional[str] = None


class DetailedTableInfo(BaseModel):
    name: str
    database: Optional[str] = None
    schema: Optional[str] = None
    columns: List[Dict[str, Any]]
    ddl: Optional[str] = None
    row_count: Optional[int] = None
    bytes: Optional[int] = None
    created: Optional[str] = None
    last_altered: Optional[str] = None


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


class TableInfoResponse(BaseModel):
    data: DetailedTableInfo
    message: Optional[str] = None


class TestConnectionResult(BaseModel):
    success: bool
    message: str


class TestConnectionResponse(BaseModel):
    data: TestConnectionResult
    message: Optional[str] = None
