from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class CommonParams(BaseModel):
    numResults: Optional[int] = Field(
        10, 
        ge=1, 
        le=100,
        description="Number of results to return (1-100)"
    )

class SearchParams(CommonParams):
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="Search query"
    )
    includeDomains: Optional[List[str]] = Field(
        None,
        description="List of domains to include in search results"
    )
    excludeDomains: Optional[List[str]] = Field(
        None,
        description="List of domains to exclude from search results"
    )
    includeText: Optional[List[str]] = Field(
        None,
        description="List of text patterns to include in search results"
    )
    excludeText: Optional[List[str]] = Field(
        None,
        description="List of text patterns to exclude from search results"
    )
    startCrawlDate: Optional[str] = Field(
        None,
        description="Start date for crawled content (ISO format)"
    )
    endCrawlDate: Optional[str] = Field(
        None,
        description="End date for crawled content (ISO format)"
    )
    startPublishedDate: Optional[str] = Field(
        None,
        description="Start date for published content (ISO format)"
    )
    endPublishedDate: Optional[str] = Field(
        None,
        description="End date for published content (ISO format)"
    )
    useAutoprompt: Optional[bool] = Field(
        None,
        description="Whether to use autoprompt to enhance the query"
    )
    contents: Optional[Dict[str, bool]] = Field(
        None,
        description="Content types to include (e.g., {\"text\": true})"
    )

class ContentsParams(BaseModel):
    ids: List[str] = Field(
        ...,
        description="List of IDs or URLs to retrieve content for"
    )
    text: Optional[bool] = Field(
        True,
        description="Whether to include text content"
    )

class FindSimilarParams(CommonParams):
    url: str = Field(
        ...,
        description="URL to find similar content for"
    )
    excludeDomains: Optional[List[str]] = Field(
        None,
        description="List of domains to exclude from results"
    )

class SearchResult(BaseModel):
    id: str
    title: str
    url: str
    publishedDate: Optional[str] = None
    author: Optional[str] = None
    score: Optional[float] = None
    text: Optional[str] = None
    image: Optional[str] = None
    favicon: Optional[str] = None
    
    class Config:
        extra = 'allow'

class ContentResult(BaseModel):
    id: str
    title: str
    url: str
    publishedDate: Optional[str] = None
    author: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None
    favicon: Optional[str] = None
    
    class Config:
        extra = 'allow'

class SimilarResult(BaseModel):
    id: str
    title: str
    url: str
    publishedDate: Optional[str] = None
    author: Optional[str] = None
    score: float
    
    class Config:
        extra = 'allow'

class CostBreakdown(BaseModel):
    total: float
    search: Optional[Dict[str, float]] = None
    contents: Optional[Dict[str, float]] = None
    
    class Config:
        extra = 'allow'

class SearchResponse(BaseModel):
    requestId: str
    results: List[SearchResult]
    autopromptString: Optional[str] = None
    resolvedSearchType: Optional[str] = None
    effectiveFilters: Optional[Dict[str, Any]] = None
    costDollars: CostBreakdown
    
    class Config:
        extra = 'allow'

class ContentsResponse(BaseModel):
    requestId: str
    results: List[ContentResult]
    costDollars: CostBreakdown
    
    class Config:
        extra = 'allow'

class FindSimilarResponse(BaseModel):
    requestId: str
    results: List[SimilarResult]
    costDollars: CostBreakdown
    
    class Config:
        extra = 'allow'

# API Response
class ApiResponse(BaseModel):
    data: Union[SearchResponse, ContentsResponse, FindSimilarResponse]
    component: Optional[Dict[str, Any]] = None