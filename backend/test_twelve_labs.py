#!/usr/bin/env python3
"""
Test script for TwelveLabs integration
"""
import asyncio
import os
from pathlib import Path
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.services.twelve_labs_client import TwelveLabsClient, UrbanAnalyzer

# Setup logging
setup_logging("INFO")
logger = get_logger(__name__)

async def test_twelve_labs_connection():
    """Test TwelveLabs API connection and basic functionality"""
    try:
        logger.info("Testing TwelveLabs API connection...")
        
        # Check if API key is configured
        if not settings.TWELVE_LABS_API_KEY:
            logger.error("TwelveLabs API key not configured. Set TWELVE_LABS_API_KEY environment variable.")
            return False
        
        # Initialize client
        client = TwelveLabsClient()
        logger.info("TwelveLabs client initialized successfully")
        
        # Test index management
        logger.info("Testing index management...")
        index_id = await client.get_or_create_index("coolcity-test-index")
        logger.info(f"Index ready: {index_id}")
        
        # List existing indexes to verify
        try:
            indexes = client.client.indexes.list()
            if hasattr(indexes, 'data'):
                logger.info(f"Found {len(indexes.data)} indexes in account")
                for idx in indexes.data:
                    logger.info(f"  - {idx.name} (ID: {idx.id})")
            else:
                logger.info("Indexes retrieved but no data attribute found")
        except Exception as e:
            logger.warning(f"Could not list indexes: {e}")
        
        logger.info("✅ TwelveLabs connection test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ TwelveLabs connection test failed: {str(e)}")
        return False

async def test_urban_analyzer():
    """Test the UrbanAnalyzer with a sample image"""
    try:
        logger.info("Testing UrbanAnalyzer...")
        
        # Create a simple test image if it doesn't exist
        test_image_path = Path("test_satellite.jpg")
        if not test_image_path.exists():
            logger.info("Creating test image...")
            import cv2
            import numpy as np
            
            # Create a simple test image (satellite-like)
            img = np.zeros((512, 512, 3), dtype=np.uint8)
            # Add some "urban" patterns
            cv2.rectangle(img, (100, 100), (200, 200), (100, 100, 100), -1)  # Building
            cv2.rectangle(img, (250, 150), (350, 250), (50, 150, 50), -1)    # Park
            cv2.rectangle(img, (0, 400), (512, 450), (50, 50, 50), -1)       # Road
            
            cv2.imwrite(str(test_image_path), img)
            logger.info(f"Created test image: {test_image_path}")
        
        # Test urban analysis (this will use mock data if API not fully configured)
        analyzer = UrbanAnalyzer()
        
        logger.info("Analyzing test image...")
        features = await analyzer.analyze_satellite_image(str(test_image_path))
        
        logger.info("Urban analysis results:")
        logger.info(f"  - Buildings: {len(features.buildings)}")
        logger.info(f"  - Vegetation areas: {len(features.vegetation)}")
        logger.info(f"  - Surface areas: {len(features.surfaces)}")
        logger.info(f"  - Infrastructure: {len(features.infrastructure)}")
        
        # Clean up test image
        if test_image_path.exists():
            test_image_path.unlink()
        
        logger.info("✅ Urban analyzer test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Urban analyzer test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("CoolCity Planner - TwelveLabs Integration Test")
    logger.info("=" * 60)
    
    # Test 1: Basic connection
    connection_ok = await test_twelve_labs_connection()
    
    print("\n" + "-" * 60 + "\n")
    
    # Test 2: Urban analyzer
    analyzer_ok = await test_urban_analyzer()
    
    print("\n" + "=" * 60)
    
    if connection_ok and analyzer_ok:
        logger.info("🎉 All tests passed! TwelveLabs integration is ready.")
    else:
        logger.error("⚠️  Some tests failed. Check configuration and try again.")
        
    logger.info("Configuration status:")
    logger.info(f"  - TwelveLabs API Key: {'✅ Set' if settings.TWELVE_LABS_API_KEY else '❌ Missing'}")
    logger.info(f"  - Index ID: {'✅ Set' if settings.TWELVE_LABS_INDEX_ID else '⚠️  Will auto-create'}")
    logger.info(f"  - Environment: {settings.ENVIRONMENT}")

if __name__ == "__main__":
    asyncio.run(main())
