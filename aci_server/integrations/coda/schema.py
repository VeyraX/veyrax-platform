from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Common parameter model
class CommonParams(BaseModel):
    limit: Optional[int] = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )
    page_token: Optional[str] = Field(
        None,
        description="Token for pagination"
    )

# Document parameters
class ListDocsParams(CommonParams):
    is_owner: Optional[bool] = Field(
        None,
        description="If true, only return docs owned by the user"
    )
    query: Optional[str] = Field(
        None,
        description="Search term used to filter results"
    )
    source_doc_id: Optional[str] = Field(
        None,
        description="Show only docs copied from the specified doc"
    )
    workspace_id: Optional[str] = Field(
        None,
        description="Show only docs in the specified workspace"
    )

# Page parameters
class ListPagesParams(CommonParams):
    include_hidden: Optional[bool] = Field(
        False,
        description="If true, include hidden pages in the results"
    )

class CreatePageParams(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Name of the page"
    )
    subtitle: Optional[str] = Field(
        None,
        description="Subtitle of the page"
    )
    icon_name: Optional[str] = Field(
        None,
        description="Name of the icon"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL of the image to use"
    )
    parent_page_id: Optional[str] = Field(
        None,
        description="ID of the parent page for this page"
    )
    page_content: Optional[Dict[str, Any]] = Field(
        None,
        description="Content to populate page with"
    )

class UpdatePageParams(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Name of the page"
    )
    subtitle: Optional[str] = Field(
        None,
        description="Subtitle of the page"
    )
    icon_name: Optional[str] = Field(
        None,
        description="Name of the icon"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL of the image to use"
    )
    is_hidden: Optional[bool] = Field(
        None,
        description="Whether the page is hidden"
    )
    content_update: Optional[Dict[str, Any]] = Field(
        None,
        description="Updates to the page content"
    )

class ExportPageParams(BaseModel):
    output_format: str = Field(
        ...,
        description="Format to export the page in: html or markdown",
        alias="outputFormat"
    )

    class Config:
        populate_by_name = True

# Common response models
class Person(BaseModel):
    context: Optional[str] = Field(None, alias="@context")
    type: Optional[str] = Field(None, alias="@type")
    additional_type: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        populate_by_name = True

class Icon(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    browser_link: Optional[str] = None

class Image(BaseModel):
    browser_link: Optional[str] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class PageReference(BaseModel):
    id: str
    type: str
    href: Optional[str] = None
    browser_link: Optional[str] = None
    name: Optional[str] = None

# Page response model
class Page(BaseModel):
    id: str
    type: str
    href: Optional[str] = None
    browser_link: Optional[str] = None
    name: str
    subtitle: Optional[str] = None
    icon: Optional[Icon] = None
    image: Optional[Image] = None
    content_type: Optional[str] = None
    is_hidden: Optional[bool] = None
    is_effectively_hidden: Optional[bool] = None
    parent: Optional[PageReference] = None
    children: Optional[List[PageReference]] = None
    authors: Optional[List[Person]] = None
    created_at: Optional[str] = None
    created_by: Optional[Person] = None
    updated_at: Optional[str] = None
    updated_by: Optional[Person] = None

class PageList(BaseModel):
    items: List[Page]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None

class PageActionResponse(BaseModel):
    request_id: Optional[str] = Field(None, alias="requestId")
    id: str

    class Config:
        populate_by_name = True

class ExportStatus(BaseModel):
    id: str
    status: str
    href: Optional[str] = None
    download_link: Optional[str] = None
    error: Optional[str] = None

# Table parameters
class ListTablesParams(CommonParams):
    table_types: Optional[List[str]] = Field(
        None,
        description="Types of tables to include"
    )

# Column parameters
class ListColumnsParams(CommonParams):
    visible_only: Optional[bool] = Field(
        False,
        description="If true, only return visible columns"
    )

# Table and Column response models
class ColumnFormat(BaseModel):
    type: Optional[str] = None
    is_array: Optional[bool] = Field(None, alias="isArray")
    label: Optional[str] = None
    disable_if: Optional[str] = Field(None, alias="disableIf")
    action: Optional[str] = None

    class Config:
        populate_by_name = True

class Column(BaseModel):
    id: str
    type: str
    href: Optional[str] = None
    name: str
    display: Optional[bool] = None
    calculated: Optional[bool] = None
    formula: Optional[str] = None
    default_value: Optional[str] = Field(None, alias="defaultValue")
    format: Optional[ColumnFormat] = None
    parent: Optional[PageReference] = None

    class Config:
        populate_by_name = True

class ColumnList(BaseModel):
    items: List[Column]
    href: Optional[str] = None
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")

    class Config:
        populate_by_name = True

class Table(BaseModel):
    id: str
    type: str
    table_type: Optional[str] = Field(None, alias="tableType")
    href: Optional[str] = None
    browser_link: Optional[str] = Field(None, alias="browserLink")
    name: str
    parent: Optional[PageReference] = None
    parent_table: Optional[Dict[str, Any]] = Field(None, alias="parentTable")
    display_column: Optional[Dict[str, Any]] = Field(None, alias="displayColumn")
    row_count: Optional[int] = Field(None, alias="rowCount")
    sorts: Optional[List[Dict[str, Any]]] = None
    layout: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True

class TableList(BaseModel):
    items: List[Table]
    href: Optional[str] = None
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")

    class Config:
        populate_by_name = True

# Row parameters
class ListRowsParams(CommonParams):
    query: Optional[str] = Field(
        None,
        description="Query string to filter rows"
    )
    sort_by: Optional[str] = Field(
        None,
        description="Column ID to sort by",
        alias="sortBy"
    )
    use_column_names: Optional[bool] = Field(
        False,
        description="Use column names instead of IDs in the response",
        alias="useColumnNames"
    )
    value_format: Optional[str] = Field(
        None,
        description="Format of cell values in the response",
        alias="valueFormat"
    )
    sync_token: Optional[str] = Field(
        None,
        description="Token for synchronization",
        alias="syncToken"
    )

    class Config:
        populate_by_name = True

class Cell(BaseModel):
    column: str
    value: Any

class Row(BaseModel):
    cells: List[Cell]

class CreateRowsRequest(BaseModel):
    rows: List[Row]
    key_columns: Optional[List[str]] = Field(None, alias="keyColumns")

    class Config:
        populate_by_name = True

class UpdateRowsRequest(BaseModel):
    rows: List[Row]
    key_columns: Optional[List[str]] = Field(None, alias="keyColumns")

    class Config:
        populate_by_name = True

class DeleteRowsRequest(BaseModel):
    row_ids: List[str] = Field(..., alias="rowIds")

    class Config:
        populate_by_name = True

# Row response models
class RowValue(BaseModel):
    id: str
    type: str
    href: Optional[str] = None
    name: Optional[str] = None
    index: Optional[int] = None
    browser_link: Optional[str] = Field(None, alias="browserLink")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    values: Dict[str, Any]
    parent: Optional[PageReference] = None

    class Config:
        populate_by_name = True

class RowList(BaseModel):
    items: List[RowValue]
    href: Optional[str] = None
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")
    next_sync_token: Optional[str] = Field(None, alias="nextSyncToken")

    class Config:
        populate_by_name = True

class RowActionResponse(BaseModel):
    request_id: str = Field(..., alias="requestId")
    id: Optional[str] = None
    row_id: Optional[str] = Field(None, alias="rowId")
    column_id: Optional[str] = Field(None, alias="columnId")
    added_row_ids: Optional[List[str]] = Field(None, alias="addedRowIds")
    row_ids: Optional[List[str]] = Field(None, alias="rowIds")

    class Config:
        populate_by_name = True

# Formula and Control parameters
class ListFormulasParams(CommonParams):
    pass

class ListControlsParams(CommonParams):
    pass

# Formula and Control response models
class Formula(BaseModel):
    id: str
    type: str
    href: Optional[str] = None
    name: str
    parent: Optional[PageReference] = None
    value: Optional[Any] = None

class FormulaList(BaseModel):
    items: List[Formula]
    href: Optional[str] = None
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")

    class Config:
        populate_by_name = True

class Control(BaseModel):
    id: str
    type: str
    href: Optional[str] = None
    name: str
    parent: Optional[PageReference] = None

class ControlList(BaseModel):
    items: List[Control]
    href: Optional[str] = None
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")

    class Config:
        populate_by_name = True

# User response model
class Workspace(BaseModel):
    id: str
    type: str
    organization_id: Optional[str] = Field(None, alias="organizationId")
    browser_link: Optional[str] = Field(None, alias="browserLink")
    name: Optional[str] = None

    class Config:
        populate_by_name = True

class UserInfo(BaseModel):
    name: str
    login_id: Optional[str] = Field(None, alias="loginId")
    type: str
    picture_link: Optional[str] = Field(None, alias="pictureLink")
    scoped: Optional[bool] = None
    token_name: Optional[str] = Field(None, alias="tokenName")
    href: Optional[str] = None
    workspace: Optional[Workspace] = None

    class Config:
        populate_by_name = True

# API response
class ApiResponse(BaseModel):
    data: Union[
        Page, 
        PageList, 
        PageActionResponse, 
        ExportStatus, 
        Table, 
        TableList, 
        Column, 
        ColumnList, 
        RowValue, 
        RowList, 
        RowActionResponse,
        Formula,
        FormulaList,
        Control,
        ControlList,
        UserInfo
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )

# New models for methods where Dict[str, str] is used
class GetDocParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")

class GetPageParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    page_id: str = Field(..., description="ID of the page")

class DeletePageParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    page_id: str = Field(..., description="ID of the page to delete")

class GetExportStatusParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    page_id: str = Field(..., description="ID of the page")
    request_id: str = Field(..., description="ID of the export request")

class GetTableParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    table_id: str = Field(..., description="ID of the table")

class GetColumnParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    table_id: str = Field(..., description="ID of the table")
    column_id: str = Field(..., description="ID of the column")

class GetRowParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    table_id: str = Field(..., description="ID of the table")
    row_id: str = Field(..., description="ID of the row")

class DeleteRowParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    table_id: str = Field(..., description="ID of the table")
    row_id: str = Field(..., description="ID of the row to delete")

class PushButtonParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    table_id: str = Field(..., description="ID of the table")
    row_id: str = Field(..., description="ID of the row")
    column_id: str = Field(..., description="ID of the button column")

class GetFormulaParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    formula_id: str = Field(..., description="ID of the formula")

class GetControlParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    control_id: str = Field(..., description="ID of the control")

class WhoamiParams(BaseModel):
    """Empty params for whoami endpoint"""
    pass

class UpdateRowParams(BaseModel):
    doc_id: str = Field(..., description="ID of the Coda document")
    table_id: str = Field(..., description="ID of the table")
    row_id: str = Field(..., description="ID of the row to update")
    row: Dict[str, Any] = Field(..., description="Data to update in the row")

class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
