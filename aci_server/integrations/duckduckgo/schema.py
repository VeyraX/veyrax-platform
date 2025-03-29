from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class SearchParams(BaseModel):
    query: str = Field(
        ..., 
        min_length=1,
        description="Search query"
    )
    max_results: Optional[int] = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)"
    )

class ContentParams(BaseModel):
    url: str = Field(
        ...,
        description="URL to fetch content for"
    )

class SearchResult(BaseModel):
    title: str
    url: str
    description: str
    source: Optional[str] = None
    icon: Optional[str] = None

class SearchResults(BaseModel):
    results: List[SearchResult]

class Content(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    html: Optional[str] = None
    source: str = "duckduckgo"

class SearchResponse(BaseModel):
    data: SearchResults

class ContentResponse(BaseModel):
    data: Content

class ApiResponse(BaseModel):
    data: Union[SearchResults, Content]
    component: Optional[Dict[str, Any]] = None