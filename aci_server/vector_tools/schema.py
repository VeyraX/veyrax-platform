from pydantic import BaseModel, Field
from typing import Optional, Union

class SearchQueryGoogleDrive(BaseModel):
    doc_id: Optional[str] = None
    title: Optional[str] = None
    modified_time: Optional[str] = None
    web_view_link: Optional[str] = None
    parent_ids: Optional[list[str]] = None
    part: Optional[int] = None
    total_parts: Optional[int] = None
    user_id: str = Field(..., description="Required user ID")

class SearchQueryNotion(BaseModel):
    doc_id: Optional[str] = None
    title: Optional[str] = None
    database_id: Optional[str] = None
    url: Optional[str] = None
    last_edited_time: Optional[str] = None
    part: Optional[int] = None
    total_parts: Optional[int] = None
    user_id: str = Field(..., description="Required user ID")

class SearchParams(BaseModel):
    query: Union[SearchQueryGoogleDrive, SearchQueryNotion]
    collection: str = Field(..., description="Required collection name")
    limit: Optional[int] = 5

class SearchRequest(BaseModel):
    query_text: str
    search_params: SearchParams

    