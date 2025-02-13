from fastapi import APIRouter, Depends
from .schema import WeatherData, ForecastData, WeatherRequest
from .service import WeatherService
from .client import WeatherClient
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/weather", tags=["weather"])

async def get_weather_service():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    client = WeatherClient(api_key)
    return WeatherService(client)

@router.post("/current", response_model=WeatherData)
async def get_current_weather(
    request: WeatherRequest,
    service: WeatherService = Depends(get_weather_service)
):
    return service.get_weather(city=request.city, country=request.country)

@router.post("/forecast", response_model=ForecastData)
async def get_weather_forecast(
    request: WeatherRequest,
    service: WeatherService = Depends(get_weather_service)
):
    return service.get_forecast(city=request.city, country=request.country)