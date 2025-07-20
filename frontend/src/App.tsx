import React, { useState } from "react";
import HeatMap from "./components/HeatMap";
import RecommendationPanel from "./components/RecommendationPanel";
import AnalysisResults from "./components/AnalysisResults";
import GoogleMapSelector from "./components/GoogleMapSelector";
import {
  analyzeLocation,
  checkServerHealth,
  APIError,
  LocationAnalysisRequest,
  AnalysisResult,
} from "./api/analyze";
import "./App.css";

function App() {
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number;
    lng: number;
    zoom: number;
  } | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);

  const handleLocationSelect = (
    coordinates: { lat: number; lng: number },
    zoom: number = 13
  ) => {
    setSelectedLocation({
      ...coordinates,
      zoom,
    });
    setAnalysisComplete(false);
  };

  const runAnalysis = async () => {
    if (!selectedLocation) return;

    setIsAnalyzing(true);

    try {
      // Check server health first
      const isHealthy = await checkServerHealth();
      if (!isHealthy) {
        throw new APIError(
          "Analysis server is not responding. Please ensure the FastAPI server is running.",
          503
        );
      }

      // Prepare the analysis request
      const request: LocationAnalysisRequest = {
        latitude: selectedLocation.lat,
        longitude: selectedLocation.lng,
        zoom: selectedLocation.zoom,
        location_name: "Selected Location",
      };

      // Call the FastAPI endpoint
      const result: AnalysisResult = await analyzeLocation(request);

      setAnalysisData(result);
      setAnalysisComplete(true);
    } catch (error) {
      console.error("Analysis failed:", error);

      // Handle different types of errors
      if (error instanceof APIError) {
        alert(`Analysis Error: ${error.message}`);
      } else {
        alert(
          "An unexpected error occurred during analysis. Please try again."
        );
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedLocation(null);
    setAnalysisComplete(false);
    setAnalysisData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b-2 border-green-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold">
              🌡️
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              CoolCity Planner
            </h1>
            <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
              AI-Powered Urban Climate Analysis
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!selectedLocation && (
          <div className="text-center">
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
                <div className="h-16 w-16 bg-green-500 rounded-full flex items-center justify-center text-white text-2xl mx-auto mb-4">
                  📍
                </div>
                <h2 className="text-2xl font-semibold mb-4">
                  Select Urban Area for Analysis
                </h2>
                <p className="text-gray-600 mb-6">
                  Click on the map below to select a location for AI-powered
                  climate analysis
                </p>

                <div className="mb-6">
                  <GoogleMapSelector onLocationSelect={handleLocationSelect} />
                </div>

                <p className="text-sm text-gray-500">
                  💡 Tip: Use satellite view to better identify urban areas and
                  buildings
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center text-white mx-auto mb-2">
                    📍
                  </div>
                  <p className="text-sm font-medium">Urban Mapping</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="h-8 w-8 bg-red-500 rounded-full flex items-center justify-center text-white mx-auto mb-2">
                    🌡️
                  </div>
                  <p className="text-sm font-medium">Heat Analysis</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="h-8 w-8 bg-green-500 rounded-full flex items-center justify-center text-white mx-auto mb-2">
                    🌲
                  </div>
                  <p className="text-sm font-medium">Green Solutions</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="h-8 w-8 bg-purple-500 rounded-full flex items-center justify-center text-white mx-auto mb-2">
                    📄
                  </div>
                  <p className="text-sm font-medium">Policy Reports</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedLocation && !analysisComplete && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Location Analysis</h2>
                <button
                  onClick={resetAnalysis}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Select Different Location
                </button>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="mb-4">
                    <h3 className="text-lg font-medium mb-2">
                      Selected Coordinates
                    </h3>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Latitude:</span>{" "}
                        {selectedLocation.lat.toFixed(6)}
                      </p>
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Longitude:</span>{" "}
                        {selectedLocation.lng.toFixed(6)}
                      </p>
                    </div>
                  </div>

                  <div className="h-64 bg-gray-100 rounded-lg overflow-hidden">
                    {selectedLocation && (
                      <img
                        src={`https://maps.googleapis.com/maps/api/staticmap?center=${selectedLocation.lat},${selectedLocation.lng}&zoom=${selectedLocation.zoom}&size=400x256&maptype=hybrid&markers=color:red%7C${selectedLocation.lat},${selectedLocation.lng}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`}
                        alt="Selected Location Preview"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = "none";
                          target.parentElement!.innerHTML = `
                            <div class="flex items-center justify-center h-full">
                              <div class="text-center">
                                <div class="text-4xl mb-2">📍</div>
                                <p class="text-gray-600">Location Preview</p>
                                <p class="text-xs text-gray-400 mt-1">Map preview unavailable</p>
                              </div>
                            </div>
                          `;
                        }}
                      />
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-medium">AI Analysis Pipeline</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <div className="h-5 w-5 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs">
                        ⚡
                      </div>
                      <span className="text-sm">
                        Google Maps Satellite Data
                      </span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="h-5 w-5 bg-purple-500 rounded-full flex items-center justify-center text-white text-xs">
                        ⚡
                      </div>
                      <span className="text-sm">
                        Vellum Multi-Agent Processing
                      </span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="h-5 w-5 bg-green-500 rounded-full flex items-center justify-center text-white text-xs">
                        ⚡
                      </div>
                      <span className="text-sm">
                        Gemini Intelligence Synthesis
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={runAnalysis}
                    disabled={isAnalyzing}
                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
                  >
                    {isAnalyzing ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Analyzing Urban Climate...
                      </span>
                    ) : (
                      "Start AI Analysis"
                    )}
                  </button>

                  <button
                    onClick={resetAnalysis}
                    className="w-full bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 mt-3"
                  >
                    ← Back to Map Selection
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {analysisComplete && analysisData && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Analysis Results
              </h2>
              <button
                onClick={resetAnalysis}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                New Analysis
              </button>
            </div>

            <AnalysisResults data={analysisData} />

            <div className="grid lg:grid-cols-2 gap-6">
              <HeatMap
                imageUrl={null}
                interventions={analysisData.interventions}
              />
              <RecommendationPanel
                recommendations={analysisData.recommendations}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
