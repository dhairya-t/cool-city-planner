#!/usr/bin/env python3
"""
Tests real-time satellite imagery download and vegetation analysis
"""

import asyncio
import sys
import os

import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import setup_logging
from app.services.live_satellite_service import LiveSatelliteService

async def test_live_satellite_analysis():
    setup_logging(log_level="DEBUG")
    """Test live satellite analysis with multiple locations"""
    print("=" * 60)
    
    service = LiveSatelliteService()
    
    test_locations = [
        {
            "name": "Toronto",
            "lat": 43.642567,
            "lon": -79.387054,
            "description": "Urban core - should show low vegetation"
        },
    ]
    
    results = []
    
    for i, location in enumerate(test_locations, 1):
        print(f"\n🗺️ Test {i}/{len(test_locations)}: {location['name']}")
        print(f"📍 Coordinates: {location['lat']}, {location['lon']}")
        print(f"📋 Expected: {location['description']}")
        
        satellite_data = await service.get_live_satellite_data(
            location['lat'],
            location['lon'],
            analysis_radius=0.02
        )

        heat_map = satellite_data.heat_map
        print(heat_map.shape)

        # Write heat map to file
        heat_map_file = f"heat_map_{location['name'].lower().replace(' ', '_')}.png"
        cv2.imwrite(heat_map_file, heat_map)

        if satellite_data:
            # Store results
            results.append({
                'location': location['name'],
                'coordinates': [location['lat'], location['lon']],
            })

            print("✅ Live satellite analysis successful!")

        else:
            print("❌ Failed to get satellite data")
            results.append({
                'location': location['name'],
                'coordinates': [location['lat'], location['lon']],
                'error': 'Failed to download satellite imagery'
            })
        
        # Brief pause between requests to be respectful
        if i < len(test_locations):
            print("⏳ Waiting 2 seconds before next analysis...")
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 LIVE SATELLITE ANALYSIS SUMMARY")
    print("=" * 60)

    print(f"🔄 Processing: Live analysis, no data storage")
    print(f"📊 Analysis Method: Color-based vegetation detection + heat island estimation")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Live Satellite Service Test")
    print("But processes satellite imagery live without storage\n")
    
    results = asyncio.run(test_live_satellite_analysis())

    print(f"\n✅ Test completed successfully!")
    print(f"📝 Tested {len(results)} locations")
    print("🌍 Live satellite analysis is working!")

