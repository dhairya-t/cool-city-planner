from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.services.live_satellite_service import LiveSatelliteService
from app.models.schemas import SatelliteAnalysisRequest, SatelliteAnalysisResponse

logger = get_logger(__name__)

# Global router
router = APIRouter()

# Initialize satellite service
satellite_service = LiveSatelliteService()


@router.post("/analyze-satellite", response_model=SatelliteAnalysisResponse)
async def analyze_satellite_data(request: SatelliteAnalysisRequest):
    """
    Analyze satellite data for given coordinates

    Takes latitude and longitude coordinates and returns satellite image analysis
    including vegetation detection, building detection, and heat mapping.
    """
    try:
        logger.info(f"🛰️ Starting satellite analysis for lat: {request.latitude}, lon: {request.longitude}")

        # Get live satellite data and analysis
        image_analysis = await satellite_service.get_live_satellite_data(
            lat=request.latitude,
            lon=request.longitude,
            analysis_radius=request.analysis_radius
        )

        if image_analysis is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve or analyze satellite data"
            )

        logger.info(f"✅ Satellite analysis completed successfully")

        # TODO: Process ImageAnalysis object and return meaningful data
        # For now, return a stub response
        return SatelliteAnalysisResponse(
            status="success",
            message=f"Satellite analysis completed for coordinates ({request.latitude}, {request.longitude})",
            data={
                "region": {
                    "north_lat": image_analysis.region[0],
                    "west_lon": image_analysis.region[1],
                    "south_lat": image_analysis.region[2],
                    "east_lon": image_analysis.region[3]
                },
                "analysis_complete": True,
                "has_vegetation_mask": image_analysis.vegetation_mask is not None,
                "has_building_mask": image_analysis.building_mask is not None,
                "has_heat_map": image_analysis.heat_map is not None
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error during satellite analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during satellite analysis: {str(e)}"
        )
