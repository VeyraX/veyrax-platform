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
    STATUS = "status"

class Color(StrEnum):
    BLUE = "blue"
    BROWN = "brown"
    DEFAULT = "default"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"

# Database property option models
class SelectOption(BaseModel):
    id: Optional[str] = Field(None, description="An identifier for the option. It doesn't change if the name is changed")
    name: str = Field(..., description="The name of the option as it appears in the Notion UI")
    color: Optional[Color] = Field(Color.DEFAULT, description="The color of the option as rendered in the Notion UI")

# Database property type-specific configuration models
class TitleProperty(BaseModel):
    """Title property configuration - empty object as there's no additional configuration"""
    pass

class RichTextProperty(BaseModel):
    """Rich text property configuration - empty object as there's no additional configuration"""
    pass

class NumberProperty(BaseModel):
    format: Optional[str] = Field(
        "number", 
        description="The way that the number is displayed in Notion (e.g., dollar, percent, etc.)"
    )

class SelectProperty(BaseModel):
    options: List[SelectOption] = Field(
        default_factory=list, 
        description="List of options available for this select property"
    )

class MultiSelectProperty(BaseModel):
    options: List[SelectOption] = Field(
        default_factory=list, 
        description="List of options available for this multi-select property"
    )

class DateProperty(BaseModel):
    """Date property configuration - empty object as there's no additional configuration"""
    pass

class PeopleProperty(BaseModel):
    """People property configuration - empty object as there's no additional configuration"""
    pass

class FilesProperty(BaseModel):
    """Files property configuration - empty object as there's no additional configuration"""
    pass

class CheckboxProperty(BaseModel):
    """Checkbox property configuration - empty object as there's no additional configuration"""
    pass

class URLProperty(BaseModel):
    """URL property configuration - empty object as there's no additional configuration"""
    pass

class EmailProperty(BaseModel):
    """Email property configuration - empty object as there's no additional configuration"""
    pass

class PhoneNumberProperty(BaseModel):
    """Phone number property configuration - empty object as there's no additional configuration"""
    pass

class FormulaProperty(BaseModel):
    expression: str = Field(
        ..., 
        description="The formula that is used to compute the values for this property",
        example="prop(\"Price\") * 2"
    )

class RelationProperty(BaseModel):
    database_id: str = Field(
        ..., 
        description="The database that the relation property refers to",
        example="668d797c-76fa-4934-9b05-ad288df2d136"
    )
    synced_property_id: Optional[str] = Field(
        None, 
        description="The id of the corresponding property that is updated in the related database"
    )
    synced_property_name: Optional[str] = Field(
        None, 
        description="The name of the corresponding property that is updated in the related database"
    )

class RollupProperty(BaseModel):
    relation_property_id: str = Field(
        ..., 
        description="The id of the related database property that is rolled up"
    )
    relation_property_name: str = Field(
        ..., 
        description="The name of the related database property that is rolled up"
    )
    rollup_property_id: str = Field(
        ..., 
        description="The id of the rollup property"
    )
    rollup_property_name: str = Field(
        ..., 
        description="The name of the rollup property"
    )
    function: str = Field(
        ..., 
        description="The function that computes the rollup value from the related pages",
        example="sum"
    )

class CreatedTimeProperty(BaseModel):
    """Created time property configuration - empty object as there's no additional configuration"""
    pass

class CreatedByProperty(BaseModel):
    """Created by property configuration - empty object as there's no additional configuration"""
    pass

class LastEditedTimeProperty(BaseModel):
    """Last edited time property configuration - empty object as there's no additional configuration"""
    pass

class LastEditedByProperty(BaseModel):
    """Last edited by property configuration - empty object as there's no additional configuration"""
    pass

class StatusGroup(BaseModel):
    id: str = Field(..., description="Identifier for the group")
    name: str = Field(..., description="Name of the group as it appears in Notion")
    color: Color = Field(..., description="Color of the group")
    option_ids: List[str] = Field(..., description="List of option IDs that belong to this group")

class StatusProperty(BaseModel):
    options: List[SelectOption] = Field(
        ..., 
        description="List of status options available for this property"
    )
    groups: List[StatusGroup] = Field(
        ..., 
        description="Groups that organize the status options"
    )

# Updated PropertyType model to include all specific property configurations
class PropertyType(BaseModel):
    id: str = Field(..., description="Identifier for the property")
    type: PropertyKind = Field(
        ...,
        description="REQUIRED. Must match Notion database property type",
        example=PropertyKind.TITLE
    )
    name: str = Field(..., description="The name of the property as it appears in Notion")
    description: Optional[str] = Field(None, description="The description of the property as it appears in Notion")
    
    # Type-specific configurations
    title: Optional[TitleProperty] = None
    rich_text: Optional[RichTextProperty] = None
    number: Optional[NumberProperty] = None
    select: Optional[SelectProperty] = None
    multi_select: Optional[MultiSelectProperty] = None
    date: Optional[DateProperty] = None
    people: Optional[PeopleProperty] = None
    files: Optional[FilesProperty] = None
    checkbox: Optional[CheckboxProperty] = None
    url: Optional[URLProperty] = None
    email: Optional[EmailProperty] = None
    phone_number: Optional[PhoneNumberProperty] = None
    formula: Optional[FormulaProperty] = None
    relation: Optional[RelationProperty] = None
    rollup: Optional[RollupProperty] = None
    created_time: Optional[CreatedTimeProperty] = None
    created_by: Optional[CreatedByProperty] = None
    last_edited_time: Optional[LastEditedTimeProperty] = None
    last_edited_by: Optional[LastEditedByProperty] = None
    status: Optional[StatusProperty] = None

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

# Improved DatabaseCreate model with updated properties field
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
    properties: Dict[str, Any] = Field(
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

# Notion Block Types
class BlockType(StrEnum):
    BOOKMARK = "bookmark"
    BREADCRUMB = "breadcrumb"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    CALLOUT = "callout"
    CHILD_DATABASE = "child_database"
    CHILD_PAGE = "child_page"
    CODE = "code"
    COLUMN = "column"
    COLUMN_LIST = "column_list"
    DIVIDER = "divider"
    EMBED = "embed"
    EQUATION = "equation"
    FILE = "file"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    IMAGE = "image"
    LINK_PREVIEW = "link_preview"
    LINK_TO_PAGE = "link_to_page"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    PARAGRAPH = "paragraph"
    PDF = "pdf"
    QUOTE = "quote"
    SYNCED_BLOCK = "synced_block"
    TABLE = "table"
    TABLE_OF_CONTENTS = "table_of_contents"
    TABLE_ROW = "table_row"
    TEMPLATE = "template"
    TO_DO = "to_do"
    TOGGLE = "toggle"
    VIDEO = "video"
    UNSUPPORTED = "unsupported"

# Extended Color enum for background colors
class Color(StrEnum):
    BLUE = "blue"
    BLUE_BACKGROUND = "blue_background"
    BROWN = "brown"
    BROWN_BACKGROUND = "brown_background"
    DEFAULT = "default"
    GRAY = "gray"
    GRAY_BACKGROUND = "gray_background"
    GREEN = "green"
    GREEN_BACKGROUND = "green_background"
    ORANGE = "orange"
    ORANGE_BACKGROUND = "orange_background"
    PINK = "pink"
    PINK_BACKGROUND = "pink_background"
    PURPLE = "purple"
    PURPLE_BACKGROUND = "purple_background"
    RED = "red"
    RED_BACKGROUND = "red_background"
    YELLOW = "yellow"
    YELLOW_BACKGROUND = "yellow_background"

# Rich Text Objects
class Annotations(BaseModel):
    bold: Optional[bool] = False
    italic: Optional[bool] = False
    strikethrough: Optional[bool] = False
    underline: Optional[bool] = False
    code: Optional[bool] = False
    color: Optional[Color] = Color.DEFAULT

class TextContent(BaseModel):
    content: str
    link: Optional[Dict[str, str]] = None

class TextObject(BaseModel):
    type: str = "text"
    text: TextContent
    annotations: Optional[Annotations] = None
    plain_text: Optional[str] = None
    href: Optional[str] = None

class MentionObject(BaseModel):
    type: str = "mention"
    mention: Dict[str, Any]
    annotations: Optional[Annotations] = None
    plain_text: Optional[str] = None
    href: Optional[str] = None

class EquationObject(BaseModel):
    type: str = "equation"
    equation: Dict[str, str]
    annotations: Optional[Annotations] = None
    plain_text: Optional[str] = None
    href: Optional[str] = None

RichTextObject = Union[TextObject, MentionObject, EquationObject]

# Base Block model
class Block(BaseModel):
    object: str = "block"
    id: Optional[str] = None
    parent: Optional[Parent] = None
    created_time: Optional[str] = None
    created_by: Optional[Dict[str, Any]] = None
    last_edited_time: Optional[str] = None
    last_edited_by: Optional[Dict[str, Any]] = None
    has_children: Optional[bool] = None
    archived: Optional[bool] = None
    in_trash: Optional[bool] = None
    type: str

# Block Type specific models
class ParagraphBlock(Block):
    type: str = BlockType.PARAGRAPH
    paragraph: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Example text"}}],
        "color": "default"
    })

class HeadingOneBlock(Block):
    type: str = BlockType.HEADING_1
    heading_1: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Heading 1"}}],
        "color": "default",
        "is_toggleable": False
    })

class HeadingTwoBlock(Block):
    type: str = BlockType.HEADING_2
    heading_2: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Heading 2"}}],
        "color": "default",
        "is_toggleable": False
    })

class HeadingThreeBlock(Block):
    type: str = BlockType.HEADING_3
    heading_3: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Heading 3"}}],
        "color": "default",
        "is_toggleable": False
    })

class BulletedListItemBlock(Block):
    type: str = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Bulleted item"}}],
        "color": "default"
    })

class NumberedListItemBlock(Block):
    type: str = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Numbered item"}}],
        "color": "default"
    })

class ToDoBlock(Block):
    type: str = BlockType.TO_DO
    to_do: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "To do item"}}],
        "checked": False,
        "color": "default"
    })

class ToggleBlock(Block):
    type: str = BlockType.TOGGLE
    toggle: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Toggle"}}],
        "color": "default"
    })

class CodeBlock(Block):
    type: str = BlockType.CODE
    code: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "console.log('Hello World')"}}],
        "language": "javascript",
        "caption": []
    })

class CalloutBlock(Block):
    type: str = BlockType.CALLOUT
    callout: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Callout"}}],
        "icon": {"emoji": "💡"},
        "color": "default"
    })

class QuoteBlock(Block):
    type: str = BlockType.QUOTE
    quote: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Quote"}}],
        "color": "default"
    })

class DividerBlock(Block):
    type: str = BlockType.DIVIDER
    divider: Dict[str, Any] = Field(default_factory=dict)

class EmbedBlock(Block):
    type: str = BlockType.EMBED
    embed: Dict[str, Any] = Field(..., example={
        "url": "https://example.com"
    })

class BookmarkBlock(Block):
    type: str = BlockType.BOOKMARK
    bookmark: Dict[str, Any] = Field(..., example={
        "url": "https://example.com",
        "caption": []
    })

class ImageBlock(Block):
    type: str = BlockType.IMAGE
    image: Dict[str, Any] = Field(..., example={
        "type": "external",
        "external": {"url": "https://example.com/image.jpg"}
    })

class VideoBlock(Block):
    type: str = BlockType.VIDEO
    video: Dict[str, Any] = Field(..., example={
        "type": "external",
        "external": {"url": "https://example.com/video.mp4"}
    })

class FileBlock(Block):
    type: str = BlockType.FILE
    file: Dict[str, Any] = Field(..., example={
        "type": "external",
        "external": {"url": "https://example.com/file.pdf"},
        "caption": []
    })

class PDFBlock(Block):
    type: str = BlockType.PDF
    pdf: Dict[str, Any] = Field(..., example={
        "type": "external",
        "external": {"url": "https://example.com/document.pdf"}
    })

class TableBlock(Block):
    type: str = BlockType.TABLE
    table: Dict[str, Any] = Field(..., example={
        "table_width": 3,
        "has_column_header": False,
        "has_row_header": False,
        "children": [
            {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [
                        [{"type": "text", "text": {"content": "Cell content"}}]
                    ]
                }
            }
        ]
    })

class TableRowBlock(Block):
    type: str = BlockType.TABLE_ROW
    table_row: Dict[str, Any] = Field(..., example={
        "cells": [[{"type": "text", "text": {"content": "Cell content"}}]]
    })

class ColumnListBlock(Block):
    type: str = BlockType.COLUMN_LIST
    column_list: Dict[str, Any] = Field(default_factory=dict)

class ColumnBlock(Block):
    type: str = BlockType.COLUMN
    column: Dict[str, Any] = Field(default_factory=dict)

class EquationBlock(Block):
    type: str = BlockType.EQUATION
    equation: Dict[str, Any] = Field(..., example={
        "expression": "e=mc^2"
    })

class TableOfContentsBlock(Block):
    type: str = BlockType.TABLE_OF_CONTENTS
    table_of_contents: Dict[str, Any] = Field(..., example={
        "color": "default"
    })

class BreadcrumbBlock(Block):
    type: str = BlockType.BREADCRUMB
    breadcrumb: Dict[str, Any] = Field(default_factory=dict)

class SyncedBlock(Block):
    type: str = BlockType.SYNCED_BLOCK
    synced_block: Dict[str, Any] = Field(..., example={
        "synced_from": None
    })

class TemplateBlock(Block):
    type: str = BlockType.TEMPLATE
    template: Dict[str, Any] = Field(..., example={
        "rich_text": [{"type": "text", "text": {"content": "Template"}}]
    })

class LinkPreviewBlock(Block):
    type: str = BlockType.LINK_PREVIEW
    link_preview: Dict[str, Any] = Field(..., example={
        "url": "https://example.com"
    })

class LinkToPageBlock(Block):
    type: str = BlockType.LINK_TO_PAGE
    link_to_page: Dict[str, Any] = Field(..., example={
        "type": "page_id",
        "page_id": "123e4567-e89b-12d3-a456-426614174000"
    })

class ChildPageBlock(Block):
    type: str = BlockType.CHILD_PAGE
    child_page: Dict[str, Any] = Field(..., example={
        "title": "Page title"
    })

class ChildDatabaseBlock(Block):
    type: str = BlockType.CHILD_DATABASE
    child_database: Dict[str, Any] = Field(..., example={
        "title": "Database title"
    })

# Union of all block types
NotionBlock = Union[
    ParagraphBlock, 
    HeadingOneBlock, 
    HeadingTwoBlock, 
    HeadingThreeBlock,
    BulletedListItemBlock,
    NumberedListItemBlock,
    ToDoBlock,
    ToggleBlock,
    CodeBlock,
    CalloutBlock,
    QuoteBlock,
    DividerBlock,
    EmbedBlock,
    BookmarkBlock,
    ImageBlock,
    VideoBlock,
    FileBlock,
    PDFBlock,
    TableBlock,
    TableRowBlock,
    ColumnListBlock,
    ColumnBlock,
    EquationBlock,
    TableOfContentsBlock,
    BreadcrumbBlock,
    SyncedBlock,
    TemplateBlock,
    LinkPreviewBlock,
    LinkToPageBlock,
    ChildPageBlock,
    ChildDatabaseBlock
]

class AppendBlockChildrenParams(BaseModel):
    block_id: str = Field(..., description="REQUIRED. Valid block ID from existing Notion content")
    children: List[NotionBlock] = Field(
        ...,
        description="REQUIRED. List of block objects to append. "
        "Max 100 blocks per request. Total content size < 50KB."
    )
    after: Optional[str] = Field(
        None,
        description="The ID of the existing block that the new block should be appended after."
    )

class AppendBlockChildrenResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class AppendMediaParams(BaseModel):
    block_id: str = Field(..., description="REQUIRED. Valid block ID from existing Notion content")
    media_type: str = Field(
        ..., 
        description="Type of media block: 'file', 'image', or 'pdf'",
        example="image"
    )
    url: str = Field(
        ..., 
        description="URL of the media file",
        example="https://example.com/image.jpg"
    )
    caption: Optional[str] = Field(
        None, 
        description="Optional caption for the media",
        example="Project diagram"
    )
    name: Optional[str] = Field(
        None, 
        description="Optional filename for file blocks",
        example="document.pdf"
    )

class AppendMediaResponse(BaseModel):
    data: Page
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
