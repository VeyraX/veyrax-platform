from agents import Agent, Runner
from typing import Dict, Any, Optional, List
import json
import uuid
from .tools import get_flow_by_id, get_available_tools, tool_call, set_api_key
from .services import setup_openrouter_client, format_agent_result, setup_posthog_tracing

def create_agent(api_key: str, instructions: str = None, flow_id: str = None, run_id: str = None, user_id: str = None, trace_id: str = None) -> Agent:
    set_api_key(api_key)
    
    setup_posthog_tracing()
    
    posthog_properties = {
        "flow_id": flow_id, 
        "run_id": run_id, 
        "user_id": user_id,
        "trace_id": trace_id
    }
    
    setup_openrouter_client(posthog_properties=posthog_properties)
    
    tools = [get_flow_by_id, tool_call]
    
    agent = Agent(
        name="Veyrax Assistant",
        instructions=instructions,
        tools=tools,
        model="anthropic/claude-3.7-sonnet"
    )
    
    return agent

async def run_flow_agent(agent: Agent, user_input: str, flow_id: str = None, trace_id: str = None, user_id: str = None) -> str:
    try:
        result = await Runner.run(
            agent, 
            user_input, 
            max_turns=30
        )

        formatted_result = format_agent_result(result)
        
        api_response = {
            "status": "success",
            "response": result.final_output,
            "formatted_result": formatted_result,
            "debug_info": {
                "flow_id": flow_id or "unknown",
                "user_id": user_id or "unknown",
                "query": user_input,
                "instructions_length": 0,
                "trace_id": trace_id
            }
        }
        
        if "metadata" not in formatted_result:
            formatted_result["metadata"] = {}
        
        formatted_result["metadata"]["trace_id"] = trace_id
        if user_id:
            formatted_result["metadata"]["user_id"] = user_id
            
        api_response["formatted_result"] = formatted_result
        
        if "metadata" in formatted_result and "toolInvocations" in formatted_result["metadata"]:
            tool_invocations = formatted_result["metadata"]["toolInvocations"]
            if tool_invocations:
                api_response["tool_invocations"] = tool_invocations
        
        return json.dumps(api_response)
    except Exception as e:
        error_response = {
            "status": "error",
            "error": str(e),
            "trace_id": trace_id
        }
        return json.dumps(error_response)

