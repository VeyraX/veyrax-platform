from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class DriveFile(BaseModel):
    id: str
    name: str
    mime_type: str
    parent_ids: Optional[List[str]]
    parent_names: Optional[List[str]] = None
    created_time: datetime
    modified_time: datetime
    size: Optional[int]
    web_view_link: Optional[str] = None
    web_content_link: Optional[str] = None
    component: Optional[Dict[str, Any]] = None

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
    max_results: Optional[int] = 20

class ApiResponse(BaseModel):
    data: Union[DriveFile, FileList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# New parameter classes for routes
class ListFilesParams(BaseModel):
    pageToken: Optional[str] = None
    filters: Optional[FileFilters] = None

class GetFileParams(BaseModel):
    file_id: str

class CreateFolderParams(BaseModel):
    folder: FolderCreate

class UploadFileParams(BaseModel):
    parent_id: Optional[str] = None

class DownloadFileParams(BaseModel):
    file_id: str

class DeleteFileParams(BaseModel):
    file_id: str

class MoveFileParams(BaseModel):
    file_id: str
    new_parent_id: str

class ListFoldersParams(BaseModel):
    pageToken: Optional[str] = None
    filters: Optional[FileFilters] = None

class ReadFileParams(BaseModel):
    file_id: str