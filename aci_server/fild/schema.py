from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union


class AgentRequest(BaseModel):
    query: str

class ExtractedValue(BaseModel):
    result: str
    reasoning: str

class AgentResponse(BaseModel):
    query: str
    result: str
    success: bool
    payload: Optional[List[Dict[str, Any]]] = None

class WaterfallRequest(BaseModel):
    sheet_id: str
    row_indexes: Optional[List[int]] = None
    row_range: Optional[Dict[str, int]] = None
    column_ids: List[int]

class WaterfallResponse(BaseModel):
    success: bool
    message: str
    process_details: Optional[Dict[str, Any]] = None
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