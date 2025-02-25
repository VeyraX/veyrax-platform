from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class Database(BaseModel):
    id: str
    title: str

class DatabaseList(BaseModel):
    items: List[Database]
    next_cursor: Optional[str] = None
    has_more: bool

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
    
class Page(BaseModel):
    id: str
    created_time: datetime
    last_edited_time: datetime
    archived: bool
    url: str
    properties: Dict[str, Any]
    parent: Dict[str, Any]

class PageList(BaseModel):
    items: List[Page]
    next_cursor: Optional[str] = None
    has_more: bool

class PageCreate(BaseModel):
    parent: Dict[str, str] = Field(
        ..., 
        description="Parent database reference in format {'database_id': 'xxx'}"
    )
    properties: Dict[str, Any] = Field(
        ..., 
        description="Page properties matching the database schema"
    )
    children: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Page content blocks"
    )

class PageUpdate(BaseModel):
    properties: Optional[Dict[str, Any]] = Field(
        None, 
        description="Page properties in Notion format"
    )
    archived: Optional[bool] = None
    children: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Page content blocks"
    )

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
