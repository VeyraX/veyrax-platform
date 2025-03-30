from fastapi import APIRouter, Request, HTTPException
from db.supabase import get_supabase
from integrations.common.auth import get_user_from_request
from integrations.common.utils import get_user_flows_actions, log_api_call
import os
import json
import httpx
from integrations.common.prompt_example import get_tools_example_prompt

router = APIRouter(prefix="/flow", tags=["Flow"])

@router.get("/get-flows")
async def get_user_flows_endpoint(request: Request):
    try:
        user_id = await get_user_from_request(request)
    except Exception as e:  
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    try:
        flows = get_user_flows_actions(user_id)
        print(flows)
        
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
async def run_flow(flow_id: str, request: Request, allow_draft: bool = True):
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
            
        if not api_key_response.data or len(api_key_response.data) == 0:
            raise HTTPException(status_code=400, detail="No API key found for this user")
        
        api_key = api_key_response.data['api_key']
        
        FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://veyrax.com")
        if "NEXT_PUBLIC_APP_URL" in os.environ:
            FRONTEND_URL = os.environ.get("NEXT_PUBLIC_APP_URL")
            
        qstash_token = os.environ.get("QSTASH_TOKEN")
        
        if not qstash_token:
            raise HTTPException(status_code=500, detail="QStash token not configured")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            qstash_url = "https://qstash.upstash.io/v2/publish/"
            response = await client.post(
                f"{qstash_url}{FRONTEND_URL}/api/flow/qstash",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {qstash_token}",
                    "Upstash-Retries": "3",
                },
                json={
                    "flowId": flow_id,
                    "apiKey": api_key,
                    "allowDraft": allow_draft
                }
            )
            
            if response.status_code >= 400:
                raise Exception(f"QStash request failed with status {response.status_code}: {response.text}")
            
            log_api_call(
                user_id=user_id,
                endpoint=f"/flow/run-flow/{flow_id}",
                success=1
            )
            
            return {"status": "started", "message": "Flow execution has been started", "flowId": flow_id, "url": f"{FRONTEND_URL}/flow/{flow_id}/view?tab=runs"}
        
    except Exception as e:
        log_api_call(
            user_id=user_id,
            endpoint=f"/flow/run-flow/{flow_id}",
            success=0,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {str(e)}")
