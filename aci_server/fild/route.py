from fastapi import APIRouter, Body, HTTPException, Request, Depends
from typing import Dict, Any, List, Optional
from .schema import AgentRequest, AgentResponse, WaterfallRequest, WaterfallResponse, PeopleSearchRequest, PeopleSearchResponse, CompanySearchRequest, CompanySearchResponse
from .agent import run_agent
from .services import run_waterfall, search_people, search_companies
import logging
import traceback
from integrations.common.auth import get_user_from_request

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
async def perform_waterfall(request: WaterfallRequest, req: Request) -> Dict[str, Any]:
    try:
        user_id = await get_user_from_request(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        result = await run_waterfall(
            sheet_id=request.sheet_id,
            row_indexes=request.row_indexes,
            row_range=request.row_range,
            column_ids=request.column_ids,
            chat_id=request.chat_id
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

@router.post("/people-search", response_model=PeopleSearchResponse)
async def perform_people_search(request: PeopleSearchRequest, req: Request) -> Dict[str, Any]:
    try:
        user_id = await get_user_from_request(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        result = await search_people(
            company_query=request.company_query,
            people_query=request.people_query
        )
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error in people-search endpoint: {str(e)}\n{tb}")
        return {
            "success": False,
            "message": f"Error processing people search request: {str(e)}",
            "error": str(e),
            "results": []
        }

@router.post("/company-search", response_model=CompanySearchResponse)
async def perform_company_search(request: CompanySearchRequest, req: Request) -> Dict[str, Any]:
    try:
        user_id = await get_user_from_request(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        result = await search_companies(
            query=request.query
        )
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error in company-search endpoint: {str(e)}\n{tb}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@router.post("/run-cloud-waterfall", response_model=WaterfallResponse)
async def perform_cloud_waterfall(request: WaterfallRequest, req: Request) -> Dict[str, Any]:
    try:
        user_id = await get_user_from_request(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        from .cloud_services import run_cloud_waterfall
        
        result = await run_cloud_waterfall(
            sheet_id=request.sheet_id,
            row_indexes=request.row_indexes,
            row_range=request.row_range,
            column_ids=request.column_ids,
            chat_id=request.chat_id
        )
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error in cloud waterfall endpoint: {str(e)}\n{tb}")
        return {
            "success": False,
            "message": f"Error processing cloud waterfall request: {str(e)}",
            "error": str(e)
        }

@router.post("/process-batch")
async def process_batch_endpoint(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from .cloud_processor import process_batch
        
        result = await process_batch(batch_data)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error in process-batch endpoint: {str(e)}\n{tb}")
        return {
            "success": False,
            "error": str(e)
        }