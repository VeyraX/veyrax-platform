from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
from .schema import AgentRequest, AgentResponse
from .agent import run_agent
import logging
import traceback

router = APIRouter(tags=["fild"], prefix="/fild")

@router.post("/run-agent", response_model=AgentResponse)
async def perform_web_search(request: AgentRequest) -> Dict[str, Any]:
    try:
        result = await run_agent(request.query)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error in run-agent endpoint: {str(e)}\n{tb}")
        return {
            "query": request.query,
            "result": f"Error processing request: {str(e)}",
            "success": False,
            "payload": []
        }