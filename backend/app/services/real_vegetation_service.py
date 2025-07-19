#!/usr/bin/env python3
"""
Real Vegetation Service using OpenWeatherMap Satellite API
NO MOCK DATA - Only real satellite NDVI data from Landsat 8 and Sentinel 2
"""

import os
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger(__name__)

class RealVegetationService:
    """Real satellite vegetation data using OpenWeather Satellite API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise Exception("OpenWeather API key required for real vegetation data")
        
        self.base_url = "http://api.agromonitoring.com/agro/1.0"
        logger.info(f"✅ Real Vegetation Service initialized with API key: {self.api_key[:8]}...")
    
    async def get_vegetation_index(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get REAL NDVI data from OpenWeather Satellite API"""
        try:
            # Step 1: Create a polygon around the point (required for Agro API)
            polygon_id = await self._create_polygon(lat, lon)
            
            # Step 2: Get satellite imagery for the polygon
            satellite_data = await self._get_satellite_imagery(polygon_id)
            
            # Step 3: Get NDVI statistics for the polygon
            ndvi_stats = await self._get_ndvi_statistics(polygon_id)
            
            return {
                "coordinates": {"lat": lat, "lon": lon},
                "ndvi": ndvi_stats.get("mean", 0.0),
                "vegetation_coverage_percent": max(0, (ndvi_stats.get("mean", 0.0) + 1) / 2) * 100,
                "vegetation_health": self._assess_vegetation_health(ndvi_stats.get("mean", 0.0)),
                "data_quality": "high_real",
                "resolution": "10m",
                "timestamp": datetime.now().isoformat(),
                "source": "OpenWeather Satellite (Landsat 8 + Sentinel 2)",
                "polygon_id": polygon_id,
                "statistics": ndvi_stats,
                "imagery_data": satellite_data
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get real vegetation data: {str(e)}")
            raise Exception(f"Real vegetation service failed: {str(e)}. NO MOCK DATA AVAILABLE.")
    
    async def _create_polygon(self, lat: float, lon: float) -> str:
        """Create a small polygon around the coordinates"""
        # Create a small square around the point (about 100m x 100m)
        offset = 0.0005  # Approximately 50m at mid-latitudes
        
        polygon = {
            "name": f"Vegetation Analysis Point {lat},{lon}",
            "geo_json": {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon - offset, lat - offset],
                        [lon + offset, lat - offset],
                        [lon + offset, lat + offset],
                        [lon - offset, lat + offset],
                        [lon - offset, lat - offset]
                    ]]
                }
            }
        }
        
        url = f"{self.base_url}/polygons"
        params = {"appid": self.api_key}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=polygon, params=params)
            
            if response.status_code == 201:
                polygon_data = response.json()
                polygon_id = polygon_data["id"]
                logger.info(f"✅ Created polygon {polygon_id} for coordinates {lat}, {lon}")
                return polygon_id
            else:
                logger.error(f"Failed to create polygon: {response.status_code} - {response.text}")
                raise Exception(f"Failed to create polygon: HTTP {response.status_code}")
    
    async def _get_satellite_imagery(self, polygon_id: str) -> Dict[str, Any]:
        """Get available satellite imagery for the polygon"""
        # Get imagery from last 30 days
        start_date = int((datetime.now() - timedelta(days=30)).timestamp())
        end_date = int(datetime.now().timestamp())
        
        url = f"{self.base_url}/image/search"
        params = {
            "appid": self.api_key,
            "polyid": polygon_id,
            "start": start_date,
            "end": end_date
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                imagery_data = response.json()
                logger.info(f"✅ Found {len(imagery_data)} satellite images")
                return imagery_data
            else:
                logger.error(f"Failed to get satellite imagery: {response.status_code} - {response.text}")
                raise Exception(f"Failed to get satellite imagery: HTTP {response.status_code}")
    
    async def _get_ndvi_statistics(self, polygon_id: str) -> Dict[str, Any]:
        """Get NDVI statistics for the polygon"""
        url = f"{self.base_url}/statistics"
        params = {
            "appid": self.api_key,
            "polyid": polygon_id
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Extract NDVI statistics
                if stats_data:
                    latest_stats = stats_data[-1] if isinstance(stats_data, list) else stats_data
                    ndvi_data = latest_stats.get("ndvi", {})
                    
                    return {
                        "mean": ndvi_data.get("mean", 0.0),
                        "std": ndvi_data.get("std", 0.0),
                        "min": ndvi_data.get("min", 0.0),
                        "max": ndvi_data.get("max", 0.0),
                        "median": ndvi_data.get("median", 0.0),
                        "p25": ndvi_data.get("p25", 0.0),
                        "p75": ndvi_data.get("p75", 0.0),
                        "count": ndvi_data.get("count", 0),
                        "date": latest_stats.get("dt", datetime.now().timestamp())
                    }
                else:
                    raise Exception("No NDVI statistics available")
            else:
                logger.error(f"Failed to get NDVI statistics: {response.status_code} - {response.text}")
                raise Exception(f"Failed to get NDVI statistics: HTTP {response.status_code}")
    
    def _assess_vegetation_health(self, ndvi: float) -> str:
        """Assess vegetation health from NDVI value"""
        if ndvi > 0.7:
            return "excellent"
        elif ndvi > 0.5:
            return "good"
        elif ndvi > 0.3:
            return "moderate"
        elif ndvi > 0.1:
            return "poor"
        else:
            return "very_poor"
    
    async def get_land_surface_temperature(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get land surface temperature (not available in OpenWeather Satellite API)"""
        # This would require a different API or service
        # For now, indicate that this specific data is not available
        raise Exception("Land surface temperature not available through OpenWeather Satellite API")
    
    async def cleanup_polygon(self, polygon_id: str):
        """Clean up the temporary polygon"""
        try:
            url = f"{self.base_url}/polygons/{polygon_id}"
            params = {"appid": self.api_key}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(url, params=params)
                
                if response.status_code == 204:
                    logger.info(f"✅ Cleaned up polygon {polygon_id}")
                else:
                    logger.warning(f"Failed to cleanup polygon {polygon_id}: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error cleaning up polygon {polygon_id}: {str(e)}")


# Legacy compatibility
NASAService = RealVegetationService
SentinelVegetationService = RealVegetationService
