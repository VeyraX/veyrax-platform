from db.supabase import get_fild_supabase
from typing import List, Dict, Any, Optional

client = get_fild_supabase()

def get_sheet_by_id(sheet_id: str) -> List[Dict[str, Any]]:
    try:
        response = client.table('sheets').select('*').eq('id', sheet_id).execute()
        
        if not response.data:
            return []
        
        return response.data

    except Exception as e:
        print(f"Error getting sheet by id: {e}")
        return []
    
    
def update_sheet_data(sheet_id: str, sheet_data: Dict[str, Any]) -> bool:
    try:
        response = client.table('sheets').update({"data": sheet_data}).eq('id', sheet_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating sheet data: {e}")
        return False


def update_cell_status(sheet_id: str, row_index: int, column_id: int, status: str, value: Optional[str] = None) -> bool:
    try:
        sheets = get_sheet_by_id(sheet_id)
        if not sheets:
            return False
        
        sheet = sheets[0]
        sheet_data = sheet.get("data", {})
        col_id_str = str(column_id)
        
        found = False
        for item in sheet_data.get("data", []):
            if item["index"] == row_index:
                cell_data = {"status": status}
                if value is not None:
                    cell_data["value"] = value
                
                item["values"][col_id_str] = cell_data
                found = True
                break
        
        if not found:
            return False
        
        return update_sheet_data(sheet_id, sheet_data)
    except Exception as e:
        print(f"Error updating cell status: {e}")
        return False


def update_cell_value(sheet_id: str, row_index: int, column_id: int, value: str) -> bool:
    try:
        sheets = get_sheet_by_id(sheet_id)
        if not sheets:
            return False
        
        sheet = sheets[0]
        sheet_data = sheet.get("data", {})
        col_id_str = str(column_id)
        
        found = False
        for item in sheet_data.get("data", []):
            if item["index"] == row_index:
                item["values"][col_id_str] = value
                found = True
                break
        
        if not found:
            return False
        
        return update_sheet_data(sheet_id, sheet_data)
    except Exception as e:
        print(f"Error updating cell value: {e}")
        return False



