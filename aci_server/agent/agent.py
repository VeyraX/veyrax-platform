from agents import Agent, Runner
from typing import Dict, Any, Optional, List
import json
from .tools import get_flow_by_id, get_available_tools, tool_call, set_api_key
from .services import setup_openrouter_client, format_agent_result

def create_agent(api_key: str, instructions: str = None) -> Agent:
    set_api_key(api_key)
    
    setup_openrouter_client()
    
    tools = [get_flow_by_id, tool_call]
    
    agent = Agent(
        name="Veyrax Assistant",
        instructions=instructions,
        tools=tools,
        model="anthropic/claude-3.7-sonnet"
    )
    
    return agent

async def run_flow_agent(agent: Agent, user_input: str) -> str:
    try:
        result = await Runner.run(agent, user_input, max_turns=30)

        formatted_result = format_agent_result(result)
        
        api_response = {
            "status": "success",
            "response": result.final_output,
            "formatted_result": formatted_result,
            "debug_info": {
                "flow_id": "unknown",
                "user_id": "unknown",
                "query": user_input,
                "instructions_length": 0
            }
        }
        
        if "metadata" in formatted_result and "toolInvocations" in formatted_result["metadata"]:
            tool_invocations = formatted_result["metadata"]["toolInvocations"]
            if tool_invocations:
                api_response["tool_invocations"] = tool_invocations
        
        return json.dumps(api_response)
    except Exception as e:
        error_response = {
            "status": "error",
            "error": str(e)
        }
        return json.dumps(error_response)

