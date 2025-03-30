from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled
import os
import json
from typing import Dict, Any, List, Optional, Union
import re

def setup_openrouter_client():
    set_tracing_disabled(True)
    
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set or empty")
    
    site_url = os.environ.get("SITE_URL", "https://veyraxapp.com")
    site_name = os.environ.get("SITE_NAME", "Veyrax")
    
    custom_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
        default_headers={
            "HTTP-Referer": site_url,
            "X-Title": site_name
        }
    )
    
    set_default_openai_api("chat_completions")
    
    set_default_openai_client(custom_client)
    
    return custom_client

def format_agent_result(result: Any) -> Dict[str, Any]:
    final_output = result.final_output if hasattr(result, "final_output") else ""
    tool_invocations = []
    tool_calls = []
    tool_outputs = {}
    
    if hasattr(result, "new_items"):
        for item in result.new_items:
            if hasattr(item, "type") and item.type == "tool_call_output_item":
                call_id = None
                output = None
                
                if hasattr(item, "raw_item"):
                    if hasattr(item.raw_item, "call_id"):
                        call_id = item.raw_item.call_id
                    elif isinstance(item.raw_item, dict) and "call_id" in item.raw_item:
                        call_id = item.raw_item["call_id"]
                
                if not call_id:
                    call_id = f"unknown_{len(tool_outputs)}"
                
                if hasattr(item, "raw_item"):
                    if hasattr(item.raw_item, "output"):
                        output = item.raw_item.output
                    elif isinstance(item.raw_item, dict) and "output" in item.raw_item:
                        output = item.raw_item["output"]
                
                if output is None and hasattr(item, "output"):
                    output = item.output
                
                if output is not None:
                    tool_outputs[call_id] = output
    
    if hasattr(result, "raw_responses"):
        for resp_idx, resp in enumerate(result.raw_responses):
            if hasattr(resp, "output"):
                for out_idx, output in enumerate(resp.output):
                    if hasattr(output, "type") and output.type == "function_call":
                        tool_id = None
                        if hasattr(output, "call_id"):
                            tool_id = output.call_id
                        elif hasattr(output, "id"):
                            tool_id = output.id
                        else:
                            tool_id = f"toolu_{resp_idx}_{out_idx}"
                        
                        tool_name = getattr(output, "name", "unknown")
                        
                        args = {}
                        if hasattr(output, "arguments"):
                            try:
                                args = json.loads(output.arguments)
                            except:
                                args = output.arguments
                        elif hasattr(output, "function") and hasattr(output.function, "arguments"):
                            try:
                                args = json.loads(output.function.arguments)
                            except:
                                args = output.function.arguments
                        
                        tool_calls.append({
                            "id": tool_id,
                            "name": tool_name,
                            "args": args
                        })
    
    for idx, call in enumerate(tool_calls):
        raw_output = None
        if call["id"] in tool_outputs:
            try:
                output_value = tool_outputs[call["id"]]
                if isinstance(output_value, str):
                    try:
                        raw_output = json.loads(output_value)
                    except json.JSONDecodeError:
                        try:
                            import ast
                            raw_output = ast.literal_eval(output_value)
                        except (SyntaxError, ValueError):
                            raw_output = output_value
                else:
                    raw_output = output_value
            except Exception as e:
                raw_output = {"error": str(e), "raw": str(tool_outputs[call["id"]])}
        
        tool_invocation = {
            "args": call["args"],
            "step": idx,
            "state": "result",
            "toolName": call["name"],
            "toolCallId": call["id"],
            "result": raw_output
        }
        tool_invocations.append(tool_invocation)
    
    parts = []
    
    for invocation in tool_invocations:
        parts.append({
            "type": "tool-invocation",
            "toolInvocation": {
                "args": invocation["args"],
                "toolName": invocation["toolName"],
                "toolCallId": invocation["toolCallId"]
            }
        })
    
    if final_output:
        parts.append({
            "type": "text",
            "text": final_output
        })
    
    formatted_result = {
        "parts": parts,
        "sender": "assistant",
        "metadata": {
            "finishReason": "success",
            "toolInvocations": tool_invocations,
            "isServiceAccount": True
        },
        "message_id": f"msg-{os.urandom(12).hex()}",
        "message_text": final_output
    }
    
    return formatted_result
