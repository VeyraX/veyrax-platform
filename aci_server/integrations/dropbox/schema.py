from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

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
    component: Optional[Dict[str, Any]] = None

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

class SearchResult(BaseModel):
    files: List[DropboxFile]
    cursor: Optional[str] = None
    has_more: bool

class ApiResponse(BaseModel):
    data: Union[DropboxFile, FileList, SearchResult]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

# New parameter classes for routes
class ListFilesParams(BaseModel):
    filters: Optional[FileFilters] = FileFilters()

class GetFileParams(BaseModel):
    path: str

class CreateFolderParams(BaseModel):
    folder: FolderCreate
    autorename: Optional[bool] = False

class UploadFileParams(BaseModel):
    path: str
    file_content: str  # base64 encoded
    mode: Optional[str] = "add"

class DownloadFileParams(BaseModel):
    path: str

class DeleteFileParams(BaseModel):
    path: str

class MoveFileParams(BaseModel):
    from_path: str
    to_path: str

class ReadFileParams(BaseModel):
    path: str

class ListFilesResponse(BaseModel):
    data: FileList
    message: Optional[str] = None

class GetFileResponse(BaseModel):
    data: DropboxFile
    message: Optional[str] = None

class CreateFolderResponse(BaseModel):
    data: DropboxFile
    message: Optional[str] = None

class UploadFileResponse(BaseModel):
    data: DropboxFile
    message: Optional[str] = None

class DownloadFileResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class DeleteFileResponse(BaseModel):
    data: DropboxFile
    message: Optional[str] = None

class MoveFileResponse(BaseModel):
    data: DropboxFile
    message: Optional[str] = None

class ReadFileResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class RequestedVisibility(str, Enum):
    PUBLIC = "public"
    TEAM_ONLY = "team_only"
    PASSWORD = "password"
    TEAM_AND_PASSWORD = "team_and_password"
    SHARED_FOLDER_ONLY = "shared_folder_only"

class Audience(str, Enum):
    PUBLIC = "public"
    TEAM = "team"
    NO_ONE = "no_one"

class Access(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    MAX = "max"

class SharedLinkSettings(BaseModel):
    requested_visibility: Optional[RequestedVisibility] = RequestedVisibility.PUBLIC
    audience: Optional[Audience] = Audience.PUBLIC
    access: Optional[Access] = Access.VIEWER
    allow_download: Optional[bool] = True

class CreateSharedLinkParams(BaseModel):
    path: str
    settings: Optional[SharedLinkSettings] = None

class CreateSharedLinkResponse(BaseModel):
    data: DropboxFile
    message: Optional[str] = None

# New classes for search functionality
class SearchParams(BaseModel):
    query: str
    path: Optional[str] = ""
    max_results: Optional[int] = 20
    filename_only: Optional[bool] = False
    file_status: Optional[str] = "active"

class SearchContinueParams(BaseModel):
    cursor: str



class SearchResponse(BaseModel):
    data: SearchResult
    message: Optional[str] = None

class SearchContinueResponse(BaseModel):
    data: SearchResult
    message: Optional[str] = None