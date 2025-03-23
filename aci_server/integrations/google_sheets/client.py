from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional, Dict, Any, List

class GoogleSheetsClient:
    def __init__(self, credentials: Credentials):
        self.service = build('sheets', 'v4', credentials=credentials)

    def get_spreadsheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        return self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

    def get_spreadsheet_values(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        return self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

    def get_spreadsheet_values_batch(self, spreadsheet_id: str, ranges: List[str]) -> Dict[str, Any]:
        return self.service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges
        ).execute()

    def update_spreadsheet_values(self, spreadsheet_id: str, range_name: str, 
                                 values: List[List[Any]], value_input_option: str = "RAW") -> Dict[str, Any]:
        body = {
            'values': values
        }
        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()

    def append_spreadsheet_values(self, spreadsheet_id: str, range_name: str, 
                                 values: List[List[Any]], value_input_option: str = "RAW") -> Dict[str, Any]:
        body = {
            'values': values
        }
        return self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()

    def clear_spreadsheet_values(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        return self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

    def create_spreadsheet(self, title: str) -> Dict[str, Any]:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        return self.service.spreadsheets().create(body=spreadsheet).execute()

    def add_sheet(self, spreadsheet_id: str, sheet_title: str) -> Dict[str, Any]:
        request = {
            'addSheet': {
                'properties': {
                    'title': sheet_title
                }
            }
        }
        return self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()

    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> Dict[str, Any]:
        request = {
            'deleteSheet': {
                'sheetId': sheet_id
            }
        }
        return self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()

    def search_in_spreadsheet(self, spreadsheet_id: str, sheet_ranges: Optional[List[str]] = None, 
                             search_term: str = "", case_sensitive: bool = False) -> Dict[str, Any]:
        result = {
            'matches': [],
            'total_found': 0
        }
        
        if not sheet_ranges:
            spreadsheet = self.get_spreadsheet(spreadsheet_id)
            sheet_ranges = []
            for sheet in spreadsheet.get('sheets', []):
                sheet_title = sheet.get('properties', {}).get('title')
                if sheet_title:
                    sheet_ranges.append(f"'{sheet_title}'!A1:ZZ")
        
        if not sheet_ranges:
            return result
        
        batch_response = self.get_spreadsheet_values_batch(spreadsheet_id, sheet_ranges)
        
        for value_range in batch_response.get('valueRanges', []):
            range_name = value_range.get('range', '')
            values = value_range.get('values', [])
            
            for row_idx, row in enumerate(values):
                for col_idx, cell in enumerate(row):
                    cell_str = str(cell)
                    if case_sensitive:
                        if search_term in cell_str:
                            col_letter = self._index_to_column_letter(col_idx)
                            cell_ref = f"{range_name.split('!')[0]}!{col_letter}{row_idx + 1}"
                            result['matches'].append({
                                'sheet': range_name.split('!')[0],
                                'cell': f"{col_letter}{row_idx + 1}",
                                'value': cell_str,
                                'a1_notation': cell_ref
                            })
                    else:
                        if search_term.lower() in cell_str.lower():
                            col_letter = self._index_to_column_letter(col_idx)
                            cell_ref = f"{range_name.split('!')[0]}!{col_letter}{row_idx + 1}"
                            result['matches'].append({
                                'sheet': range_name.split('!')[0],
                                'cell': f"{col_letter}{row_idx + 1}",
                                'value': cell_str,
                                'a1_notation': cell_ref
                            })
        
        result['total_found'] = len(result['matches'])
        return result
    
    def get_formulas(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        return self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueRenderOption="FORMULA"
        ).execute()
    
    def add_formula(self, spreadsheet_id: str, range_name: str, formula: str) -> Dict[str, Any]:
        body = {
            'values': [[formula]]
        }
        
        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
    
    def _index_to_column_letter(self, index: int) -> str:
        result = ""
        while index >= 0:
            index, remainder = divmod(index, 26)
            result = chr(65 + remainder) + result
            index -= 1
            if index < 0:
                break
        return result
