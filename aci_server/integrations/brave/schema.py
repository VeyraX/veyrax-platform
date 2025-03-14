from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Common parameters
class CommonSearchParams(BaseModel):
    country: Optional[str] = Field(
        "US", 
        max_length=2,
        pattern="^[A-Z]{2}$",
        description="2-letter uppercase country code for localized results (e.g. US, GB, CA). See: https://api.search.brave.com/app/documentation/enums#country-codes"
    )
    search_lang: Optional[str] = Field(
        "en",
        description="2+ character language code for results. Supported codes are like en, nl, es, fr, de, it, ja, etc. See: https://api.search.brave.com/app/documentation/enums#language-codes"
    )
    ui_lang: Optional[str] = Field(
        "en-US",
        description="UI language in RFC 9110 format (language-country). Supported codes are like en-US, nl-NL, es-ES, fr-FR, de-DE, it-IT, ja-JP, etc. See: https://api.search.brave.com/app/documentation/enums#ui-language-codes"
    )
    units: Optional[str] = Field(
        None,
        pattern="^(metric|imperial)$",
        description="Measurement system: 'metric' or 'imperial'. Auto-detected from country if not set."
    )

# Web Search Parameters
class WebSearchParams(CommonSearchParams):
    q: str = Field(
        ..., 
        min_length=1, 
        max_length=400,
        json_schema_extra={"example": "latest AI developments"},
        description="Search query term. Cannot be empty. Maximum 400 characters and 50 words"
    )
    count: Optional[int] = Field(
        5, 
        ge=1, 
        le=20,
        description="Number of results per page (1-20). Combine with offset for pagination"
    )
    offset: Optional[int] = Field(
        0, 
        ge=0, 
        le=9,
        description="Zero-based offset for pagination. Max 9. Use with count parameter"
    )
    safesearch: Optional[str] = Field(
        "moderate", 
        pattern="^(off|moderate|strict)$",
        description="Adult content filter: 'off', 'moderate' (default), or 'strict'"
    )
    freshness: Optional[str] = Field(
        None, 
        pattern="^(pd|pw|pm|py[1-5]|\d{4}-\d{2}-\d{2}to\d{4}-\d{2}-\d{2})$",
        description="Filter by discovery date. Formats: pd(day), pw(week), pm(month), py(year), or date range (YYYY-MM-DDtoYYYY-MM-DD)"
    )
    text_decorations: Optional[bool] = Field(
        True,
        description="Include decoration markers in snippets (e.g. highlighting)"
    )
    spellcheck: Optional[bool] = Field(
        True,
        description="Enable query spellchecking. Alters query if corrections found"
    )
    result_filter: Optional[str] = Field(
        None,
        description="Comma-separated result types: discussions,faq,infobox,news,query,summarizer,videos,web,locations"
    )
    goggles: Optional[str] = Field(
        None,
        description="Goggles ID/URL for custom ranking. See https://github.com/brave/goggles-quickstart"
    )
    extra_snippets: Optional[bool] = Field(
        None,
        description="Get up to 5 additional excerpts (requires specific plans)"
    )
    summary: Optional[bool] = Field(
        None,
        description="Enable summary generation for summarizer endpoint"
    )

# Response Models
class WebSearchResult(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    meta_url: Optional[Dict[str, Any]] = None
    thumbnail: Optional[Dict[str, str]] = None
    age: Optional[str] = None
    page_age: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = 'allow'

class WebSearchApiResponse(BaseModel):
    query: Optional[Dict[str, Any]] = None
    mixed: Optional[Dict[str, Any]] = None
    type: str
    web: Optional[Dict[str, Any]] = Field(
        None,
        description="Web search results container",
        examples=[{
            "type": "search",
            "results": [{
                "title": "Example Result",
                "url": "https://example.com",
                "description": "Example description"
            }],
            "family_friendly": True
        }]
    )
    news: Optional[Dict[str, Any]] = None
    videos: Optional[Dict[str, Any]] = None
    locations: Optional[Dict[str, Any]] = None

# Add new parameter models
class ImageSearchParams(CommonSearchParams):
    q: str = Field(..., min_length=1, max_length=400,
                  description="Search query for images")
    count: Optional[int] = Field(5, ge=1, le=50,
                                description="Number of results (1-50)")
    size: Optional[str] = Field(None, pattern="^(small|medium|large|xlarge)$",
                               description="Image size filter")
    aspect_ratio: Optional[str] = Field(None, pattern="^(square|wide|tall)$",
                                       description="Aspect ratio filter")
    color: Optional[str] = Field(None,
                                description="Color filter in hex format (e.g. #FF0000)")

class VideoSearchParams(CommonSearchParams):
    q: str = Field(..., min_length=1, max_length=400,
                  description="Search query for videos")
    count: Optional[int] = Field(20, ge=1, le=50,
                                description="Number of results (1-50)")
    duration: Optional[str] = Field(None, pattern="^(short|medium|long)$",
                                   description="Video duration filter")

class NewsSearchParams(CommonSearchParams):
    q: str = Field(..., min_length=1, max_length=400,
                  description="Search query for news articles")
    count: Optional[int] = Field(20, ge=1, le=50,
                                description="Number of results (1-50)")
    freshness: Optional[str] = Field(None, 
                                    pattern="^(pd|pw|pm|py[1-5]|\d{4}-\d{2}-\d{2}to\d{4}-\d{2}-\d{2})$",
                                    description="Filter by publication date")

# Add new response models
class ImageSearchResult(BaseModel):
    title: str
    url: str
    thumbnail: Dict[str, str]
    source: str
    width: Optional[int] = Field(None, description="Image width in pixels if available")
    height: Optional[int] = Field(None, description="Image height in pixels if available")
    size: Optional[int] = Field(None, description="File size in bytes if available")
    aspect_ratio: Optional[float] = Field(None, description="Width/height ratio if calculable")
    
    class Config:
        extra = 'allow'  # To handle unexpected fields

class VideoSearchResult(BaseModel):
    title: str
    url: str
    thumbnail: Dict[str, str]
    duration: Optional[str] = Field(None, description="Duration in HH:MM:SS format")
    views: Optional[int] = Field(None, description="Approximate view count")
    publisher: Optional[str] = None
    published_date: Optional[str] = Field(None, description="ISO 8601 date format")
    description: Optional[str] = None
    
    class Config:
        extra = 'allow'  # To handle unexpected fields

class NewsSearchResult(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    source: Optional[str] = Field(None, description="News source domain")
    date: Optional[str] = Field(None, description="Publication date in ISO format")
    thumbnail: Optional[Dict[str, str]] = None
    authors: List[str] = Field(default_factory=list)
    
    class Config:
        extra = 'allow'

# Update ApiResponse union
class ApiResponse(BaseModel):
    data: Union[
        WebSearchApiResponse,
        List[ImageSearchResult],
        List[VideoSearchResult],
        List[NewsSearchResult]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )