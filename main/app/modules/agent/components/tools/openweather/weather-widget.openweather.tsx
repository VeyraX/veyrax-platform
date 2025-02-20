// @ts-ignore
import ReactRain from 'react-rain-animation';
import 'react-rain-animation/lib/style.css';
import { useEffect, useState } from 'react';
import Snowfall from 'react-snowfall';

import { WeatherData, WeatherProps } from "./types.openweather"

const MistOverlay = () => {
  return (
    <div className="absolute inset-0 z-10 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-t from-white/50 to-transparent mix-blend-overlay" />
      {[...Array(3)].map((_, i) => (
        <div
          key={i}
          className={`
            absolute inset-0 opacity-${30 + i * 20}
            bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxmaWx0ZXIgaWQ9ImEiIHg9IjAlIiB5PSIwJSIgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9Ii4wMDUiIG51bU9jdGF2ZXM9IjUiLz48L2ZpbHRlcj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsdGVyPSJ1cmwoI2EpIiBvcGFjaXR5PSIuMTUiLz48L3N2Zz4=')]
            animate-mistFlow${i + 1}
          `}
        />
      ))}
    </div>
  );
};

const Weather: React.FC<WeatherProps> = ({ data }) => {

  const currentWeather = data.forecast[0];
  const isMisty = currentWeather.description.toLowerCase().includes('mist') || 
                  currentWeather.description.toLowerCase().includes('fog');
  const isSnowing = currentWeather.description.toLowerCase().includes('snow');
  
  const getWeatherStyles = () => {
    const condition = currentWeather.description.toLowerCase();
    if (condition.includes('rain') || condition.includes('drizzle')) {
      return {
        background: 'bg-gradient-to-br from-gray-700 via-gray-800 to-gray-900',
        animation: '',
        overlay: 'before:absolute before:inset-0 before:bg-rain-overlay'
      };
    } else if (condition.includes('cloud')) {
      return {
        background: 'bg-gradient-to-br from-gray-100 via-gray-300 to-gray-500',
        animation: 'animate-float',
        overlay: 'before:absolute before:inset-0 before:bg-cloud-overlay before:animate-float'
      };
    } else if (condition.includes('clear')) {
      return {
        background: 'bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600',
        animation: 'animate-shine',
        overlay: 'before:absolute before:inset-0 before:bg-sun-overlay before:animate-spin-slow'
      };
    } else if (condition.includes('snow')) {
      return {
        background: 'bg-gradient-to-br from-blue-100 via-blue-200 to-gray-200',
        animation: 'animate-snow',
        overlay: 'before:absolute before:inset-0 before:bg-snow-overlay before:animate-snow'
      };
    } else if (condition.includes('thunder')) {
      return {
        background: 'bg-gradient-to-br from-gray-900 via-purple-900 to-gray-800',
        animation: 'animate-thunder',
        overlay: 'before:absolute before:inset-0 before:bg-lightning-overlay before:animate-flash'
      };
    } else {
      return {
        background: 'bg-gradient-to-br from-blue-400 to-blue-600',
        animation: '',
        overlay: ''
      };
    }
  };

  const getTextColor = () => {
    const condition = currentWeather.description.toLowerCase();
    return condition.includes('rain') || condition.includes('thunder') 
      ? 'text-white' 
      : condition.includes('cloud') || condition.includes('snow')
        ? 'text-gray-800'
        : 'text-white';
  };

  const weatherStyles = getWeatherStyles();
  const isRaining = currentWeather.description.toLowerCase().includes('rain') || 
                    currentWeather.description.toLowerCase().includes('drizzle');

  return (
    <div className={`
      relative overflow-hidden rounded-xl shadow-2xl p-6 max-w-sm 
      ${weatherStyles.background} ${weatherStyles.animation} ${weatherStyles.overlay}
      transition-all duration-500
    `}>
      {isRaining && (
        <div className="absolute inset-0 z-10">
          <ReactRain numDrops="50" rainSpeed={1} />
        </div>
      )}
      {isSnowing && (
        <div className="absolute inset-0 z-10">
          <Snowfall 
            snowflakeCount={100}
            radius={[0.5, 3.0]}
            speed={[0.5, 3.0]}
            wind={[-0.5, 2.0]}
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%'
            }}
          />
        </div>
      )}
      {isMisty && <MistOverlay />}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className={`text-2xl font-bold ${getTextColor()}`}>
            {data.city_name}, {data.country}
          </h2>
          <p className={`text-xl ${getTextColor()} capitalize opacity-90`}>
            {currentWeather.description}
          </p>
        </div>
      </div>

      <div className="mb-6">
        <div className={`text-5xl font-bold ${getTextColor()} mb-2`}>
          {Math.round(currentWeather.temperature)}°C
        </div>
        <p className={`${getTextColor()} opacity-90`}>
          Feels like: {Math.round(currentWeather.feels_like)}°C
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-white/20">
        <h3 className={`${getTextColor()} text-lg font-semibold mb-3`}>Forecast</h3>
        <div className="grid grid-cols-4 gap-2">
          {data.forecast.slice(1, 5).map((day, index) => (
            <div 
              key={index} 
              className="bg-white/10 backdrop-blur-md p-2 rounded-lg text-center"
            >
              <p className={`${getTextColor()} text-sm font-medium`}>
                {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
              </p>
              <p className={`${getTextColor()} text-lg font-bold`}>
                {Math.round(day.temperature)}°C
              </p>
              <p className={`${getTextColor()} text-xs opacity-75 capitalize truncate`}>
                {day.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Weather;