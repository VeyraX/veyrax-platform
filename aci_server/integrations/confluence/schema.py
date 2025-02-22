from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SpaceSchema(BaseModel):
    id: str
    name: str
    description: Optional[Dict[str, Any]] = None
    homepageId: Optional[str] = None
    type: str

class PageSchema(BaseModel):
    id: str
    title: str
    type: str
    space: Optional[Dict[str, Any]]
    version: Dict[str, Any]
    body: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    _links: Optional[Dict[str, Any]] = None

class PageCreateSchema(BaseModel):
    title: str
    content: str
    spaceId: str
    parentId: Optional[str] = None

class PageUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    version: Optional[int] = None

class PaginatedResponseSchema(BaseModel):
    results: List[Any]
    start: int
    limit: int
    size: int

class ContentSearchSchema(BaseModel):
    cql: Optional[str] = None
    space_key: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = 'page'
    limit: Optional[int] = 50