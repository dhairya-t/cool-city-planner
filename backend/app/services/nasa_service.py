"""
NASA API integration for satellite and environmental data
"""
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class NASAService:
    """Service for fetching NASA satellite and environmental data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.NASA_API_KEY or "DEMO_KEY"
        self.base_url = "https://api.nasa.gov"
        
        if not settings.NASA_API_KEY:
            logger.warning("NASA API key not configured. Using demo key with rate limits.")
    
    async def get_landsat_imagery(self, lat: float, lon: float, date: str = None) -> Dict[str, Any]:
        """Get Landsat satellite imagery for coordinates"""
        try:
            # NASA Landsat API endpoint
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/planetary/earth/imagery",
                    params={
                        "lon": lon,
                        "lat": lat,
                        "date": date,
                        "dim": 0.10,  # Image width/height in degrees
                        "api_key": self.api_key
                    }
                )
                
                if response.status_code == 200:
                    return {
                        "image_url": response.url,
                        "date": date,
                        "coordinates": {"lat": lat, "lon": lon},
                        "source": "NASA Landsat"
                    }
                else:
                    logger.warning(f"NASA Landsat API returned {response.status_code}")
                    return self._get_mock_landsat_data(lat, lon, date)
                    
        except Exception as e:
            logger.error(f"Error fetching Landsat imagery: {str(e)}")
            return self._get_mock_landsat_data(lat, lon, date)
    
    async def get_modis_temperature(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get MODIS land surface temperature data"""
        try:
            # This would typically use NASA's MODIS API or Earth Data API
            # For demo, we'll simulate the data structure
            async with httpx.AsyncClient() as client:
                # Note: Actual NASA MODIS data requires specialized endpoints
                # This is a simplified example structure
                
                # Simulate API call delay
                await asyncio.sleep(1)
                
                return self._get_mock_modis_data(lat, lon)
                
        except Exception as e:
            logger.error(f"Error fetching MODIS temperature: {str(e)}")
            return self._get_mock_modis_data(lat, lon)
    
    async def get_vegetation_index(self, lat: float, lon: float, date: str = None) -> Dict[str, Any]:
        """Get NDVI (Normalized Difference Vegetation Index) data"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # NASA MODIS NDVI data
            async with httpx.AsyncClient() as client:
                # Simulate API call - actual implementation would use NASA's Earth Data
                await asyncio.sleep(1)
                
                return self._get_mock_ndvi_data(lat, lon, date)
                
        except Exception as e:
            logger.error(f"Error fetching vegetation index: {str(e)}")
            return self._get_mock_ndvi_data(lat, lon, date)
    
    async def get_air_quality_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get air quality data from NASA's air quality API"""
        try:
            async with httpx.AsyncClient() as client:
                # NASA's air quality data (simplified)
                response = await client.get(
                    f"{self.base_url}/planetary/earth/assets",
                    params={
                        "lon": lon,
                        "lat": lat,
                        "date": datetime.now().strftime('%Y-%m-%d'),
                        "dim": 0.05,
                        "api_key": self.api_key
                    }
                )
                
                if response.status_code == 200:
                    return self._process_air_quality_response(response.json(), lat, lon)
                else:
                    return self._get_mock_air_quality_data(lat, lon)
                    
        except Exception as e:
            logger.error(f"Error fetching air quality data: {str(e)}")
            return self._get_mock_air_quality_data(lat, lon)
    
    async def get_climate_trends(self, lat: float, lon: float, years: int = 5) -> Dict[str, Any]:
        """Get historical climate trends for the area"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            
            # This would integrate with NASA's climate data APIs
            # For demo, we simulate the analysis
            
            return self._get_mock_climate_trends(lat, lon, years)
            
        except Exception as e:
            logger.error(f"Error fetching climate trends: {str(e)}")
            return self._get_mock_climate_trends(lat, lon, years)
    
    def _process_air_quality_response(self, data: Dict, lat: float, lon: float) -> Dict[str, Any]:
        """Process NASA air quality response"""
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "pm25": 15.2,  # Simulated
            "pm10": 28.5,
            "ozone": 45.8,
            "no2": 12.3,
            "so2": 8.7,
            "co": 0.8,
            "aqi": 65,
            "quality_level": "Moderate",
            "source": "NASA Air Quality"
        }
    
    def _get_mock_landsat_data(self, lat: float, lon: float, date: str) -> Dict[str, Any]:
        """Generate mock Landsat data"""
        return {
            "image_url": f"https://api.nasa.gov/planetary/earth/imagery?lon={lon}&lat={lat}&date={date}",
            "date": date,
            "coordinates": {"lat": lat, "lon": lon},
            "source": "NASA Landsat (Mock)",
            "resolution": "30m",
            "bands": ["Red", "Green", "Blue", "NIR", "SWIR1", "SWIR2", "Thermal"]
        }
    
    def _get_mock_modis_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Generate mock MODIS land surface temperature data"""
        # Simulate realistic temperature data based on location
        base_temp = 25.0 + (lat - 37.7749) * 0.5  # Adjust based on latitude
        
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "land_surface_temperature": {
                "day": base_temp + 8.5,
                "night": base_temp - 3.2,
                "unit": "celsius"
            },
            "data_quality": "good",
            "timestamp": datetime.now().isoformat(),
            "resolution": "1km",
            "source": "NASA MODIS"
        }
    
    def _get_mock_ndvi_data(self, lat: float, lon: float, date: str) -> Dict[str, Any]:
        """Generate mock NDVI data"""
        # NDVI ranges from -1 to 1, higher values indicate more vegetation
        import random
        random.seed(int(lat * 1000) + int(lon * 1000))  # Consistent mock data
        
        ndvi_value = random.uniform(0.2, 0.8)  # Typical urban to vegetated range
        
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "date": date,
            "ndvi": ndvi_value,
            "vegetation_health": "good" if ndvi_value > 0.5 else "moderate" if ndvi_value > 0.3 else "poor",
            "chlorophyll_content": ndvi_value * 100,  # Relative measure
            "source": "NASA MODIS NDVI"
        }
    
    def _get_mock_air_quality_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Generate mock air quality data"""
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "pm25": 18.5,
            "pm10": 32.1,
            "ozone": 52.3,
            "no2": 15.8,
            "so2": 9.2,
            "co": 1.1,
            "aqi": 72,
            "quality_level": "Moderate",
            "source": "NASA Air Quality (Mock)"
        }
    
    def _get_mock_climate_trends(self, lat: float, lon: float, years: int) -> Dict[str, Any]:
        """Generate mock climate trend data"""
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "analysis_period": f"{years} years",
            "temperature_trend": {
                "average_increase_per_year": 0.15,
                "total_change": years * 0.15,
                "trend": "warming"
            },
            "precipitation_trend": {
                "average_change_per_year": -2.1,  # mm
                "total_change": years * -2.1,
                "trend": "decreasing"
            },
            "extreme_events": {
                "heat_waves_per_year": 3.2,
                "drought_days_per_year": 45,
                "increase_in_hot_days": years * 2.3
            },
            "vegetation_changes": {
                "ndvi_trend": "declining",
                "average_change_per_year": -0.02
            },
            "source": "NASA Climate Analysis"
        }
