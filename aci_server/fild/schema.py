from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union


class AgentRequest(BaseModel):
    query: str

class ExtractedValue(BaseModel):
    result: str
    reasoning: str
    confidence: int = Field(..., ge=1, le=5, description="Confidence level from 1 (very uncertain) to 5 (very confident)")
    source: str = Field(..., description="URL where the information was found, or 'Not Found' if no source")

class AgentResponse(BaseModel):
    query: str
    result: str
    success: bool
    payload: Optional[List[Dict[str, Any]]] = None

class EnrichmentRequest(BaseModel):
    sheet_id: str
    row_indexes: Optional[List[int]] = None
    row_range: Optional[Dict[str, int]] = None
    column_ids: List[int]
    chat_id: Optional[str] = None

class EnrichmentResponse(BaseModel):
    success: bool
    message: str
    process_details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PeopleSearchRequest(BaseModel):
    company_query: str = Field(..., description="Query to find relevant companies")
    people_query: str = Field(..., description="Query to find relevant people within those companies")

class PersonResult(BaseModel):
    url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    full_name: Optional[str] = None
    linkedin_url: Optional[str] = None

class PeopleSearchResponse(BaseModel):
    success: bool
    results: Optional[List[PersonResult]] = None
    error: Optional[str] = None

class CompanySearchRequest(BaseModel):
    query: str = Field(..., description="Query to find relevant companies")

class CompanyResult(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    linkedin_id: Optional[int] = None
    geo_country: Optional[str] = None
    traffic: Optional[float] = None
    size_range: Optional[str] = None
    founded: Optional[float] = None
    domain: Optional[str] = None
    screenshot_url: Optional[str] = None
    company_relevance_score: Optional[int] = None
    company_relevance_reasoning_1: Optional[str] = None
    company_relevance_reasoning_2: Optional[str] = None

class CompanySearchResponse(BaseModel):
    success: bool
    results: Optional[List[CompanyResult]] = None
    error: Optional[str] = None

class BraveWebSearchRequest(BaseModel):
    q: str
    count: int = 5
    offset: int = 0
    country: str = "US"
    safesearch: str = "moderate"
    spellcheck: bool = True
    search_lang: str = "en"
    text_decorations: bool = True

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="The search query to look up on the web")
    max_results: int = Field(5, description="Maximum number of results to return")
    
class ExtractPageRequest(BaseModel):
    url: str = Field(..., description="The URL of the webpage to extract content from")