import React, { useState } from "react";
import HeatMap from "./components/HeatMap";
import RecommendationPanel from "./components/RecommendationPanel";
import AnalysisResults from "./components/AnalysisResults";
import DetailedAnalysis from "./components/DetailedAnalysis";
import GoogleMapSelector from "./components/GoogleMapSelector";
import "./App.css";

// Define types for the API response

interface ApiResponse {
  status: string;
  image: string;
  heatmap: string;
  vellum_analysis: any[];
  building_coverage: number;
  vegetation_coverage: number;
}

function App() {
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number;
    lng: number;
    zoom: number;
  } | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisData, setAnalysisData] = useState<ApiResponse | null>(null);

  const handleLocationSelect = (coordinates: { lat: number; lng: number }) => {
    setSelectedLocation({
      ...coordinates,
      zoom: 13,
    });
    setAnalysisComplete(false);
  };

  const runAnalysis = async () => {
    if (!selectedLocation) return;

    setIsAnalyzing(true);

    try {
      // Make API call to backendz
      const response = await fetch("https://urban.midnightsky.net/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Headers": "*",
        },
        body: JSON.stringify({
          latitude: selectedLocation.lat,
          longitude: selectedLocation.lng,
          analysis_radius: 0.005,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const apiResponse: ApiResponse = await response.json();
      setAnalysisData(apiResponse);
      setIsAnalyzing(false);
      setAnalysisComplete(true);
    } catch (error) {
      console.error("Error during analysis:", error);
      setIsAnalyzing(false);
      setAnalysisComplete(false);
      // Show error to user instead of using fallback data
      alert("Failed to connect to analysis service. Please try again.");
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
              UrbanTherm
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
                        OpenAI Intelligence Synthesis
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

            {/* Transform API data for AnalysisResults component */}
            {(() => {
              const hotspotAnalysis = analysisData.vellum_analysis.find(
                (analysis) => analysis.name === "hotspot_analysis"
              );

              const analysisMetrics = {
                vegetation_coverage: Math.round(
                  analysisData.vegetation_coverage * 100
                ),
                building_coverage: Math.round(
                  analysisData.building_coverage * 100
                ),
              };

              // Transform recommendations data
              const recommendationsData = analysisData.vellum_analysis.find(
                (analysis) => analysis.name === "recommendations"
              );

              const transformedRecommendations = [
                ...(recommendationsData?.value?.immediate_actions?.map(
                  (action: any, index: number) => ({
                    type: "Immediate Action",
                    title: action.action,
                    impact: action.temperature_impact,
                    cost: action.cost_range,
                    timeline: action.timeline,
                  })
                ) || []),
                ...(recommendationsData?.value?.short_term_projects?.map(
                  (project: any, index: number) => ({
                    type: "Short-term Project",
                    title: project.project,
                    impact: project.cooling_impact,
                    cost: project.cost_estimate,
                    timeline: project.timeline,
                  })
                ) || []),
                ...(recommendationsData?.value?.long_term_strategies?.map(
                  (strategy: any, index: number) => ({
                    type: "Long-term Strategy",
                    title: strategy.strategy,
                    impact: strategy.temperature_impact,
                    cost: strategy.investment,
                    timeline: strategy.timeline,
                  })
                ) || []),
              ];

              // Create interventions from hotspot analysis
              const interventions = [
                ...(hotspotAnalysis?.value?.hot_zones?.map(
                  (zone: any, index: number) => ({
                    id: zone.id,
                    lat: selectedLocation!.lat + (Math.random() - 0.5) * 0.01,
                    lng: selectedLocation!.lng + (Math.random() - 0.5) * 0.01,
                    type: "hot_zone",
                    impact:
                      zone.intensity === "extreme"
                        ? 4
                        : zone.intensity === "high"
                        ? 3
                        : 2,
                  })
                ) || []),
                ...(hotspotAnalysis?.value?.cool_zones?.map(
                  (zone: any, index: number) => ({
                    id: `cool_${zone.id}`,
                    lat: selectedLocation!.lat + (Math.random() - 0.5) * 0.01,
                    lng: selectedLocation!.lng + (Math.random() - 0.5) * 0.01,
                    type: "cool_zone",
                    impact: zone.cooling_intensity === "high" ? -3 : -2,
                  })
                ) || []),
              ];

              return (
                <>
                  <AnalysisResults data={analysisMetrics} />

                  <div className="grid lg:grid-cols-2 gap-6">
                    <HeatMap
                      imageUrl={analysisData.image}
                      heatmapUrl={analysisData.heatmap}
                      interventions={interventions}
                    />
                    <RecommendationPanel
                      recommendations={transformedRecommendations}
                    />
                  </div>

                  <div className="grid lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg shadow-lg p-6">
                      <h3 className="text-lg font-semibold mb-4">
                        Analysis Summary
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Analysis Status:
                          </span>
                          <span className="text-sm font-medium text-green-600">
                            {analysisData.status}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Satellite Image:
                          </span>
                          <span className="text-sm font-medium">
                            {analysisData.image ? "Available" : "Not available"}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Heat Map:
                          </span>
                          <span className="text-sm font-medium">
                            {analysisData.heatmap
                              ? "Available"
                              : "Not available"}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Analysis Components:
                          </span>
                          <span className="text-sm font-medium">
                            {analysisData.vellum_analysis.length}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <DetailedAnalysis
                    vellumAnalysis={analysisData.vellum_analysis}
                  />
                </>
              );
            })()}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
