from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled, set_tracing_export_api_key
import os
import json
from typing import Dict, Any, List, Optional, Union, Iterable
import re
import logging
from agents import Runner
from .queries import get_sheet_by_id, update_sheet_data
from openai import OpenAI
from .prompts import STRUCTURED_OUTPUT_PROMPT
from .schema import ExtractedValue


def openai_llm_call(human_message, system_message, model_class=None, model_name='gpt-4o-mini'):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    if model_class:
        response = client.responses.parse(
            model=model_name,
            input=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": human_message}
            ],
            text_format=model_class
        )
        return response.output_parsed
    else:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": human_message}, {"role": "system", "content": system_message}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content


def setup_openrouter_client():
    try:
        set_tracing_disabled(True)
        
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        
        site_url = os.environ.get("SITE_URL", "https://veyraxapp.com")
        site_name = os.environ.get("SITE_NAME", "Veyrax")
        
        custom_client = AsyncOpenAI(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_name
            }
        )

        set_default_openai_api("chat_completions")
        set_default_openai_client(custom_client)
        
        return custom_client
    except Exception as e:
        logging.exception("Error setting up OpenRouter client")
        raise


def extract_data(data: str, column_name: str) -> ExtractedValue:
    human_message = f"Extract data from the following text: {data} for column {column_name}"
    system_message = STRUCTURED_OUTPUT_PROMPT
    return openai_llm_call(human_message, system_message, ExtractedValue)


def format_payload(result: Any) -> List[Dict[str, Any]]:
    sequence_payload = []
    
    for i, item in enumerate(result.new_items):
        step_info = {
            "step_type": item.type,
            "step_id": i + 1
        }
        
        try:
            if item.type == "message_output_item":
                if hasattr(item, "content"):
                    step_info["content"] = str(item.content)
                elif hasattr(item.raw_item, "content"):
                    try:
                        content_texts = []
                        for content_part in item.raw_item.content:
                            if hasattr(content_part, "text"):
                                content_texts.append(content_part.text)
                        if content_texts:
                            step_info["content"] = " ".join(content_texts)
                    except:
                        pass
                
            elif item.type == "tool_call_item":
                if hasattr(item.raw_item, "name"):
                    step_info["tool_name"] = item.raw_item.name
                if hasattr(item.raw_item, "arguments"):
                    try:
                        import json
                        step_info["input"] = json.loads(item.raw_item.arguments)
                    except:
                        step_info["input"] = str(item.raw_item.arguments)
                        
            elif item.type == "tool_call_output_item":
                if hasattr(item, "output"):
                    step_info["output"] = str(item.output)
                
            elif item.type == "reasoning_item":
                if hasattr(item.raw_item, "reasoning"):
                    step_info["content"] = str(item.raw_item.reasoning)
            
            if hasattr(item, "raw_item"):
                raw_info = {}
                for attr in ["id", "type", "name", "call_id"]:
                    if hasattr(item.raw_item, attr):
                        try:
                            raw_info[attr] = getattr(item.raw_item, attr)
                        except:
                            pass
                if raw_info:
                    step_info["raw_info"] = raw_info
                    
        except Exception as e:
            step_info["error"] = str(e)
            
        sequence_payload.append(step_info)
    
    return sequence_payload

async def run_waterfall(sheet_id: str, query: str, row_indexes: List[int] = None, 
                    row_range: Dict[str, int] = None, column_ids: List[int] = None) -> Dict[str, Any]:
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
        for col in sheet_data.get("columns", []):
            col_id = col.get("id")
            col_name = col.get("column")
            if col_id is not None and col_name:
                column_names[col_id] = col_name
        
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
                        cells_to_process.append({
                            "row_index": item["index"],
                            "column_id": col_id,
                            "column_name": column_names.get(col_id, f"column_{col_id}"),
                            "current_value": cell_value
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
        
        from .tasks import process_cell
        
        all_columns = sheet_data.get("columns", [])
        
        task_ids = []
        for cell in cells_to_process:
            row_index = cell["row_index"]
            task = process_cell.delay(
                sheet_id=sheet_id,
                row_index=row_index,
                column_id=cell["column_id"],
                column_name=cell["column_name"],
                query=query,
                full_row_data=row_data_map.get(row_index),
                current_value=cell["current_value"],
                all_columns=all_columns
            )
            task_ids.append(task.id)
        
        return {
            "success": True,
            "message": f"Started waterfall process for {len(cells_to_process)} cells",
            "process_details": {
                "sheet_id": sheet_id,
                "query": query,
                "total_cells": len(cells_to_process),
                "row_indexes": list(target_indexes),
                "column_ids": column_ids,
                "task_ids": task_ids
            }
        }
    
    except Exception as e:
        logging.exception(f"Error in run_waterfall: {str(e)}")
        return {
            "success": False,
            "message": f"Error running waterfall process: {str(e)}",
            "error": str(e)
        }