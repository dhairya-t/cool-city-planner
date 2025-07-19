"""
API routes for the CoolCity Planner backend
"""
import os
import uuid
import asyncio
from typing import Dict, Any
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import (
    ImageUploadResponse,
    AnalysisStatusResponse,
    UrbanAnalysisResponse,
    UrbanFeatures
)
from app.services.twelve_labs_client import UrbanAnalyzer

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

@router.get("/api/status/{task_id}", response_model=AnalysisStatusResponse)
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
        
        return AnalysisStatusResponse(
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
            return UrbanAnalysisResponse(
                success=False,
                task_id=task_id,
                error_message=task_data.get('error_message', 'Analysis failed')
            )
        
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
        
        # Initialize the urban analyzer
        analyzer = UrbanAnalyzer()
        
        # Update progress
        task_storage[task_id]['progress'] = 30
        
        # For demo purposes, we'll use mock data if TwelveLabs API is not configured
        if not settings.TWELVE_LABS_API_KEY:
            logger.warning("TwelveLabs API key not configured. Using mock data.")
            
            # Simulate processing time
            await asyncio.sleep(5)
            task_storage[task_id]['progress'] = 60
            await asyncio.sleep(3)
            task_storage[task_id]['progress'] = 90
            
            # Generate mock urban features
            mock_features = generate_mock_urban_features()
            task_storage[task_id]['result'] = mock_features
            
        else:
            # Real analysis using TwelveLabs
            logger.info("Performing real analysis with TwelveLabs API")
            
            # Update progress
            task_storage[task_id]['progress'] = 50
            
            # Analyze the image
            urban_features = await analyzer.analyze_satellite_image(file_path)
            
            # Update progress
            task_storage[task_id]['progress'] = 90
            
            # Store results
            task_storage[task_id]['result'] = urban_features
        
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
