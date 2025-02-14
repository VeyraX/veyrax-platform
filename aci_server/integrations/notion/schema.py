from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Database(BaseModel):
    id: str
    title: str

class DatabaseList(BaseModel):
    items: List[Database]
    next_cursor: Optional[str] = None

class DatabaseList(BaseModel):
    items: List[Database]
    next_cursor: Optional[str] = None
    
class PageBase(BaseModel):
    id: str
    created_time: datetime
    last_edited_time: datetime
    archived: bool
    url: str

class Page(BaseModel):
    id: str
    title: str
    created_time: str
    last_edited_time: str
    archived: bool
    url: str

class PageList(BaseModel):
    items: List[Page]
    next_cursor: Optional[str] = None

class PageCreate(BaseModel):
    parent_id: str
    title: str
    properties: Dict[str, Any]
    content: Optional[Dict[str, Any]]

class PageUpdate(BaseModel):
    title: Optional[str]
    properties: Optional[Dict[str, Any]]
    archived: Optional[bool]

class PageFilters(BaseModel):
    database_id: Optional[str] = None
    search_query: Optional[str] = None
    filter_by: Optional[Dict[str, Any]] = None
    sort_by: Optional[Dict[str, Any]] = None
