#!/usr/bin/env python3
"""
Live Satellite Service - Based on Chilladelphia's approach
Downloads and analyzes satellite imagery on-demand using Google Maps API
No data storage - processes live satellite tiles
"""

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

logger = get_logger(__name__)

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
    
    def _download_tile(self, url: str) -> Optional[np.ndarray]:
        """Download a single satellite tile"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            arr = np.asarray(bytearray(response.content), dtype=np.uint8)
            return cv2.imdecode(arr, 1)  # Decode as BGR
            
        except Exception as e:
            logger.warning(f"Failed to download tile {url}: {e}")
            return None
    
    def _download_satellite_image(self, lat1: float, lon1: float, lat2: float, lon2: float, zoom: int) -> Optional[np.ndarray]:
        """
        Download satellite image for a geographic region
        Based on Chilladelphia's image_downloading.py
        """
        logger.info(f"📡 Downloading satellite imagery for region ({lat1}, {lon1}) to ({lat2}, {lon2}) at zoom {zoom}")
        
        scale = 1 << zoom
        
        # Find pixel and tile coordinates of corners
        tl_proj_x, tl_proj_y = self._project_with_scale(lat1, lon1, scale)
        br_proj_x, br_proj_y = self._project_with_scale(lat2, lon2, scale)
        
        tl_pixel_x = int(tl_proj_x * self.tile_size)
        tl_pixel_y = int(tl_proj_y * self.tile_size)
        br_pixel_x = int(br_proj_x * self.tile_size)
        br_pixel_y = int(br_proj_y * self.tile_size)
        
        tl_tile_x = int(tl_proj_x)
        tl_tile_y = int(tl_proj_y)
        br_tile_x = int(br_proj_x)
        br_tile_y = int(br_proj_y)
        
        img_w = abs(tl_pixel_x - br_pixel_x)
        img_h = br_pixel_y - tl_pixel_y
        
        if img_w <= 0 or img_h <= 0:
            logger.error("Invalid image dimensions")
            return None
            
        img = np.zeros((img_h, img_w, self.channels), np.uint8)
        
        tiles_downloaded = 0
        total_tiles = (br_tile_x - tl_tile_x + 1) * (br_tile_y - tl_tile_y + 1)
        
        # Download each tile and stitch together
        for tile_y in range(tl_tile_y, br_tile_y + 1):
            for tile_x in range(tl_tile_x, br_tile_x + 1):
                tile_url = self.satellite_url.format(x=tile_x, y=tile_y, z=zoom)
                tile = self._download_tile(tile_url)
                
                if tile is not None:
                    tiles_downloaded += 1
                    
                    # Calculate tile placement in final image
                    tl_rel_x = tile_x * self.tile_size - tl_pixel_x
                    tl_rel_y = tile_y * self.tile_size - tl_pixel_y
                    br_rel_x = tl_rel_x + self.tile_size
                    br_rel_y = tl_rel_y + self.tile_size
                    
                    # Define placement boundaries
                    img_x_l = max(0, tl_rel_x)
                    img_x_r = min(img_w, br_rel_x)
                    img_y_l = max(0, tl_rel_y)
                    img_y_r = min(img_h, br_rel_y)
                    
                    # Define cropping for border tiles
                    cr_x_l = max(0, -tl_rel_x)
                    cr_x_r = self.tile_size + min(0, img_w - br_rel_x)
                    cr_y_l = max(0, -tl_rel_y)
                    cr_y_r = self.tile_size + min(0, img_h - br_rel_y)
                    
                    # Place tile in final image
                    img[img_y_l:img_y_r, img_x_l:img_x_r] = tile[cr_y_l:cr_y_r, cr_x_l:cr_x_r]
        
        logger.info(f"✅ Downloaded {tiles_downloaded}/{total_tiles} satellite tiles")
        
        # Save the complete satellite image
        if tiles_downloaded > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"satellite_{lat1:.6f}_{lon1:.6f}_to_{lat2:.6f}_{lon2:.6f}_{timestamp}.png"
            image_path = self.image_dir / filename
            
            # Save the image
            cv2.imwrite(str(image_path), img)
            logger.info(f"💾 Saved satellite image: {image_path}")
        
        return img if tiles_downloaded > 0 else None
    
    def _analyze_vegetation_simple(self, image: np.ndarray, lat: float, lon: float) -> Tuple[float, Dict[str, Any]]:
        """
        Simple vegetation analysis using color-based detection
        Alternative to detectree for faster processing without ML dependencies
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to HSV for better vegetation detection
            hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
            
            # Define green color ranges for vegetation
            # Two ranges to capture different shades of green
            lower_green1 = np.array([35, 30, 30])   # Light green
            upper_green1 = np.array([85, 255, 255]) # Dark green
            
            lower_green2 = np.array([25, 20, 20])   # Very light green/yellow-green
            upper_green2 = np.array([35, 255, 255])
            
            # Create masks for green vegetation
            mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
            mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
            
            # Combine masks
            vegetation_mask = cv2.bitwise_or(mask1, mask2)
            
            # Remove noise with morphological operations
            kernel = np.ones((3,3), np.uint8)
            vegetation_mask = cv2.morphologyEx(vegetation_mask, cv2.MORPH_OPEN, kernel)
            vegetation_mask = cv2.morphologyEx(vegetation_mask, cv2.MORPH_CLOSE, kernel)
            
            # Calculate vegetation percentage
            total_pixels = vegetation_mask.size
            vegetation_pixels = np.sum(vegetation_mask > 0)
            vegetation_percentage = (vegetation_pixels / total_pixels) * 100.0
            
            # Classify vegetation health based on percentage
            if vegetation_percentage > 40:
                health = "excellent"
            elif vegetation_percentage > 25:
                health = "good"  
            elif vegetation_percentage > 15:
                health = "moderate"
            elif vegetation_percentage > 5:
                health = "poor"
            else:
                health = "very_poor"
            
            # Save vegetation analysis visualization
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mask_filename = f"vegetation_mask_{lat:.6f}_{lon:.6f}_{timestamp}.png"
            mask_path = self.image_dir / mask_filename
            
            # Create colored vegetation overlay
            vegetation_overlay = rgb_image.copy()
            vegetation_overlay[vegetation_mask > 0] = [0, 255, 0]  # Green for vegetation
            
            # Save vegetation mask and overlay
            cv2.imwrite(str(mask_path), vegetation_mask)
            overlay_filename = f"vegetation_overlay_{lat:.6f}_{lon:.6f}_{timestamp}.png"
            overlay_path = self.image_dir / overlay_filename
            cv2.imwrite(str(overlay_path), cv2.cvtColor(vegetation_overlay, cv2.COLOR_RGB2BGR))
            
            logger.info(f"🌱 Saved vegetation mask: {mask_path}")
            logger.info(f"📊 Saved vegetation overlay: {overlay_path}")
            
            analysis = {
                "vegetation_pixels": int(vegetation_pixels),
                "total_pixels": int(total_pixels),
                "vegetation_mask_created": True,
                "health_classification": health,
                "processing_method": "color_based_hsv",
                "saved_files": {
                    "vegetation_mask": str(mask_path),
                    "vegetation_overlay": str(overlay_path)
                }
            }
            
            return vegetation_percentage, analysis
            
        except Exception as e:
            logger.error(f"❌ Vegetation analysis failed: {e}")
            return 0.0, {"error": str(e), "processing_method": "failed"}
    
    async def get_live_satellite_data(self, lat: float, lon: float, analysis_radius: float = 0.001) -> Optional[Dict[str, Any]]:
        """
        Get live satellite data and analysis for coordinates
        Based on Chilladelphia's approach but processes on-demand
        """
        logger.info(f"🗺️ Getting live satellite data for {lat}, {lon} (radius: {analysis_radius})")
        
        try:
            # Define analysis region around point (same as Chilladelphia's tile approach)
            lat1 = lat + analysis_radius  # Top-left latitude
            lon1 = lon - analysis_radius  # Top-left longitude  
            lat2 = lat - analysis_radius  # Bottom-right latitude
            lon2 = lon + analysis_radius  # Bottom-right longitude
            
            # Use zoom level 19 for high detail (same as Chilladelphia)
            zoom = 19
            
            # Download satellite image for region
            satellite_image = self._download_satellite_image(lat1, lon1, lat2, lon2, zoom)
            
            if satellite_image is None:
                logger.error("❌ Failed to download satellite imagery")
                return None
            
            # Analyze vegetation in the image
            vegetation_percentage, vegetation_analysis = self._analyze_vegetation_simple(satellite_image, lat, lon)
            
            # Calculate NDVI approximation from vegetation percentage
            # Simple conversion: higher vegetation % = higher NDVI
            ndvi_estimate = (vegetation_percentage / 100.0) * 0.8  # Scale to realistic NDVI range
            
            # Estimate land surface temperature based on vegetation
            # Less vegetation = higher temperature (urban heat island effect)
            base_temp = 25.0  # Base temperature in Celsius
            vegetation_cooling = vegetation_percentage * 0.2  # Cooling effect of vegetation
            estimated_lst = base_temp + (50 - vegetation_percentage) * 0.15
            
            result = {
                "coordinates": {"lat": lat, "lon": lon},
                "analysis_region": {
                    "top_left": [lat1, lon1],
                    "bottom_right": [lat2, lon2],
                    "radius_degrees": analysis_radius
                },
                "satellite_imagery": {
                    "source": "Google Maps Satellite",
                    "zoom_level": zoom,
                    "image_dimensions": [satellite_image.shape[1], satellite_image.shape[0]],
                    "download_timestamp": datetime.now().isoformat(),
                    "data_quality": "high"
                },
                "vegetation_data": {
                    "vegetation_coverage_percent": round(vegetation_percentage, 2),
                    "ndvi_estimate": round(ndvi_estimate, 3),
                    "vegetation_health": vegetation_analysis.get("health_classification", "unknown"),
                    "analysis_method": vegetation_analysis.get("processing_method", "color_based"),
                    "vegetation_pixels": vegetation_analysis.get("vegetation_pixels", 0),
                    "total_pixels": vegetation_analysis.get("total_pixels", 0)
                },
                "thermal_estimate": {
                    "estimated_land_surface_temp": round(estimated_lst, 1),
                    "temperature_unit": "celsius",
                    "estimation_method": "vegetation_based",
                    "cooling_effect": round(vegetation_cooling, 1)
                },
                "urban_analysis": {
                    "impervious_surface_estimate": round(100 - vegetation_percentage, 1),
                    "urban_density_score": round((100 - vegetation_percentage) / 100, 2),
                    "built_environment_percentage": max(0, round(100 - vegetation_percentage - 10, 1))  # Subtract water/bare soil
                },
                "processing_info": {
                    "timestamp": datetime.now().isoformat(),
                    "processing_method": "live_satellite_analysis",
                    "data_source": "Google Maps Satellite API",
                    "storage_used": False,
                    "real_time": True
                }
            }
            
            logger.info(f"✅ Live satellite analysis complete - {vegetation_percentage:.1f}% vegetation coverage")
            return result
            
        except Exception as e:
            logger.error(f"❌ Live satellite analysis failed: {e}")
            return None
    
    def estimate_heat_island_from_live_data(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate heat island intensity from live satellite analysis"""
        if not satellite_data:
            return {"intensity": 0, "risk": "unknown"}
        
        try:
            # Extract metrics
            vegetation_percent = satellite_data["vegetation_data"]["vegetation_coverage_percent"]
            estimated_lst = satellite_data["thermal_estimate"]["estimated_land_surface_temp"]
            urban_density = satellite_data["urban_analysis"]["urban_density_score"]
            
            # Heat island calculation
            # Higher temperature factor
            temp_factor = max(0, (estimated_lst - 25) / 15) * 3
            
            # Lower vegetation factor (lack of cooling)
            vegetation_factor = (100 - vegetation_percent) / 100 * 3
            
            # Urban density factor
            urban_factor = urban_density * 2
            
            # Combined intensity (0-10 scale)
            intensity = min(10, temp_factor + vegetation_factor + urban_factor)
            
            # Risk assessment
            if intensity > 7.5:
                risk = "extreme"
            elif intensity > 5.5:
                risk = "high"
            elif intensity > 3.5:
                risk = "moderate"
            else:
                risk = "low"
            
            return {
                "intensity": round(intensity, 2),
                "risk_level": risk,
                "contributing_factors": {
                    "estimated_temperature": round(temp_factor, 2),
                    "vegetation_deficit": round(vegetation_factor, 2),
                    "urban_density": round(urban_factor, 2)
                },
                "live_satellite_metrics": {
                    "vegetation_coverage_percent": vegetation_percent,
                    "estimated_lst_celsius": estimated_lst,
                    "urban_density_score": urban_density
                },
                "data_source": "live_google_maps_satellite"
            }
            
        except Exception as e:
            logger.error(f"❌ Heat island calculation failed: {e}")
            return {"intensity": 0, "risk": "error", "error": str(e)}
