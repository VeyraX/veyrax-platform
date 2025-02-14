export interface WeatherData {
    city_name: string;
    country: string;
    success: boolean;
    forecast: Array<{
      date: string;
      temperature: number;
      feels_like: number;
      humidity: number;
      pressure: number;
      wind_speed: number;
      description: string;
    }>;
  }
  
export interface WeatherProps {
    data: WeatherData;
  }
  