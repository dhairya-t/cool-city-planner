#!/usr/bin/env python3
"""
Sentinel Hub Vegetation Service - Real satellite vegetation data
Uses European Space Agency's Sentinel-2 satellites for NDVI analysis
"""

import os
import asyncio
import httpx
import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger(__name__)

class SentinelVegetationService:
    """Service for real satellite vegetation data using Sentinel Hub API"""
    
    def __init__(self):
        # Sentinel Hub credentials (free tier available)
        self.client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
        self.client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
        self.base_url = "https://sh.dataspace.copernicus.eu"
        self.access_token = None
        self.token_expires = None
    
    async def get_access_token(self) -> str:
        """Get OAuth2 access token for Sentinel Hub"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        if not self.client_id or not self.client_secret:
            raise Exception("Sentinel Hub credentials not configured. Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET")
        
        auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        
        # Create basic auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        auth_header = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(auth_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                # Set expiration 5 minutes before actual expiration
                expires_in = token_data.get("expires_in", 3600) - 300
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                return self.access_token
            else:
                raise Exception(f"Failed to get Sentinel Hub token: {response.status_code}")
    
    async def get_vegetation_index(self, lat: float, lon: float, date: str = None) -> Dict[str, Any]:
        """Get real NDVI data from Sentinel-2 satellite"""
        try:
            # Get access token
            access_token = await self.get_access_token()
            
            # Set date range (last 30 days if not specified)
            if not date:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            else:
                end_date = datetime.strptime(date, "%Y-%m-%d")
                start_date = end_date - timedelta(days=15)
            
            # Create bounding box (small area around point)
            bbox_size = 0.01  # About 1km
            bbox = [
                lon - bbox_size, lat - bbox_size,
                lon + bbox_size, lat + bbox_size
            ]
            
            # Sentinel Hub Statistical API request for NDVI
            stats_url = f"{self.base_url}/api/v1/statistics"
            
            # NDVI calculation evalscript
            evalscript = """
            //VERSION=3
            function setup() {
              return {
                input: [{
                  bands: ["B04", "B08", "dataMask"],
                  units: "DN"
                }],
                output: [
                  {
                    id: "ndvi",
                    bands: 1,
                    sampleType: "FLOAT32"
                  },
                  {
                    id: "dataMask",
                    bands: 1
                  }
                ]
              }
            }
            
            function evaluatePixel(sample) {
              let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
              return {
                ndvi: [ndvi],
                dataMask: [sample.dataMask]
              };
            }
            """
            
            request_payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
                    },
                    "data": [{
                        "dataFilter": {
                            "timeRange": {
                                "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                                "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                            },
                            "mosaickingOrder": "leastCC"
                        },
                        "type": "sentinel-2-l2a"
                    }]
                },
                "aggregation": {
                    "timeRange": {
                        "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                        "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                    },
                    "aggregationInterval": {
                        "of": "P1D"
                    },
                    "evalscript": evalscript
                },
                "calculations": {
                    "ndvi": {
                        "statistics": {
                            "default": {
                                "histogramBins": 20,
                                "percentiles": {
                                    "k": [10, 50, 90]
                                }
                            }
                        }
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(stats_url, json=request_payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_sentinel_response(data, lat, lon)
                else:
                    logger.error(f"Sentinel Hub API error: {response.status_code} - {response.text}")
                    # Return realistic mock data as fallback
                    return self._get_enhanced_mock_ndvi(lat, lon)
        
        except Exception as e:
            logger.error(f"Error fetching Sentinel vegetation data: {str(e)}")
            logger.info("Falling back to enhanced mock NDVI data")
            return self._get_enhanced_mock_ndvi(lat, lon)
    
    def _process_sentinel_response(self, data: Dict[str, Any], lat: float, lon: float) -> Dict[str, Any]:
        """Process real Sentinel Hub API response"""
        try:
            if "data" in data and data["data"]:
                # Get the most recent NDVI statistics
                latest_data = data["data"][-1]  # Most recent date
                ndvi_stats = latest_data.get("outputs", {}).get("ndvi", {}).get("bands", {}).get("B0", {})
                
                if ndvi_stats.get("stats", {}):
                    stats = ndvi_stats["stats"]
                    
                    # Use median NDVI value as the representative value
                    ndvi_value = stats.get("percentiles", {}).get("50.0", stats.get("mean", 0.3))
                    
                    # Clamp NDVI to valid range
                    ndvi_value = max(-1.0, min(1.0, ndvi_value))
                    
                    # Calculate vegetation coverage percentage
                    vegetation_coverage = max(0, (ndvi_value + 1) / 2) * 100
                    
                    return {
                        "coordinates": {"lat": lat, "lon": lon},
                        "ndvi": ndvi_value,
                        "vegetation_coverage_percent": vegetation_coverage,
                        "vegetation_health": self._assess_vegetation_health(ndvi_value),
                        "data_quality": "high",
                        "resolution": "10m",
                        "timestamp": latest_data.get("interval", {}).get("from", datetime.now().isoformat()),
                        "source": "Sentinel-2 L2A (Real Data)",
                        "statistics": {
                            "mean": stats.get("mean"),
                            "std": stats.get("stDev"),
                            "min": stats.get("min"),
                            "max": stats.get("max"),
                            "sample_count": stats.get("sampleCount", 0)
                        }
                    }
                else:
                    logger.warning("No NDVI statistics in Sentinel response")
                    return self._get_enhanced_mock_ndvi(lat, lon)
            else:
                logger.warning("No data in Sentinel response")
                return self._get_enhanced_mock_ndvi(lat, lon)
                
        except Exception as e:
            logger.error(f"Error processing Sentinel response: {str(e)}")
            return self._get_enhanced_mock_ndvi(lat, lon)
    
    def _get_enhanced_mock_ndvi(self, lat: float, lon: float) -> Dict[str, Any]:
        """Enhanced mock NDVI based on geographic location"""
        import random
        
        # Seed for consistency
        random.seed(int((lat + lon) * 1000))
        
        # Enhanced geographic-based NDVI estimation
        abs_lat = abs(lat)
        
        # Climate zone-based estimation
        if abs_lat < 10:  # Tropical
            if -80 < lon < -30 and -20 < lat < 10:  # Amazon
                base_ndvi = 0.85 + random.uniform(-0.05, 0.1)
            elif 95 < lon < 155 and -10 < lat < 10:  # SE Asia rainforest
                base_ndvi = 0.8 + random.uniform(-0.1, 0.15)
            else:  # Other tropical
                base_ndvi = 0.6 + random.uniform(-0.2, 0.3)
        elif abs_lat < 25:  # Subtropical
            if 15 < lon < 50 and 15 < lat < 35:  # Sahara
                base_ndvi = 0.05 + random.uniform(-0.05, 0.1)
            elif -120 < lon < -90 and 25 < lat < 35:  # US Southwest desert
                base_ndvi = 0.15 + random.uniform(-0.1, 0.2)
            else:  # Other subtropical
                base_ndvi = 0.45 + random.uniform(-0.25, 0.35)
        elif abs_lat < 45:  # Temperate
            # Urban areas detection (approximate)
            if (-74.5 < lon < -73.5 and 40.5 < lat < 41):  # NYC area
                base_ndvi = 0.25 + random.uniform(-0.15, 0.4)  # Mix of urban and parks
            elif (-122.7 < lon < -122.3 and 37.6 < lat < 37.9):  # SF Bay area  
                base_ndvi = 0.35 + random.uniform(-0.2, 0.3)
            elif (-87.9 < lon < -87.5 and 41.6 < lat < 42.1):  # Chicago
                base_ndvi = 0.3 + random.uniform(-0.2, 0.4)
            else:  # Other temperate (farmland, forest)
                base_ndvi = 0.5 + random.uniform(-0.3, 0.4)
        elif abs_lat < 60:  # Boreal
            base_ndvi = 0.4 + random.uniform(-0.25, 0.35)
        else:  # Arctic/Antarctic
            base_ndvi = 0.1 + random.uniform(-0.1, 0.15)
        
        # Clamp to valid NDVI range
        ndvi_value = max(-1.0, min(1.0, base_ndvi))
        vegetation_coverage = max(0, (ndvi_value + 1) / 2) * 100
        
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "ndvi": ndvi_value,
            "vegetation_coverage_percent": vegetation_coverage,
            "vegetation_health": self._assess_vegetation_health(ndvi_value),
            "data_quality": "mock_enhanced",
            "resolution": "10m_equivalent",
            "timestamp": datetime.now().isoformat(),
            "source": "Enhanced Geographic Model (Fallback)"
        }
    
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
        """Get land surface temperature (simplified mock for now)"""
        # For now, provide mock data. Real implementation would use Sentinel-3 SLSTR
        import random
        random.seed(int((lat + lon) * 1000))
        
        # Base temperature based on latitude
        abs_lat = abs(lat)
        if abs_lat < 10:  # Tropical
            base_temp = 28 + random.uniform(-5, 7)
        elif abs_lat < 25:  # Subtropical  
            base_temp = 25 + random.uniform(-8, 10)
        elif abs_lat < 45:  # Temperate
            base_temp = 20 + random.uniform(-10, 12)
        elif abs_lat < 60:  # Boreal
            base_temp = 15 + random.uniform(-12, 8)
        else:  # Polar
            base_temp = 0 + random.uniform(-15, 10)
        
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "land_surface_temperature": {
                "day": base_temp + random.uniform(0, 8),
                "night": base_temp - random.uniform(2, 12)
            },
            "timestamp": datetime.now().isoformat(),
            "source": "Mock LST Data"
        }


# Legacy compatibility - alias to old name
NASAService = SentinelVegetationService
