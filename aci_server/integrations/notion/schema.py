from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
import re
from enum import Enum, StrEnum

class DatabaseFilters(BaseModel):
    search_query: Optional[str] = None
    filter_by: Optional[Dict[str, Any]] = None
    sort_by: Optional[Dict[str, Any]] = None
    max_results: Optional[int] = 100

class PageFilters(BaseModel):
    query: Optional[str] = None
    sort_direction: Optional[str] = None
    max_results: Optional[int] = 100

class DatabaseProperty(BaseModel):
    id: str
    name: str
    type: str
    options: Optional[List[Dict[str, Any]]] = None

class Database(BaseModel):
    id: str = Field(
        ...,
        description="Valid Notion database UUID in format 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'",
        example="2f26ee68-df30-4251-aad4-8ddc420cba3d"
    )
    title: Optional[str] = None
    properties: Optional[Dict[str, Any]] = Field(
        None,
        description="Database properties/schema. Must include exactly one title property. "
        "Total schema size should be <50KB for optimal performance"
    )
    url: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None

# Updated Parent type definitions with Field descriptions
class DatabaseParent(BaseModel):
    type: str = Field(
        "database_id",
        description="Must be 'database_id' for database parent type",
        example="database_id"
    )
    database_id: str = Field(
        ...,
        description="REQUIRED. Valid Notion database UUID in format 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'",
        example="123e4567-e89b-12d3-a456-426614174000"
    )

class PageParent(BaseModel):
    type: str = Field(
        "page_id",
        description="Must be 'page_id' for page parent type",
        example="page_id"
    )
    page_id: str = Field(..., description="UUID of the parent page")

class WorkspaceParent(BaseModel):
    type: str = Field(
        "workspace", 
        description="Must be 'workspace' for workspace parent type",
        example="workspace"
    )
    workspace: bool = Field(True, description="Always true for workspace parent")

class BlockParent(BaseModel):
    type: str = Field(
        "block_id",
        description="Must be 'block_id' for block parent type", 
        example="block_id"
    )
    block_id: str = Field(..., description="UUID of the parent block")

Parent = Union[DatabaseParent, PageParent, WorkspaceParent, BlockParent]

# Updated Page model
class Page(BaseModel):
    id: str
    title: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None
    parent: Optional[Parent] = None  # Changed from Dict
    component: Optional[Dict[str, Any]] = None

# Updated PageCreate model to use proper parent types
class PageCreate(BaseModel):
    parent: Union[DatabaseParent, PageParent] = Field(
        ...,
        description="REQUIRED. Parent must be either a database or page. "
        "Database parent requires properties matching the database schema."
    )
    properties: Dict[str, Any] = Field(
        ...,
        description="REQUIRED. Page properties. For database pages, must match parent database schema. "
        "Must include title for database pages."
    )
    children: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Block content children. Each block must have 'object: block' and valid type. "
        "Total content size must be < 50KB per request."
    )

class PageUpdate(BaseModel):
    properties: Dict[str, Any]

class DatabaseList(BaseModel):
    items: List[Database]
    next_cursor: Optional[str] = None

class PageList(BaseModel):
    items: List[Page]
    next_cursor: Optional[str] = None

class SearchResult(BaseModel):
    items: List[Union[Page, Database]]
    next_cursor: Optional[str] = None

class PropertyKind(StrEnum):
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"

class PropertyType(BaseModel):
    id: str
    type: PropertyKind = Field(
        ...,
        description="REQUIRED. Must match Notion database property type",
        example=PropertyKind.TITLE
    )
    name: str

class DatabaseProperties(BaseModel):
    id: str
    title: str
    properties: Dict[str, PropertyType]

class ListPagesRequest(BaseModel):
    start_cursor: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    page_size: Optional[int] = Field(
        default=100,
        le=100,
        description="REQUIRED MAX: 100. Use pagination for more results"
    )

# New parameter classes for routes
class ListDatabasesParams(BaseModel):
    start_cursor: Optional[str] = None
    max_results: Optional[int] = Field(default=100, le=100)

class GetDatabaseParams(BaseModel):
    database_id: str

class ListDatabasePagesParams(BaseModel):
    database_id: str
    filters: Optional[DatabaseFilters] = None
    start_cursor: Optional[str] = None

class QueryDatabaseParams(BaseModel):
    database_id: str = Field(
        ...,
        description="REQUIRED. Valid Notion database UUID",
        example="2f26ee68-df30-4251-aad4-8ddc420cba3d"
    )
    filter: Optional[Dict[str, Any]] = Field(
        None,
        description="Filter conditions using property filters and/or compound filters"
    )
    sorts: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Array of sort objects. Can sort by property values or timestamps"
    )
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)

class CreatePageParams(BaseModel):
    page: PageCreate

class GetPageParams(BaseModel):
    page_id: str = Field(..., description="UUID of the page to get, example: 1b25c159-362a-80c2-8aeb-c05f1f880bdc")

class UpdatePageParams(BaseModel):
    page_id: str = Field(..., description="UUID of the page to update, example: 1b25c159-362a-80c2-8aeb-c05f1f880bdc")
    page_update: PageUpdate

class SearchParams(BaseModel):
    query: Optional[str] = ''
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)
    sort_direction: Optional[str] = None

# Response schema classes
class ListDatabasesResponse(BaseModel):
    data: DatabaseList
    message: Optional[str] = None

class GetDatabaseResponse(BaseModel):
    data: Database
    message: Optional[str] = None

class ListDatabasePagesResponse(BaseModel):
    data: PageList
    message: Optional[str] = None

class QueryDatabaseResponse(BaseModel):
    data: PageList
    message: Optional[str] = None

class CreatePageResponse(BaseModel):
    data: Page
    message: Optional[str] = None

class GetPageResponse(BaseModel):
    data: Page
    message: Optional[str] = None

class UpdatePageResponse(BaseModel):
    data: Page
    message: Optional[str] = None

class SearchResponse(BaseModel):
    data: SearchResult
    message: Optional[str] = None

class DatabaseCreate(BaseModel):
    parent: Union[PageParent, WorkspaceParent] = Field(
        ...,
        description="REQUIRED. Parent must be a page or workspace. "
        "Page parent creates inline database, workspace creates full-page database"
    )
    title: List[Dict[str, Any]] = Field(
        ...,
        description="REQUIRED. Database title as rich text array. "
        "Must contain exactly one text object with content",
        example=[{"type": "text", "text": {"content": "Project Tracker"}}]
    )
    properties: Dict[str, PropertyType] = Field(
        ...,
        description="REQUIRED. Initial database schema. Must include exactly one title property. "
        "Property types must match Notion-supported types"
    )
    is_inline: Optional[bool] = False

class CreateDatabaseParams(BaseModel):
    database: DatabaseCreate

class CreateDatabaseResponse(BaseModel):
    data: Database
    message: Optional[str] = None

class AppendBlockChildrenParams(BaseModel):
    block_id: str = Field(..., description="REQUIRED. Valid block ID from existing Notion content")
    children: List[Dict[str, Any]] = Field(
        ...,
        description="REQUIRED. List of block objects to append. "
        "Max 100 blocks per request. Total content size < 50KB."
    )

class AppendBlockChildrenResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class CreatePageWithDatabaseParams(BaseModel):
    page: PageCreate
    database_id: str

class CreatePageWithInlineDatabaseParams(BaseModel):
    page: PageCreate
    database: DatabaseCreate

class NotionUser(BaseModel):
    id: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    type: str
    person: Optional[Dict[str, Any]] = None
    bot: Optional[Dict[str, Any]] = None

class UserList(BaseModel):
    items: List[NotionUser]
    next_cursor: Optional[str] = None

class GetUsersParams(BaseModel):
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)

class GetUserParams(BaseModel):
    user_id: str

class GetUsersResponse(BaseModel):
    data: UserList
    message: Optional[str] = None

class GetUserResponse(BaseModel):
    data: NotionUser
    message: Optional[str] = None


class ApiResponse(BaseModel):
    data: Union[Page, PageList, Database, DatabaseList, SearchResult, UserList, NotionUser, Dict[str, Any], DatabaseProperties]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class DatabaseBlock(BaseModel):
    """Schema for a database block that can be included in page children"""
    type: str = "database"
    object: str = "block"
    database: Dict[str, Any]
