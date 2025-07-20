"""
API routes for the CoolCity Planner backend
"""
import asyncio
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ImageUploadResponse, 
    TaskStatusResponse,
    UrbanAnalysisResponse,
    UrbanFeatures,
    Coordinates
)
from app.core.config import settings
from app.core.logging import get_logger
from app.services.twelve_labs_client import UrbanAnalyzer
from app.services.live_satellite_service import LiveSatelliteService

logger = get_logger(__name__)

# Global router
router = APIRouter()

# In-memory storage for task status (in production, use Redis or database)
task_storage: Dict[str, Dict[str, Any]] = {}

@router.post("/api/upload", response_model=ImageUploadResponse)
async def upload_satellite_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload satellite image for analysis"""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique task ID and filename
        task_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix if file.filename else '.jpg'
        filename = f"{task_id}{file_extension}"
        file_path = upload_dir / filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Initialize task status
        task_storage[task_id] = {
            'status': 'uploaded',
            'file_path': str(file_path),
            'progress': 0,
            'created_at': asyncio.get_event_loop().time(),
            'error_message': None,
            'result': None
        }
        
        # Start analysis in background
        background_tasks.add_task(process_satellite_image, task_id, str(file_path))
        
        logger.info(f"Image uploaded successfully. Task ID: {task_id}")
        
        return ImageUploadResponse(
            success=True,
            task_id=task_id,
            message="Image uploaded successfully. Analysis started.",
            processing_time_estimate=180  # 3 minutes estimate
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")

@router.get("/api/status/{task_id}", response_model=TaskStatusResponse)
async def get_analysis_status(task_id: str):
    """Get the status of an analysis task"""
    try:
        if task_id not in task_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = task_storage[task_id]
        
        # Calculate estimated completion time
        estimated_completion = None
        if task_data['status'] == 'processing':
            elapsed_time = asyncio.get_event_loop().time() - task_data['created_at']
            estimated_completion = max(0, 180 - int(elapsed_time))  # 3 minutes total estimate
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task_data['status'],
            progress=task_data.get('progress', 0),
            error_message=task_data.get('error_message'),
            estimated_completion=estimated_completion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/results/{task_id}", response_model=UrbanAnalysisResponse)
async def get_analysis_results(task_id: str):
    """Get the results of a completed analysis"""
    try:
        if task_id not in task_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = task_storage[task_id]
        
        if task_data['status'] == 'processing':
            raise HTTPException(status_code=202, detail="Analysis still in progress")
        
        if task_data['status'] == 'failed':
            return {
                "task_id": task_id,
                "coordinates": {"lat": 37.7749, "lon": -122.4194},
                "satellite_analysis": {},
                "heat_island_analysis": {},
                "data_sources": {
                    "primary": "live_google_maps_satellite",
                    "backup": "none",
                    "storage_used": False,
                },
                "processing_info": {
                    "analysis_type": "live_satellite_imagery",
                    "external_apis": ["Google Maps Satellite API"],
                    "processing_time_estimate": "5-15 seconds",
                    "vegetation_analysis": "color_based_detection",
                    "heat_island_calculation": "satellite_derived"
                }
            }
        
        if task_data['status'] == 'completed' and task_data.get('result'):
            processing_time = asyncio.get_event_loop().time() - task_data['created_at']
            
            return UrbanAnalysisResponse(
                success=True,
                task_id=task_id,
                urban_features=task_data['result'],
                summary=generate_analysis_summary(task_data['result']),
                processing_time=processing_time
            )
        
        raise HTTPException(status_code=404, detail="Results not available")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/coordinates/analyze")
async def analyze_coordinates(request: Coordinates) -> UrbanAnalysisResponse:
    try:
        logger.info(f"🗺️ Analyzing coordinates: {request.lat}, {request.lon}")
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize live satellite service
        satellite_service = LiveSatelliteService()
        satellite_data = await satellite_service.get_live_satellite_data(
            lat=request.lat,
            lon=request.lon,
            analysis_radius=0.002
        )
        
        if not satellite_data:
            raise HTTPException(status_code=500, detail="Failed to get live satellite data")
        
        # Calculate heat island intensity from satellite data
        heat_island_analysis = satellite_service.estimate_heat_island_from_live_data(satellite_data)
        
        # Convert to expected response format
        urban_features = generate_mock_urban_features()
        summary = f"Heat island intensity: {heat_island_analysis['intensity']:.1f}/10 ({heat_island_analysis['risk_level']})"
        
        return UrbanAnalysisResponse(
            success=True,
            task_id=task_id,
            urban_features=urban_features,
            summary=summary,
            processing_time=0.05,
            analysis_data={
                "satellite_analysis": satellite_data,
                "heat_island_analysis": heat_island_analysis,
                "data_sources": {
                    "primary": "live_google_maps_satellite",
                    "backup": "none",
                    "storage_used": False,
                },
                "processing_info": {
                    "analysis_type": "live_satellite_imagery",
                    "external_apis": ["Google Maps Satellite API"],
                    "processing_time_estimate": "5-15 seconds",
                    "vegetation_analysis": "color_based_detection",
                    "heat_island_calculation": "satellite_derived"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing coordinates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.delete("/api/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """Clean up task data and files"""
    try:
        if task_id not in task_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = task_storage[task_id]
        
        # Remove uploaded file
        if 'file_path' in task_data:
            file_path = Path(task_data['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed file: {file_path}")
        
        # Remove task from storage
        del task_storage[task_id]
        
        return JSONResponse(content={"success": True, "message": "Task cleaned up successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Background task functions
async def process_satellite_image(task_id: str, file_path: str):
    """Background task to process satellite image"""
    try:
        logger.info(f"Starting analysis for task {task_id}")
        
        # Update status
        task_storage[task_id]['status'] = 'processing'
        task_storage[task_id]['progress'] = 10
        
        # Initialize the local analysis service
        local_service = LocalAnalysisService()
        
        # Update progress
        task_storage[task_id]['progress'] = 20
        
        # Perform local analysis (no external APIs)
        analysis_result = await local_service.analyze_coordinates(
            lat=37.7749,
            lon=-122.4194
        )
        
        # Update progress
        task_storage[task_id]['progress'] = 90
        
        # Store comprehensive results
        task_storage[task_id]['result'] = analysis_result
        
        # Mark as completed
        task_storage[task_id]['status'] = 'completed'
        task_storage[task_id]['progress'] = 100
        
        logger.info(f"Analysis completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error processing satellite image for task {task_id}: {str(e)}")
        task_storage[task_id]['status'] = 'failed'
        task_storage[task_id]['error_message'] = str(e)

def generate_mock_urban_features() -> UrbanFeatures:
    """Generate mock urban features for demo purposes"""
    from app.models.schemas import (
        Building, VegetationArea, SurfaceArea, InfrastructureElement,
        Coordinates, BuildingType, VegetationType, SurfaceMaterial, InfrastructureType
    )
    
    # Mock coordinates around San Francisco
    mock_coords = [
        Coordinates(lat=37.7749, lng=-122.4194),
        Coordinates(lat=37.7849, lng=-122.4094),
        Coordinates(lat=37.7649, lng=-122.4294),
        Coordinates(lat=37.7549, lng=-122.4394),
    ]
    
    # Mock buildings
    buildings = [
        Building(
            id=str(uuid.uuid4()),
            coordinates=mock_coords[0],
            type=BuildingType.COMMERCIAL,
            estimated_height=50.0,
            material="concrete",
            confidence=0.85,
            description="Large commercial building with glass facade"
        ),
        Building(
            id=str(uuid.uuid4()),
            coordinates=mock_coords[1],
            type=BuildingType.RESIDENTIAL,
            estimated_height=15.0,
            material="brick",
            confidence=0.92,
            description="Residential apartment complex"
        )
    ]
    
    # Mock vegetation
    vegetation = [
        VegetationArea(
            id=str(uuid.uuid4()),
            coordinates=mock_coords[2],
            type=VegetationType.PARK,
            coverage_area=5000.0,
            health_score=0.8,
            confidence=0.88
        )
    ]
    
    # Mock surfaces
    surfaces = [
        SurfaceArea(
            id=str(uuid.uuid4()),
            coordinates=mock_coords[3],
            material_type=SurfaceMaterial.ASPHALT,
            area_estimate=10000.0,
            heat_absorption=0.9,
            confidence=0.95
        )
    ]
    
    # Mock infrastructure
    infrastructure = [
        InfrastructureElement(
            id=str(uuid.uuid4()),
            coordinates=mock_coords[0],
            type=InfrastructureType.HIGHWAY,
            traffic_impact="High traffic volume during peak hours",
            confidence=0.87
        )
    ]
    
    return UrbanFeatures(
        buildings=buildings,
        vegetation=vegetation,
        surfaces=surfaces,
        infrastructure=infrastructure,
        processing_metadata={
            "analysis_version": "1.0.0",
            "processing_method": "mock_data",
            "features_detected": len(buildings) + len(vegetation) + len(surfaces) + len(infrastructure)
        }
    )

def generate_analysis_summary(features: UrbanFeatures) -> Dict[str, Any]:
    """Generate a summary of the analysis results"""
    return {
        "total_buildings": len(features.buildings),
        "total_vegetation_areas": len(features.vegetation),
        "total_surface_areas": len(features.surfaces),
        "total_infrastructure": len(features.infrastructure),
        "building_types": {
            building_type.value: sum(1 for b in features.buildings if b.type == building_type)
            for building_type in BuildingType
        },
        "surface_materials": {
            material.value: sum(1 for s in features.surfaces if s.material_type == material)
            for material in SurfaceMaterial
        },
        "average_building_confidence": (
            sum(b.confidence for b in features.buildings) / len(features.buildings)
            if features.buildings else 0
        ),
        "heat_risk_assessment": calculate_heat_risk(features)
    }

def calculate_heat_risk(features: UrbanFeatures) -> str:
    """Calculate overall heat risk based on detected features"""
    if not features.surfaces:
        return "Unable to assess"
    
    high_absorption_surfaces = sum(
        1 for surface in features.surfaces 
        if surface.heat_absorption > 0.7
    )
    
    total_surfaces = len(features.surfaces)
    high_absorption_ratio = high_absorption_surfaces / total_surfaces
    
    vegetation_coverage = len(features.vegetation)
    building_density = len(features.buildings)
    
    # Simple risk assessment logic
    if high_absorption_ratio > 0.6 and vegetation_coverage < 2:
        return "High"
    elif high_absorption_ratio > 0.4 or building_density > 5:
        return "Medium"
    else:
        return "Low"

def generate_mock_integrated_analysis(task_id: str):
    """Generate mock integrated analysis result combining all data sources"""
    from datetime import datetime
    
    # Generate mock urban features
    mock_urban_features = generate_mock_urban_features()
    
    # Mock coordinates (San Francisco)
    coordinates = Coordinates(lat=37.7749, lon=-122.4194)
    
    # Mock weather data
    mock_weather = {
        "temperature": 26.5,
        "feels_like": 29.2,
        "humidity": 68,
        "pressure": 1015,
        "description": "partly cloudy",
        "wind_speed": 4.1,
        "wind_direction": 225,
        "cloudiness": 35,
        "visibility": 12.0
    }
    
    # Mock heat forecast
    mock_forecast = [
        {"datetime": "2024-07-19 18:00:00", "temperature": 27.5, "humidity": 65, "heat_index": 30.2, "description": "sunny", "wind_speed": 3.8},
        {"datetime": "2024-07-20 06:00:00", "temperature": 22.1, "humidity": 75, "heat_index": 23.8, "description": "clear", "wind_speed": 2.5},
        {"datetime": "2024-07-20 12:00:00", "temperature": 28.9, "humidity": 62, "heat_index": 31.5, "description": "sunny", "wind_speed": 4.2},
        {"datetime": "2024-07-20 18:00:00", "temperature": 26.8, "humidity": 68, "heat_index": 29.1, "description": "partly cloudy", "wind_speed": 3.9}
    ]
    
    # Mock NASA data
    mock_land_temp = {
        "coordinates": {"lat": 37.7749, "lon": -122.4194},
        "land_surface_temperature": {"day": 32.5, "night": 19.8, "unit": "celsius"},
        "data_quality": "good",
        "timestamp": datetime.now().isoformat(),
        "resolution": "1km",
        "source": "NASA MODIS (Mock)"
    }
    
    mock_vegetation = {
        "coordinates": {"lat": 37.7749, "lon": -122.4194},
        "date": "2024-07-19",
        "ndvi": 0.42,
        "vegetation_health": "moderate",
        "chlorophyll_content": 42.0,
        "source": "NASA MODIS NDVI (Mock)"
    }
    
    mock_air_quality = {
        "coordinates": {"lat": 37.7749, "lon": -122.4194},
        "pm25": 16.8,
        "pm10": 29.3,
        "ozone": 48.7,
        "no2": 14.2,
        "so2": 7.9,
        "co": 0.9,
        "aqi": 68,
        "quality_level": "Moderate",
        "source": "NASA Air Quality (Mock)"
    }
    
    mock_climate_trends = {
        "coordinates": {"lat": 37.7749, "lon": -122.4194},
        "analysis_period": "5 years",
        "temperature_trend": {"average_increase_per_year": 0.18, "total_change": 0.9, "trend": "warming"},
        "precipitation_trend": {"average_change_per_year": -1.8, "total_change": -9.0, "trend": "decreasing"},
        "extreme_events": {"heat_waves_per_year": 4.1, "drought_days_per_year": 52, "increase_in_hot_days": 11.5},
        "vegetation_changes": {"ndvi_trend": "declining", "average_change_per_year": -0.025},
        "source": "NASA Climate Analysis (Mock)"
    }
    
    # Mock recommendations
    mock_recommendations = [
        {
            "category": "Green Infrastructure",
            "priority": "high",
            "action": "Increase Urban Tree Canopy",
            "description": "Plant 500+ additional trees in identified heat hotspots",
            "impact": "Reduce local temperatures by 2-4°C",
            "cost_estimate": "$75,000 - $150,000",
            "timeline": "8-12 months",
            "data_source": "TwelveLabs + NASA NDVI Analysis"
        },
        {
            "category": "Surface Materials",
            "priority": "high",
            "action": "Cool Roof Initiative",
            "description": "Install reflective roofing on 20+ identified buildings",
            "impact": "Reduce building surface temperatures by 12-18°C",
            "cost_estimate": "$45,000 - $90,000",
            "timeline": "4-6 months",
            "data_source": "TwelveLabs Material Analysis"
        },
        {
            "category": "Long-term Planning",
            "priority": "medium",
            "action": "Climate Resilience Strategy",
            "description": "Develop comprehensive heat adaptation plan",
            "impact": "Prepare for projected 0.9°C temperature increase",
            "cost_estimate": "$200,000 - $400,000",
            "timeline": "12-18 months",
            "data_source": "NASA Climate Trends + Integrated Analysis"
        }
    ]
    
    # Create the integrated result
    return IntegratedAnalysisResult(
        task_id=task_id,
        coordinates=coordinates,
        urban_features=mock_urban_features,
        current_weather=mock_weather,
        heat_forecast=mock_forecast,
        land_surface_temp=mock_land_temp,
        vegetation_index=mock_vegetation,
        air_quality=mock_air_quality,
        climate_trends=mock_climate_trends,
        heat_island_intensity=6.2,  # 0-10 scale
        risk_assessment="high",
        recommendations=mock_recommendations,
        processing_time=8.5,
        data_sources_used=["TwelveLabs (Mock)", "OpenWeather (Mock)", "NASA (Mock)"],
        analysis_timestamp=datetime.now().isoformat()
    )
