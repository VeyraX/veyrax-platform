from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from aci_server.utils.healthcheck import check_tools_endpoint

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    details: Dict[str, Any]


@router.get("/@healthcheck", response_model=HealthCheckResponse)
async def healthcheck():
    """
    API endpoint to check the health of the system.
    Tests connectivity to Supabase and the tools endpoint.
    """
    result = check_tools_endpoint()
    
    # If the status is error or unhealthy, return a 500 status code
    if result.get("status") in ["error", "unhealthy"]:
        raise HTTPException(
            status_code=500,
            detail=result
        )
    
    return {
        "status": "healthy",
        "details": result
    } 