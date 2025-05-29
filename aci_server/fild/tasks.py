from celery import shared_task
import logging
from typing import Dict, Any, Optional
from .queries import update_cell_status, update_cell_value, get_sheet_by_id, add_sheet_task
import asyncio
from .agent import run_agent
import json
from .services import extract_data

@shared_task(name="process_cell")
def process_cell(sheet_id: str, row_index: int, column_id: int, column_name: str, query: str, 
                column_type: Optional[str] = None, column_subtype: Optional[str] = None,
                full_row_data: Optional[Dict] = None, current_value: Optional[Any] = None, 
                all_columns: Optional[Dict] = None, chat_id: Optional[str] = None) -> Dict[str, Any]:
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
        
        columns_info = ""
        if all_columns:
            columns_info = "All Sheet Columns:\n"
            for col in all_columns:
                columns_info += f"        Column ID: {col['id']}, Name: {col['column']}, Type: {col['columnType']}\n"
        
        human_readable_row = {}
        if full_row_data and all_columns and "values" in full_row_data:
            for col in all_columns:
                col_id_str = str(col["id"])
                if col_id_str in full_row_data["values"]:
                    human_readable_row[col["column"]] = full_row_data["values"][col_id_str]
        
        row_data_str = json.dumps(full_row_data) if not human_readable_row else json.dumps(human_readable_row)

        column_type_str = ""
        if column_type:
            column_type_str = f"Column Type: {column_type}"
            if column_subtype:
                column_type_str += f", Subtype: {column_subtype}"
                
        prompt = f"""Process the following cell data:
        Query/Context: {query}
        Row Index: {row_index}
        Column Name: {column_name}
        Column ID: {column_id}
        {column_type_str}
        Current Value: {current_value_str}
        {columns_info}
        Row Data: {row_data_str}

        Generate an appropriate response for this cell based on the given context and query. 
        You are filling the "{column_name}" column with relevant information from the row data.
        Keep your response brief and to the point. 2-3 words is ideal unless more detail is necessary.
        """

        print(f"Prompt: {prompt}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_agent(prompt))
        finally:
            loop.close()
        
        if not result or not result.get("success", False) or "result" not in result:
            error_msg = result.get("result", "AI processing failed") if result else "AI processing failed"
            agent_steps = result.get("payload", []) if result else []
            raise ValueError(error_msg)
        
        processed_value = result["result"].strip()
        agent_steps = result.get("payload", [])

        column_type_for_extract = column_subtype if column_subtype else column_type
        structured_output = extract_data(processed_value, column_name, column_type_for_extract)
        
        cell_data = {
            "result": structured_output.result,
            "status": "completed",
            "reasoning": structured_output.reasoning
        }
        
        update_success = update_cell_value(
            sheet_id=sheet_id,
            row_index=row_index,
            column_id=column_id,
            value=cell_data
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
        
        error_result = {
            "success": False,
            "message": f"Error processing cell: {str(e)}",
            "error": str(e)
        }
        
        try:
            add_sheet_task(
                sheet_id=sheet_id,
                status="error",
                payload={
                    "row_index": row_index,
                    "column_id": column_id,
                    "column_name": column_name,
                    "query": query,
                    "raw_output": str(e),
                    "agent_steps": agent_steps
                },
                chat_id=chat_id
            )
        except Exception as task_e:
            logging.exception(f"Error saving task to sheets_tasks: {str(task_e)}")
        
        return error_result
    
    finally:
        if 'processed_value' in locals() and 'cell_data' in locals():
            try:
                add_sheet_task(
                    sheet_id=sheet_id,
                    status="completed",
                    payload={
                        "row_index": row_index,
                        "column_id": column_id,
                        "column_name": column_name,
                        "query": query,
                        "raw_output": processed_value,
                        "structured_output": cell_data,
                        "agent_steps": agent_steps
                    },
                    chat_id=chat_id
                )
            except Exception as task_e:
                logging.exception(f"Error saving completed task to sheets_tasks: {str(task_e)}")
