from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# Base models
class User(BaseModel):
    id: str
    handle: str
    img_url: Optional[str] = None
    email: Optional[str] = None

class Team(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class Project(BaseModel):
    id: str
    name: str
    thumbnail_url: Optional[str] = None
    last_modified: Optional[datetime] = None

class File(BaseModel):
    key: str
    name: str
    thumbnail_url: Optional[str] = None
    last_modified: Optional[datetime] = None
    version: Optional[str] = None
    document: Optional[Dict[str, Any]] = None

class Node(BaseModel):
    id: str
    name: str
    type: str
    visible: Optional[bool] = True
    locked: Optional[bool] = False
    children: Optional[List[Any]] = None
    absoluteBoundingBox: Optional[Dict[str, float]] = None
    fills: Optional[List[Dict[str, Any]]] = None
    strokes: Optional[List[Dict[str, Any]]] = None
    style: Optional[Dict[str, Any]] = None

class Component(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    node_id: str
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[User] = None
    containing_frame: Optional[Dict[str, Any]] = None

class Style(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    style_type: str
    node_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[User] = None

class Comment(BaseModel):
    id: str
    message: str
    file_key: str
    parent_id: Optional[str] = None
    user: Optional[User] = None
    created_at: Optional[datetime] = None
    client_meta: Optional[Dict[str, Any]] = None
    order_id: Optional[int] = None

# List models
class FileList(BaseModel):
    items: List[File]
    cursor: Optional[str] = None

class NodeList(BaseModel):
    nodes: Dict[str, Dict[str, Any]]

class ComponentList(BaseModel):
    items: List[Component]
    cursor: Optional[str] = None

class StyleList(BaseModel):
    items: List[Style]
    cursor: Optional[str] = None

class CommentList(BaseModel):
    items: List[Comment]
    cursor: Optional[str] = None

# Input schemas
class GetFileParams(BaseModel):
    file_key: str

class GetFileNodesParams(BaseModel):
    file_key: str
    node_ids: List[str]

class GetImageParams(BaseModel):
    file_key: str
    node_ids: List[str]
    format: Optional[str] = "png"
    scale: Optional[float] = 1

class GetFileComponentsParams(BaseModel):
    file_key: str

class GetComponentSetsParams(BaseModel):
    file_key: str

class GetStylesParams(BaseModel):
    file_key: str

class GetTeamProjectsParams(BaseModel):
    team_id: str

class GetTeamComponentsParams(BaseModel):
    team_id: str

class GetTeamComponentSetsParams(BaseModel):
    team_id: str

class GetTeamStylesParams(BaseModel):
    team_id: str

class GetProjectFilesParams(BaseModel):
    project_id: str
    branch_name: Optional[str] = None

# Output schemas
class GetFileResponse(BaseModel):
    data: File
    message: Optional[str] = None

class GetFileNodesResponse(BaseModel):
    data: NodeList
    message: Optional[str] = None

class GetImageResponse(BaseModel):
    data: Dict[str, str]
    message: Optional[str] = None

class GetFileComponentsResponse(BaseModel):
    data: ComponentList
    message: Optional[str] = None

class GetComponentSetsResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class GetStylesResponse(BaseModel):
    data: StyleList
    message: Optional[str] = None

class GetMeResponse(BaseModel):
    data: User
    message: Optional[str] = None

class GetTeamProjectsResponse(BaseModel):
    data: List[Project]
    message: Optional[str] = None

class GetTeamComponentsResponse(BaseModel):
    data: ComponentList
    message: Optional[str] = None

class GetTeamComponentSetsResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class GetTeamStylesResponse(BaseModel):
    data: StyleList
    message: Optional[str] = None

class GetProjectFilesResponse(BaseModel):
    data: FileList
    message: Optional[str] = None

# General API response
class ApiResponse(BaseModel):
    data: Union[
        File, FileList,
        NodeList,
        Dict[str, str],  # For images
        Component, ComponentList,
        Style, StyleList,
        User,
        Project, List[Project],
        Comment, CommentList,
        Dict[str, Any]  # For other responses
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
