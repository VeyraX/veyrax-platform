from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled, set_tracing_export_api_key
import os
import json
from typing import Dict, Any, List, Optional, Union, Iterable
import re
import logging
from agents import Runner

def setup_openrouter_client():
    try:
        tracing_disabled = os.environ.get("OPENAI_AGENTS_DISABLE_TRACING", "0") == "1"
        set_tracing_disabled(tracing_disabled)
        
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            logging.error("OPENROUTER_API_KEY environment variable is not set or empty")
            raise ValueError("OPENROUTER_API_KEY environment variable is not set or empty")
        
        site_url = os.environ.get("SITE_URL", "https://veyraxapp.com")
        site_name = os.environ.get("SITE_NAME", "Veyrax")
        
        logging.info(f"Setting up OpenRouter client with URL: {site_url}")
        
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