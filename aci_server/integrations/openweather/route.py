from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
from .schema import WeatherData, ForecastData, WeatherRequest, ApiResponse
from .service import WeatherService
from .client import WeatherClient
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/weather", tags=["weather"])

async def get_weather_service():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenWeather API key not found")
    
    client = WeatherClient(api_key)
    return WeatherService(client)

@router.post("/forecast", response_model=ApiResponse)
async def get_weather_forecast(
    params: Dict[str, Any] = Body(...),
    service: WeatherService = Depends(get_weather_service)
):
    try:
        request = WeatherRequest(**params)
        return service.get_forecast(city=request.city, country=request.country)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))