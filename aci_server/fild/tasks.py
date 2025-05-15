from celery import shared_task
import logging
from typing import Dict, Any, Optional
from .queries import update_cell_status, update_cell_value
import asyncio
from .agent import run_agent

@shared_task(name="process_cell")
def process_cell(sheet_id: str, row_index: int, column_id: int, query: str, current_value: Optional[str] = None) -> Dict[str, Any]:
    try:
        update_cell_status(
            sheet_id=sheet_id,
            row_index=row_index,
            column_id=column_id,
            status="processing"
        )
        
        column_name = f"column_{column_id}"
        
        prompt = f"""Process the following cell data:
        Query/Context: {query}
        Row: {row_index}
        Column: {column_name}
        Current Value: {current_value if current_value else 'None'}

        Generate an appropriate response for this cell based on the given context and query.
        """
        
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_agent(prompt))
        
        if not result or "result" not in result:
            raise ValueError("AI processing failed to return a valid result")
        
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
                value=f"Error: {str(e)}"
            )
        except Exception as inner_e:
            logging.exception(f"Error updating cell status after error: {str(inner_e)}")
        
        return {
            "success": False,
            "message": f"Error processing cell: {str(e)}",
            "error": str(e)
        }
