"""
OpenWeather API integration for climate data
"""
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class WeatherService:
    """Service for fetching weather data from OpenWeather API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("OpenWeather API key not configured. Weather data will be mocked.")
    
    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather conditions for coordinates"""
        if not self.api_key:
            return self._get_mock_weather_data()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "cloudiness": data["clouds"]["all"],
                    "visibility": data.get("visibility", 10000) / 1000  # Convert to km
                }
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return self._get_mock_weather_data()
    
    async def get_historical_weather(self, lat: float, lon: float, dt: int) -> Dict[str, Any]:
        """Get historical weather data (requires One Call API subscription)"""
        if not self.api_key:
            return self._get_mock_historical_data()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openweathermap.org/data/3.0/onecall/timemachine",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "dt": dt,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                return {
                    "temperature": data["data"][0]["temp"],
                    "humidity": data["data"][0]["humidity"],
                    "pressure": data["data"][0]["pressure"],
                    "wind_speed": data["data"][0]["wind_speed"],
                    "cloudiness": data["data"][0]["clouds"]
                }
                
        except Exception as e:
            logger.error(f"Error fetching historical weather: {str(e)}")
            return self._get_mock_historical_data()
    
    async def get_heat_index_forecast(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Get 5-day weather forecast with heat index calculations"""
        if not self.api_key:
            return self._get_mock_forecast_data()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                forecast = []
                
                for item in data["list"][:20]:  # 5 days, 4 times per day
                    heat_index = self._calculate_heat_index(
                        item["main"]["temp"], 
                        item["main"]["humidity"]
                    )
                    
                    forecast.append({
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "humidity": item["main"]["humidity"],
                        "heat_index": heat_index,
                        "description": item["weather"][0]["description"],
                        "wind_speed": item["wind"]["speed"]
                    })
                
                return forecast
                
        except Exception as e:
            logger.error(f"Error fetching forecast data: {str(e)}")
            return self._get_mock_forecast_data()
    
    def _calculate_heat_index(self, temp_c: float, humidity: float) -> float:
        """Calculate heat index from temperature (Celsius) and humidity"""
        # Convert to Fahrenheit for calculation
        temp_f = (temp_c * 9/5) + 32
        
        # Simplified heat index formula
        if temp_f >= 80:
            heat_index_f = (
                -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
                - 0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2
                - 5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity
                + 8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2
            )
            # Convert back to Celsius
            return (heat_index_f - 32) * 5/9
        else:
            return temp_c
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """Generate mock weather data for testing"""
        return {
            "temperature": 28.5,
            "feels_like": 31.2,
            "humidity": 65,
            "pressure": 1013,
            "description": "partly cloudy",
            "wind_speed": 3.2,
            "wind_direction": 180,
            "cloudiness": 40,
            "visibility": 10.0
        }
    
    def _get_mock_historical_data(self) -> Dict[str, Any]:
        """Generate mock historical weather data"""
        return {
            "temperature": 26.8,
            "humidity": 70,
            "pressure": 1015,
            "wind_speed": 2.8,
            "cloudiness": 30
        }
    
    def _get_mock_forecast_data(self) -> List[Dict[str, Any]]:
        """Generate mock forecast data"""
        forecast = []
        base_temp = 25.0
        
        for i in range(20):
            temp = base_temp + (i % 4) * 2 + (i // 4) * 0.5
            humidity = 60 + (i % 3) * 5
            heat_index = self._calculate_heat_index(temp, humidity)
            
            forecast.append({
                "datetime": f"2024-07-{19 + i//4:02d} {6 + (i%4)*6:02d}:00:00",
                "temperature": temp,
                "humidity": humidity,
                "heat_index": heat_index,
                "description": "partly cloudy",
                "wind_speed": 2.5 + (i % 2) * 0.8
            })
        
        return forecast
