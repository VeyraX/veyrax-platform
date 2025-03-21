from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal


class CommonParams(BaseModel):
    cloud_name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


class UploadParams(CommonParams):
    file: str = Field(..., description="File to upload - URL, base64 data, or file path")
    public_id: Optional[str] = Field(None, description="Public ID for the uploaded asset")
    upload_preset: Optional[str] = Field(None, description="Upload preset name for unsigned uploads")
    transformation: Optional[str] = Field(None, description="Transformation to apply on upload")
    eager: Optional[str] = Field(None, description="List of transformations to eagerly generate")
    tags: Optional[str] = Field(None, description="Comma-separated list of tags")
    context: Optional[str] = Field(None, description="Pipe-separated key-value pairs of context metadata")
    resource_type: Optional[str] = Field("image", description="Resource type: image, video, raw")
    invalidate: Optional[bool] = Field(None, description="Invalidate CDN cache")


class ExplicitParams(CommonParams):
    public_id: str = Field(..., description="Public ID of the asset to transform")
    type: Optional[str] = Field("upload", description="Type of asset (upload, private, authenticated)")
    eager: str = Field(..., description="Transformations to generate")
    invalidate: Optional[bool] = Field(None, description="Invalidate CDN cache for the asset")
    async_: Optional[bool] = Field(None, description="Perform transformations asynchronously")
    notification_url: Optional[str] = Field(None, description="Webhook URL for async transformations")
    resource_type: Optional[str] = Field("image", description="Resource type: image, video, raw")


class ListAssetsParams(CommonParams):
    max_results: Optional[int] = Field(10, description="Maximum number of results to return", ge=1, le=500)
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page of results")
    prefix: Optional[str] = Field(None, description="Filter by prefix (e.g. folder path)")
    direction: Optional[str] = Field("desc", description="Sort direction: asc or desc")
    resource_type: Optional[str] = Field("image", description="Resource type: image, video, raw")
    type: Optional[str] = Field("upload", description="Type of asset (upload, private, authenticated)")


class GetAssetDetailsParams(CommonParams):
    public_id: str = Field(..., description="Public ID of the asset")
    metadata: Optional[bool] = Field(None, description="Include metadata in response")
    exif: Optional[bool] = Field(None, description="Include EXIF data for images")
    colors: Optional[bool] = Field(None, description="Include colors data for images")
    derived_next_cursor: Optional[str] = Field(None, description="Cursor for paginating derived assets")
    resource_type: Optional[str] = Field("image", description="Resource type: image, video, raw")
    type: Optional[str] = Field("upload", description="Type of asset (upload, private, authenticated)")


class DeleteAssetParams(CommonParams):
    public_id: str = Field(..., description="Public ID of the asset to delete")
    invalidate: Optional[bool] = Field(None, description="Invalidate CDN cache")
    resource_type: Optional[str] = Field("image", description="Resource type: image, video, raw")
    type: Optional[str] = Field("upload", description="Type of asset (upload, private, authenticated)")


class RenameAssetParams(CommonParams):
    from_public_id: str = Field(..., description="Current public ID of the asset")
    to_public_id: str = Field(..., description="New public ID for the asset")
    overwrite: Optional[bool] = Field(None, description="Overwrite if an asset exists with the target name")
    invalidate: Optional[bool] = Field(None, description="Invalidate CDN cache for the old public ID")
    resource_type: Optional[str] = Field("image", description="Resource type: image, video, raw")
    type: Optional[str] = Field("upload", description="Type of asset (upload, private, authenticated)")


# Response models
class ResourceData(BaseModel):
    public_id: str
    version: int
    signature: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    resource_type: Optional[str] = None
    created_at: Optional[str] = None
    tags: Optional[List[str]] = None
    bytes: Optional[int] = None
    type: Optional[str] = None
    etag: Optional[str] = None
    url: Optional[str] = None
    secure_url: Optional[str] = None
    original_filename: Optional[str] = None
    
    # Video-specific fields
    duration: Optional[float] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    audio: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None


class EagerTransformation(BaseModel):
    transformation: str
    width: int
    height: int
    bytes: int
    format: str
    url: str
    secure_url: str


class UploadResponse(BaseModel):
    public_id: str
    version: int
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    resource_type: str
    created_at: str
    tags: List[str] = []
    bytes: int
    type: str
    url: str
    secure_url: str
    signature: Optional[str] = None
    original_filename: Optional[str] = None
    eager: Optional[List[EagerTransformation]] = None
    
    # Video-specific fields
    duration: Optional[float] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    audio: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None


class ExplicitResponse(BaseModel):
    public_id: str
    version: int
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    resource_type: str
    created_at: str
    bytes: int
    type: str
    url: str
    secure_url: str
    signature: Optional[str] = None
    eager: List[EagerTransformation] = []


class ListAssetsResponse(BaseModel):
    resources: List[ResourceData]
    next_cursor: Optional[str] = None


class GetAssetDetailsResponse(BaseModel):
    public_id: str
    version: int
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    resource_type: str
    created_at: str
    tags: List[str] = []
    bytes: int
    type: str
    url: str
    secure_url: str
    signature: Optional[str] = None
    
    # Media-specific fields
    duration: Optional[float] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    audio: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    
    # Optional fields
    colors: Optional[List[str]] = None
    exif: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    faces: Optional[List[Dict[str, Any]]] = None
    pages: Optional[int] = None
    derived_next_cursor: Optional[str] = None


class BasicResponse(BaseModel):
    result: str


class DeleteAssetResponse(BasicResponse):
    pass


class RenameAssetResponse(BasicResponse):
    pass


class ErrorResponse(BaseModel):
    result: str
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class ApiResponse(BaseModel):
    data: Union[UploadResponse, ExplicitResponse, ListAssetsResponse, 
                GetAssetDetailsResponse, DeleteAssetResponse, RenameAssetResponse,
                ErrorResponse]
    component: Optional[Dict[str, Any]] = None 