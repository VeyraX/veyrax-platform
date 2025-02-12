from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DatabaseBase(BaseModel):
    id: str
    title: str
    description: Optional[str]
    created_time: datetime
    last_edited_time: datetime
    url: str

class Database(DatabaseBase):
    properties: Dict[str, Any]

class DatabaseList(BaseModel):
    items: List[DatabaseBase]
    next_cursor: Optional[str]

class PageBase(BaseModel):
    id: str
    created_time: datetime
    last_edited_time: datetime
    archived: bool
    url: str

class Page(PageBase):
    parent: Dict[str, Any]
    properties: Dict[str, Any]
    content: Optional[Dict[str, Any]]

class PageList(BaseModel):
    items: List[PageBase]
    next_cursor: Optional[str]

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