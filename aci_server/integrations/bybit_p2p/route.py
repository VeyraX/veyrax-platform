from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
import os
from .schema import (
    GetP2POffersParams,
    GetP2POffersResponse,
    ApiResponse
)
from .service import BybitP2PService
from .client import BybitP2PClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema
from ..common.utils import apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from ..common.examples_handler import ExamplesLoader

router = APIRouter(prefix="/bybit_p2p", tags=["bybit_p2p"])

examples = ExamplesLoader()

async def get_bybit_p2p_service(request: Request):
    try:
        # Try to get the API key from user's provider keys
        # api_key = await validate_provider_api_key(request, "bybit_p2p")
        
        # Fallback to environment variable if not found
        # if not api_key:
        api_key = os.environ.get("RAPIDAPI_KEY")
            
        if not api_key:
            raise HTTPException(status_code=401, detail="API key is required")
            
        client = BybitP2PClient(api_key)
        apply_error_handler_to_client(client)
        service = BybitP2PService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize ByBit P2P service: {str(e)}")

@router.post("/get_p2p_offers", response_model=ApiResponse)
@schema(
    input_schema_class=GetP2POffersParams,
    output_schema_class=GetP2POffersResponse,
    examples=examples["/bybit_p2p/get_p2p_offers"]
)
async def get_p2p_offers(
    params: Dict[str, Any] = Body(...),
    service: BybitP2PService = Depends(get_bybit_p2p_service)
):
    validated_params = GetP2POffersParams(**params)
    return service.get_p2p_offers(validated_params)

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...)
):
    try:
        api_key = params.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = BybitP2PClient(api_key=api_key)
        if client.validate_api_key():
            return {"valid": True, "message": "API key is valid"}
        else:
            return {"valid": False, "message": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key: {str(e)}"}

apply_error_handler_to_router(router) 