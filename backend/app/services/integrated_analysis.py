"""
Integrated analysis service that combines TwelveLabs, OpenWeather, and NASA data
for comprehensive urban heat island analysis
"""
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.services.twelve_labs_client import UrbanAnalyzer
from app.services.weather_service import WeatherService  
from app.services.nasa_service import NASAService
from app.models.schemas import UrbanFeatures, Coordinates
from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class IntegratedAnalysisResult:
    """Complete analysis result combining all data sources"""
    task_id: str
    coordinates: Coordinates
    
    # TwelveLabs Analysis
    urban_features: UrbanFeatures
    
    # Weather Data
    current_weather: Dict[str, Any]
    heat_forecast: List[Dict[str, Any]]
    
    # NASA Data
    land_surface_temp: Dict[str, Any]
    vegetation_index: Dict[str, Any]
    air_quality: Dict[str, Any]
    climate_trends: Dict[str, Any]
    
    # Integrated Insights
    heat_island_intensity: float  # 0-10 scale
    risk_assessment: str  # low, moderate, high, extreme
    recommendations: List[Dict[str, Any]]
    
    # Processing metadata
    processing_time: float
    data_sources_used: List[str]
    analysis_timestamp: str

class IntegratedAnalysisService:
    """Service that orchestrates analysis across multiple APIs"""
    
    def __init__(self):
        self.urban_analyzer = UrbanAnalyzer()
        self.weather_service = WeatherService()
        self.nasa_service = NASAService()
        self.logger = get_logger(__name__)
    
    async def perform_comprehensive_analysis(
        self, 
        task_id: str, 
        image_path: str, 
        coordinates: Optional[Coordinates] = None
    ) -> IntegratedAnalysisResult:
        """
        Perform comprehensive urban heat island analysis combining:
        - TwelveLabs video analysis of satellite imagery
        - OpenWeather current conditions and forecasts
        - NASA satellite data (temperature, vegetation, air quality)
        """
        start_time = asyncio.get_event_loop().time()
        data_sources = []
        
        try:
            # If no coordinates provided, estimate from image analysis or use default
            if not coordinates:
                coordinates = Coordinates(lat=37.7749, lon=-122.4194)  # San Francisco default
            
            self.logger.info(f"Starting integrated analysis for task {task_id} at {coordinates.lat}, {coordinates.lon}")
            
            # Step 1: TwelveLabs Analysis (Visual Features)
            self.logger.info("Phase 1: Analyzing visual urban features with TwelveLabs...")
            urban_features = await self.urban_analyzer.analyze_satellite_image(image_path)
            data_sources.append("TwelveLabs")
            
            # Step 2: Weather Analysis (Current + Forecast)
            self.logger.info("Phase 2: Fetching weather data...")
            weather_tasks = [
                self.weather_service.get_current_weather(coordinates.lat, coordinates.lon),
                self.weather_service.get_heat_index_forecast(coordinates.lat, coordinates.lon)
            ]
            current_weather, heat_forecast = await asyncio.gather(*weather_tasks)
            data_sources.append("OpenWeather")
            
            # Step 3: NASA Analysis (Satellite + Environmental)
            self.logger.info("Phase 3: Fetching NASA satellite and environmental data...")
            nasa_tasks = [
                self.nasa_service.get_modis_temperature(coordinates.lat, coordinates.lon),
                self.nasa_service.get_vegetation_index(coordinates.lat, coordinates.lon),
                self.nasa_service.get_air_quality_data(coordinates.lat, coordinates.lon),
                self.nasa_service.get_climate_trends(coordinates.lat, coordinates.lon)
            ]
            land_surface_temp, vegetation_index, air_quality, climate_trends = await asyncio.gather(*nasa_tasks)
            data_sources.append("NASA")
            
            # Step 4: Integrate and Analyze
            self.logger.info("Phase 4: Performing integrated analysis...")
            heat_island_intensity = self._calculate_heat_island_intensity(
                urban_features, current_weather, land_surface_temp, vegetation_index
            )
            
            risk_assessment = self._assess_heat_risk(
                heat_island_intensity, current_weather, heat_forecast, climate_trends
            )
            
            recommendations = self._generate_integrated_recommendations(
                urban_features, current_weather, land_surface_temp, vegetation_index, 
                air_quality, heat_island_intensity
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            result = IntegratedAnalysisResult(
                task_id=task_id,
                coordinates=coordinates,
                urban_features=urban_features,
                current_weather=current_weather,
                heat_forecast=heat_forecast,
                land_surface_temp=land_surface_temp,
                vegetation_index=vegetation_index,
                air_quality=air_quality,
                climate_trends=climate_trends,
                heat_island_intensity=heat_island_intensity,
                risk_assessment=risk_assessment,
                recommendations=recommendations,
                processing_time=processing_time,
                data_sources_used=data_sources,
                analysis_timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"Integrated analysis completed. Heat Island Intensity: {heat_island_intensity:.2f}/10")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in integrated analysis: {str(e)}")
            raise
    
    def _calculate_heat_island_intensity(
        self, 
        urban_features: UrbanFeatures,
        weather: Dict[str, Any],
        land_temp: Dict[str, Any],
        vegetation: Dict[str, Any]
    ) -> float:
        """Calculate heat island intensity on 0-10 scale"""
        
        # Base score from current temperature vs feels_like
        temperature_factor = min((weather.get("feels_like", 25) - weather.get("temperature", 25)) * 2, 3.0)
        
        # Surface material analysis (from TwelveLabs)
        high_absorption_surfaces = len([
            s for s in urban_features.surfaces 
            if s.heat_absorption > 0.7  # High absorption materials
        ])
        surface_factor = min(high_absorption_surfaces * 0.5, 2.5)
        
        # Vegetation coverage (inverse relationship)
        total_vegetation = len(urban_features.vegetation)
        building_count = len(urban_features.buildings)
        vegetation_ratio = total_vegetation / max(building_count, 1) if building_count > 0 else 1
        vegetation_factor = max(0, 2.0 - vegetation_ratio * 2.0)
        
        # NASA vegetation index (NDVI)
        ndvi_value = vegetation.get("ndvi", 0.5)
        ndvi_factor = max(0, 2.0 - ndvi_value * 4.0)  # Lower NDVI = higher heat island
        
        # Land surface temperature differential
        day_temp = land_temp.get("land_surface_temperature", {}).get("day", 30)
        temp_factor = min((day_temp - 25) * 0.2, 1.5)  # Above 25°C contributes to heat island
        
        # Calculate weighted intensity
        intensity = (
            temperature_factor * 0.25 +  # Current weather impact
            surface_factor * 0.30 +      # Urban surface materials
            vegetation_factor * 0.20 +   # Local vegetation analysis
            ndvi_factor * 0.15 +         # Satellite vegetation data
            temp_factor * 0.10           # Land surface temperature
        )
        
        return min(max(intensity, 0.0), 10.0)  # Clamp to 0-10 range
    
    def _assess_heat_risk(
        self,
        heat_intensity: float,
        weather: Dict[str, Any],
        forecast: List[Dict[str, Any]],
        trends: Dict[str, Any]
    ) -> str:
        """Assess overall heat risk level"""
        
        current_heat_index = weather.get("feels_like", 25)
        max_forecast_heat = max([f.get("heat_index", 25) for f in forecast[:8]])  # Next 2 days
        
        # Risk factors
        if heat_intensity >= 8.0 or current_heat_index >= 40 or max_forecast_heat >= 38:
            return "extreme"
        elif heat_intensity >= 6.0 or current_heat_index >= 35 or max_forecast_heat >= 33:
            return "high"
        elif heat_intensity >= 4.0 or current_heat_index >= 30 or max_forecast_heat >= 28:
            return "moderate"
        else:
            return "low"
    
    def _generate_integrated_recommendations(
        self,
        urban_features: UrbanFeatures,
        weather: Dict[str, Any], 
        land_temp: Dict[str, Any],
        vegetation: Dict[str, Any],
        air_quality: Dict[str, Any],
        intensity: float
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on integrated analysis"""
        
        recommendations = []
        
        # Green infrastructure recommendations
        vegetation_ratio = len(urban_features.vegetation) / max(len(urban_features.buildings), 1)
        if vegetation_ratio < 0.3 or vegetation.get("ndvi", 0.5) < 0.4:
            recommendations.append({
                "category": "Green Infrastructure",
                "priority": "high",
                "action": "Increase Urban Vegetation",
                "description": "Add green roofs, urban trees, and pocket parks to improve cooling",
                "impact": f"Could reduce local temperatures by 2-5°C",
                "cost_estimate": "$50,000 - $200,000",
                "timeline": "6-12 months",
                "data_source": "TwelveLabs + NASA NDVI Analysis"
            })
        
        # Surface material recommendations
        high_absorption_count = len([s for s in urban_features.surfaces if s.heat_absorption > 0.7])
        if high_absorption_count > len(urban_features.surfaces) * 0.4:  # >40% high absorption
            recommendations.append({
                "category": "Surface Materials",
                "priority": "high",
                "action": "Cool Roof and Pavement Implementation",
                "description": "Replace dark surfaces with reflective materials",
                "impact": f"Reduce surface temperatures by 10-15°C",
                "cost_estimate": "$30,000 - $100,000",
                "timeline": "3-6 months",
                "data_source": "TwelveLabs Material Analysis"
            })
        
        # Air quality improvements
        aqi = air_quality.get("aqi", 50)
        if aqi > 100:
            recommendations.append({
                "category": "Air Quality",
                "priority": "medium",
                "action": "Improve Air Circulation",
                "description": "Enhance natural ventilation and reduce emissions",
                "impact": f"Improve AQI from {aqi} to healthier levels",
                "cost_estimate": "$20,000 - $80,000", 
                "timeline": "2-4 months",
                "data_source": "NASA Air Quality Data"
            })
        
        # Weather-based immediate actions
        if weather.get("feels_like", 25) > 32:
            recommendations.append({
                "category": "Immediate Actions",
                "priority": "urgent",
                "action": "Activate Cooling Centers",
                "description": "Public spaces with air conditioning for heat relief",
                "impact": "Immediate heat relief for residents",
                "cost_estimate": "$5,000 - $15,000",
                "timeline": "24-48 hours",
                "data_source": "OpenWeather Current Conditions"
            })
        
        # Long-term planning based on climate trends
        temp_trend = land_temp.get("land_surface_temperature", {})
        day_temp = temp_trend.get("day", 30)
        if day_temp > 35:
            recommendations.append({
                "category": "Long-term Planning",
                "priority": "medium",
                "action": "Urban Heat Resilience Strategy",
                "description": "Comprehensive planning for increasing temperatures",
                "impact": "Prepare city for climate change impacts",
                "cost_estimate": "$100,000 - $500,000",
                "timeline": "1-2 years",
                "data_source": "NASA Climate Trends + Weather Patterns"
            })
        
        return recommendations
