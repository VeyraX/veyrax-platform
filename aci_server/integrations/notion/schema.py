from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
import re
from enum import Enum, StrEnum

# ---------------------------------------------------------------------------------------
# Sort & Timestamp Enums
# ---------------------------------------------------------------------------------------
class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"

class TimestampType(StrEnum):
    CREATED_TIME = "created_time"
    LAST_EDITED_TIME = "last_edited_time"


# ---------------------------------------------------------------------------------------
# Sort Models
# ---------------------------------------------------------------------------------------
class PropertySort(BaseModel):
    property: str = Field(..., description="The name of the property to sort against")
    direction: SortDirection

class TimestampSort(BaseModel):
    timestamp: TimestampType = Field(..., description="The name of the timestamp to sort against")
    direction: SortDirection

Sort = Union[PropertySort, TimestampSort]


# ---------------------------------------------------------------------------------------
# Filter Condition Models
# ---------------------------------------------------------------------------------------
class CheckboxCondition(BaseModel):
    equals: Optional[bool] = None
    does_not_equal: Optional[bool] = None

class DateCondition(BaseModel):
    after: Optional[str] = Field(None, description="ISO 8601 date string")
    before: Optional[str] = Field(None, description="ISO 8601 date string")
    equals: Optional[str] = Field(None, description="ISO 8601 date string")
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None
    next_month: Optional[dict] = None
    next_week: Optional[dict] = None
    next_year: Optional[dict] = None
    on_or_after: Optional[str] = Field(None, description="ISO 8601 date string")
    on_or_before: Optional[str] = Field(None, description="ISO 8601 date string")
    past_month: Optional[dict] = None
    past_week: Optional[dict] = None
    past_year: Optional[dict] = None
    this_week: Optional[dict] = None

class FilesCondition(BaseModel):
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

class NumberCondition(BaseModel):
    equals: Optional[float] = None
    does_not_equal: Optional[float] = None
    greater_than: Optional[float] = None
    greater_than_or_equal_to: Optional[float] = None
    less_than: Optional[float] = None
    less_than_or_equal_to: Optional[float] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

class PeopleCondition(BaseModel):
    contains: Optional[str] = Field(None, description="UUIDv4 string")
    does_not_contain: Optional[str] = Field(None, description="UUIDv4 string")
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

class RelationCondition(BaseModel):
    contains: Optional[str] = Field(None, description="UUIDv4 string")
    does_not_contain: Optional[str] = Field(None, description="UUIDv4 string")
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

class RichTextCondition(BaseModel):
    contains: Optional[str] = None
    does_not_contain: Optional[str] = None
    does_not_equal: Optional[str] = None
    ends_with: Optional[str] = None
    equals: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None
    starts_with: Optional[str] = None

class SelectCondition(BaseModel):
    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

class StatusCondition(BaseModel):
    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

class UniqueIDCondition(BaseModel):
    equals: Optional[int] = None
    does_not_equal: Optional[int] = None
    greater_than: Optional[int] = None
    greater_than_or_equal_to: Optional[int] = None
    less_than: Optional[int] = None
    less_than_or_equal_to: Optional[int] = None


# ---------------------------------------------------------------------------------------
# Filter Models
# ---------------------------------------------------------------------------------------
class TimestampFilter(BaseModel):
    timestamp: TimestampType
    created_time: Optional[DateCondition] = None
    last_edited_time: Optional[DateCondition] = None

class PropertyFilter(BaseModel):
    property: str = Field(..., description="The name of the property to filter against")
    checkbox: Optional[CheckboxCondition] = None
    date: Optional[DateCondition] = None
    files: Optional[FilesCondition] = None
    number: Optional[NumberCondition] = None
    people: Optional[PeopleCondition] = None
    relation: Optional[RelationCondition] = None
    rich_text: Optional[RichTextCondition] = None
    select: Optional[SelectCondition] = None
    status: Optional[StatusCondition] = None
    unique_id: Optional[UniqueIDCondition] = None

# Removed the self-reference (no nested CompoundFilter)
class CompoundFilter(BaseModel):
    and_: Optional[List[Union[PropertyFilter, TimestampFilter]]] = Field(None, alias="and")
    or_: Optional[List[Union[PropertyFilter, TimestampFilter]]] = Field(None, alias="or")

    class Config:
        allow_population_by_field_name = True

Filter = Union[PropertyFilter, TimestampFilter, CompoundFilter]


# ---------------------------------------------------------------------------------------
# Sorting & Filtering Request Models
# ---------------------------------------------------------------------------------------
class DatabaseFilters(BaseModel):
    search_query: Optional[str] = Field(None, description="Search query to filter database entries")
    filter_by: Optional[Filter] = Field(
        None,
        description="Filter conditions using property filters and/or compound filters"
    )
    sort_by: Optional[Sort] = Field(
        None,
        description="Sort object for ordering database entries"
    )
    max_results: Optional[int] = Field(
        default=100,
        le=100,
        description="Maximum number of results to return (max: 100)"
    )

class PageFilters(BaseModel):
    query: Optional[str] = Field(
        None,
        description="Search query to filter pages"
    )
    filter_by: Optional[Filter] = Field(
        None,
        description="Filter conditions using property filters and/or compound filters"
    )
    sort_by: Optional[Sort] = Field(
        None,
        description="Sort object for ordering pages"
    )
    sort_direction: Optional[SortDirection] = Field(
        None,
        description="Direction to sort results (ascending or descending)"
    )
    max_results: Optional[int] = Field(
        default=100,
        le=100,
        description="Maximum number of results to return (max: 100)"
    )


# ---------------------------------------------------------------------------------------
# Fundamental Database/Page Models
# ---------------------------------------------------------------------------------------
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

class Page(BaseModel):
    id: str
    title: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None

# ---------------------------------------------------------------------------------------
# Parent Models
# ---------------------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------------------
# Create & Update Models
# ---------------------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------------------
# Database Property Models
# ---------------------------------------------------------------------------------------
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

class SelectOption(BaseModel):
    id: Optional[str] = Field(None, description="An identifier for the option. It doesn't change if the name is changed")
    name: str = Field(..., description="The name of the option as it appears in the Notion UI")
    color: Optional[Color] = Field(Color.DEFAULT, description="The color of the option as rendered in the Notion UI")

class TitleProperty(BaseModel):
    pass

class RichTextProperty(BaseModel):
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
    pass

class PeopleProperty(BaseModel):
    pass

class FilesProperty(BaseModel):
    pass

class CheckboxProperty(BaseModel):
    pass

class URLProperty(BaseModel):
    pass

class EmailProperty(BaseModel):
    pass

class PhoneNumberProperty(BaseModel):
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
    pass

class CreatedByProperty(BaseModel):
    pass

class LastEditedTimeProperty(BaseModel):
    pass

class LastEditedByProperty(BaseModel):
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

class PropertyType(BaseModel):
    id: str = Field(..., description="Identifier for the property")
    type: PropertyKind = Field(
        ...,
        description="REQUIRED. Must match Notion database property type",
        example=PropertyKind.TITLE
    )
    name: str = Field(..., description="The name of the property as it appears in Notion")
    description: Optional[str] = Field(None, description="The description of the property as it appears in Notion")
    
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

class PropertyTypeUpdate(BaseModel):
    id: Optional[str] = Field(None, description="Identifier for the property, optional for new properties")
    type: PropertyKind = Field(
        ...,
        description="REQUIRED. Must match Notion database property type",
        example=PropertyKind.TITLE
    )
    name: Optional[str] = Field(None, description="The name of the property as it appears in Notion")
    description: Optional[str] = Field(None, description="The description of the property as it appears in Notion")
    
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


# ---------------------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------------------
class ListPagesRequest(BaseModel):
    start_cursor: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    page_size: Optional[int] = Field(
        default=100,
        le=100,
        description="REQUIRED MAX: 100. Use pagination for more results"
    )

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
    filter: Optional[Filter] = Field(
        None,
        description="Filter conditions using property filters and/or compound filters"
    )
    sorts: Optional[List[Sort]] = Field(
        None,
        description="Array of sort objects. Can sort by property values or timestamps"
    )
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)

class CreatePageParams(BaseModel):
    page: PageCreate

class GetPageParams(BaseModel):
    page_id: str = Field(..., description="UUID of the page to get")

class UpdatePageParams(BaseModel):
    page_id: str = Field(..., description="UUID of the page to update")
    page_update: PageUpdate

class SearchParams(BaseModel):
    query: Optional[str] = ''
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=100, le=100)
    sort_direction: Optional[str] = None


# ---------------------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------------------
# Notion Block Types & Models
# ---------------------------------------------------------------------------------------
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

class ParagraphBlock(Block):
    type: str = BlockType.PARAGRAPH
    paragraph: Dict[str, Any] = Field(...)

class HeadingOneBlock(Block):
    type: str = BlockType.HEADING_1
    heading_1: Dict[str, Any] = Field(...)

class HeadingTwoBlock(Block):
    type: str = BlockType.HEADING_2
    heading_2: Dict[str, Any] = Field(...)

class HeadingThreeBlock(Block):
    type: str = BlockType.HEADING_3
    heading_3: Dict[str, Any] = Field(...)

class BulletedListItemBlock(Block):
    type: str = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: Dict[str, Any] = Field(...)

class NumberedListItemBlock(Block):
    type: str = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: Dict[str, Any] = Field(...)

class ToDoBlock(Block):
    type: str = BlockType.TO_DO
    to_do: Dict[str, Any] = Field(...)

class ToggleBlock(Block):
    type: str = BlockType.TOGGLE
    toggle: Dict[str, Any] = Field(...)

class CodeBlock(Block):
    type: str = BlockType.CODE
    code: Dict[str, Any] = Field(...)

class CalloutBlock(Block):
    type: str = BlockType.CALLOUT
    callout: Dict[str, Any] = Field(...)

class QuoteBlock(Block):
    type: str = BlockType.QUOTE
    quote: Dict[str, Any] = Field(...)

class DividerBlock(Block):
    type: str = BlockType.DIVIDER
    divider: Dict[str, Any] = Field(default_factory=dict)

class EmbedBlock(Block):
    type: str = BlockType.EMBED
    embed: Dict[str, Any] = Field(...)

class BookmarkBlock(Block):
    type: str = BlockType.BOOKMARK
    bookmark: Dict[str, Any] = Field(...)

class ImageBlock(Block):
    type: str = BlockType.IMAGE
    image: Dict[str, Any] = Field(...)

class VideoBlock(Block):
    type: str = BlockType.VIDEO
    video: Dict[str, Any] = Field(...)

class FileBlock(Block):
    type: str = BlockType.FILE
    file: Dict[str, Any] = Field(...)

class PDFBlock(Block):
    type: str = BlockType.PDF
    pdf: Dict[str, Any] = Field(...)

class TableBlock(Block):
    type: str = BlockType.TABLE
    table: Dict[str, Any] = Field(...)

class TableRowBlock(Block):
    type: str = BlockType.TABLE_ROW
    table_row: Dict[str, Any] = Field(...)

class ColumnListBlock(Block):
    type: str = BlockType.COLUMN_LIST
    column_list: Dict[str, Any] = Field(default_factory=dict)

class ColumnBlock(Block):
    type: str = BlockType.COLUMN
    column: Dict[str, Any] = Field(default_factory=dict)

class EquationBlock(Block):
    type: str = BlockType.EQUATION
    equation: Dict[str, Any] = Field(...)

class TableOfContentsBlock(Block):
    type: str = BlockType.TABLE_OF_CONTENTS
    table_of_contents: Dict[str, Any] = Field(...)

class BreadcrumbBlock(Block):
    type: str = BlockType.BREADCRUMB
    breadcrumb: Dict[str, Any] = Field(default_factory=dict)

class SyncedBlock(Block):
    type: str = BlockType.SYNCED_BLOCK
    synced_block: Dict[str, Any] = Field(...)

class TemplateBlock(Block):
    type: str = BlockType.TEMPLATE
    template: Dict[str, Any] = Field(...)

class LinkPreviewBlock(Block):
    type: str = BlockType.LINK_PREVIEW
    link_preview: Dict[str, Any] = Field(...)

class LinkToPageBlock(Block):
    type: str = BlockType.LINK_TO_PAGE
    link_to_page: Dict[str, Any] = Field(...)

class ChildPageBlock(Block):
    type: str = BlockType.CHILD_PAGE
    child_page: Dict[str, Any] = Field(...)

class ChildDatabaseBlock(Block):
    type: str = BlockType.CHILD_DATABASE
    child_database: Dict[str, Any] = Field(...)

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

class DatabaseBlock(BaseModel):
    """Schema for a database block that can be included in page children"""
    type: str = "database"
    object: str = "block"
    database: Dict[str, Any]

class DatabaseUpdate(BaseModel):
    title: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Array of rich text objects representing the title. If omitted, title remains unchanged."
    )
    description: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Array of rich text objects representing the description. If omitted, description remains unchanged."
    )
    properties: Optional[Dict[str, PropertyTypeUpdate]] = Field(
        None,
        description="Properties to update or add. Keys are property names/IDs, values are property schema objects."
    )

class UpdateDatabaseParams(BaseModel):
    database_id: str = Field(..., description="Identifier for the Notion database to update")
    database_update: DatabaseUpdate = Field(..., description="The updates to apply to the database")

class UpdateDatabaseResponse(BaseModel):
    data: Database
    message: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[
        Page, 
        PageList, 
        Database, 
        DatabaseList, 
        SearchResult, 
        UserList, 
        NotionUser, 
        Dict[str, Any], 
        DatabaseProperties, 
        UpdateDatabaseResponse
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
