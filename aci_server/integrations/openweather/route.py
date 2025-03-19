from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Any
from .schema import (
    WeatherData, ForecastData, WeatherRequest, ApiResponse,
    GetWeatherForecastParams, GetWeatherForecastResponse
)
from .service import WeatherService
from .client import WeatherClient
from ..common.auth import validate_provider_api_key
from ..common.input_schema_decorator import schema, input_schema, output_schema
from ..common.utils import format_validation_error, apply_error_handler_to_service, apply_error_handler_to_router, apply_error_handler_to_client
from pydantic import ValidationError
from ..common.examples_handler import ExamplesLoader
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/openweather", tags=["openweather"])

examples = ExamplesLoader()  # Will automatically use /integrations/openweather directory

async def get_weather_service(request: Request):
    try:
        api_key = await validate_provider_api_key(request, "openweather")
        client = WeatherClient(api_key)
        apply_error_handler_to_client(client)
        service = WeatherService(client)
        apply_error_handler_to_service(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Weather service: {str(e)}")

@router.post("/forecast", response_model=ApiResponse)
@schema(input_schema_class=GetWeatherForecastParams, output_schema_class=GetWeatherForecastResponse, examples=examples["/weather/forecast"])
async def get_weather_forecast(
    params: Dict[str, Any] = Body(...),
    service: WeatherService = Depends(get_weather_service)
):
    validated_params = GetWeatherForecastParams(**params)
    return service.get_forecast(
        city=validated_params.city, 
        country=validated_params.country
    )

@router.post("/validate_key")
async def validate_key(
    params: Dict[str, Any] = Body(...),
):
    try:
        api_key = params.get("api_key", "")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        client = WeatherClient(api_key)
        response = client.get_weather_by_city("London", "GB")
        
        return {"valid": True, "message": "API key is valid"}
    except Exception as e:
        return {"valid": False, "message": f"Invalid API key"}

apply_error_handler_to_router(router)