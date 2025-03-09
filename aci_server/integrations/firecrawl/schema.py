from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union

# Input schemas
class LocationSettings(BaseModel):
    country: Optional[str] = "US"
    languages: Optional[List[str]] = ["en-US"]

class JsonOptions(BaseModel):
    schema: Optional[Dict[str, Any]] = {}
    systemPrompt: Optional[str] = None
    prompt: Optional[str] = None

class ActionBase(BaseModel):
    type: str

class WaitAction(ActionBase):
    type: str = "wait"
    milliseconds: int
    selector: Optional[str] = None

class ClickAction(ActionBase):
    type: str = "click"
    selector: str

class WriteAction(ActionBase):
    type: str = "write"
    selector: str
    text: str

class PressAction(ActionBase):
    type: str = "press"
    key: str

class ScrollAction(ActionBase):
    type: str = "scroll"
    direction: str
    amount: Optional[int] = None

class ScrapeAction(ActionBase):
    type: str = "scrape"
    selector: str

class ExecuteJsAction(ActionBase):
    type: str = "executeJs"
    code: str

Action = Union[WaitAction, ClickAction, WriteAction, PressAction, ScrollAction, ScrapeAction, ExecuteJsAction]

# Scrape endpoint schemas
class ScrapeParams(BaseModel):
    url: str
    formats: Optional[List[str]] = ["markdown"]
    onlyMainContent: Optional[bool] = True
    includeTags: Optional[List[str]] = None
    excludeTags: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    waitFor: Optional[int] = 0
    mobile: Optional[bool] = False
    skipTlsVerification: Optional[bool] = False
    timeout: Optional[int] = 30000
    jsonOptions: Optional[JsonOptions] = None
    actions: Optional[List[Action]] = None
    location: Optional[LocationSettings] = None
    removeBase64Images: Optional[bool] = None
    blockAds: Optional[bool] = True
    proxy: Optional[str] = None

# Batch scrape endpoint schemas
class WebhookSpec(BaseModel):
    url: str
    headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    events: Optional[List[str]] = ["completed"]

class BatchScrapeParams(BaseModel):
    urls: List[str]
    webhook: Optional[WebhookSpec] = None
    ignoreInvalidURLs: Optional[bool] = False
    formats: Optional[List[str]] = ["markdown"]
    onlyMainContent: Optional[bool] = True
    includeTags: Optional[List[str]] = None
    excludeTags: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    waitFor: Optional[int] = 0
    mobile: Optional[bool] = False
    skipTlsVerification: Optional[bool] = False
    timeout: Optional[int] = 30000
    jsonOptions: Optional[JsonOptions] = None
    actions: Optional[List[Action]] = None
    location: Optional[LocationSettings] = None
    removeBase64Images: Optional[bool] = None
    blockAds: Optional[bool] = True
    proxy: Optional[str] = None

class GetBatchScrapeParams(BaseModel):
    id: str

class GetBatchScrapeErrorsParams(BaseModel):
    id: str

# Crawl endpoint schemas
class ScrapeOptions(BaseModel):
    formats: Optional[List[str]] = ["markdown"]
    onlyMainContent: Optional[bool] = True
    includeTags: Optional[List[str]] = None
    excludeTags: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    waitFor: Optional[int] = 0
    mobile: Optional[bool] = False
    skipTlsVerification: Optional[bool] = False
    timeout: Optional[int] = 30000
    jsonOptions: Optional[JsonOptions] = None
    actions: Optional[List[Action]] = None
    location: Optional[LocationSettings] = None
    removeBase64Images: Optional[bool] = None
    blockAds: Optional[bool] = True
    proxy: Optional[str] = None

class CrawlParams(BaseModel):
    url: str
    excludePaths: Optional[List[str]] = None
    includePaths: Optional[List[str]] = None
    maxDepth: Optional[int] = 2
    ignoreSitemap: Optional[bool] = False
    ignoreQueryParameters: Optional[bool] = False
    limit: Optional[int] = 10000
    allowBackwardLinks: Optional[bool] = False
    allowExternalLinks: Optional[bool] = False
    webhook: Optional[WebhookSpec] = None
    scrapeOptions: Optional[ScrapeOptions] = None

class GetCrawlParams(BaseModel):
    id: str

class CancelCrawlParams(BaseModel):
    id: str

class GetCrawlErrorsParams(BaseModel):
    id: str

# Output schemas
class ScrapeMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    sourceURL: Optional[str] = None
    statusCode: Optional[int] = None
    error: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

class ActionScreenshots(BaseModel):
    screenshots: Optional[List[str]] = None

class ScrapeData(BaseModel):
    markdown: Optional[str] = None
    html: Optional[str] = None
    rawHtml: Optional[str] = None
    screenshot: Optional[str] = None
    links: Optional[List[str]] = None
    actions: Optional[ActionScreenshots] = None
    metadata: Optional[ScrapeMetadata] = None
    llm_extraction: Optional[Dict[str, Any]] = None
    warning: Optional[str] = None

class ScrapeResponse(BaseModel):
    success: bool
    data: ScrapeData

class BatchScrapeResponse(BaseModel):
    success: bool
    id: str
    url: Optional[str] = None
    invalidURLs: Optional[List[str]] = None

class BatchScrapeResultItem(BaseModel):
    markdown: Optional[str] = None
    html: Optional[str] = None
    rawHtml: Optional[str] = None
    links: Optional[List[str]] = None
    screenshot: Optional[str] = None
    metadata: Optional[ScrapeMetadata] = None

class BatchScrapeStatusResponse(BaseModel):
    status: str
    total: int
    completed: int
    creditsUsed: int
    expiresAt: str
    next: Optional[str] = None
    data: List[BatchScrapeResultItem]

class BatchScrapeError(BaseModel):
    id: str
    timestamp: str
    url: str
    error: str

class BatchScrapeErrorsResponse(BaseModel):
    errors: List[BatchScrapeError]
    robotsBlocked: List[str]

class CrawlResponse(BaseModel):
    success: bool
    id: str
    url: str

class CrawlStatusResponse(BaseModel):
    status: str
    total: int
    completed: int
    creditsUsed: int
    expiresAt: str
    next: Optional[str] = None
    data: List[BatchScrapeResultItem]  # Reusing the same item model from batch scrape

class CancelCrawlResponse(BaseModel):
    status: str

class CrawlErrorsResponse(BaseModel):
    errors: List[BatchScrapeError]  # Reusing the same error model from batch scrape
    robotsBlocked: List[str]


# Map endpoint schemas
class MapParams(BaseModel):
    url: str
    search: Optional[str] = None
    ignoreSitemap: Optional[bool] = True
    sitemapOnly: Optional[bool] = False
    includeSubdomains: Optional[bool] = False
    limit: Optional[int] = 5000
    timeout: Optional[int] = None

class MapResponse(BaseModel):
    success: bool
    links: List[str]

# Extract endpoint schemas
class ExtractParams(BaseModel):
    urls: List[str]
    prompt: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    enableWebSearch: Optional[bool] = False
    ignoreSitemap: Optional[bool] = False
    includeSubdomains: Optional[bool] = True
    showSources: Optional[bool] = False
    scrapeOptions: Optional[ScrapeOptions] = None

class ExtractResponse(BaseModel):
    success: bool
    id: str

class GetExtractParams(BaseModel):
    id: str

class ExtractStatusResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    status: str
    expiresAt: str

# Search endpoint schemas
class SearchParams(BaseModel):
    query: str
    limit: Optional[int] = 5
    tbs: Optional[str] = None
    lang: Optional[str] = "en"
    country: Optional[str] = "us"
    location: Optional[str] = None
    timeout: Optional[int] = 60000
    scrapeOptions: Optional[ScrapeOptions] = None

class SearchResultItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    markdown: Optional[str] = None
    html: Optional[str] = None
    rawHtml: Optional[str] = None
    links: Optional[List[str]] = None
    screenshot: Optional[str] = None
    metadata: Optional[ScrapeMetadata] = None

class SearchResponse(BaseModel):
    success: bool
    data: List[SearchResultItem]
    warning: Optional[str] = None

# Credit Usage endpoint schemas
class CreditUsageResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

# API Response models
class ApiResponse(BaseModel):
    data: Optional[Union[
        ScrapeData, 
        BatchScrapeResponse, 
        BatchScrapeStatusResponse, 
        BatchScrapeErrorsResponse,
        CrawlResponse,
        CrawlStatusResponse,
        CancelCrawlResponse,
        CrawlErrorsResponse,
        MapResponse,
        ExtractResponse,
        ExtractStatusResponse,
        SearchResponse,
        CreditUsageResponse
    ]] = None
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    message: Optional[str] = None