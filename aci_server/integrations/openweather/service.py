from datetime import datetime
from .client import WeatherClient
from .schema import WeatherData, ForecastData, ForecastItem

class WeatherService:
    def __init__(self, client: WeatherClient):
        self.client = client

    def get_weather(self, city: str, country: str) -> WeatherData:
        response = self.client.get_weather_by_city(city, country)
        
        return WeatherData(
            temperature=response['main']['temp'],
            feels_like=response['main']['feels_like'],
            humidity=response['main']['humidity'],
            pressure=response['main']['pressure'],
            description=response['weather'][0]['description'],
            wind_speed=response['wind']['speed'],
            city_name=response['name'],
            country=response['sys']['country']
        )

    def get_forecast(self, city: str, country: str) -> ForecastData:
        response = self.client.get_forecast_by_city(city, country)
        
        forecast_items = []
        daily_forecasts = {}

        for item in response['list']:
            dt = datetime.fromtimestamp(item['dt'])
            if dt.hour == 12:
                forecast_items.append(
                    ForecastItem(
                        date=dt,
                        temperature=item['main']['temp'],
                        feels_like=item['main']['feels_like'],
                        humidity=item['main']['humidity'],
                        pressure=item['main']['pressure'],
                        description=item['weather'][0]['description'],
                        wind_speed=item['wind']['speed']
                    )
                )

        return ForecastData(
            city_name=response['city']['name'],
            country=response['city']['country'],
            forecast=forecast_items
        )