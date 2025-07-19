"""
Test script for image-to-video conversion for TwelveLabs
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.utils.video_converter import VideoConverter
from app.core.logging import get_logger

logger = get_logger(__name__)

def create_test_satellite_image(width: int = 1920, height: int = 1080) -> str:
    """Create a test satellite image for conversion testing"""
    
    # Create a realistic satellite image mockup
    img = Image.new('RGB', (width, height), color=(34, 139, 34))  # Forest green base
    draw = ImageDraw.Draw(img)
    
    # Draw some "urban" features
    # Buildings (rectangles in gray)
    for i in range(5):
        x1 = np.random.randint(100, width-200)
        y1 = np.random.randint(100, height-200)
        x2 = x1 + np.random.randint(50, 150)
        y2 = y1 + np.random.randint(30, 100)
        draw.rectangle([x1, y1, x2, y2], fill=(169, 169, 169))  # Gray buildings
    
    # Roads (lines in black)
    for i in range(3):
        x1 = np.random.randint(0, width)
        y1 = np.random.randint(0, height)
        x2 = np.random.randint(0, width)
        y2 = np.random.randint(0, height)
        draw.line([x1, y1, x2, y2], fill=(64, 64, 64), width=8)  # Dark gray roads
    
    # Parks/vegetation (circles in green)
    for i in range(4):
        x = np.random.randint(50, width-50)
        y = np.random.randint(50, height-50)
        r = np.random.randint(30, 80)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(0, 128, 0))  # Green vegetation
    
    # Water (blue areas)
    for i in range(2):
        x1 = np.random.randint(100, width-300)
        y1 = np.random.randint(100, height-100)
        x2 = x1 + np.random.randint(100, 250)
        y2 = y1 + np.random.randint(30, 80)
        draw.ellipse([x1, y1, x2, y2], fill=(30, 144, 255))  # Blue water
    
    # Add some text to identify it as a test image
    try:
        font = ImageFont.load_default()
        draw.text((10, 10), "Test Satellite Image - CoolCity Planner", fill=(255, 255, 255), font=font)
        draw.text((10, 30), f"Resolution: {width}x{height}", fill=(255, 255, 255), font=font)
    except:
        # If font loading fails, just skip text
        pass
    
    # Save the test image
    test_image_path = Path(tempfile.gettempdir()) / f"test_satellite_{width}x{height}.jpg"
    img.save(test_image_path, "JPEG", quality=85)
    
    logger.info(f"Created test satellite image: {test_image_path}")
    return str(test_image_path)

async def test_video_conversion_methods():
    """Test both FFmpeg and OpenCV conversion methods"""
    print("🎬 Testing Image-to-Video Conversion Methods...")
    print("=" * 60)
    
    # Create test image
    test_image = create_test_satellite_image(1920, 1080)
    
    converter = VideoConverter()
    
    # Test 1: FFmpeg conversion (if available)
    print("\n🔧 Testing FFmpeg Conversion...")
    ffmpeg_available = VideoConverter.check_ffmpeg_available()
    
    if ffmpeg_available:
        print("✅ FFmpeg detected on system")
        try:
            video_path_ffmpeg = await converter.image_to_video_ffmpeg(
                test_image, 
                duration=3.0, 
                fps=30
            )
            file_size = os.path.getsize(video_path_ffmpeg) / (1024 * 1024)  # MB
            print(f"✅ FFmpeg conversion successful!")
            print(f"   Output: {video_path_ffmpeg}")
            print(f"   Size: {file_size:.2f} MB")
            
            # Cleanup
            converter.cleanup_video(video_path_ffmpeg)
            
        except Exception as e:
            print(f"❌ FFmpeg conversion failed: {str(e)}")
    else:
        print("⚠️  FFmpeg not available on system")
    
    # Test 2: OpenCV conversion (fallback)
    print("\n🐍 Testing OpenCV Conversion...")
    try:
        video_path_cv = await converter.image_to_video_opencv(
            test_image, 
            duration=3.0, 
            fps=30
        )
        file_size = os.path.getsize(video_path_cv) / (1024 * 1024)  # MB
        print(f"✅ OpenCV conversion successful!")
        print(f"   Output: {video_path_cv}")
        print(f"   Size: {file_size:.2f} MB")
        
        # Cleanup
        converter.cleanup_video(video_path_cv)
        
    except Exception as e:
        print(f"❌ OpenCV conversion failed: {str(e)}")
    
    # Test 3: Smart conversion (automatic method selection)
    print("\n🤖 Testing Smart Conversion...")
    try:
        video_path_smart = await converter.convert_image_to_video(
            test_image, 
            duration=2.0, 
            fps=25
        )
        file_size = os.path.getsize(video_path_smart) / (1024 * 1024)  # MB
        print(f"✅ Smart conversion successful!")
        print(f"   Output: {video_path_smart}")
        print(f"   Size: {file_size:.2f} MB")
        print(f"   Method: {'FFmpeg' if ffmpeg_available else 'OpenCV'}")
        
        # Cleanup
        converter.cleanup_video(video_path_smart)
        
    except Exception as e:
        print(f"❌ Smart conversion failed: {str(e)}")
    
    # Cleanup test image
    try:
        os.unlink(test_image)
        print(f"\n🧹 Cleaned up test image: {test_image}")
    except:
        pass

async def test_different_resolutions():
    """Test conversion with different image resolutions"""
    print("\n📐 Testing Different Resolutions...")
    print("-" * 40)
    
    converter = VideoConverter()
    resolutions = [
        (640, 480),    # VGA
        (1280, 720),   # HD
        (1920, 1080),  # Full HD
        (2560, 1440),  # 2K
    ]
    
    for width, height in resolutions:
        print(f"\n📏 Testing {width}x{height}...")
        try:
            # Create test image
            test_image = create_test_satellite_image(width, height)
            
            # Convert to video
            video_path = await converter.convert_image_to_video(
                test_image, 
                duration=1.5, 
                fps=24
            )
            
            # Check output
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"✅ {width}x{height}: {file_size:.2f} MB")
            
            # Cleanup
            converter.cleanup_video(video_path)
            os.unlink(test_image)
            
        except Exception as e:
            print(f"❌ {width}x{height}: {str(e)}")

async def test_performance_benchmark():
    """Benchmark conversion performance"""
    print("\n⏱️  Performance Benchmark...")
    print("-" * 40)
    
    import time
    
    converter = VideoConverter()
    test_image = create_test_satellite_image(1920, 1080)
    
    # Benchmark different settings
    test_configs = [
        {"duration": 1.0, "fps": 15, "name": "Fast (1s, 15fps)"},
        {"duration": 2.0, "fps": 24, "name": "Balanced (2s, 24fps)"},
        {"duration": 3.0, "fps": 30, "name": "Quality (3s, 30fps)"},
    ]
    
    for config in test_configs:
        print(f"\n🎯 Testing {config['name']}...")
        try:
            start_time = time.time()
            
            video_path = await converter.convert_image_to_video(
                test_image, 
                duration=config["duration"], 
                fps=config["fps"]
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            print(f"✅ Processing time: {processing_time:.2f}s")
            print(f"   File size: {file_size:.2f} MB")
            print(f"   Efficiency: {file_size/processing_time:.2f} MB/s")
            
            # Cleanup
            converter.cleanup_video(video_path)
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    
    # Cleanup test image
    os.unlink(test_image)

def installation_check():
    """Check system requirements and provide installation guidance"""
    print("🔍 System Requirements Check...")
    print("-" * 40)
    
    # Check Python packages
    required_packages = ["cv2", "PIL", "numpy"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Available")
        except ImportError:
            print(f"❌ {package}: Missing")
    
    # Check FFmpeg
    ffmpeg_available = VideoConverter.check_ffmpeg_available()
    if ffmpeg_available:
        print("✅ FFmpeg: Available")
    else:
        print("⚠️  FFmpeg: Not available")
        print("   Install FFmpeg for better video quality:")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
        print("   - macOS: brew install ffmpeg")
        print("   - Linux: sudo apt install ffmpeg")
    
    print(f"\n📝 Recommendation:")
    if ffmpeg_available:
        print("   Your system is optimally configured!")
    else:
        print("   Install FFmpeg for best results, OpenCV fallback will work")

async def main():
    """Run all video conversion tests"""
    print("🚀 CoolCity Planner - Video Conversion Testing")
    print("=" * 60)
    print("Testing image-to-video conversion for TwelveLabs integration")
    
    # System check
    installation_check()
    
    # Main conversion tests
    await test_video_conversion_methods()
    
    # Resolution tests
    await test_different_resolutions()
    
    # Performance tests
    await test_performance_benchmark()
    
    print("\n" + "=" * 60)
    print("🎉 Video Conversion Testing Complete!")
    print("\n💡 Key Features:")
    print("✅ Automatic FFmpeg/OpenCV fallback")
    print("✅ Multiple resolution support") 
    print("✅ Configurable duration and frame rate")
    print("✅ Automatic temporary file cleanup")
    print("✅ High-quality video output for TwelveLabs")
    
    print("\n🎬 Your images are now ready for TwelveLabs video analysis!")
    print("   The system will automatically convert satellite images")
    print("   to high-quality videos optimized for AI analysis.")

if __name__ == "__main__":
    asyncio.run(main())
