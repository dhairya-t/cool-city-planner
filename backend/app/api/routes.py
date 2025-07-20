import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pathlib import Path
import cv2
import numpy as np
import io

from app.core.logging import get_logger
from app.services.live_satellite_service import LiveSatelliteService
from app.models.schemas import SatelliteAnalysisRequest, SatelliteAnalysisResponse

import os
from vellum.client import Vellum
import vellum.types as types

logger = get_logger(__name__)

# Global router
router = APIRouter()

# Initialize satellite service
satellite_service = LiveSatelliteService()

# Image dictionary mapping keys to actual image data (numpy arrays)
images = {}

@router.get("/image/{image_key}")
async def get_image(image_key: str):
    """
    Serve an image from the in-memory dictionary

    Available image keys depend on what's currently loaded in memory.
    """
    try:
        # Check if the key exists in our image dictionary
        if image_key not in images:
            available_keys = list(images.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Image key '{image_key}' not found. Available keys: {available_keys}"
            )

        # Get the image data from the dictionary
        image_data = images[image_key]

        if image_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Image data is None for key '{image_key}'"
            )

        logger.info(f"📷 Serving image from memory: {image_key} (shape: {image_data.shape})")

        # Encode the numpy array as PNG
        success, encoded_image = cv2.imencode('.png', image_data)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to encode image for key '{image_key}'"
            )

        # Convert to bytes
        image_bytes = encoded_image.tobytes()

        # Return the image as a response
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=\"{image_key}.png\""}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error serving image '{image_key}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while serving image: {str(e)}"
        )


@router.get("/images/available")
async def get_available_images():
    """Get list of available image keys and their metadata"""
    try:
        available_images = {}
        for key, image_data in images.items():
            if image_data is not None:
                available_images[key] = {
                    "shape": image_data.shape,
                    "dtype": str(image_data.dtype),
                    "size_mb": round(image_data.nbytes / (1024 * 1024), 2)
                }

        return {
            "available_keys": list(images.keys()),
            "count": len(images),
            "details": available_images
        }
    except Exception as e:
        logger.error(f"❌ Error getting available images: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/analyze", response_model=SatelliteAnalysisResponse)
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

        heatmap_image = image_analysis.heat_map
        heatmap_normalized = ((heatmap_image + 1) / 2 * 255).astype(np.uint8)
        heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)

        hm_id = f"{str(uuid.uuid4())}-heatmap"
        im_id = f"{str(uuid.uuid4())}-image"

        images[hm_id] = heatmap_colored
        images[im_id] = image_analysis.image

        try:

            client = Vellum(
                api_key=os.getenv("VELLUM_API_KEY")
            )

            hm_url = f"https://urban.midnightsky.net/image/{hm_id}"
            im_url = f"https://urban.midnightsky.net/image/{im_id}"

            result = client.execute_workflow(
                workflow_deployment_name="heat-mapper-agent-workflow",
                release_tag="LATEST",
                inputs=[
                    types.WorkflowRequestStringInputRequest(
                        name="heatmap_image_url",
                        type="STRING",
                        value=hm_url,
                    ),
                    types.WorkflowRequestStringInputRequest(
                        name="city_image_url",
                        type="STRING",
                        value=im_url,
                    ),
                ],
            )

            if result.data.state == "REJECTED":
                raise Exception(result.data.error.message)

            outputs = result.data.outputs

            return SatelliteAnalysisResponse(
                status="success",
                image=im_id,
                heatmap=hm_id,
                vellum_analysis=outputs,
            )
        finally:
            pass
            images.pop(hm_id)
            images.pop(im_id)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"❌ Error during satellite analysis:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during satellite analysis: {str(e)}"
        )
