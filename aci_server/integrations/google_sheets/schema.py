from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class SpreadsheetMetadata(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    sheets: List[Dict[str, Any]]

class SpreadsheetValues(BaseModel):
    spreadsheet_id: str
    sheet_title: Optional[str] = None
    range: str
    values: List[List[Any]]
    majorDimension: Optional[str] = "ROWS"

class SpreadsheetValuesBatch(BaseModel):
    spreadsheet_id: str
    value_ranges: List[Dict[str, Any]]

class SpreadsheetUpdateResult(BaseModel):
    spreadsheet_id: str
    updated_range: str
    updated_cells: int
    updated_rows: Optional[int] = None
    updated_columns: Optional[int] = None

class SheetFilters(BaseModel):
    title_contains: Optional[str] = None
    max_results: Optional[int] = 20

# Request Schema
class GetSpreadsheetParams(BaseModel):
    spreadsheet_id: str

class GetSpreadsheetValuesParams(BaseModel):
    spreadsheet_id: str
    range: str

class GetSpreadsheetValuesBatchParams(BaseModel):
    spreadsheet_id: str
    ranges: List[str]

class UpdateSpreadsheetValuesParams(BaseModel):
    spreadsheet_id: str
    range: str
    values: List[List[Any]]
    value_input_option: Optional[str] = "RAW"

class AppendSpreadsheetValuesParams(BaseModel):
    spreadsheet_id: str
    range: str
    values: List[List[Any]]
    value_input_option: Optional[str] = "RAW"

class ClearSpreadsheetValuesParams(BaseModel):
    spreadsheet_id: str
    range: str

class CreateSpreadsheetParams(BaseModel):
    title: str

class AddSheetParams(BaseModel):
    spreadsheet_id: str
    sheet_title: str

class DeleteSheetParams(BaseModel):
    spreadsheet_id: str
    sheet_id: int

class ListSpreadsheetsParams(BaseModel):
    filters: Optional[SheetFilters] = None
    pageToken: Optional[str] = None

class GetSpreadsheetResponse(BaseModel):
    data: SpreadsheetMetadata
    message: Optional[str] = None

class GetSpreadsheetValuesResponse(BaseModel):
    data: SpreadsheetValues
    message: Optional[str] = None

class GetSpreadsheetValuesBatchResponse(BaseModel):
    data: SpreadsheetValuesBatch
    message: Optional[str] = None

class UpdateSpreadsheetValuesResponse(BaseModel):
    data: SpreadsheetUpdateResult
    message: Optional[str] = None

class AppendSpreadsheetValuesResponse(BaseModel):
    data: SpreadsheetUpdateResult
    message: Optional[str] = None

class ClearSpreadsheetValuesResponse(BaseModel):
    data: Dict[str, str]
    message: Optional[str] = None

class CreateSpreadsheetResponse(BaseModel):
    data: SpreadsheetMetadata
    message: Optional[str] = None

class AddSheetResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class DeleteSheetResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class ListSpreadsheetsResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

# New schema classes for search and formulas
class SearchResult(BaseModel):
    matches: List[Dict[str, Any]]
    total_found: int

class SpreadsheetFormulas(BaseModel):
    spreadsheet_id: str
    range: str
    formulas: List[List[Any]]
    majorDimension: Optional[str] = "ROWS"

class FormulaResult(BaseModel):
    spreadsheet_id: str
    range: str
    applied: bool
    formula: str

# Request Schema classes
class SearchSpreadsheetParams(BaseModel):
    spreadsheet_id: str
    search_term: str
    ranges: Optional[List[str]] = None
    case_sensitive: Optional[bool] = False

class GetFormulasParams(BaseModel):
    spreadsheet_id: str
    range: str

class AddFormulaParams(BaseModel):
    spreadsheet_id: str
    range: str
    formula: str

# Response Schema classes
class SearchSpreadsheetResponse(BaseModel):
    data: SearchResult
    message: Optional[str] = None

class GetFormulasResponse(BaseModel):
    data: SpreadsheetFormulas
    message: Optional[str] = None

class AddFormulaResponse(BaseModel):
    data: FormulaResult
    message: Optional[str] = None

# Update ApiResponse to include new response types
class ApiResponse(BaseModel):
    data: Union[
        SpreadsheetMetadata, SpreadsheetValues, SpreadsheetValuesBatch, 
        SpreadsheetUpdateResult, DeleteSheetResponse, AddSheetResponse, 
        ListSpreadsheetsResponse, CreateSpreadsheetResponse, 
        GetSpreadsheetValuesResponse, GetSpreadsheetValuesBatchResponse, 
        UpdateSpreadsheetValuesResponse, AppendSpreadsheetValuesResponse, 
        ClearSpreadsheetValuesResponse, GetSpreadsheetResponse, 
        SearchResult, SpreadsheetFormulas, FormulaResult,  # New types
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None