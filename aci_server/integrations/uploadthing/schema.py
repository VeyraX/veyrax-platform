from pydantic import BaseModel, Field, AnyUrl, HttpUrl
from typing import List, Optional, Dict, Any, Union, Literal


class ListFilesParams(BaseModel):
    limit: Optional[int] = Field(
        500,
        ge=0,
        le=100000,
        description="The maximum number of files to retrieve."
    )
    offset: Optional[int] = Field(
        0,
        ge=0,
        description="The number of files to skip."
    )


class UploadThingFile(BaseModel):
    id: str = Field(..., description="The file id (deprecated).")
    customId: Optional[str] = Field(None, description="The custom id of the file.")
    key: str = Field(..., description="The file key.")
    name: str = Field(..., description="The name of the file.")
    status: str = Field(..., description="The status of the file.")
    size: int = Field(..., description="The size of the file in bytes.")
    uploadedAt: int = Field(..., description="The timestamp of when the file was uploaded.")


class FileList(BaseModel):
    hasMore: bool = Field(..., description="Whether there are more files to retrieve.")
    files: List[UploadThingFile] = Field(..., description="The list of files.")


class ListFilesResponse(BaseModel):
    data: FileList
    message: Optional[str] = None


class PollUploadParams(BaseModel):
    fileKey: str = Field(..., description="The unique key of the file to poll.")


class UploadThingFileDetail(BaseModel):
    fileKey: str = Field(..., description="The unique key of the file.")
    fileName: str = Field(..., description="The name of the file.")
    fileSize: int = Field(..., description="The size of the file in bytes.")
    fileType: Optional[str] = Field(None, description="The mime type of the file.")
    fileUrl: Optional[str] = Field(None, description="The URL to access the file.")
    customId: Optional[str] = Field(None, description="The custom id of the file.")
    callbackUrl: str = Field(..., description="The callback URL for this file upload.")
    callbackSlug: str = Field(..., description="The callback slug for this file upload.")


class PollUploadResult(BaseModel):
    status: str = Field(..., description="The status of the upload.", enum=["still working", "done"])
    file: Optional[UploadThingFileDetail] = None
    metadata: Optional[Any] = Field(None, description="The metadata returned from the file route's middleware function.")
    callbackData: Optional[Any] = Field(None, description="The callback data set by the server.")


class PollUploadResponse(BaseModel):
    data: PollUploadResult
    message: Optional[str] = None


# Server Callback models
class GetServerCallbackParams(BaseModel):
    authorization: str = Field(..., description="The JWT token received from prepareUpload endpoint.")


class GetServerCallbackResult(BaseModel):
    status: str = Field(..., description="Status of the callback data retrieval.", enum=["ok", "still waiting"])


class GetServerCallbackResponse(BaseModel):
    data: GetServerCallbackResult
    message: Optional[str] = None


class SetServerCallbackParams(BaseModel):
    fileKey: str = Field(
        ..., 
        max_length=300,
        description="The file key to set callback data for."
    )
    callbackData: Optional[Any] = Field(
        None,
        description="The callback data to set for the file, which will be returned in onUploadComplete callback."
    )


class SetServerCallbackResult(BaseModel):
    status: str = Field(..., description="Status of the callback data setting operation.")


class SetServerCallbackResponse(BaseModel):
    data: SetServerCallbackResult
    message: Optional[str] = None


# Prepare Upload models
class FileToUpload(BaseModel):
    name: str = Field(..., description="The name of the file to upload.")
    size: int = Field(..., description="The size of the file in bytes.")
    customId: Optional[str] = Field(None, description="A custom ID for the file.")


class PrepareUploadParams(BaseModel):
    callbackUrl: HttpUrl = Field(..., max_length=2048, description="The callback URL to use when upload is complete.")
    callbackSlug: str = Field(..., max_length=128, description="The slug for the callback.")
    files: List[FileToUpload] = Field(..., description="The files to prepare uploads for.")
    routeConfig: Union[List[str], Dict[str, Any]] = Field(..., description="The route configuration for the upload.")
    metadata: Optional[Any] = Field(None, description="Additional metadata to include with the upload.")


class PrepareUploadFields(BaseModel):
    key: str
    fileName: str
    fileType: Optional[str] = None
    fileUrl: str
    contentDisposition: Literal["inline", "attachment"]
    pollingJwt: str
    pollingUrl: str
    customId: Optional[str] = None
    url: str
    fields: Dict[str, str]


class PrepareUploadMultipart(BaseModel):
    key: str
    fileName: str
    fileType: Optional[str] = None
    fileUrl: str
    contentDisposition: Literal["inline", "attachment"]
    pollingJwt: str
    pollingUrl: str
    customId: Optional[str] = None
    urls: List[str]
    uploadId: str
    chunkSize: int
    chunkCount: int


class PrepareUploadResponse(BaseModel):
    data: List[Union[PrepareUploadFields, PrepareUploadMultipart]]
    message: Optional[str] = None


# Upload Files models
class FileDetails(BaseModel):
    name: str = Field(..., description="The name of the file to upload.")
    size: int = Field(..., description="The size of the file in bytes.")
    type: str = Field(..., description="The MIME type of the file.")
    customId: Optional[str] = Field(None, description="A custom ID for the file.")


class UploadFilesParams(BaseModel):
    files: List[FileDetails] = Field(..., description="The files to upload.")
    acl: Literal["public-read", "private"] = Field("public-read", description="The access control level for the files.")
    metadata: Optional[Any] = Field(None, description="Additional metadata to include with the files.")
    contentDisposition: Literal["inline", "attachment"] = Field("inline", description="How the file should be presented in a browser.")


class UploadFilesResponse(BaseModel):
    data: List[Union[PrepareUploadFields, PrepareUploadMultipart]]
    message: Optional[str] = None


# Upload From URL models
class UploadFromUrlParams(BaseModel):
    url: HttpUrl = Field(..., description="The URL of the file to upload.")
    customId: Optional[str] = Field(None, description="A custom ID for the file.")
    callbackUrl: HttpUrl = Field(..., max_length=2048, description="The callback URL to use when upload is complete.")
    callbackSlug: str = Field(..., max_length=128, description="The slug for the callback.")
    routeConfig: Union[List[str], Dict[str, Any]] = Field(..., description="The route configuration for the upload.")
    metadata: Optional[Any] = Field(None, description="Additional metadata to include with the upload.")


class UploadFromUrlResponse(BaseModel):
    data: List[Union[PrepareUploadFields, PrepareUploadMultipart]]
    message: Optional[str] = None


# Rename Files models
class FileRenameInfo(BaseModel):
    fileKey: str = Field(..., description="The key of the file to rename.")
    newName: str = Field(..., description="The new name for the file.")


class RenameFilesParams(BaseModel):
    updates: List[FileRenameInfo] = Field(..., description="List of files to rename with their new names.")


class RenameFilesResult(BaseModel):
    success: bool = Field(..., description="Whether the rename operation was successful.")
    renamedCount: int = Field(..., description="The number of files renamed.")


class RenameFilesResponse(BaseModel):
    data: RenameFilesResult
    message: Optional[str] = None


# Delete Files models
class DeleteFilesParams(BaseModel):
    fileKeys: Optional[List[str]] = Field(None, description="List of file keys to delete.")
    customIds: Optional[List[str]] = Field(None, description="List of custom IDs of files to delete.")


class DeleteFilesResult(BaseModel):
    success: bool = Field(..., description="Whether the delete operation was successful.")
    deletedCount: int = Field(..., description="The number of files marked for deletion.")


class DeleteFilesResponse(BaseModel):
    data: DeleteFilesResult
    message: Optional[str] = None


# Get App Info models
class GetAppInfoParams(BaseModel):
    pass  # No parameters needed for this endpoint


class AppInfoResult(BaseModel):
    appId: str = Field(..., description="The app ID.")
    defaultACL: str = Field(..., description="The app's default ACL.")
    allowACLOverride: bool = Field(..., description="Whether the app allows overriding the ACL on a per-request basis.")


class GetAppInfoResponse(BaseModel):
    data: AppInfoResult
    message: Optional[str] = None


# Get Usage Info models
class GetUsageInfoParams(BaseModel):
    pass  # No parameters needed for this endpoint


class UsageInfoResult(BaseModel):
    totalBytes: int = Field(..., description="Total bytes used counting towards the quota.")
    appTotalBytes: int = Field(..., description="Total bytes used by this app.")
    filesUploaded: int = Field(..., description="Total number of files uploaded by this app.")
    limitBytes: int = Field(..., description="The allocated storage quota for the app in bytes.")


class GetUsageInfoResponse(BaseModel):
    data: UsageInfoResult
    message: Optional[str] = None


# API Response
class ApiResponse(BaseModel):
    data: Union[
        FileList, 
        PollUploadResult, 
        GetServerCallbackResult, 
        SetServerCallbackResult, 
        List[Union[PrepareUploadFields, PrepareUploadMultipart]],
        RenameFilesResult,
        DeleteFilesResult,
        AppInfoResult,
        UsageInfoResult
    ]
    component: Optional[Dict[str, Any]] = None 