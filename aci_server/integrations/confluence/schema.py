from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class SpaceSchema(BaseModel):
    id: str
    name: str
    key: str
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
    spaceKey: str = Field(..., min_length=1, max_length=255, pattern="^[A-Z0-9]+$", 
                        description="Space key in uppercase (e.g. 'PRAC')")
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
    data: Optional[Union[PageSchema, PageList, SpaceList]] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None

class DeletePageResponse(BaseModel):
    message: str

class GetSpacesParams(BaseModel):
    pass 

class GetPagesParams(BaseModel):
    filters: Optional[PageFilters] = None

    class Config:
        arbitrary_types_allowed = True

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

class DeletePageParams(BaseModel):
    page_id: str

class SpacesResponse(BaseModel):
    data: SpaceList
    message: Optional[str] = None

class PagesResponse(BaseModel):
    data: PageList
    message: Optional[str] = None

class PageResponse(BaseModel):
    data: PageSchema
    message: Optional[str] = None

class CreatePageResponse(BaseModel):
    data: PageSchema
    message: Optional[str] = None

class UpdatePageResponse(BaseModel):
    data: PageSchema
    message: Optional[str] = None

class SearchContentResponse(BaseModel):
    data: PageList
    message: Optional[str] = None

class DeletePageResponse(BaseModel):
    message: str
    data: Optional[Any] = None