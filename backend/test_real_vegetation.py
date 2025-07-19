#!/usr/bin/env python3
"""
Test Real Vegetation Service - NO MOCK DATA
Uses OpenWeather Satellite API for real Landsat 8 + Sentinel 2 NDVI data
"""

import asyncio
import sys
import os

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.real_vegetation_service import RealVegetationService

async def test_real_vegetation_data():
    """Test REAL vegetation data with NO fallback to mock"""
    print("🛰️ Testing REAL Vegetation Data (OpenWeather Satellite API)")
    print("=" * 70)
    print("📡 Data Sources: Landsat 8 + Sentinel 2 satellites")
    print("🚫 NO MOCK DATA - Real satellite data ONLY")
    print()
    
    try:
        # Initialize service - will fail if no API key
        service = RealVegetationService()
        print(f"✅ Service initialized with API key")
        print()
        
        # Test single location first
        print("📍 Testing: Central Park, New York City")
        lat, lon = 40.7829, -73.9654
        
        print("🔄 Fetching REAL satellite NDVI data...")
        vegetation_data = await service.get_vegetation_index(lat, lon)
        
        print("🎯 REAL VEGETATION DATA RESULTS:")
        print(f"   🌱 NDVI Value: {vegetation_data['ndvi']:.4f}")
        print(f"   🌿 Vegetation Coverage: {vegetation_data['vegetation_coverage_percent']:.1f}%")
        print(f"   💚 Health Assessment: {vegetation_data['vegetation_health']}")
        print(f"   📊 Data Quality: {vegetation_data['data_quality']}")
        print(f"   📡 Source: {vegetation_data['source']}")
        print(f"   🕐 Timestamp: {vegetation_data['timestamp']}")
        print(f"   📐 Resolution: {vegetation_data['resolution']}")
        
        if 'statistics' in vegetation_data:
            stats = vegetation_data['statistics']
            print(f"   📈 Statistics:")
            print(f"      Mean: {stats.get('mean', 'N/A'):.4f}")
            print(f"      Std Dev: {stats.get('std', 'N/A'):.4f}")
            print(f"      Min: {stats.get('min', 'N/A'):.4f}")
            print(f"      Max: {stats.get('max', 'N/A'):.4f}")
            print(f"      Sample Count: {stats.get('count', 'N/A')}")
        
        # Cleanup the polygon
        if 'polygon_id' in vegetation_data:
            print(f"🧹 Cleaning up polygon {vegetation_data['polygon_id']}...")
            await service.cleanup_polygon(vegetation_data['polygon_id'])
        
        print()
        print("✅ SUCCESS: Retrieved REAL satellite vegetation data!")
        
        # Test additional locations
        additional_locations = [
            {"name": "Amazon Rainforest, Brazil", "lat": -3.4653, "lon": -62.2159},
            {"name": "Hyde Park, London", "lat": 51.5085, "lon": -0.1464},
        ]
        
        for location in additional_locations:
            print(f"\n📍 Testing: {location['name']}")
            try:
                veg_data = await service.get_vegetation_index(location['lat'], location['lon'])
                print(f"   🌱 NDVI: {veg_data['ndvi']:.4f}")
                print(f"   🌿 Coverage: {veg_data['vegetation_coverage_percent']:.1f}%")
                print(f"   💚 Health: {veg_data['vegetation_health']}")
                
                # Cleanup
                if 'polygon_id' in veg_data:
                    await service.cleanup_polygon(veg_data['polygon_id'])
                    
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
        
        print("\n" + "=" * 70)
        print("🎉 REAL VEGETATION DATA TEST COMPLETED!")
        print("🚫 NO MOCK DATA WAS USED - All data is from real satellites!")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        print("\n💡 Common issues:")
        print("   1. Check OPENWEATHER_API_KEY environment variable")
        print("   2. Ensure API key has access to Agro API features")
        print("   3. Check internet connection")
        print("   4. Verify API quota limits")
        print("\n🔑 API Key Status:")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            print(f"   ✅ Present: {api_key[:8]}...")
        else:
            print("   ❌ Missing: Set OPENWEATHER_API_KEY environment variable")

if __name__ == "__main__":
    asyncio.run(test_real_vegetation_data())
