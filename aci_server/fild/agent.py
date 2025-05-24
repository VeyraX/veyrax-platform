from agents import Agent, Runner
from typing import Dict, Any, Optional, List
import json
import uuid
from .tools import web_search, extract_page
from .services import setup_openrouter_client, format_payload
from .prompts import AGENT_PROMPT, WEB_SEARCH_PROMPT
import logging

def create_agent() -> Agent:
    try:
        setup_openrouter_client()
        
        agent = Agent(
            name="Fild Agent",
            instructions=AGENT_PROMPT + WEB_SEARCH_PROMPT,
            tools=[
                web_search,
                extract_page
            ],
            model="google/gemini-2.5-flash-preview:thinking"
        )
        
        return agent
    except Exception as e:
        logging.exception(f"Error creating agent: {e}")
        raise


async def run_agent(query: str) -> Dict[str, Any]:
    try:
        agent = create_agent()
        
        result = await Runner.run(agent, query, max_turns=30)
        
        sequence_payload = format_payload(result)
        
        output = result.final_output
        
        return {
            "query": query,
            "result": output,
            "success": True,
            "payload": sequence_payload
        }
    except Exception as e:
        logging.exception(f"Error running Agent: {e}")
        return {
            "query": query,
            "result": f"Unable to process this request due to an error: {str(e)}. The system is currently experiencing technical difficulties.",
            "success": False,
            "payload": [],
            "reasoning": None,
            "extracted_values": None
        }
