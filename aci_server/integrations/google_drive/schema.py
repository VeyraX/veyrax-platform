from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DriveFile(BaseModel):
    id: str
    name: str
    mime_type: str
    parent_ids: Optional[List[str]]
    parent_names: Optional[List[str]]
    created_time: datetime
    modified_time: datetime
    size: Optional[int]
    web_view_link: Optional[str] = None
    web_content_link: Optional[str] = None

class FileList(BaseModel):
    files: List[DriveFile]
    page_token: Optional[str]

class FileUpload(BaseModel):
    name: str
    parent_id: Optional[str]
    mime_type: str

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[str]

class FileMove(BaseModel):
    new_parent_id: str

class FileFilters(BaseModel):
    name_contains: Optional[str] = None
    mime_type: Optional[str] = None
    parent_id: Optional[str] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    folders_only: Optional[bool] = False