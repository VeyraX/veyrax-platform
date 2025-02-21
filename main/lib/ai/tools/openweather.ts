import { tool } from 'ai';
import { z } from 'zod';

export const openweather_getWeather = tool({
  description: 'Get weather forecast and current weather for a specific city and country',
  parameters: z.object({
    city: z.string().describe('Name of the city'),
    country: z.string().describe('Country code (e.g., US, UK, FR)'),
  }),
  execute: async function({ city, country }) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/weather/forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, country }),
      });

      if (!response.ok) throw new Error('Failed to fetch forecast data');
      
      const data = await response.json();
      
      const result = {
        success: true,
        city_name: data.city_name,
        country: data.country,
        forecast: data.forecast
      };
      
      return result;
    } catch (error) {
      console.error('Weather API Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch forecast data'
      };
    }
  }
});
