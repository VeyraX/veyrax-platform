import asyncio
import logging
from typing import Dict, Any, List, Optional
from .queries import update_cell_status, update_cell_value, add_sheet_task
from .agent import run_agent
from .services import extract_data
import json

async def process_batch(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    cells = batch_data.get("cells", [])
    sheet_id = batch_data.get("sheet_id")
    chat_id = batch_data.get("chat_id")
    
    if not cells or not sheet_id:
        return {
            "success": False,
            "error": "Missing cells or sheet_id in batch_data"
        }
    
    tasks = []
    for cell in cells:
        task = process_single_cell(
            sheet_id=sheet_id,
            cell_data=cell,
            chat_id=chat_id
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.exception(f"Error processing cell {cells[i].get('row_index')}/{cells[i].get('column_id')}: {result}")
            final_results.append({
                "success": False,
                "row_index": cells[i].get("row_index"),
                "column_id": cells[i].get("column_id"),
                "error": str(result)
            })
        else:
            final_results.append(result)
    
    results = final_results
    
    successful = sum(1 for r in results if r.get("success", False))
    
    return {
        "success": True,
        "batch_size": len(cells),
        "successful": successful,
        "failed": len(cells) - successful,
        "results": results
    }

async def process_single_cell(sheet_id: str, cell_data: Dict[str, Any], chat_id: Optional[str] = None) -> Dict[str, Any]:
    row_index = cell_data["row_index"]
    column_id = cell_data["column_id"]
    column_name = cell_data["column_name"]
    query = cell_data["query"]
    column_type = cell_data.get("column_type")

    full_row_data = cell_data.get("full_row_data")
    current_value = cell_data.get("current_value")
    all_columns = cell_data.get("all_columns")
    
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
        
        result = await run_agent(prompt)
        
        if not result or not result.get("success", False) or "result" not in result:
            error_msg = result.get("result", "AI processing failed") if result else "AI processing failed"
            raise ValueError(error_msg)
        
        processed_value = result["result"].strip()
        agent_steps = result.get("payload", [])

        column_type_for_extract = column_type
        structured_output = extract_data(processed_value, column_name, column_type_for_extract)
        
        cell_data_result = {
            "result": structured_output.result,
            "status": "completed",
            "reasoning": structured_output.reasoning,
            "confidence": structured_output.confidence,
            "source": structured_output.source
        }
        
        update_success = update_cell_value(
            sheet_id=sheet_id,
            row_index=row_index,
            column_id=column_id,
            value=cell_data_result
        )
        
        if not update_success:
            raise ValueError("Failed to update cell with processed value")
        
        add_sheet_task(
            sheet_id=sheet_id,
            status="completed",
            payload={
                "row_index": row_index,
                "column_id": column_id,
                "column_name": column_name,
                "query": query,
                "raw_output": processed_value,
                "structured_output": cell_data_result,
                "agent_steps": agent_steps
            },
            chat_id=chat_id
        )
        
        return {
            "success": True,
            "row_index": row_index,
            "column_id": column_id,
            "processed_value": processed_value
        }
        
    except Exception as e:
        logging.exception(f"Error processing cell: {e}")
        
        update_cell_status(
            sheet_id=sheet_id,
            row_index=row_index,
            column_id=column_id,
            status="error",
            message=f"Error: {str(e)}"
        )
        
        add_sheet_task(
            sheet_id=sheet_id,
            status="error",
            payload={
                "row_index": row_index,
                "column_id": column_id,
                "column_name": column_name,
                "query": query,
                "raw_output": str(e),
                "agent_steps": []
            },
            chat_id=chat_id
        )
        
        return {
            "success": False,
            "row_index": row_index,
            "column_id": column_id,
            "error": str(e)
        } 