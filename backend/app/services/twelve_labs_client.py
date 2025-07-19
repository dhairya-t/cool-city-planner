"""
TwelveLabs API client for satellite image analysis using official SDK
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from twelvelabs import TwelveLabs
from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import (
    TwelveLabsTaskStatus,
    TwelveLabsSearchResult,
    TwelveLabsSearchResponse,
    UrbanFeatures,
    Building,
    VegetationArea,
    SurfaceArea,
    InfrastructureElement,
    Coordinates,
    BuildingType,
    SurfaceMaterial,
    VegetationType,
    InfrastructureType
)

logger = get_logger(__name__)

class TwelveLabsClient:
    """Client for interacting with TwelveLabs API using official SDK"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TWELVE_LABS_API_KEY
        self.index_id = settings.TWELVE_LABS_INDEX_ID
        self.timeout = settings.REQUEST_TIMEOUT
        
        if not self.api_key:
            raise ValueError("TwelveLabs API key is required")
        
        # Initialize the TwelveLabs client
        import os
        os.environ['TWELVE_LABS_API_KEY'] = self.api_key
        self.client = TwelveLabs()
        
        # Initialize index_id if not provided
        if not self.index_id:
            logger.warning("No index ID configured. Will create or use default index.")
    
    async def get_or_create_index(self, name: str = "coolcity-satellite-analysis") -> str:
        """Get existing index or create a new one for satellite image analysis"""
        try:
            # Try to find existing index by name
            indexes = self.client.indexes.list()
            if indexes and hasattr(indexes, 'data'):
                # Look for existing index with matching name
                for idx in indexes.data:
                    if hasattr(idx, 'name') and idx.name == name:
                        logger.info(f"Using existing index: {idx.id}")
                        return idx.id
            
            # Create new index if none exists
            logger.info(f"Creating new index: {name}")
            index = self.client.indexes.create(
                name=name,
                engines=[
                    {
                        "name": "marengo-2.6",
                        "options": ["visual", "conversation", "text_in_video", "logo"]
                    }
                ]
            )
            
            logger.info(f"Created new index: {index.id}")
            return index.id
            
        except Exception as e:
            logger.error(f"Error managing index: {str(e)}")
            raise
    
    async def upload_video(self, file_path: str, metadata: Optional[Dict] = None) -> str:
        """Upload a video file to TwelveLabs for processing"""
        try:
            logger.info(f"Uploading video: {file_path}")
            
            # Ensure we have an index
            if not self.index_id:
                self.index_id = await self.get_or_create_index()
            
            # Upload the video using SDK
            task = self.client.tasks.create(
                index_id=self.index_id,
                file=file_path,
                language="en",
                **(metadata or {})
            )
            
            task_id = task.id
            logger.info(f"Video upload initiated. Task ID: {task_id}")
            return task_id
                    
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            raise
    
    async def check_task_status(self, task_id: str) -> TwelveLabsTaskStatus:
        """Check the status of a processing task"""
        try:
            task = self.client.tasks.retrieve(task_id)
            
            return TwelveLabsTaskStatus(
                task_id=task_id,
                status=task.status,
                video_id=getattr(task, 'video_id', None),
                error_message=getattr(task, 'error_message', None),
                created_at=getattr(task, 'created_at', None),
                updated_at=getattr(task, 'updated_at', None)
            )
                
        except Exception as e:
            logger.error(f"Error checking task status: {str(e)}")
            raise
    
    async def wait_for_processing(self, task_id: str, max_wait_time: int = 600) -> str:
        """Wait for video processing to complete and return video_id"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.check_task_status(task_id)
            
            if status.status == "ready":
                logger.info(f"Video processing completed. Video ID: {status.video_id}")
                return status.video_id
            
            elif status.status == "failed":
                error_msg = status.error_message or "Unknown error"
                logger.error(f"Video processing failed: {error_msg}")
                raise Exception(f"Processing failed: {error_msg}")
            
            # Check timeout
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > max_wait_time:
                raise Exception(f"Processing timeout after {max_wait_time} seconds")
            
            logger.info(f"Processing status: {status.status}. Waiting...")
            await asyncio.sleep(10)  # Wait 10 seconds before checking again
    
    async def search_video(self, video_id: str, query: str, search_options: Optional[List] = None) -> TwelveLabsSearchResponse:
        """Search within a processed video"""
        try:
            # Ensure we have an index
            if not self.index_id:
                self.index_id = await self.get_or_create_index()
            
            search_result = self.client.search.query(
                index_id=self.index_id,
                query_text=query,
                options=search_options or ["visual", "conversation", "text_in_video", "logo"],
                filter={"id": video_id}
            )
                
            # Parse search results
            results = []
            for item in search_result.data:
                result = TwelveLabsSearchResult(
                    confidence=getattr(item, 'confidence', 0.0),
                    start_time=getattr(item, 'start', 0.0),
                    end_time=getattr(item, 'end', 0.0),
                    metadata=getattr(item, 'metadata', {}),
                    text_description=getattr(item, 'text', "")
                )
                results.append(result)
            
            return TwelveLabsSearchResponse(
                data=results,
                page_info=getattr(search_result, 'page_info', None),
                total_results=len(results)
            )
                
        except Exception as e:
            logger.error(f"Error searching video: {str(e)}")
            raise

class UrbanAnalyzer:
    """Urban feature analyzer using TwelveLabs"""
    
    def __init__(self):
        self.client = TwelveLabsClient()
        
        # Urban feature detection queries
        self.detection_queries = [
            "buildings and residential structures",
            "commercial buildings and office complexes",
            "parks, trees, and green vegetation areas",
            "roads, streets, and transportation infrastructure",
            "parking lots and paved surfaces",
            "concrete and asphalt surfaces",
            "water bodies and rivers",
            "industrial facilities and warehouses"
        ]
    
    async def analyze_satellite_image(self, image_path: str) -> UrbanFeatures:
        """Analyze satellite image for urban features"""
        try:
            # Convert image to video if needed (TwelveLabs expects video format)
            video_path = await self._prepare_video_from_image(image_path)
            
            # Upload and process
            task_id = await self.client.upload_video(video_path, {
                "type": "satellite_imagery",
                "source": "urban_analysis"
            })
            
            video_id = await self.client.wait_for_processing(task_id)
            
            # Perform multiple searches for different urban features
            all_features = UrbanFeatures()
            
            for query in self.detection_queries:
                logger.info(f"Searching for: {query}")
                search_results = await self.client.search_video(video_id, query)
                
                # Parse and categorize results
                await self._parse_search_results(query, search_results, all_features)
            
            # Clean up temporary video file
            from app.utils.video_converter import cleanup_video
            cleanup_video(video_path)
            
            return all_features
            
        except Exception as e:
            logger.error(f"Error analyzing satellite image: {str(e)}")
            raise
    
    async def _prepare_video_from_image(self, image_path: str) -> str:
        """Convert static image to video format for TwelveLabs processing"""
        try:
            from app.utils.video_converter import VideoConverter
            
            logger.info(f"Converting satellite image to video: {image_path}")
            
            # Use enhanced video converter with FFmpeg/OpenCV fallback
            converter = await VideoConverter.get_optimal_converter()
            
            # Create a 3-second video at 30 FPS for better quality
            video_path = await converter.convert_image_to_video(
                image_path=image_path,
                duration=3.0,  # 3 seconds for better analysis
                fps=30,  # Higher FPS for smoother video
                prefer_ffmpeg=True  # Prefer FFmpeg for better quality
            )
            
            logger.info(f"Successfully created video for TwelveLabs: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error creating video from image: {str(e)}")
            raise
    
    async def _parse_search_results(self, query: str, results: TwelveLabsSearchResponse, features: UrbanFeatures):
        """Parse search results and categorize into urban features"""
        try:
            for result in results.data:
                # Generate mock coordinates (in real implementation, would extract from video analysis)
                coords = Coordinates(
                    lat=37.7749 + (hash(result.text_description or "") % 1000) / 100000,
                    lng=-122.4194 + (hash(result.text_description or "") % 1000) / 100000
                )
                
                if "building" in query.lower():
                    building = Building(
                        id=str(uuid.uuid4()),
                        coordinates=coords,
                        type=self._determine_building_type(result.text_description or ""),
                        confidence=result.confidence,
                        description=result.text_description
                    )
                    features.buildings.append(building)
                
                elif "vegetation" in query.lower() or "park" in query.lower() or "tree" in query.lower():
                    vegetation = VegetationArea(
                        id=str(uuid.uuid4()),
                        coordinates=coords,
                        type=self._determine_vegetation_type(result.text_description or ""),
                        confidence=result.confidence
                    )
                    features.vegetation.append(vegetation)
                
                elif "surface" in query.lower() or "concrete" in query.lower() or "asphalt" in query.lower():
                    surface = SurfaceArea(
                        id=str(uuid.uuid4()),
                        coordinates=coords,
                        material_type=self._determine_surface_material(result.text_description or ""),
                        heat_absorption=self._estimate_heat_absorption(result.text_description or ""),
                        confidence=result.confidence
                    )
                    features.surfaces.append(surface)
                
                elif "road" in query.lower() or "infrastructure" in query.lower():
                    infrastructure = InfrastructureElement(
                        id=str(uuid.uuid4()),
                        coordinates=coords,
                        type=self._determine_infrastructure_type(result.text_description or ""),
                        confidence=result.confidence
                    )
                    features.infrastructure.append(infrastructure)
            
            logger.info(f"Parsed {len(results.data)} results for query: {query}")
            
        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}")
    
    def _determine_building_type(self, description: str) -> BuildingType:
        """Determine building type from description"""
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["residential", "house", "apartment"]):
            return BuildingType.RESIDENTIAL
        elif any(word in desc_lower for word in ["commercial", "office", "retail", "store"]):
            return BuildingType.COMMERCIAL
        elif any(word in desc_lower for word in ["industrial", "factory", "warehouse"]):
            return BuildingType.INDUSTRIAL
        return BuildingType.UNKNOWN
    
    def _determine_vegetation_type(self, description: str) -> VegetationType:
        """Determine vegetation type from description"""
        desc_lower = description.lower()
        if "park" in desc_lower:
            return VegetationType.PARK
        elif any(word in desc_lower for word in ["tree", "trees"]):
            return VegetationType.TREES
        elif "grass" in desc_lower:
            return VegetationType.GRASS
        elif "forest" in desc_lower:
            return VegetationType.FOREST
        return VegetationType.UNKNOWN
    
    def _determine_surface_material(self, description: str) -> SurfaceMaterial:
        """Determine surface material from description"""
        desc_lower = description.lower()
        if "asphalt" in desc_lower:
            return SurfaceMaterial.ASPHALT
        elif "concrete" in desc_lower:
            return SurfaceMaterial.CONCRETE
        elif any(word in desc_lower for word in ["grass", "vegetation"]):
            return SurfaceMaterial.GRASS
        elif "water" in desc_lower:
            return SurfaceMaterial.WATER
        return SurfaceMaterial.UNKNOWN
    
    def _determine_infrastructure_type(self, description: str) -> InfrastructureType:
        """Determine infrastructure type from description"""
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["highway", "freeway"]):
            return InfrastructureType.HIGHWAY
        elif "road" in desc_lower or "street" in desc_lower:
            return InfrastructureType.ROAD
        elif "parking" in desc_lower:
            return InfrastructureType.PARKING
        elif "bridge" in desc_lower:
            return InfrastructureType.BRIDGE
        return InfrastructureType.UNKNOWN
    
    def _estimate_heat_absorption(self, description: str) -> float:
        """Estimate heat absorption coefficient based on material"""
        desc_lower = description.lower()
        if "asphalt" in desc_lower:
            return 0.9
        elif "concrete" in desc_lower:
            return 0.8
        elif any(word in desc_lower for word in ["grass", "vegetation", "tree"]):
            return 0.3
        elif "water" in desc_lower:
            return 0.1
        return 0.5  # Default moderate absorption
