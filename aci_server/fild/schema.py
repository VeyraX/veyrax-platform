from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union


class AgentRequest(BaseModel):
    query: str

class ExtractedValue(BaseModel):
    value: str
    reasoning: str

class AgentResponse(BaseModel):
    query: str
    result: str
    success: bool
    payload: Optional[List[Dict[str, Any]]] = None

class WaterfallRequest(BaseModel):
    sheet_id: str
    query: str
    row_indexes: Optional[List[int]] = None
    row_range: Optional[Dict[str, int]] = None
    column_ids: List[int]

class WaterfallResponse(BaseModel):
    success: bool
    message: str
    process_details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Brave web search schemas
class BraveWebSearchRequest(BaseModel):
    q: str
    count: int = 5
    offset: int = 0
    country: str = "US"
    safesearch: str = "moderate"
    spellcheck: bool = True
    search_lang: str = "en"
    text_decorations: bool = True

class BraveWebSearchResponse(BaseModel):
    web: Dict[str, Any]
    query: Dict[str, Any]

class LinkedInProfileRequest(BaseModel):
    username: Optional[str] = None

class LinkedInProfileResponse(BaseModel):
    data: Dict[str, Any]
    component: Optional[Dict[str, str]] = None

class LinkedInSearchPeopleRequest(BaseModel):
    keywords: str
    geo: Optional[str] = None
    start: Optional[str] = "0"
    company: Optional[str] = None
    lastName: Optional[str] = None
    schoolId: Optional[str] = None
    firstName: Optional[str] = None
    keywordTitle: Optional[str] = None
    keywordSchool: Optional[str] = None

class LinkedInSearchPeopleResponse(BaseModel):
    data: Dict[str, Any]
    component: Optional[Dict[str, str]] = None

class LinkedInCompanyDetailsRequest(BaseModel):
    username: Optional[str] = None

class LinkedInCompanyDetailsResponse(BaseModel):
    data: Dict[str, Any]
    component: Optional[Dict[str, str]] = None

class LinkedInSearchCompaniesRequest(BaseModel):
    page: Optional[int] = 1
    hasJobs: Optional[bool] = None
    keyword: Optional[str] = None
    locations: Optional[List[int]] = None
    industries: Optional[List[int]] = None
    companySizes: Optional[List[str]] = None

class LinkedInSearchCompaniesResponse(BaseModel):
    data: Dict[str, Any]
    component: Optional[Dict[str, str]] = None
