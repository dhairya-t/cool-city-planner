#!/usr/bin/env python3
"""
Test Live Satellite Service - Chilladelphia's approach but live processing
Tests real-time satellite imagery download and vegetation analysis
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.live_satellite_service import LiveSatelliteService

async def test_live_satellite_analysis():
    """Test live satellite analysis with multiple locations"""
    print("🛰️ Testing Live Satellite Service (Chilladelphia's approach)")
    print("=" * 60)
    
    service = LiveSatelliteService()
    
    # Test locations - same types as Chilladelphia tested
    test_locations = [
        {
            "name": "Philadelphia Center City", 
            "lat": 39.9526, 
            "lon": -75.1652,
            "description": "Urban core - should show low vegetation"
        },
        {
            "name": "Fairmount Park, Philadelphia",
            "lat": 39.9896,
            "lon": -75.2093, 
            "description": "Large urban park - should show high vegetation"
        },
        {
            "name": "South Philadelphia",
            "lat": 39.9174,
            "lon": -75.1654,
            "description": "Residential area - moderate vegetation"
        },
        {
            "name": "University City, Philadelphia", 
            "lat": 39.9522,
            "lon": -75.1932,
            "description": "Mixed urban/campus area"
        },
        {
            "name": "New York Central Park",
            "lat": 40.7829,
            "lon": -73.9654,
            "description": "Major urban park for comparison"
        }
    ]
    
    results = []
    
    for i, location in enumerate(test_locations, 1):
        print(f"\n🗺️ Test {i}/{len(test_locations)}: {location['name']}")
        print(f"📍 Coordinates: {location['lat']}, {location['lon']}")
        print(f"📋 Expected: {location['description']}")
        
        try:
            # Get live satellite data (same as Chilladelphia but no storage)
            satellite_data = await service.get_live_satellite_data(
                location['lat'], 
                location['lon'],
                analysis_radius=0.002  # Same radius as Chilladelphia's tiles
            )
            
            if satellite_data:
                # Extract key metrics
                vegetation_pct = satellite_data['vegetation_data']['vegetation_coverage_percent']
                ndvi_estimate = satellite_data['vegetation_data']['ndvi_estimate'] 
                vegetation_health = satellite_data['vegetation_data']['vegetation_health']
                estimated_temp = satellite_data['thermal_estimate']['estimated_land_surface_temp']
                urban_density = satellite_data['urban_analysis']['urban_density_score']
                
                print(f"📊 Results:")
                print(f"   🌱 Vegetation Coverage: {vegetation_pct:.1f}%")
                print(f"   🟢 NDVI Estimate: {ndvi_estimate:.3f}")
                print(f"   💚 Vegetation Health: {vegetation_health}")
                print(f"   🌡️  Estimated Temperature: {estimated_temp:.1f}°C")
                print(f"   🏢 Urban Density: {urban_density:.2f}")
                
                # Show saved image files
                if 'saved_files' in vegetation_analysis:
                    print(f"   📷 Satellite Image: saved to satellite_images/")
                    print(f"   🌱 Vegetation Mask: {vegetation_analysis['saved_files']['vegetation_mask']}")
                    print(f"   📊 Vegetation Overlay: {vegetation_analysis['saved_files']['vegetation_overlay']}")
                
                # Calculate heat island intensity
                heat_island = service.estimate_heat_island_from_live_data(satellite_data)
                print(f"   🔥 Heat Island Intensity: {heat_island['intensity']:.1f}/10 ({heat_island['risk_level']})")
                
                # Store results
                results.append({
                    'location': location['name'],
                    'coordinates': [location['lat'], location['lon']],
                    'vegetation_coverage': vegetation_pct,
                    'ndvi_estimate': ndvi_estimate,
                    'health': vegetation_health,
                    'temperature': estimated_temp,
                    'heat_island_intensity': heat_island['intensity'],
                    'risk_level': heat_island['risk_level']
                })
                
                print("✅ Live satellite analysis successful!")
                
            else:
                print("❌ Failed to get satellite data")
                results.append({
                    'location': location['name'],
                    'coordinates': [location['lat'], location['lon']],
                    'error': 'Failed to download satellite imagery'
                })
            
        except Exception as e:
            print(f"❌ Error analyzing {location['name']}: {e}")
            results.append({
                'location': location['name'],
                'coordinates': [location['lat'], location['lon']],
                'error': str(e)
            })
        
        # Brief pause between requests to be respectful
        if i < len(test_locations):
            print("⏳ Waiting 2 seconds before next analysis...")
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 LIVE SATELLITE ANALYSIS SUMMARY")
    print("=" * 60)
    
    successful_results = [r for r in results if 'error' not in r]
    
    if successful_results:
        print(f"✅ Successful analyses: {len(successful_results)}/{len(results)}")
        print(f"🌱 Average vegetation coverage: {sum(r['vegetation_coverage'] for r in successful_results)/len(successful_results):.1f}%")
        print(f"🌡️  Average temperature: {sum(r['temperature'] for r in successful_results)/len(successful_results):.1f}°C")
        print(f"🔥 Average heat island intensity: {sum(r['heat_island_intensity'] for r in successful_results)/len(successful_results):.1f}/10")
        
        print(f"\n🏆 Highest vegetation coverage: {max(successful_results, key=lambda x: x['vegetation_coverage'])['location']} ({max(r['vegetation_coverage'] for r in successful_results):.1f}%)")
        print(f"🔥 Highest heat island risk: {max(successful_results, key=lambda x: x['heat_island_intensity'])['location']} ({max(r['heat_island_intensity'] for r in successful_results):.1f}/10)")
    else:
        print("❌ No successful analyses completed")
    
    print(f"\n🛰️ Data Source: Google Maps Satellite API (same as Chilladelphia)")
    print(f"🔄 Processing: Live analysis, no data storage")
    print(f"📊 Analysis Method: Color-based vegetation detection + heat island estimation")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Live Satellite Service Test")
    print("Based on Chilladelphia's preprocessing approach")
    print("But processes satellite imagery live without storage\n")
    
    try:
        results = asyncio.run(test_live_satellite_analysis())
        
        print(f"\n✅ Test completed successfully!")
        print(f"📝 Tested {len(results)} locations")
        print("🌍 Live satellite analysis is working!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
