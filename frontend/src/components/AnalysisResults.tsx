import React from "react";

interface AnalysisData {
  building_coverage: number;
  vegetation_coverage: number;
}

interface AnalysisResultsProps {
  data: AnalysisData;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data }) => {
  const metrics = [
    {
      icon: (
        <div className="h-6 w-6 bg-green-500 rounded-full flex items-center justify-center text-white text-sm">
          🌲
        </div>
      ),
      label: "Vegetation Coverage",
      value: `${Math.min(data.vegetation_coverage * 10, 100)}%`,
      description: "Current green space",
      progress: Math.min(data.vegetation_coverage * 10, 100),
      color: "bg-green-500",
    },
    {
      icon: (
        <div className="h-6 w-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm">
          🏢
        </div>
      ),
      label: "Building Density",
      value: `${Math.min(data.building_coverage * 10, 100)}%`,
      description: "Urban development",
      progress: Math.min(data.building_coverage * 10, 100),
      color: "bg-blue-500",
    },
  ];

  const getStatusColor = (metric: any) => {
    switch (metric.label) {
      case "Heat Island Intensity":
        return parseFloat(metric.value) > 3
          ? "text-red-600 bg-red-50"
          : "text-yellow-600 bg-yellow-50";
      case "Vegetation Coverage":
        return parseFloat(metric.value) < 30
          ? "text-red-600 bg-red-50"
          : "text-green-600 bg-green-50";
      case "Building Density":
        return parseFloat(metric.value) > 60
          ? "text-orange-600 bg-orange-50"
          : "text-blue-600 bg-blue-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <div className="flex flex-row justify-center gap-12 mb-6">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex flex-row justify-between">
            <div className="flex items-center space-x-3">
              {metric.icon}
              <div>
                <h3 className="font-medium text-gray-900 text-sm">
                  {metric.label}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {metric.description}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-3">
            <div
              className={`inline-flex items-center px-2.5 py-1.5 rounded-full text-sm font-medium ${getStatusColor(
                metric
              )}`}
            >
              {metric.value}
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${metric.color}`}
                style={{
                  width: `${Math.min(metric.progress, 100)}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AnalysisResults;
