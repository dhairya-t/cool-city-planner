import React, { useState } from "react";

interface VellumAnalysis {
  id: string;
  name: string;
  value: any;
  type: string;
}

interface DetailedAnalysisProps {
  vellumAnalysis: VellumAnalysis[];
}

const DetailedAnalysis: React.FC<DetailedAnalysisProps> = ({
  vellumAnalysis,
}) => {
  const [activeTab, setActiveTab] = useState("hotspots");

  const hotspotAnalysis = vellumAnalysis.find(
    (analysis) => analysis.name === "hotspot_analysis"
  );
  const vegetationInsights = vellumAnalysis.find(
    (analysis) => analysis.name === "vegetation_insights"
  );
  const urbanCorrelations = vellumAnalysis.find(
    (analysis) => analysis.name === "urban_correlations"
  );

  const tabs = [
    { id: "hotspots", name: "Hotspot Analysis", icon: "🔥" },
    { id: "vegetation", name: "Vegetation Insights", icon: "🌲" },
    { id: "urban", name: "Urban Correlations", icon: "🏢" },
  ];

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case "extreme":
        return "bg-red-600 text-white";
      case "high":
        return "bg-orange-500 text-white";
      case "medium":
        return "bg-yellow-500 text-white";
      default:
        return "bg-gray-500 text-white";
    }
  };

  const getCoolingColor = (intensity: string) => {
    switch (intensity) {
      case "high":
        return "bg-blue-600 text-white";
      case "medium":
        return "bg-green-500 text-white";
      default:
        return "bg-gray-500 text-white";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Detailed Analysis</h3>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.name}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === "hotspots" && hotspotAnalysis && (
          <div className="space-y-6">
            {/* Thermal Overview */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">
                Thermal Overview
              </h4>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-red-600">
                    {hotspotAnalysis.value.thermal_overview.hotspot_count}
                  </div>
                  <div className="text-sm text-gray-600">Hot Spots</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {hotspotAnalysis.value.thermal_overview.coolspot_count}
                  </div>
                  <div className="text-sm text-gray-600">Cool Spots</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-orange-600">
                    {hotspotAnalysis.value.urban_heat_island_assessment
                      .severity === "high"
                      ? "High"
                      : "Moderate"}
                  </div>
                  <div className="text-sm text-gray-600">
                    Heat Island Severity
                  </div>
                </div>
              </div>
              <p className="text-sm text-blue-800 mt-3">
                {
                  hotspotAnalysis.value.thermal_overview
                    .dominant_temperature_pattern
                }
              </p>
            </div>

            {/* Hot Zones */}
            <div>
              <h4 className="font-medium mb-3">Hot Zones</h4>
              <div className="space-y-3">
                {hotspotAnalysis.value.hot_zones.map((zone: any) => (
                  <div
                    key={zone.id}
                    className="border border-red-200 rounded-lg p-3 bg-red-50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-red-900">
                        {zone.location}
                      </h5>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getIntensityColor(
                          zone.intensity
                        )}`}
                      >
                        {zone.intensity}
                      </span>
                    </div>
                    <p className="text-sm text-red-800 mb-2">
                      {zone.description}
                    </p>
                    <div className="text-xs text-red-700">
                      <strong>Cause:</strong> {zone.likely_urban_cause}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cool Zones */}
            <div>
              <h4 className="font-medium mb-3">Cool Zones</h4>
              <div className="space-y-3">
                {hotspotAnalysis.value.cool_zones.map((zone: any) => (
                  <div
                    key={zone.id}
                    className="border border-blue-200 rounded-lg p-3 bg-blue-50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-blue-900">
                        {zone.location}
                      </h5>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getCoolingColor(
                          zone.cooling_intensity
                        )}`}
                      >
                        {zone.cooling_intensity}
                      </span>
                    </div>
                    <p className="text-sm text-blue-800 mb-2">
                      {zone.description}
                    </p>
                    <div className="text-xs text-blue-700">
                      <strong>Source:</strong> {zone.likely_cooling_source}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "vegetation" && vegetationInsights && (
          <div className="space-y-6">
            {/* Existing Vegetation */}
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-medium text-green-900 mb-3">
                Existing Vegetation
              </h4>
              <p className="text-sm text-green-800 mb-3">
                {vegetationInsights.value.existing_vegetation.overall_coverage}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-green-900 mb-2">
                    Tree Coverage
                  </h5>
                  {vegetationInsights.value.existing_vegetation.tree_coverage.map(
                    (tree: any, index: number) => (
                      <div key={index} className="bg-white p-2 rounded mb-2">
                        <div className="text-sm font-medium">
                          {tree.location}
                        </div>
                        <div className="text-xs text-gray-600">
                          {tree.density} density, {tree.coverage_area} area
                        </div>
                      </div>
                    )
                  )}
                </div>

                <div>
                  <h5 className="font-medium text-green-900 mb-2">
                    Parks & Green Spaces
                  </h5>
                  {vegetationInsights.value.existing_vegetation.parks_green_spaces.map(
                    (park: any, index: number) => (
                      <div key={index} className="bg-white p-2 rounded mb-2">
                        <div className="text-sm font-medium">
                          {park.location}
                        </div>
                        <div className="text-xs text-gray-600">
                          {park.size} size, {park.vegetation_quality} quality
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>

            {/* Vegetation Gaps */}
            <div>
              <h4 className="font-medium mb-3">Vegetation Gaps</h4>
              <div className="space-y-3">
                {vegetationInsights.value.vegetation_gaps.map(
                  (gap: any, index: number) => (
                    <div
                      key={index}
                      className="border border-orange-200 rounded-lg p-3 bg-orange-50"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-medium text-orange-900">
                          {gap.location}
                        </h5>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-500 text-white">
                          {gap.gap_type}
                        </span>
                      </div>
                      <div className="text-sm text-orange-800">
                        <strong>Development:</strong> {gap.development_type}
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Green Opportunities */}
            <div>
              <h4 className="font-medium mb-3">Green Opportunities</h4>
              <div className="space-y-3">
                {vegetationInsights.value.green_opportunities.map(
                  (opportunity: any, index: number) => (
                    <div
                      key={index}
                      className="border border-green-200 rounded-lg p-3 bg-green-50"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-medium text-green-900">
                          {opportunity.location}
                        </h5>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-500 text-white">
                          {opportunity.intervention_type}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm text-green-800">
                        <div>
                          <strong>Feasibility:</strong>{" "}
                          {opportunity.feasibility}
                        </div>
                        <div>
                          <strong>Impact:</strong>{" "}
                          {opportunity.potential_impact}
                        </div>
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "urban" && urbanCorrelations && (
          <div className="space-y-6">
            {/* Urban Heat Sources */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">
                Urban Heat Sources
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {urbanCorrelations.value.urban_heat_sources.map(
                  (source: string, index: number) => (
                    <div
                      key={index}
                      className="bg-white p-2 rounded text-sm text-center"
                    >
                      {source.replace("_", " ")}
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Building Analysis */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-3">
                Building Analysis
              </h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-blue-800">
                    <strong>Density:</strong>{" "}
                    {urbanCorrelations.value.building_analysis.density}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-blue-800">
                    <strong>Materials:</strong>{" "}
                    {urbanCorrelations.value.building_analysis.materials.join(
                      ", "
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Heat Correlations */}
            <div>
              <h4 className="font-medium mb-3">Heat Correlations</h4>
              <div className="space-y-3">
                {urbanCorrelations.value.heat_correlations.map(
                  (correlation: string, index: number) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-3 bg-gray-50"
                    >
                      <p className="text-sm text-gray-800">{correlation}</p>
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Infrastructure Impact */}
            <div className="bg-red-50 p-4 rounded-lg">
              <h4 className="font-medium text-red-900 mb-2">
                Infrastructure Impact
              </h4>
              <p className="text-sm text-red-800">
                {urbanCorrelations.value.infrastructure_impact}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetailedAnalysis;
