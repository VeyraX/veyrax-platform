from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from fastapi import UploadFile, File
from ..common.schema_generation.classes import FileReference
from enum import Enum
from pydantic import root_validator, model_validator

# Add enum classes at the top of the file
class PermissionRole(str, Enum):
    READER = "reader"
    WRITER = "writer"
    COMMENTER = "commenter"
    OWNER = "owner"

class PermissionType(str, Enum):
    USER = "user"
    GROUP = "group"
    DOMAIN = "domain"
    ANYONE = "anyone"

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
    parent_id: Optional[str] = None

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

class PermissionResponse(BaseModel):
    id: str
    role: PermissionRole
    type: PermissionType
    email_address: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[DriveFile, FileList, PermissionResponse, List[PermissionResponse]]
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
    file: FileReference

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

# Response schema classes
class ListFilesResponse(BaseModel):
    data: FileList
    message: Optional[str] = None

class GetFileResponse(BaseModel):
    data: DriveFile
    message: Optional[str] = None

class CreateFolderResponse(BaseModel):
    data: DriveFile
    message: Optional[str] = None

class UploadFileResponse(BaseModel):
    data: DriveFile
    message: Optional[str] = None

class DownloadFileResponse(BaseModel):
    status: str
    file_content: bytes
    mime_type: str
    filename: str
    message: Optional[str] = None

class DeleteFileResponse(BaseModel):
    status: str
    message: Optional[str] = None

class MoveFileResponse(BaseModel):
    data: DriveFile
    message: Optional[str] = None

class ListFoldersResponse(BaseModel):
    data: FileList
    message: Optional[str] = None

class ReadFileResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    file: Optional[Dict[str, Any]] = None
    mime_type: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None

# Add these new classes
class PermissionRequest(BaseModel):
    role: PermissionRole
    type: PermissionType
    email: Optional[str] = None
    domain: Optional[str] = None
    email_message: Optional[str] = None

    @model_validator(mode='after')
    def validate_permission_fields(self):
        perm_type = self.type
        email = self.email
        domain = self.domain
        
        if perm_type in [PermissionType.USER, PermissionType.GROUP]:
            if not email:
                raise ValueError("Email is required for user/group permissions")
            if domain:
                raise ValueError("Domain should not be provided for user/group permissions")
                
        elif perm_type == PermissionType.DOMAIN:
            if not domain:
                raise ValueError("Domain is required for domain permissions")
            if email:
                raise ValueError("Email should not be provided for domain permissions")
                
        elif perm_type == PermissionType.ANYONE:
            if email or domain:
                raise ValueError("Email/domain should not be provided for 'anyone' permission")
                
        return self



# Add to existing parameter classes
class SetPermissionParams(BaseModel):
    file_id: str
    permission: PermissionRequest

class ListPermissionsParams(BaseModel):
    file_id: str

class DeletePermissionParams(BaseModel):
    file_id: str
    permission_id: str

# Add new class for copy operation
class CopyFileParams(BaseModel):
    file_id: str
    name: Optional[str] = None  # New name for the copy (optional)
    parent_id: Optional[str] = None  # Parent folder ID (optional)

