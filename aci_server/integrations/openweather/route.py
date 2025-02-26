from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import WeatherData, ForecastData, WeatherRequest, ApiResponse
from .service import WeatherService
from .client import WeatherClient
from ..common.auth import validate_provider_api_key

router = APIRouter(prefix="/weather", tags=["weather"])

async def get_weather_service(request: Request):
    api_key = await validate_provider_api_key(request, "openweather")
    client = WeatherClient(api_key)
    return WeatherService(client)

@router.post("/forecast", response_model=ApiResponse)
async def get_weather_forecast(
    params: Dict[str, Any] = Body(...),
    service: WeatherService = Depends(get_weather_service)
):
    try:
        request_data = WeatherRequest(**params)
        return service.get_forecast(city=request_data.city, country=request_data.country)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))