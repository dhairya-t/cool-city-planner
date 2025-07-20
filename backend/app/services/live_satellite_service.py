#!/usr/bin/env python3
"""
Live Satellite Service - Based on Chilladelphia's approach
Downloads and analyzes satellite imagery on-demand using Google Maps API
No data storage - processes live satellite tiles
"""
import logging

import aiohttp
import asyncio
import cv2
import requests
import numpy as np
import math
import tempfile
import os
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path
from app.core.logging import get_logger
from dataclasses import dataclass

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

@dataclass
class ImageAnalysis:
    region: Tuple[float, float, float, float]  # (north_lat, west_lon, south_lat, east_lon)
    image: np.ndarray  # Satellite image
    vegetation_mask: np.ndarray | None  # Vegetation mask
    building_mask: np.ndarray | None  # Building mask


class LiveSatelliteService:
    """Live satellite imagery processing - downloads and analyzes on demand"""
    
    def __init__(self):
        logger.info("🛰️ Live Satellite Service initialized - using Google Maps satellite imagery")
        self.tile_size = 256
        self.channels = 3
        
        # Create directory for saving satellite images
        self.image_dir = Path("satellite_images")
        self.image_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Satellite images will be saved to: {self.image_dir.absolute()}")
        self.headers = {
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
        }
        # Google Maps satellite imagery URL - same as Chilladelphia uses
        self.satellite_url = 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
    
    def _project_with_scale(self, lat: float, lon: float, scale: int) -> Tuple[float, float]:
        """Mercator projection for coordinate conversion"""
        siny = np.sin(lat * np.pi / 180)
        siny = min(max(siny, -0.9999), 0.9999)
        x = scale * (0.5 + lon / 360)
        y = scale * (0.5 - np.log((1 + siny) / (1 - siny)) / (4 * np.pi))
        return x, y

    async def _download_tile_async(self, session: aiohttp.ClientSession, tile_x: int, tile_y: int, zoom: int) -> Tuple[int, int, Optional[np.ndarray]]:
        """Download a single satellite tile asynchronously"""
        tile_url = self.satellite_url.format(x=tile_x, y=tile_y, z=zoom)
        try:
            async with session.get(tile_url, headers=self.headers, timeout=10) as response:
                if response.status == 200:
                    content = await response.read()
                    arr = np.asarray(bytearray(content), dtype=np.uint8)
                    tile = cv2.imdecode(arr, 1)  # Decode as BGR
                    return tile_x, tile_y, tile
                else:
                    logger.warning(f"Failed to download tile {tile_url}: HTTP {response.status}")
                    return tile_x, tile_y, None
        except Exception as e:
            logger.warning(f"Failed to download tile {tile_url}: {e}")
            return tile_x, tile_y, None

    async def fetch_satellite_region(self, north_lat: float, west_lon: float, south_lat: float, east_lon: float, zoom: int) -> Optional[np.ndarray]:
        """
        Downloads and stitches satellite imagery for a rectangular geographic region.
        Uses parallel downloads for faster processing.
        """
        logger.info(f"📡 Downloading satellite imagery for region ({north_lat}, {west_lon}) to ({south_lat}, {east_lon}) at zoom {zoom}")

        # Calculate the scale factor for the current zoom level (2^zoom)
        scale = 1 << zoom

        # Convert geographic coordinates to projected coordinates
        tl_proj_x, tl_proj_y = self._project_with_scale(north_lat, west_lon, scale)
        br_proj_x, br_proj_y = self._project_with_scale(south_lat, east_lon, scale)

        # Convert projected coordinates to pixel coordinates
        tl_pixel_x = int(tl_proj_x * self.tile_size)
        tl_pixel_y = int(tl_proj_y * self.tile_size)
        br_pixel_x = int(br_proj_x * self.tile_size)
        br_pixel_y = int(br_proj_y * self.tile_size)

        # Determine which tiles we need to download
        tl_tile_x = int(tl_proj_x)
        tl_tile_y = int(tl_proj_y)
        br_tile_x = int(br_proj_x)
        br_tile_y = int(br_proj_y)

        # Calculate dimensions of the final stitched image
        img_w = abs(tl_pixel_x - br_pixel_x)
        img_h = br_pixel_y - tl_pixel_y

        if img_w <= 0 or img_h <= 0:
            logger.error("Invalid image dimensions - check coordinate ordering")
            return None

        # Initialize empty image to hold the stitched result
        img = np.zeros((img_h, img_w, self.channels), np.uint8)

        total_tiles = (br_tile_x - tl_tile_x + 1) * (br_tile_y - tl_tile_y + 1)
        logger.info(f"🧩 Need to download {total_tiles} tiles")

        # Set up tasks for parallel downloading
        async with aiohttp.ClientSession() as session:
            download_tasks = []

            for tile_y in range(tl_tile_y, br_tile_y + 1):
                for tile_x in range(tl_tile_x, br_tile_x + 1):
                    task = self._download_tile_async(session, tile_x, tile_y, zoom)
                    download_tasks.append(task)

            # Wait for all downloads to complete
            results = await asyncio.gather(*download_tasks)

            # Process results and place tiles in the image
            tiles_downloaded = 0
            for tile_x, tile_y, tile in results:
                if tile is not None:
                    tiles_downloaded += 1

                    # Calculate where in the final image this tile should be placed
                    tl_rel_x = tile_x * self.tile_size - tl_pixel_x
                    tl_rel_y = tile_y * self.tile_size - tl_pixel_y
                    br_rel_x = tl_rel_x + self.tile_size
                    br_rel_y = tl_rel_y + self.tile_size

                    # Calculate destination region in the final image (handling edge cases)
                    img_x_l = max(0, tl_rel_x)
                    img_x_r = min(img_w, br_rel_x)
                    img_y_l = max(0, tl_rel_y)
                    img_y_r = min(img_h, br_rel_y)

                    # Calculate source region from the tile (for partial tiles at edges)
                    cr_x_l = max(0, -tl_rel_x)
                    cr_x_r = self.tile_size + min(0, img_w - br_rel_x)
                    cr_y_l = max(0, -tl_rel_y)
                    cr_y_r = self.tile_size + min(0, img_h - br_rel_y)

                    # Copy the appropriate portion of the tile into the result image
                    img[img_y_l:img_y_r, img_x_l:img_x_r] = tile[cr_y_l:cr_y_r, cr_x_l:cr_x_r]

        logger.info(f"✅ Downloaded {tiles_downloaded}/{total_tiles} satellite tiles")

        # Only save the image if we successfully downloaded at least some tiles
        if tiles_downloaded > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"satellite_{north_lat:.6f}_{west_lon:.6f}_to_{south_lat:.6f}_{east_lon:.6f}.png"
            image_path = self.image_dir / filename

            # Save the stitched image to disk
            cv2.imwrite(str(image_path), img)
            logger.info(f"💾 Saved satellite image: {image_path}")

        return img if tiles_downloaded > 0 else None
    
    def analyze(self, image: np.ndarray, bounds: Tuple[float, float, float, float]) -> ImageAnalysis:
        """
        Simple vegetation analysis using color-based detection
        Alternative to detectree for faster processing without ML dependencies
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to HSV for better vegetation detection
        hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

        # Define green color ranges for vegetation
        # Two ranges to capture different shades of green
        lower_green = np.array([30, 18, 10])   # Light green
        upper_green = np.array([200, 120, 120]) # Dark green

        # Create masks for green vegetation
        mask1 = cv2.inRange(hsv, lower_green, upper_green)

        # Combine masks
        vegetation_mask = mask1

        # Calculate vegetation percentage
        total_pixels = vegetation_mask.size
        vegetation_pixels = np.sum(vegetation_mask > 0)
        vegetation_percentage = (vegetation_pixels / total_pixels) * 100.0

        # Save vegetation analysis visualization
        mask_filename = f"vegetation_mask.png"
        mask_path = self.image_dir / mask_filename

        # Create colored vegetation overlay
        vegetation_overlay = rgb_image.copy()
        vegetation_overlay[vegetation_mask > 0] = [0, 255, 0]  # Green for vegetation

        # Save vegetation mask and overlay
        cv2.imwrite(str(mask_path), vegetation_mask)
        overlay_filename = f"vegetation_overlay.png"
        overlay_path = self.image_dir / overlay_filename
        cv2.imwrite(str(overlay_path), cv2.cvtColor(vegetation_overlay, cv2.COLOR_RGB2BGR))

        logger.info(f"🌱 Saved vegetation mask: {mask_path}")
        logger.info(f"📊 Saved vegetation overlay: {overlay_path}")

        return ImageAnalysis(
            region=bounds,
            image=image,
            vegetation_mask=vegetation_mask,
            building_mask=None,
        )
    
    async def get_live_satellite_data(self, lat: float, lon: float, analysis_radius: float = 0.001) -> Optional[Dict[str, Any]]:
        """
        Get live satellite data and analysis for coordinates
        """
        logger.info(f"🗺️ Getting live satellite data for {lat}, {lon} (radius: {analysis_radius})")
        
        try:
            # Define analysis region around point (same as Chilladelphia's tile approach)
            lat1 = lat + analysis_radius  # Top-left latitude
            lon1 = lon - analysis_radius  # Top-left longitude  
            lat2 = lat - analysis_radius  # Bottom-right latitude
            lon2 = lon + analysis_radius  # Bottom-right longitude
            
            zoom = 17
            
            # Download satellite image for region
            satellite_image = await self.fetch_satellite_region(lat1, lon1, lat2, lon2, zoom)
            
            if satellite_image is None:
                logger.error("❌ Failed to download satellite imagery")
                return None
            
            # Analyze vegetation in the image
            analysis = self.analyze(satellite_image, lat, lon)

            result = {
                "coordinates": {"lat": lat, "lon": lon},
                "analysis_region": {
                    "top_left": [lat1, lon1],
                    "bottom_right": [lat2, lon2],
                    "radius_degrees": analysis_radius
                },
                "analysis": analysis
            }
            
            logger.info(f"✅ Live satellite analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"❌ Live satellite analysis failed: {e}")
            return None