from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class SearchParams(BaseModel):
    search: str = Field(..., description="Search query")
    page: Optional[int] = Field(1, description="Page number")
    per_page: Optional[int] = Field(20, description="Results per page")

# Component Data Schema
class ComponentData(BaseModel):
    name: str
    description: str
    code: str
    install_command: str

# Component User Data Schema
class ComponentUserData(BaseModel):
    name: str
    username: str
    image_url: str

# Search Result Item Schema
class SearchResultItem(BaseModel):
    name: str
    preview_url: str
    video_url: str
    demo_id: int
    component_data: ComponentData
    component_user_data: ComponentUserData
    usage_count: int

# Pagination Schema
class Pagination(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int

# Metadata Schema
class Metadata(BaseModel):
    plan: str
    requests_remaining: int
    pagination: Pagination

# Search Results List Schema
class SearchResultsList(BaseModel):
    results: List[SearchResultItem]
    metadata: Metadata

# Generate Prompt API Input Schema
class GeneratePromptParams(BaseModel):
    prompt_type: str = Field(..., description="Type of prompt to generate")
    demo_id: int = Field(..., description="Demo ID from search results")

# Generate Prompt Response Schema
class GeneratePromptResponse(BaseModel):
    prompt: str

# API Response Schema
class ApiResponse(BaseModel):
    data: Union[SearchResultsList, GeneratePromptResponse]
    component: Optional[Dict[str, Any]] = None

# Specific Response Schemas
class SearchResponse(BaseModel):
    data: SearchResultsList

class PromptResponse(BaseModel):
    data: GeneratePromptResponse
