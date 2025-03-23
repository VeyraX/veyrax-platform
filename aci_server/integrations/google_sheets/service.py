from typing import Optional, Dict, Any, List, Union
from .client import GoogleSheetsClient
from .schema import (
    SpreadsheetMetadata, SpreadsheetValues, SpreadsheetValuesBatch,
    SpreadsheetUpdateResult, SheetFilters, ApiResponse,
    SearchResult, SpreadsheetFormulas, FormulaResult 
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class GoogleSheetsService:
    def __init__(self, client: GoogleSheetsClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "google_sheets"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_spreadsheet(self, spreadsheet_id: str) -> ApiResponse:
        spreadsheet_data = self.client.get_spreadsheet(spreadsheet_id)
        
        sheets = []
        for sheet in spreadsheet_data.get('sheets', []):
            properties = sheet.get('properties', {})
            sheets.append({
                'id': properties.get('sheetId'),
                'title': properties.get('title'),
                'index': properties.get('index'),
                'rowCount': properties.get('gridProperties', {}).get('rowCount'),
                'columnCount': properties.get('gridProperties', {}).get('columnCount')
            })
        
        metadata = SpreadsheetMetadata(
            id=spreadsheet_data['spreadsheetId'],
            title=spreadsheet_data['properties']['title'],
            url=f"https://docs.google.com/spreadsheets/d/{spreadsheet_data['spreadsheetId']}",
            sheets=sheets
        )
        
        return self.prepare_response(metadata, "GoogleSheetsSpreadsheetCard")
    
    def get_spreadsheet_values(self, spreadsheet_id: str, range_name: str) -> ApiResponse:
        response = self.client.get_spreadsheet_values(spreadsheet_id, range_name)
        
        result = SpreadsheetValues(
            spreadsheet_id=spreadsheet_id,
            range=response.get('range', ''),
            values=response.get('values', []),
            majorDimension=response.get('majorDimension', 'ROWS')
        )
        
        # If range includes sheet name, extract it
        if '!' in response.get('range', ''):
            sheet_title = response.get('range', '').split('!')[0].strip("'")
            result.sheet_title = sheet_title
        
        return self.prepare_response(result, "GoogleSheetsDataTable")
    
    def get_spreadsheet_values_batch(self, spreadsheet_id: str, ranges: List[str]) -> ApiResponse:
        response = self.client.get_spreadsheet_values_batch(spreadsheet_id, ranges)
        
        result = SpreadsheetValuesBatch(
            spreadsheet_id=spreadsheet_id,
            value_ranges=response.get('valueRanges', [])
        )
        
        return self.prepare_response(result, "GoogleSheetsDataTableBatch")
    
    def update_spreadsheet_values(self, spreadsheet_id: str, range_name: str, 
                                 values: List[List[Any]], value_input_option: str = "RAW") -> ApiResponse:
        response = self.client.update_spreadsheet_values(
            spreadsheet_id, range_name, values, value_input_option
        )
        
        result = SpreadsheetUpdateResult(
            spreadsheet_id=spreadsheet_id,
            updated_range=response.get('updatedRange', ''),
            updated_cells=response.get('updatedCells', 0),
            updated_rows=response.get('updatedRows', 0),
            updated_columns=response.get('updatedColumns', 0)
        )
        
        return self.prepare_response(result, "GoogleSheetsUpdateResult")
    
    def append_spreadsheet_values(self, spreadsheet_id: str, range_name: str, 
                                 values: List[List[Any]], value_input_option: str = "RAW") -> ApiResponse:
        response = self.client.append_spreadsheet_values(
            spreadsheet_id, range_name, values, value_input_option
        )
        
        result = SpreadsheetUpdateResult(
            spreadsheet_id=spreadsheet_id,
            updated_range=response.get('updates', {}).get('updatedRange', ''),
            updated_cells=response.get('updates', {}).get('updatedCells', 0),
            updated_rows=response.get('updates', {}).get('updatedRows', 0),
            updated_columns=response.get('updates', {}).get('updatedColumns', 0)
        )
        
        return self.prepare_response(result, "GoogleSheetsUpdateResult")
    
    def clear_spreadsheet_values(self, spreadsheet_id: str, range_name: str) -> ApiResponse:
        response = self.client.clear_spreadsheet_values(spreadsheet_id, range_name)
        
        return self.prepare_response({
            'spreadsheet_id': spreadsheet_id,
            'cleared_range': response.get('clearedRange', ''),
            'message': 'Values cleared successfully'
        }, "GoogleSheetsClearResult")
    
    def create_spreadsheet(self, title: str) -> ApiResponse:
        spreadsheet_data = self.client.create_spreadsheet(title)
        
        metadata = SpreadsheetMetadata(
            id=spreadsheet_data['spreadsheetId'],
            title=spreadsheet_data['properties']['title'],
            url=f"https://docs.google.com/spreadsheets/d/{spreadsheet_data['spreadsheetId']}",
            sheets=[{
                'id': sheet.get('properties', {}).get('sheetId'),
                'title': sheet.get('properties', {}).get('title'),
                'index': sheet.get('properties', {}).get('index'),
                'rowCount': sheet.get('properties', {}).get('gridProperties', {}).get('rowCount'),
                'columnCount': sheet.get('properties', {}).get('gridProperties', {}).get('columnCount')
            } for sheet in spreadsheet_data.get('sheets', [])]
        )
        
        return self.prepare_response(metadata, "GoogleSheetsSpreadsheetCard")
    
    def add_sheet(self, spreadsheet_id: str, sheet_title: str) -> ApiResponse:
        response = self.client.add_sheet(spreadsheet_id, sheet_title)
        
        return self.prepare_response({
            'spreadsheet_id': spreadsheet_id,
            'sheet_id': response.get('replies', [{}])[0].get('addSheet', {}).get('properties', {}).get('sheetId'),
            'sheet_title': sheet_title,
            'message': 'Sheet added successfully'
        }, "GoogleSheetsActionResult")
    
    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> ApiResponse:
        self.client.delete_sheet(spreadsheet_id, sheet_id)
        
        return self.prepare_response({
            'spreadsheet_id': spreadsheet_id,
            'sheet_id': sheet_id,
            'message': 'Sheet deleted successfully'
        }, "GoogleSheetsActionResult")

    def search_in_spreadsheet(self, spreadsheet_id: str, search_term: str, 
                             ranges: Optional[List[str]] = None, 
                             case_sensitive: bool = False) -> ApiResponse:
        """
        Search for a term in a spreadsheet
        """
        response = self.client.search_in_spreadsheet(
            spreadsheet_id, ranges, search_term, case_sensitive
        )
        
        result = SearchResult(
            matches=response.get('matches', []),
            total_found=response.get('total_found', 0)
        )
        
        return self.prepare_response(result, "GoogleSheetsSearchResult")
    
    def get_formulas(self, spreadsheet_id: str, range_name: str) -> ApiResponse:
        """
        Get formulas from a range
        """
        response = self.client.get_formulas(spreadsheet_id, range_name)
        
        result = SpreadsheetFormulas(
            spreadsheet_id=spreadsheet_id,
            range=response.get('range', ''),
            formulas=response.get('values', []),
            majorDimension=response.get('majorDimension', 'ROWS')
        )
        
        return self.prepare_response(result, "GoogleSheetsFormulasResult")
    
    def add_formula(self, spreadsheet_id: str, range_name: str, formula: str) -> ApiResponse:
        """
        Add a formula to a specific cell or range
        """
        response = self.client.add_formula(spreadsheet_id, range_name, formula)
        
        result = FormulaResult(
            spreadsheet_id=spreadsheet_id,
            range=range_name,
            applied=True if response.get('updatedCells', 0) > 0 else False,
            formula=formula
        )
        
        return self.prepare_response(result, "GoogleSheetsFormulaResult")
