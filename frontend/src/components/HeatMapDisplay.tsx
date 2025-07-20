import React from "react";

interface HeatMapDisplayProps {
  heatmapUrl: string | null;
}

const HeatMapDisplay: React.FC<HeatMapDisplayProps> = ({ heatmapUrl }) => {
  if (!heatmapUrl) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Heat Map</h3>
        <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-500">
            <div className="text-4xl mb-2">🌡️</div>
            <p>Heat map not available</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Thermal Heat Map</h3>
      <div className="relative">
        <img
          src={heatmapUrl}
          alt="Thermal heat map"
          className="w-full h-auto rounded-lg border"
          style={{ maxHeight: "400px" }}
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = "none";
            target.parentElement!.innerHTML = `
              <div class="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
                <div class="text-center text-gray-500">
                  <div class="text-4xl mb-2">🌡️</div>
                  <p>Heat map unavailable</p>
                </div>
              </div>
            `;
          }}
        />
      </div>

      {/* Heat map legend */}
      <div className="mt-4">
        <h4 className="font-medium mb-2">Temperature Legend</h4>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded"></div>
            <span>Cool</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span>Moderate</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span>Warm</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span>Hot</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeatMapDisplay;
