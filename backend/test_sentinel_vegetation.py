#!/usr/bin/env python3
"""
Test script for Sentinel Vegetation Service
Tests real satellite vegetation data retrieval
"""

import asyncio
import sys
import os

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.sentinel_vegetation_service import SentinelVegetationService

async def test_vegetation_analysis():
    """Test vegetation analysis with various locations"""
    print("🛰️ Testing Sentinel Hub Vegetation Analysis")
    print("=" * 60)
    
    service = SentinelVegetationService()
    
    # Test credentials
    client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
    client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
    
    print(f"🔑 Sentinel Hub Client ID: {'✅ Configured' if client_id else '❌ Missing'}")
    print(f"🔑 Sentinel Hub Secret: {'✅ Configured' if client_secret else '❌ Missing'}")
    print()
    
    # Test locations with different vegetation profiles
    test_locations = [
        {"name": "Central Park, NYC", "lat": 40.7829, "lon": -73.9654, "expected": "moderate_high"},
        {"name": "Amazon Rainforest", "lat": -3.4653, "lon": -62.2159, "expected": "excellent"},
        {"name": "Sahara Desert", "lat": 23.8859, "lon": 12.5387, "expected": "very_poor"},
        {"name": "London Hyde Park", "lat": 51.5085, "lon": -0.1464, "expected": "good"},
        {"name": "Los Angeles Downtown", "lat": 34.0522, "lon": -118.2437, "expected": "poor_moderate"}
    ]
    
    for location in test_locations:
        print(f"📍 Testing: {location['name']}")
        print(f"   Coordinates: {location['lat']}, {location['lon']}")
        
        try:
            # Get vegetation data
            veg_data = await service.get_vegetation_index(location['lat'], location['lon'])
            
            print(f"   🌱 NDVI: {veg_data['ndvi']:.3f}")
            print(f"   🌿 Vegetation Coverage: {veg_data['vegetation_coverage_percent']:.1f}%")
            print(f"   💚 Health: {veg_data['vegetation_health']}")
            print(f"   📡 Source: {veg_data['source']}")
            print(f"   📊 Quality: {veg_data['data_quality']}")
            
            # Assess if result makes sense
            ndvi = veg_data['ndvi']
            expected = location['expected']
            
            assessment = "✅ Realistic"
            if expected == "excellent" and ndvi < 0.6:
                assessment = "⚠️ Lower than expected for rainforest"
            elif expected == "very_poor" and ndvi > 0.3:
                assessment = "⚠️ Higher than expected for desert"
            elif expected in ["poor_moderate", "moderate_high"] and (ndvi < 0.1 or ndvi > 0.8):
                assessment = "⚠️ Outside expected range for urban area"
            
            print(f"   🎯 Assessment: {assessment}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            print()
    
    # Test temperature data
    print("🌡️ Testing Land Surface Temperature")
    print("-" * 40)
    
    try:
        temp_data = await service.get_land_surface_temperature(40.7829, -73.9654)
        print(f"📍 Location: Central Park, NYC")
        print(f"🌞 Day Temperature: {temp_data['land_surface_temperature']['day']:.1f}°C")
        print(f"🌙 Night Temperature: {temp_data['land_surface_temperature']['night']:.1f}°C")
        print(f"📡 Source: {temp_data['source']}")
        
    except Exception as e:
        print(f"❌ Temperature test failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    
    if not client_id or not client_secret:
        print("\n💡 To test with REAL Sentinel Hub data:")
        print("   1. Sign up at https://dataspace.copernicus.eu/")
        print("   2. Get your OAuth2 credentials")
        print("   3. Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET")
        print("   4. The service will automatically use real satellite data!")
        print("\n📝 For now, the service uses enhanced mock data based on geographic location.")

if __name__ == "__main__":
    asyncio.run(test_vegetation_analysis())
