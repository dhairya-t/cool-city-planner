import React, { useEffect, useRef } from "react";

interface Intervention {
  id: number;
  lat: number;
  lng: number;
  type: string;
  impact: number;
}

interface HeatMapProps {
  imageUrl: string | null;
  heatmapUrl?: string | null;
  interventions: Intervention[];
}

const HeatMap: React.FC<HeatMapProps> = ({
  imageUrl,
  heatmapUrl,
  interventions,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      canvas.width = 512;
      canvas.height = 512;

      if (imageUrl) {
        // Draw the original image if provided
        const img = new Image();
        img.onload = () => {
          ctx.globalAlpha = 1.0;
          ctx.drawImage(img, 0, 0, 512, 512);

          // Only load heatmap after satellite image is loaded
          if (heatmapUrl) {
            const heatmap_img = new Image();
            heatmap_img.onload = () => {
              ctx.globalAlpha = 0.1;
              ctx.drawImage(heatmap_img, 0, 0, 512, 512);
              ctx.globalAlpha = 1.0; // Reset alpha
            };
            heatmap_img.onerror = () => {
              console.warn("Failed to load heatmap image");
            };
            heatmap_img.src = heatmapUrl;
          }
        };
        img.onerror = () => {
          console.warn("Failed to load satellite image");
        };
        img.src = imageUrl;
      }
    }
  }, [imageUrl, heatmapUrl, interventions]);

  // Convert lat/lng to pixel coordinates for interventions
  const getInterventionPosition = (intervention: Intervention) => {
    // Simple mapping - in a real app, you'd use proper coordinate transformation
    const x = ((intervention.lng + 180) / 360) * 600;
    const y = ((90 - intervention.lat) / 180) * 400;
    return {
      x: Math.max(0, Math.min(600, x)),
      y: Math.max(0, Math.min(400, y)),
    };
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Heat Map Analysis</h3>

      <div className="relative">
        <canvas
          ref={canvasRef}
          className="w-full h-auto rounded-lg border"
          style={{ maxHeight: "400px" }}
        />

        {/* Intervention markers overlay */}
        <div className="absolute inset-0">
          {interventions.map((intervention) => {
            const position = getInterventionPosition(intervention);
            return (
              <div
                key={intervention.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-full p-2 shadow-lg border-2 border-gray-200 cursor-pointer hover:scale-110 transition-transform"
                style={{
                  left: `${(position.x / 600) * 100}%`,
                  top: `${(position.y / 400) * 100}%`,
                }}
                title={`${intervention.type}: ${intervention.impact}°C impact`}
              >
                {/* {getInterventionIcon(intervention.type)} */}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-red-500 rounded opacity-60"></div>
          <span className="text-sm">High Heat Areas</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded opacity-60"></div>
          <span className="text-sm">Cooling Zones</span>
        </div>

        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-blue-500 rounded opacity-60"></div>
          <span className="text-sm">Cool Zones</span>
        </div>
      </div>
    </div>
  );
};

export default HeatMap;
