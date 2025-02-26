from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class WeatherData(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float
    city_name: str
    country: str

class ForecastItem(BaseModel):
    date: datetime
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float

class ForecastData(BaseModel):
    city_name: str
    country: str
    forecast: List[ForecastItem]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class WeatherRequest(BaseModel):
    city: str
    country: str

class ApiResponse(BaseModel):
    data: ForecastData
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None