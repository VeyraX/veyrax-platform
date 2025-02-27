from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime

class DatabaseFilters(BaseModel):
    search_query: Optional[str] = None
    filter_by: Optional[Dict[str, Any]] = None
    sort_by: Optional[Dict[str, Any]] = None
    max_results: Optional[int] = 100

class PageFilters(BaseModel):
    query: Optional[str] = None
    sort_direction: Optional[str] = None
    max_results: Optional[int] = 100

class DatabaseProperty(BaseModel):
    id: str
    name: str
    type: str
    options: Optional[List[Dict[str, Any]]] = None

class Database(BaseModel):
    id: str
    title: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None

class Page(BaseModel):
    id: str
    title: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None
    parent: Optional[Dict[str, Any]] = None
    component: Optional[Dict[str, Any]] = None

class PageCreate(BaseModel):
    parent: Dict[str, str]
    properties: Dict[str, Any]
    children: Optional[List[Dict[str, Any]]] = None

class PageUpdate(BaseModel):
    properties: Dict[str, Any]

class DatabaseList(BaseModel):
    items: List[Database]
    next_cursor: Optional[str] = None

class PageList(BaseModel):
    items: List[Page]
    next_cursor: Optional[str] = None

class SearchResult(BaseModel):
    items: List[Union[Page, Database]]
    next_cursor: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[Page, PageList, Database, DatabaseList, SearchResult]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class PropertyType(BaseModel):
    id: str
    type: Literal[
        "title", "rich_text", "number", "select", 
        "multi_select", "date", "people", "files",
        "checkbox", "url", "email", "phone_number",
        "formula", "relation", "rollup", "created_time",
        "created_by", "last_edited_time", "last_edited_by"
    ]
    name: str
    
class PageFilters(BaseModel):
    filter: Optional[Dict[str, Any]] = Field(
        None,
        description="Notion filter object"
    )
    sorts: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of sort objects"
    )
    page_size: Optional[int] = Field(
        100,
        description="Number of results per page",
        le=100
    )

class DatabaseProperties(BaseModel):
    id: str
    title: str
    properties: Dict[str, PropertyType]

class ListPagesRequest(BaseModel):
    start_cursor: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    page_size: Optional[int] = Field(
        default=100,
        le=100,
        description="Maximum number of results per page"
    )

# New parameter classes for routes
class ListDatabasesParams(BaseModel):
    start_cursor: Optional[str] = None
    max_results: Optional[int] = Field(default=100, le=100)

class GetDatabaseParams(BaseModel):
    database_id: str

class ListDatabasePagesParams(BaseModel):
    database_id: str
    filters: Optional[DatabaseFilters] = None
    start_cursor: Optional[str] = None

class QueryDatabaseParams(BaseModel):
    database_id: str
    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)

class CreatePageParams(BaseModel):
    page: PageCreate

class GetPageParams(BaseModel):
    page_id: str

class UpdatePageParams(BaseModel):
    page_id: str
    page_update: PageUpdate

class SearchParams(BaseModel):
    query: Optional[str] = ''
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)
    sort_direction: Optional[str] = None
