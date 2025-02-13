from pydantic import BaseModel
from typing import List, Optional
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

class WeatherRequest(BaseModel):
    city: str
    country: str