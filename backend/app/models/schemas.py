"""
Pydantic schemas for API request/response models
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# Enums
class BuildingType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    UNKNOWN = "unknown"

class SurfaceMaterial(str, Enum):
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    GRASS = "grass"
    WATER = "water"
    VEGETATION = "vegetation"
    ROOF_TILE = "roof_tile"
    METAL = "metal"
    UNKNOWN = "unknown"

class VegetationType(str, Enum):
    PARK = "park"
    TREES = "trees"
    GRASS = "grass"
    FOREST = "forest"
    GARDEN = "garden"
    UNKNOWN = "unknown"

class InfrastructureType(str, Enum):
    HIGHWAY = "highway"
    ROAD = "road"
    BRIDGE = "bridge"
    PARKING = "parking"
    RAILWAY = "railway"
    UNKNOWN = "unknown"

# Base schemas
class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class Building(BaseModel):
    id: str = Field(..., description="Unique building identifier")
    coordinates: Coordinates
    type: BuildingType = BuildingType.UNKNOWN
    estimated_height: Optional[float] = Field(None, description="Estimated height in meters")
    material: Optional[str] = Field(None, description="Primary building material")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    description: Optional[str] = Field(None, description="AI-generated description")

class VegetationArea(BaseModel):
    id: str = Field(..., description="Unique vegetation area identifier")
    coordinates: Coordinates
    type: VegetationType = VegetationType.UNKNOWN
    coverage_area: Optional[float] = Field(None, description="Area in square meters")
    health_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Vegetation health score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")

class SurfaceArea(BaseModel):
    id: str = Field(..., description="Unique surface area identifier")
    coordinates: Coordinates
    material_type: SurfaceMaterial = SurfaceMaterial.UNKNOWN
    area_estimate: Optional[float] = Field(None, description="Area in square meters")
    heat_absorption: float = Field(..., ge=0.0, le=1.0, description="Heat absorption coefficient")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")

class InfrastructureElement(BaseModel):
    id: str = Field(..., description="Unique infrastructure element identifier")
    coordinates: Coordinates
    type: InfrastructureType = InfrastructureType.UNKNOWN
    traffic_impact: Optional[str] = Field(None, description="Traffic impact assessment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")

# Urban analysis response
class UrbanFeatures(BaseModel):
    buildings: List[Building] = Field(default_factory=list)
    vegetation: List[VegetationArea] = Field(default_factory=list)
    surfaces: List[SurfaceArea] = Field(default_factory=list)
    infrastructure: List[InfrastructureElement] = Field(default_factory=list)
    
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

# API request/response schemas
class ImageUploadResponse(BaseModel):
    success: bool
    task_id: str
    message: str
    processing_time_estimate: Optional[int] = Field(None, description="Estimated processing time in seconds")

class AnalysisStatusResponse(BaseModel):
    task_id: str
    status: str  # "processing", "completed", "failed"
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Progress percentage")
    error_message: Optional[str] = None
    estimated_completion: Optional[int] = Field(None, description="Estimated completion time in seconds")

class UrbanAnalysisResponse(BaseModel):
    success: bool
    task_id: str
    urban_features: Optional[UrbanFeatures] = None
    summary: Dict[str, Any] = Field(default_factory=dict)
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    error_message: Optional[str] = None

# TwelveLabs specific schemas
class TwelveLabsTaskStatus(BaseModel):
    task_id: str
    status: str
    video_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TwelveLabsSearchResult(BaseModel):
    confidence: float
    start_time: float
    end_time: float
    metadata: Optional[Dict[str, Any]] = None
    text_description: Optional[str] = None

class TwelveLabsSearchResponse(BaseModel):
    data: List[TwelveLabsSearchResult]
    page_info: Optional[Dict[str, Any]] = None
    total_results: Optional[int] = None
