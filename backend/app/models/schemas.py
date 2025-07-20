"""
Pydantic schemas for API request/response models
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from vellum import WorkflowOutput, WorkflowOutputJson


class SatelliteAnalysisRequest(BaseModel):
    """Request model for satellite analysis endpoint"""
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    analysis_radius: Optional[float] = Field(0.001, description="Radius for analysis area", gt=0)


class SatelliteAnalysisResponse(BaseModel):
    """Response model for satellite analysis endpoint"""
    status: str = Field(..., description="Status of the analysis")
    image: str = Field(..., description="Base64-encoded image of the analysis")
    heatmap: str = Field(..., description="Base64-encoded heatmap of the analysis")
    vellum_analysis: dict = Field(..., description="Vellum analysis output")
