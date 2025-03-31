from fastapi import APIRouter, Request, HTTPException
from db.supabase import get_supabase
from integrations.common.auth import get_user_from_request
from integrations.common.utils import get_user_flows_actions, log_api_call
import os
import json
import httpx
from integrations.common.prompt_example import get_tools_example_prompt
from agent.queries import create_flow_run, update_flow_run_completed
from .tasks import run_flow_task
import uuid
router = APIRouter(prefix="/flow", tags=["Flow"])

@router.get("/get-flows")
async def get_user_flows_endpoint(request: Request):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:  
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        flows = get_user_flows_actions(user_id)

        if isinstance(flows, dict) and "error" in flows:
            raise Exception(flows["error"])
        
        log_api_call(
            user_id=user_id,
            endpoint="/flow/get-flows",
            success=1
        )
        
        response = {
            "flows": flows,
            "examples": json.loads(get_tools_example_prompt)
        }
        
        return response
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint="/flow/get-flows",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get user flows: {str(e)}")

@router.get("/get-flow/{flow_id}")
async def get_flow_by_id(flow_id: str, request: Request):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:  
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        flow = get_user_flows_actions(user_id, flow_id)
        
        if isinstance(flow, dict) and "error" in flow:
            raise Exception(flow["error"])
            
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
            
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-flow/{flow_id}",
            success=1
        )
        
        response = {
            "flows": flow,
            "examples": json.loads(get_tools_example_prompt)
        }
        
        return response
        
    except HTTPException as http_exc:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-flow/{flow_id}",
            success=0,
            error_message=str(http_exc.detail)
        )
        raise
        
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-flow/{flow_id}",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get flow: {str(e)}")

@router.post("/run-flow/{flow_id}")
async def run_flow(flow_id: str, request: Request, skipping_draft: bool = False):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        supabase = get_supabase()
        api_key_response = supabase.table('users_api_keys') \
            .select('api_key') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        flow_data = supabase.table('user_flows') \
            .select('status') \
            .eq('id', flow_id) \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        api_key = api_key_response.data['api_key']

        if skipping_draft and flow_data.data['status'] == 'Draft':
            return {"status": "skipped", "message": "Draft flow execution skipped"}
        
        run_id = create_flow_run(flow_id)
        trace_id = str(uuid.uuid4())
        FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://veyrax.com")
        if "NEXT_PUBLIC_APP_URL" in os.environ:
            FRONTEND_URL = os.environ.get("NEXT_PUBLIC_APP_URL")
        
        run_flow_task.delay(flow_id, run_id, api_key, trace_id, user_id)
        
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/run-flow/{flow_id}",
            success=1
        )
        
        return {
            "status": "started", 
            "message": "Flow execution has been started", 
            "flow_id": flow_id,
            "run_id": run_id,
            "url": f"{FRONTEND_URL}/flow/{flow_id}/view?tab=runs"
        }
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/run-flow/{flow_id}",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {str(e)}")

@router.post("/run-flow-sync/{flow_id}")
async def run_flow_sync(flow_id: str, request: Request, skipping_draft: bool = False):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        supabase = get_supabase()
        api_key_response = supabase.table('users_api_keys') \
            .select('api_key') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        flow_data = supabase.table('user_flows') \
            .select('status') \
            .eq('id', flow_id) \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        api_key = api_key_response.data['api_key']

        if skipping_draft and flow_data.data['status'] == 'Draft':
            return {"status": "skipped", "message": "Draft flow execution skipped"}
        
        run_id = create_flow_run(flow_id)
        
        FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://veyrax.com")
        if "NEXT_PUBLIC_APP_URL" in os.environ:
            FRONTEND_URL = os.environ.get("NEXT_PUBLIC_APP_URL")
        
        headers = {
            "Content-Type": "application/json",
            "VEYRAX_API_KEY": api_key
        }
        
        agent_url = f"{os.environ.get('API_URL', 'http://localhost:8000')}/agent/run-flow/{flow_id}"
        
        async with httpx.AsyncClient(timeout=300.0) as client: 
            response = await client.post(
                agent_url,
                headers=headers,
                json={"run_id": run_id}
            )
            
            if response.status_code >= 400:
                error_payload = {
                    "status": "error",
                    "error": f"Agent request failed with status {response.status_code}: {response.text}"
                }
                update_flow_run_completed(run_id, error_payload)
                raise HTTPException(status_code=response.status_code, detail=error_payload["error"])
            
            agent_response = response.json()
            
            log_api_call(
                user_id=user_id,
                endpoint=f"/flow/run-flow-sync/{flow_id}",
                success=1
            )
            
            result = {
                "status": "completed", 
                "message": "Flow execution completed", 
                "flow_id": flow_id,
                "run_id": run_id,
                "result": agent_response,
                "url": f"{FRONTEND_URL}/flow/{flow_id}/view?tab=runs"
            }
            
            return result
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/run-flow-sync/{flow_id}",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {str(e)}")

@router.get("/get-run-status/{run_id}")
async def get_run_status(run_id: str, request: Request):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        supabase = get_supabase()
        
        run_data = supabase.table('user_flow_runs') \
            .select('run_status, flow_id') \
            .eq('run_id', run_id) \
            .single() \
            .execute()
            
        if not run_data.data:
            raise HTTPException(status_code=404, detail="Run not found")
            
        flow_data = supabase.table('user_flows') \
            .select('id') \
            .eq('id', run_data.data['flow_id']) \
            .eq('user_id', user_id) \
            .single() \
            .execute()
            
        if not flow_data.data:
            raise HTTPException(status_code=403, detail="Not authorized to access this run")
        
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-run-status/{run_id}",
            success=1
        )
        
        return {
            "status": run_data.data['run_status'],
            "run_id": run_id,
            "flow_id": run_data.data['flow_id']
        }
        
    except HTTPException as http_exc:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-run-status/{run_id}",
            success=0,
            error_message=str(http_exc.detail)
        )
        raise
        
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-run-status/{run_id}",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get run status: {str(e)}")

@router.get("/get-run-details/{run_id}")
async def get_run_details(run_id: str, request: Request):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        supabase = get_supabase()
        
        run_data = supabase.table('user_flow_runs') \
            .select('*') \
            .eq('id', run_id) \
            .single() \
            .execute()
            
        if not run_data.data:
            raise HTTPException(status_code=404, detail="Run not found")
            
        flow_data = supabase.table('user_flows') \
            .select('*') \
            .eq('id', run_data.data['flow_id']) \
            .eq('user_id', user_id) \
            .single() \
            .execute()
            
        if not flow_data.data:
            raise HTTPException(status_code=403, detail="Not authorized to access this run")
        
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-run-details/{run_id}",
            success=1
        )
        
        return {
            "run": run_data.data,
            "flow": flow_data.data
        }
        
    except HTTPException as http_exc:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-run-details/{run_id}",
            success=0,
            error_message=str(http_exc.detail)
        )
        raise
        
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/get-run-details/{run_id}",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get run details: {str(e)}")
