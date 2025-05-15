from agents import Agent, Runner
from typing import Dict, Any, Optional, List
import json
import uuid
from .tools import web_search
from .services import setup_openrouter_client, format_payload


def create_agent() -> Agent:
    setup_openrouter_client()
    
    instructions = """
    You are a specialized web search assistant. Your primary task is to find information on the web.
    Always provide clear, concise answers based on search results.
    When searching:
    1. Extract key information from search results
    2. Synthesize information from multiple sources when applicable
    3. Cite sources when providing information
    4. Be objective and present factual information
    """
    
    agent = Agent(
        name="Fild Agent",
        instructions=instructions,
        tools=[web_search],
        model="anthropic/claude-3.7-sonnet"
    )
    
    return agent


async def run_agent(query: str) -> Dict[str, Any]:
    agent = create_agent()
    
    result = await Runner.run(agent, query, max_turns=30)
    
    sequence_payload = format_payload(result)
    
    return {
        "query": query,
        "result": result.final_output,
        "success": True,
        "payload": sequence_payload
    }
