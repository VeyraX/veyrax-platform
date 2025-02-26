from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest, Body
from typing import Dict, Any
from .schema import CompletionRequest, ApiResponse
from .service import PerplexityService
from .client import PerplexityClient
import os

router = APIRouter(prefix="/perplexity", tags=["perplexity"])

async def get_perplexity_service():
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Perplexity API key not found")
    
    client = PerplexityClient(api_key)
    return PerplexityService(client)

@router.post("/create_completion", response_model=ApiResponse)
async def create_completion(
    params: Dict[str, Any] = Body(...),
    service: PerplexityService = Depends(get_perplexity_service)
):
    try:
        request = CompletionRequest(**params)
        return service.create_completion(request)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))