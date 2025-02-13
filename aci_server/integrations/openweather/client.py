import requests
from typing import Dict, Any

class WeatherClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_weather_by_city(self, city: str, country: str) -> Dict[str, Any]:
        params = {
            'q': f"{city},{country}",
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(f"{self.base_url}/weather", params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast_by_city(self, city: str, country: str) -> Dict[str, Any]:
        params = {
            'q': f"{city},{country}",
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(f"{self.base_url}/forecast", params=params)
        response.raise_for_status()
        return response.json()