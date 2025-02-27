from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union

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
    html_link: Optional[str] = None 

class PageCreateSchema(BaseModel):
    title: str
    content: str
    spaceId: str
    parentId: Optional[str] = None

class PageUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    version: Optional[int] = None

class PageList(BaseModel):
    pages: List[PageSchema]
    next_page: Optional[int] = None

class SpaceList(BaseModel):
    spaces: List[SpaceSchema]
    next_page: Optional[int] = None

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

class PageFilters(BaseModel):
    space_id: Optional[str] = None
    title: Optional[str] = None
    limit: int = 50

class ApiResponse(BaseModel):
    data: Union[PageSchema, PageList, SpaceList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# New schema classes for route parameters
class GetSpacesParams(BaseModel):
    pass  # No required parameters for get_spaces

class GetPagesParams(BaseModel):
    filters: Optional[PageFilters] = None

class GetPageParams(BaseModel):
    page_id: str

class CreatePageParams(BaseModel):
    page: PageCreateSchema

class UpdatePageParams(BaseModel):
    page_id: str
    update: PageUpdateSchema

class SearchContentParams(BaseModel):
    cql: Optional[str] = None
    space_key: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = "page"
    limit: Optional[int] = 50