from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import (
    WeatherData, ForecastData, WeatherRequest, ApiResponse,
    GetWeatherForecastParams
)
from .service import WeatherService
from .client import WeatherClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import input_schema
from ..common.utils import format_validation_error
from pydantic import ValidationError
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/weather", tags=["weather"])

async def get_weather_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "openweather")
        client = WeatherClient(api_key)
        return WeatherService(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Weather service: {str(e)}")

@router.post("/forecast", response_model=ApiResponse)
@input_schema(schema_class=GetWeatherForecastParams)
async def get_weather_forecast(
    params: Dict[str, Any] = Body(...),
    service: WeatherService = Depends(get_weather_service)
):
    try:
        validated_params = GetWeatherForecastParams(**params)
        return service.get_forecast(
            city=validated_params.city, 
            country=validated_params.country
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=format_validation_error(e, 'GetWeatherForecastParams'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))