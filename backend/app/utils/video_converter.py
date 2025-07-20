"""
Video conversion utilities for TwelveLabs integration
"""
import asyncio
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

class VideoConverter:
    """Convert images to videos for TwelveLabs processing"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "coolcity_videos"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def image_to_video_ffmpeg(
        self, 
        image_path: str, 
        duration: float = 2.0,
        fps: int = 30,
        output_format: str = "mp4"
    ) -> str:
        """
        Convert static image to video using FFmpeg (preferred method)
        
        Args:
            image_path: Path to input image
            duration: Video duration in seconds
            fps: Frames per second
            output_format: Output video format
            
        Returns:
            Path to generated video file
        """
        try:
            # Generate unique output filename
            video_filename = f"satellite_video_{uuid.uuid4().hex}.{output_format}"
            output_path = self.temp_dir / video_filename
            
            logger.info(f"Converting image to video: {image_path} -> {output_path}")
            
            # Build FFmpeg command
            cmd = [
                "ffmpeg", 
                "-y",  # Overwrite output file
                "-loop", "1",  # Loop input
                "-i", str(image_path),  # Input image
                "-c:v", "libx264",  # Video codec
                "-t", str(duration),  # Duration
                "-r", str(fps),  # Frame rate
                "-pix_fmt", "yuv420p",  # Pixel format (ensures compatibility)
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",  # Scale and pad
                str(output_path)
            ]
            
            # Run FFmpeg asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown FFmpeg error"
                logger.error(f"FFmpeg conversion failed: {error_msg}")
                # Fall back to OpenCV method
                return await self.image_to_video_opencv(image_path, duration, fps)
            
            logger.info(f"Successfully created video: {output_path}")
            return str(output_path)
            
        except FileNotFoundError:
            logger.warning("FFmpeg not found, falling back to OpenCV method")
            return await self.image_to_video_opencv(image_path, duration, fps)
        except Exception as e:
            logger.error(f"Error in FFmpeg conversion: {str(e)}")
            return await self.image_to_video_opencv(image_path, duration, fps)
    
    async def image_to_video_opencv(
        self, 
        image_path: str, 
        duration: float = 2.0,
        fps: int = 30
    ) -> str:
        """
        Convert static image to video using OpenCV (fallback method)
        
        Args:
            image_path: Path to input image
            duration: Video duration in seconds
            fps: Frames per second
            
        Returns:
            Path to generated video file
        """
        try:
            import cv2
            import numpy as np
            
            # Generate unique output filename
            video_filename = f"satellite_video_{uuid.uuid4().hex}.mp4"
            output_path = self.temp_dir / video_filename
            
            logger.info(f"Converting image to video with OpenCV: {image_path} -> {output_path}")
            
            # Read the image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Get image dimensions
            height, width, channels = image.shape
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise RuntimeError("Could not open video writer")
            
            # Calculate total frames needed
            total_frames = int(duration * fps)
            
            # Write the same frame multiple times
            for frame_num in range(total_frames):
                out.write(image)
                
                # Log progress every 30 frames (1 second at 30fps)
                if frame_num % 30 == 0:
                    progress = (frame_num / total_frames) * 100
                    logger.debug(f"Video creation progress: {progress:.1f}%")
            
            out.release()
            cv2.destroyAllWindows()
            
            logger.info(f"Successfully created video with OpenCV: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error in OpenCV conversion: {str(e)}")
            raise
    
    async def convert_image_to_video(
        self, 
        image_path: str, 
        duration: float = 2.0,
        fps: int = 30,
        prefer_ffmpeg: bool = True
    ) -> str:
        """
        Main conversion method - tries FFmpeg first, falls back to OpenCV
        
        Args:
            image_path: Path to input image
            duration: Video duration in seconds
            fps: Frames per second
            prefer_ffmpeg: Whether to prefer FFmpeg over OpenCV
            
        Returns:
            Path to generated video file
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")
        
        if prefer_ffmpeg:
            return await self.image_to_video_ffmpeg(image_path, duration, fps)
        else:
            return await self.image_to_video_opencv(image_path, duration, fps)
    
    def cleanup_video(self, video_path: str) -> None:
        """Clean up temporary video file"""
        try:
            if os.path.exists(video_path):
                os.unlink(video_path)
                logger.debug(f"Cleaned up temporary video: {video_path}")
        except Exception as e:
            logger.warning(f"Could not clean up video file {video_path}: {str(e)}")
    
    def cleanup_all_temp_videos(self) -> None:
        """Clean up all temporary video files"""
        try:
            if self.temp_dir.exists():
                for video_file in self.temp_dir.glob("satellite_video_*.mp4"):
                    try:
                        video_file.unlink()
                        logger.debug(f"Cleaned up: {video_file}")
                    except Exception as e:
                        logger.warning(f"Could not clean up {video_file}: {str(e)}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    @staticmethod
    def check_ffmpeg_available() -> bool:
        """Check if FFmpeg is available on the system"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @classmethod
    async def get_optimal_converter(cls) -> 'VideoConverter':
        """Get a video converter with optimal settings"""
        converter = cls()
        
        # Check capabilities
        has_ffmpeg = cls.check_ffmpeg_available()
        
        if has_ffmpeg:
            logger.info("FFmpeg available - using high-quality conversion")
        else:
            logger.info("FFmpeg not available - using OpenCV fallback")
        
        return converter

# Convenience functions for easy import
async def convert_image_to_video(
    image_path: str, 
    duration: float = 2.0,
    fps: int = 30
) -> str:
    """Convenience function to convert image to video"""
    converter = await VideoConverter.get_optimal_converter()
    return await converter.convert_image_to_video(image_path, duration, fps)

def cleanup_video(video_path: str) -> None:
    """Convenience function to cleanup video"""
    converter = VideoConverter()
    converter.cleanup_video(video_path)
