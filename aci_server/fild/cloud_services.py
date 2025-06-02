from typing import Dict, Any, List, Optional
import logging
from .queries import get_sheet_by_id, update_sheet_data
from .cloud_tasks_service import CloudTasksService

async def run_cloud_waterfall(sheet_id: str, row_indexes: List[int] = None, 
                    row_range: Dict[str, int] = None, column_ids: List[int] = None, 
                    chat_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        if not row_indexes and not row_range:
            return {
                "success": False,
                "message": "Either row_indexes or row_range must be provided",
                "error": "Missing row selection"
            }
            
        if not column_ids:
            return {
                "success": False,
                "message": "column_ids must be provided",
                "error": "Missing column selection"
            }
        
        sheets = get_sheet_by_id(sheet_id)
        if not sheets:
            return {
                "success": False,
                "message": f"Sheet {sheet_id} not found",
                "error": "Sheet not found"
            }
        
        sheet = sheets[0]
        sheet_data = sheet.get("data", {})
        
        column_names = {}
        column_queries = {}
        column_types = {}
        column_subtypes = {}
        
        for col in sheet_data.get("columns", []):
            col_id = col.get("id")
            col_name = col.get("column")
            col_query = col.get("query")
            col_type = col.get("columnType")
            col_subtype = col.get("columnSubType")
            
            if col_id is not None and col_name:
                column_names[col_id] = col_name
                if col_query:
                    column_queries[col_id] = col_query
                if col_type:
                    column_types[col_id] = col_type
                if col_subtype:
                    column_subtypes[col_id] = col_subtype
        
        target_indexes = set()
        if row_indexes:
            target_indexes.update(row_indexes)
        
        if row_range:
            for i in range(row_range["from"], row_range["to"] + 1):
                target_indexes.add(i)
        
        cells_to_process = []
        row_data_map = {} 
        
        for item in sheet_data.get("data", []):
            if item["index"] in target_indexes:
                row_data_map[item["index"]] = item 
                
                for col_id in column_ids:
                    col_id_str = str(col_id)
                    if col_id_str in item["values"]:
                        cell_value = item["values"][col_id_str]
                        
                        if col_id not in column_queries:
                            return {
                                "success": False,
                                "message": f"No query found for column {col_id}",
                                "error": "Missing column query"
                            }
                        
                        cells_to_process.append({
                            "row_index": item["index"],
                            "column_id": col_id,
                            "column_name": column_names.get(col_id, f"column_{col_id}"),
                            "query": column_queries.get(col_id, ""),
                            "column_type": column_types.get(col_id),
                            "column_subtype": column_subtypes.get(col_id),
                            "current_value": cell_value,
                            "full_row_data": row_data_map.get(item["index"]),
                            "all_columns": sheet_data.get("columns", [])
                        })
                        
                        item["values"][col_id_str] = {"status": "queue"}
        
        if not cells_to_process:
            return {
                "success": False,
                "message": "No valid cells found for processing",
                "error": "No cells to process"
            }
        
        update_success = update_sheet_data(sheet_id, sheet_data)
        if not update_success:
            return {
                "success": False,
                "message": "Failed to update sheet with processing status",
                "error": "Database update error"
            }
        
        cloud_tasks_service = CloudTasksService()
        
        batches = cloud_tasks_service.create_batches(cells_to_process, batch_size=5)
        
        task_names = []
        for batch in batches:
            batch_data = {
                "sheet_id": sheet_id,
                "chat_id": chat_id,
                "cells": batch
            }
            
            task_name = cloud_tasks_service.create_batch_processing_task(batch_data)
            task_names.append(task_name)
        
        return {
            "success": True,
            "message": f"Started cloud waterfall process for {len(cells_to_process)} cells in {len(batches)} batches",
            "process_details": {
                "sheet_id": sheet_id,
                "total_cells": len(cells_to_process),
                "total_batches": len(batches),
                "row_indexes": list(target_indexes),
                "column_ids": column_ids,
                "task_names": task_names
            }
        }
    
    except Exception as e:
        logging.exception(f"Error in run_cloud_waterfall: {str(e)}")
        return {
            "success": False,
            "message": f"Error running cloud waterfall process: {str(e)}",
            "error": str(e)
        } 