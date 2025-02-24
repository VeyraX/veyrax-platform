from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DropboxFile(BaseModel):
    id: str
    name: str
    path_display: str
    path_lower: str
    mime_type: Optional[str]
    size: Optional[int]
    is_folder: bool
    created_time: datetime
    modified_time: datetime
    shared_link: Optional[str] = None

class FileList(BaseModel):
    files: List[DropboxFile]
    cursor: Optional[str]
    has_more: bool

class FileUpload(BaseModel):
    path: str
    mode: Optional[str] = "add"

class FolderCreate(BaseModel):
    path: str

class FileMove(BaseModel):
    from_path: str
    to_path: str

    class Config:
        json_schema_extra = {
            "example": {
                "from_path": "/example.txt",
                "to_path": "/folder/example.txt"
            }
        }

class FileFilters(BaseModel):
    path: Optional[str] = ""
    recursive: Optional[bool] = False
    limit: Optional[int] = 20