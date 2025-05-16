from celery import shared_task
import logging
from typing import Dict, Any, Optional
from .queries import update_cell_status, update_cell_value, get_sheet_by_id
import asyncio
from .agent import run_agent
import json

@shared_task(name="process_cell")
def process_cell(sheet_id: str, row_index: int, column_id: int, column_name: str, query: str, full_row_data: Optional[Dict] = None, current_value: Optional[Any] = None) -> Dict[str, Any]:
    try:
        update_cell_status(
            sheet_id=sheet_id,
            row_index=row_index,
            column_id=column_id,
            status="processing"
        )      
        
        if current_value is None:
            current_value_str = "None"
        elif isinstance(current_value, dict):
            current_value_str = json.dumps(current_value)
        else:
            current_value_str = str(current_value)
        
        prompt = f"""Process the following cell data:
        Query/Context: {query}
        Row Index: {row_index}
        Column Name: {column_name}
        Row Data: {json.dumps(full_row_data)}
        Current Value: {current_value_str}

        Generate an appropriate response for this cell based on the given context and query. 
        You are filling the "{column_name}" column with relevant information from the row data.
        Keep your response brief and to the point. 2-3 words is ideal unless more detail is necessary.
        """

        print(f"Prompt: {prompt}")
        
        print(f"Processing cell - Row: {row_index}, Column: {column_name}")
        
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_agent(prompt))
        
        if not result or not result.get("success", False) or "result" not in result:
            error_msg = result.get("result", "AI processing failed") if result else "AI processing failed"
            raise ValueError(error_msg)
        
        processed_value = result["result"].strip()
        
        update_success = update_cell_value(
            sheet_id=sheet_id,
            row_index=row_index,
            column_id=column_id,
            value=processed_value
        )
        
        if not update_success:
            raise ValueError("Failed to update cell with processed value")
        
        return {
            "success": True,
            "message": f"Successfully processed cell at row {row_index}, column {column_id}",
            "processed_value": processed_value
        }
        
    except Exception as e:
        logging.exception(f"Error processing cell: {str(e)}")
        
        try:
            update_cell_status(
                sheet_id=sheet_id,
                row_index=row_index,
                column_id=column_id,
                status="error",
                message=f"Error: {str(e)}"
            )
        except Exception as inner_e:
            logging.exception(f"Error updating cell status after error: {str(inner_e)}")
        
        return {
            "success": False,
            "message": f"Error processing cell: {str(e)}",
            "error": str(e)
        }
