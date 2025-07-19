#!/usr/bin/env python3
"""
Test NASA vegetation analysis with real API endpoints
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the service directly
from app.services.nasa_service import NASAService

async def test_nasa_vegetation_analysis():
    """Test NASA vegetation analysis with real API endpoints"""
    print("🛰️ Testing NASA Vegetation Analysis with Real API Endpoints")
    print("=" * 60)
    
    # Test coordinates - different vegetation types
    test_locations = [
        {"name": "Central Park, NYC", "lat": 40.7829, "lon": -73.9654},
        {"name": "Golden Gate Park, SF", "lat": 37.7694, "lon": -122.4862}, 
        {"name": "Times Square, NYC (Urban)", "lat": 40.7580, "lon": -73.9855},
        {"name": "Amazon Rainforest", "lat": -3.4653, "lon": -62.2159},
        {"name": "Sahara Desert", "lat": 23.8859, "lon": 32.6197}
    ]
    
    nasa_service = NASAService()
    
    # Test date - recent but within satellite data availability
    test_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    print(f"📅 Test date: {test_date}")
    print(f"🔑 API Key configured: {'Yes' if nasa_service.api_key else 'No (using mock data)'}")
    print()
    
    for location in test_locations:
        print(f"📍 Testing: {location['name']}")
        print(f"   Coordinates: {location['lat']}, {location['lon']}")
        
        try:
            # Test vegetation index
            vegetation_data = await nasa_service.get_vegetation_index(
                location['lat'], 
                location['lon'], 
                test_date
            )
            
            print(f"   ✅ Vegetation Analysis:")
            print(f"      NDVI: {vegetation_data['ndvi']:.3f}")
            if 'vegetation_coverage_percent' in vegetation_data:
                print(f"      Coverage: {vegetation_data['vegetation_coverage_percent']:.1f}%")
            print(f"      Health: {vegetation_data['vegetation_health']}")
            print(f"      Source: {vegetation_data['source']}")
            print(f"      Resolution: {vegetation_data['resolution']}")
            
            # Interpret NDVI values
            ndvi = vegetation_data['ndvi']
            if ndvi > 0.6:
                interpretation = "Dense, healthy vegetation"
            elif ndvi > 0.4:
                interpretation = "Moderate vegetation"
            elif ndvi > 0.2:
                interpretation = "Sparse vegetation"
            elif ndvi > 0:
                interpretation = "Very sparse vegetation"
            else:
                interpretation = "No vegetation (water/urban/desert)"
            
            print(f"      Interpretation: {interpretation}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    # Test API availability and authentication
    print("🔍 API Endpoint Test Summary:")
    print("-" * 30)
    
    if nasa_service.api_key:
        print("✅ NASA API key is configured")
        print("🌍 Testing MODIS API endpoint...")
        
        # Test a simple location
        test_result = await nasa_service.get_vegetation_index(40.7829, -73.9654, test_date)
        if "real" in test_result.get('source', '').lower() or "modis" in test_result.get('source', '').lower():
            print("✅ Real NASA MODIS data successfully retrieved")
        else:
            print("⚠️  Falling back to mock data (API may be unavailable)")
    else:
        print("⚠️  NASA API key not configured - using mock data")
        print("   To use real NASA data, set NASA_API_KEY in your .env file")
    
    print("\n🎯 Vegetation Analysis Integration:")
    print("-" * 40)
    print("• TwelveLabs: Visual vegetation detection from satellite images")
    print("• NASA NDVI: Quantitative vegetation health and coverage")
    print("• Combined Analysis: Heat island intensity with dual vegetation metrics")
    print("• Enhanced Recommendations: Specific to vegetation coverage gaps")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_nasa_vegetation_analysis())
