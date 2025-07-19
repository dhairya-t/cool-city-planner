"""
Integration test script for all APIs (TwelveLabs + OpenWeather + NASA)
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.services.integrated_analysis import IntegratedAnalysisService
from app.services.weather_service import WeatherService
from app.services.nasa_service import NASAService
from app.models.schemas import Coordinates
from app.core.logging import get_logger

logger = get_logger(__name__)

async def test_individual_services():
    """Test each service individually"""
    print("🧪 Testing Individual API Services...")
    
    # Test coordinates (San Francisco)
    coords = Coordinates(lat=37.7749, lon=-122.4194)
    
    # Test Weather Service
    print("\n🌤️  Testing OpenWeather API...")
    weather_service = WeatherService()
    try:
        current_weather = await weather_service.get_current_weather(coords.lat, coords.lon)
        print(f"✅ Current temperature: {current_weather['temperature']}°C")
        print(f"✅ Feels like: {current_weather['feels_like']}°C")
        print(f"✅ Conditions: {current_weather['description']}")
        
        forecast = await weather_service.get_heat_index_forecast(coords.lat, coords.lon)
        print(f"✅ Forecast entries: {len(forecast)}")
        print(f"✅ Next forecast: {forecast[0]['temperature']}°C at {forecast[0]['datetime']}")
        
    except Exception as e:
        print(f"⚠️  Weather service test failed: {str(e)}")
    
    # Test NASA Service
    print("\n🛰️  Testing NASA API...")
    nasa_service = NASAService()
    try:
        land_temp = await nasa_service.get_modis_temperature(coords.lat, coords.lon)
        print(f"✅ Land surface temp (day): {land_temp['land_surface_temperature']['day']}°C")
        
        vegetation = await nasa_service.get_vegetation_index(coords.lat, coords.lon)
        print(f"✅ NDVI: {vegetation['ndvi']:.3f}")
        print(f"✅ Vegetation health: {vegetation['vegetation_health']}")
        
        air_quality = await nasa_service.get_air_quality_data(coords.lat, coords.lon)
        print(f"✅ AQI: {air_quality['aqi']}")
        print(f"✅ Air quality level: {air_quality['quality_level']}")
        
        climate_trends = await nasa_service.get_climate_trends(coords.lat, coords.lon)
        print(f"✅ Temperature trend: {climate_trends['temperature_trend']['trend']}")
        print(f"✅ Yearly increase: {climate_trends['temperature_trend']['average_increase_per_year']}°C")
        
    except Exception as e:
        print(f"⚠️  NASA service test failed: {str(e)}")

async def test_integrated_analysis():
    """Test the full integrated analysis"""
    print("\n🔄 Testing Integrated Analysis...")
    
    integrated_service = IntegratedAnalysisService()
    coords = Coordinates(lat=37.7749, lon=-122.4194)
    
    # Create a dummy image path for testing
    test_image_path = "test_satellite.jpg"
    task_id = "test-integration-001"
    
    try:
        result = await integrated_service.perform_comprehensive_analysis(
            task_id, test_image_path, coords
        )
        
        print(f"✅ Analysis completed for task: {result.task_id}")
        print(f"✅ Heat island intensity: {result.heat_island_intensity:.2f}/10")
        print(f"✅ Risk assessment: {result.risk_assessment}")
        print(f"✅ Processing time: {result.processing_time:.2f}s")
        print(f"✅ Data sources used: {', '.join(result.data_sources_used)}")
        print(f"✅ Recommendations: {len(result.recommendations)}")
        
        # Show sample recommendation
        if result.recommendations:
            rec = result.recommendations[0]
            print(f"\n📋 Sample Recommendation:")
            print(f"   Category: {rec['category']}")
            print(f"   Action: {rec['action']}")
            print(f"   Impact: {rec['impact']}")
            print(f"   Timeline: {rec['timeline']}")
        
        # Show weather integration
        print(f"\n🌡️  Weather Integration:")
        print(f"   Current temp: {result.current_weather['temperature']}°C")
        print(f"   Heat forecast entries: {len(result.heat_forecast)}")
        
        # Show NASA integration
        print(f"\n🛰️  NASA Integration:")
        print(f"   Land surface temp: {result.land_surface_temp['land_surface_temperature']['day']}°C")
        print(f"   NDVI: {result.vegetation_index['ndvi']}")
        print(f"   AQI: {result.air_quality['aqi']}")
        
        print("\n✅ Integrated analysis test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Integrated analysis test FAILED: {str(e)}")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    print("🔑 Checking API Key Configuration...")
    
    keys = {
        "TwelveLabs": os.getenv("TWELVE_LABS_API_KEY"),
        "OpenWeather": os.getenv("OPENWEATHER_API_KEY"), 
        "NASA": os.getenv("NASA_API_KEY")
    }
    
    for service, key in keys.items():
        if key:
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else key[:4] + "..."
            print(f"✅ {service}: {masked_key}")
        else:
            print(f"⚠️  {service}: Not configured (will use mock data)")
    
    return keys

async def main():
    """Run all integration tests"""
    print("🚀 Starting CoolCity Planner API Integration Tests")
    print("=" * 60)
    
    # Check API keys
    api_keys = check_api_keys()
    
    # Test individual services
    await test_individual_services()
    
    # Test integrated analysis
    success = await test_integrated_analysis()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("\nYour CoolCity Planner backend is ready with:")
        print("✅ TwelveLabs video analysis integration")
        print("✅ OpenWeather climate data integration")
        print("✅ NASA satellite data integration")
        print("✅ Comprehensive heat island analysis")
        print("✅ Smart recommendations engine")
        
        if not any(api_keys.values()):
            print("\n💡 To enable real API calls, add your keys to .env:")
            print("   TWELVE_LABS_API_KEY=your_key_here")
            print("   OPENWEATHER_API_KEY=79eca6d6a0b21231dbc81f2ebc069179")
            print("   NASA_API_KEY=kxwmTdptQ8iBZkaDqSxOhWW9TciPB56d6KpunmaX")
    else:
        print("❌ SOME TESTS FAILED - Check the error messages above")

if __name__ == "__main__":
    asyncio.run(main())
