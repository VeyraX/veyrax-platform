from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    data: Optional[Any] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None


# Добавляем класс для параметров подключения
class ClickHouseConnectionParams(BaseModel):
    host: str = Field(..., description="ClickHouse server host")
    port: int = Field(9000, description="ClickHouse server port")
    database: str = Field("default", description="Database name")
    user: str = Field("default", description="Username")
    password: str = Field("", description="Password")


class ExecuteQueryParams(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for parameterized queries")
    limit: Optional[int] = Field(50, description="Maximum number of rows to return (default: 50)")


class GetDatabasesParams(BaseModel):
    pass


class GetTablesParams(BaseModel):
    pass


class GetColumnsParams(BaseModel):
    table_name: str = Field(..., description="Table name")


# Output schemas
class QueryResultRow(BaseModel):
    model_config = {"extra": "allow"}
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class QueryResult(BaseModel):
    rows: List[Dict[str, Any]]
    row_count: int
    query: str


class DatabaseInfo(BaseModel):
    name: str


class DatabaseList(BaseModel):
    databases: List[DatabaseInfo]


class TableInfo(BaseModel):
    name: str


class TableList(BaseModel):
    tables: List[TableInfo]
    database: Optional[str] = None


class ColumnInfo(BaseModel):
    name: str
    type: str
    default_type: Optional[str] = None
    default_expression: Optional[str] = None
    comment: Optional[str] = None
    codec_expression: Optional[str] = None
    ttl_expression: Optional[str] = None


class ColumnList(BaseModel):
    columns: List[ColumnInfo]
    table_name: str
    database: Optional[str] = None


# Response schemas
class QueryResponse(BaseModel):
    data: QueryResult
    message: Optional[str] = None


class DatabasesResponse(BaseModel):
    data: DatabaseList
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