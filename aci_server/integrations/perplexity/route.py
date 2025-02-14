from fastapi import APIRouter, Depends, HTTPException
from .schema import CompletionRequest, CompletionResponse
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

@router.post("/completions", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    service: PerplexityService = Depends(get_perplexity_service)
):
    return service.create_completion(request)