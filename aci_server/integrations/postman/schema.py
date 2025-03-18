from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class BaseParams(BaseModel):
    workspace_id: Optional[str] = None

class GetCollectionsParams(BaseParams):
    pass

class GetCollectionParams(BaseParams):
    collection_id: str

class UpdateCollectionParams(BaseParams):
    collection_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    collection: Dict[str, Any] = Field(...)

class DeleteCollectionParams(BaseParams):
    collection_id: str

class CreateCollectionParams(BaseParams):
    collection: Dict[str, Any] = Field(...)

class CollectionInfo(BaseModel):
    id: str
    name: str
    uid: Optional[str] = None
    owner: Optional[str] = None
    schema: Optional[str] = None
    description: Optional[str] = None
    fork_label: Optional[str] = Field(None, alias="forkLabel")
    is_public: Optional[bool] = Field(None, alias="isPublic")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

class CollectionListResponse(BaseModel):
    collections: List[CollectionInfo]

class CollectionItem(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    request: Optional[Dict[str, Any]] = None
    response: Optional[List[Dict[str, Any]]] = None
    item: Optional[List['CollectionItem']] = None

CollectionItem.update_forward_refs()

class CollectionDetail(BaseModel):
    info: CollectionInfo
    item: List[CollectionItem]
    variable: Optional[List[Dict[str, Any]]] = None
    event: Optional[List[Dict[str, Any]]] = None
    auth: Optional[Dict[str, Any]] = None

class CollectionResponse(BaseModel):
    collection: CollectionDetail

class DeleteCollectionResponse(BaseModel):
    id: str
    uid: Optional[str] = None
    name: Optional[str] = None

class GetEnvironmentsParams(BaseParams):
    pass

class GetEnvironmentParams(BaseParams):
    environment_id: str

class CreateEnvironmentParams(BaseParams):
    environment: Dict[str, Any] = Field(...)

class UpdateEnvironmentParams(BaseParams):
    environment_id: str
    environment: Dict[str, Any] = Field(...)

class DeleteEnvironmentParams(BaseParams):
    environment_id: str

class EnvironmentVariable(BaseModel):
    key: str
    value: Optional[str] = None
    enabled: Optional[bool] = True
    type: Optional[str] = "default"

class EnvironmentInfo(BaseModel):
    id: str
    name: str
    uid: Optional[str] = None
    owner: Optional[str] = None
    values: Optional[List[EnvironmentVariable]] = None
    is_public: Optional[bool] = Field(None, alias="isPublic")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

class EnvironmentListResponse(BaseModel):
    environments: List[EnvironmentInfo]

class EnvironmentResponse(BaseModel):
    environment: EnvironmentInfo

class DeleteEnvironmentResponse(BaseModel):
    id: str
    uid: Optional[str] = None
    name: Optional[str] = None

class ForkCollectionParams(BaseParams):
    collection_id: str
    label: Optional[str] = None
    workspace: str = Field(...)

class ForkCollectionResponse(BaseModel):
    collection: CollectionDetail

class GetWorkspacesParams(BaseParams):
    pass

class GetWorkspaceParams(BaseParams):
    workspace_id: str

class CreateWorkspaceParams(BaseParams):
    name: str
    type: str = "personal"
    description: Optional[str] = None
    visibility: Optional[str] = None

class UpdateWorkspaceParams(BaseParams):
    workspace_id: str
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None

class DeleteWorkspaceParams(BaseParams):
    workspace_id: str

class WorkspaceInfo(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceInfo]

class WorkspaceResponse(BaseModel):
    workspace: WorkspaceInfo

class DeleteWorkspaceResponse(BaseModel):
    id: str
    uid: Optional[str] = None
    name: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[
        CollectionListResponse,
        CollectionResponse,
        DeleteCollectionResponse,
        EnvironmentListResponse,
        EnvironmentResponse,
        DeleteEnvironmentResponse,
        ForkCollectionResponse,
        WorkspaceListResponse,
        WorkspaceResponse,
        DeleteWorkspaceResponse, 
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
