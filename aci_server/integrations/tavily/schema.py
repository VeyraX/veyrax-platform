from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Search parameters
class SearchParams(BaseModel):
    query: str = Field(
        ..., 
        description="The search query to execute with Tavily",
        json_schema_extra={"example": "who is Leo Messi?"}
    )
    topic: Optional[str] = Field(
        "general",
        pattern="^(general|news)$",
        description="The category of the search. Available options: general, news"
    )
    search_depth: Optional[str] = Field(
        "basic",
        pattern="^(basic|advanced)$",
        description="The depth of the search. A basic search costs 1 API Credit, while an advanced search costs 2 API Credits."
    )
    max_results: Optional[int] = Field(
        5,
        ge=0,
        le=20,
        description="The maximum number of search results to return (0-20)."
    )
    time_range: Optional[str] = Field(
        None,
        pattern="^(day|week|month|year|d|w|m|y)$",
        description="The time range back from the current date to filter results."
    )
    days: Optional[int] = Field(
        3,
        ge=0,
        description="Number of days back from the current date to include. Available only if topic is news."
    )
    include_answer: Optional[bool] = Field(
        False,
        description="Include an LLM-generated answer to the provided query."
    )
    include_raw_content: Optional[bool] = Field(
        False,
        description="Include the cleaned and parsed HTML content of each search result."
    )
    include_images: Optional[bool] = Field(
        False,
        description="Also perform an image search and include the results in the response."
    )
    include_image_descriptions: Optional[bool] = Field(
        False,
        description="When include_images is true, also add a descriptive text for each image."
    )
    include_domains: Optional[List[str]] = Field(
        None,
        description="A list of domains to specifically include in the search results."
    )
    exclude_domains: Optional[List[str]] = Field(
        None,
        description="A list of domains to specifically exclude from the search results."
    )

# Extract parameters
class ExtractParams(BaseModel):
    urls: Union[str, List[str]] = Field(
        ...,
        description="The URL(s) to extract content from.",
        json_schema_extra={"example": "https://en.wikipedia.org/wiki/Artificial_intelligence"}
    )
    include_images: Optional[bool] = Field(
        False,
        description="Include a list of images extracted from the URLs in the response."
    )
    extract_depth: Optional[str] = Field(
        "basic",
        pattern="^(basic|advanced)$",
        description="The depth of the extraction process. advanced extraction retrieves more data."
    )

# Response models
class SearchResultItem(BaseModel):
    title: str
    url: str
    content: str
    score: float
    raw_content: Optional[str] = None

    class Config:
        extra = 'allow'

class ImageItem(BaseModel):
    url: str
    description: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    answer: Optional[str] = None
    images: List[ImageItem] = Field(default_factory=list)
    results: List[SearchResultItem]
    response_time: Union[str, float]

class ExtractResultItem(BaseModel):
    url: str
    raw_content: str
    images: List[str] = Field(default_factory=list)

class FailedExtractItem(BaseModel):
    url: str
    error: str

class ExtractResponse(BaseModel):
    results: List[ExtractResultItem]
    failed_results: List[FailedExtractItem] = Field(default_factory=list)
    response_time: Union[str, float]

# API response models
class ApiResponse(BaseModel):
    data: Union[SearchResponse, ExtractResponse]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    ) 