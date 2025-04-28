from fastapi import APIRouter, Request, HTTPException, Body
from .queries import get_flow_by_id, get_user_api_key, create_flow_run, update_flow_run_completed
from integrations.common.auth import get_user_from_request
from integrations.common.utils import get_user_tools_from_actions
from db.supabase import get_supabase
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
from .agent import create_agent, run_flow_agent
from .prompts import flow_prompt
from .schema import AgentQueryRequest, AgentResponse

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/run-flow/{flow_id}", response_model=AgentResponse)
async def execute_agent_query(
    request: Request,
    flow_id: str,
    run_id: str = None
):
    user_id = await get_user_from_request(request)
    

    
    body = await request.json()
    run_id = body.get("run_id")
    trace_id = body.get("trace_id")
    input = body.get("input", "")
    
    try:
        api_key = get_user_api_key(user_id)
        
        user_flows = get_flow_by_id(flow_id)
        system_prompt = flow_prompt
        
        if user_flows:
            flow_json = json.dumps(user_flows, indent=2)
            flow_instructions = f"\n\nUser Flows Data:\n```json\n{flow_json}\n```\n\nYou can access specific flow details using the get_flow_by_id tool."
            enhanced_instructions = system_prompt + flow_instructions
        else:
            enhanced_instructions = system_prompt
        
        agent = create_agent(
            api_key=api_key,
            instructions=enhanced_instructions
        )

        query = "Run the flow."

        if input:
            query += f"\n\nUser Input:\n```json\n{input}\n```"

        response = await run_flow_agent(
            agent=agent, 
            user_input=query,
            trace_id=trace_id,
            user_id=user_id
        )
        response_data = json.loads(response)
        
        result = {
            "status": response_data.get("status", "success"),
            "response": response_data.get("response", "") or response_data.get("error", ""),
            "trace_id": response_data.get("debug_info", {}).get("trace_id")
        }
        
        if "tool_invocations" in response_data:
            result["tool_invocations"] = response_data["tool_invocations"]
        
        formatted_result = response_data.get("formatted_result", {})
        if run_id:
            if "metadata" not in formatted_result:
                formatted_result["metadata"] = {}
            
            if "trace_id" not in formatted_result["metadata"] and "trace_id" in result:
                formatted_result["metadata"]["trace_id"] = result["trace_id"]
                
            update_flow_run_completed(run_id, formatted_result)
        
        return result
    except Exception as e:
        error_payload = {
            "status": "error",
            "error": str(e)
        }
        if run_id:
            update_flow_run_completed(run_id, error_payload, status="failed")
        
        result = {
            "status": "error",
            "error": str(e)
        }
        
        return result