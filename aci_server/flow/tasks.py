import os
import httpx
import time
import asyncio
import json
from celery import shared_task
from db.supabase import get_supabase
from agent.agent import create_agent, run_flow_agent
from agent.queries import get_flow_by_id, update_flow_run_completed
from agent.prompts import flow_prompt

@shared_task(name='flow.tasks.run_flow_task')
def run_flow_task(flow_id, run_id, api_key, trace_id, user_id):
    try:
        print(f"Running flow task for flow_id: {flow_id}, run_id: {run_id}, api_key: {api_key}")
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
            instructions=enhanced_instructions,
            flow_id=flow_id,
            run_id=run_id,
            user_id=user_id,
            trace_id=trace_id
        )
        
        response_str = asyncio.run(run_flow_agent(agent, "Run the flow.", flow_id=flow_id, trace_id=trace_id, user_id=user_id))
        
        response_data = json.loads(response_str)
        
        if response_data.get("status") == "error":
            error_payload = {
                "status": "error",
                "error": response_data.get("error", "Unknown error")
            }
            update_flow_run_completed(run_id, error_payload, status="failed")
            return error_payload
        
        formatted_result = response_data.get("formatted_result", {})
        update_flow_run_completed(run_id, formatted_result)
        
        return {
            "status": "success",
            "result": formatted_result
        }
                
    except Exception as e:
        error_payload = {
            "status": "error",
            "error": f"Agent execution error: {str(e)}"
        }
        update_flow_run_completed(run_id, error_payload, status="failed")
        return error_payload