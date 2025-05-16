from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any, List, Optional
from .schema import AgentRequest, AgentResponse, WaterfallRequest, WaterfallResponse
from .agent import run_agent
from .services import run_waterfall
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

@router.post("/run-waterfall", response_model=WaterfallResponse)
async def perform_waterfall(request: WaterfallRequest) -> Dict[str, Any]:
    try:
        result = await run_waterfall(
            sheet_id=request.sheet_id,
            query=request.query, 
            row_indexes=request.row_indexes,
            row_range=request.row_range,
            column_ids=request.column_ids
        )
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error in run-waterfall endpoint: {str(e)}\n{tb}")
        return {
            "success": False,
            "message": f"Error processing waterfall request: {str(e)}",
            "error": str(e)
        }