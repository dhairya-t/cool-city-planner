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
  interventions: Intervention[];
}

const HeatMap: React.FC<HeatMapProps> = ({ imageUrl, interventions }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      canvas.width = 600;
      canvas.height = 400;

      if (imageUrl) {
        // Draw the original image if provided
        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, 600, 400);
          drawHeatOverlay(ctx);
        };
        img.src = imageUrl;
      } else {
        // Create a mock urban landscape background
        drawMockBackground(ctx);
        drawHeatOverlay(ctx);
      }
    }
  }, [imageUrl, interventions]);

  const drawMockBackground = (ctx: CanvasRenderingContext2D) => {
    // Create a gradient background representing urban area
    const gradient = ctx.createLinearGradient(0, 0, 600, 400);
    gradient.addColorStop(0, "#2c3e50");
    gradient.addColorStop(0.5, "#34495e");
    gradient.addColorStop(1, "#2c3e50");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 600, 400);

    // Draw some mock buildings
    ctx.fillStyle = "#34495e";
    ctx.fillRect(50, 200, 80, 150);
    ctx.fillRect(200, 150, 100, 200);
    ctx.fillRect(400, 180, 120, 170);
    ctx.fillRect(150, 300, 90, 100);

    // Draw roads
    ctx.fillStyle = "#7f8c8d";
    ctx.fillRect(0, 250, 600, 20);
    ctx.fillRect(300, 0, 20, 400);
  };

  const drawHeatOverlay = (ctx: CanvasRenderingContext2D) => {
    // Add heat overlay (simulated heat islands)
    ctx.globalAlpha = 0.4;

    // Hot spots (red areas) - urban heat islands
    const hotSpots = [
      { x: 200, y: 150, intensity: 0.8 },
      { x: 400, y: 200, intensity: 0.7 },
      { x: 150, y: 300, intensity: 0.6 },
      { x: 450, y: 100, intensity: 0.5 },
    ];

    hotSpots.forEach((spot) => {
      const gradient = ctx.createRadialGradient(
        spot.x,
        spot.y,
        0,
        spot.x,
        spot.y,
        60
      );
      gradient.addColorStop(0, `rgba(255, 0, 0, ${spot.intensity})`);
      gradient.addColorStop(1, "rgba(255, 0, 0, 0)");
      ctx.fillStyle = gradient;
      ctx.fillRect(spot.x - 60, spot.y - 60, 120, 120);
    });

    // Cool spots (blue/green areas) - parks, water bodies
    const coolSpots = [
      { x: 100, y: 100, intensity: 0.5 },
      { x: 500, y: 300, intensity: 0.6 },
      { x: 50, y: 350, intensity: 0.4 },
    ];

    coolSpots.forEach((spot) => {
      const gradient = ctx.createRadialGradient(
        spot.x,
        spot.y,
        0,
        spot.x,
        spot.y,
        50
      );
      gradient.addColorStop(0, `rgba(0, 255, 0, ${spot.intensity})`);
      gradient.addColorStop(1, "rgba(0, 255, 0, 0)");
      ctx.fillStyle = gradient;
      ctx.fillRect(spot.x - 50, spot.y - 50, 100, 100);
    });

    ctx.globalAlpha = 1.0;
  };

  const getInterventionIcon = (type: string) => {
    switch (type) {
      case "tree":
        return (
          <div className="h-4 w-4 bg-green-600 rounded-full flex items-center justify-center text-white text-xs">
            🌲
          </div>
        );
      case "green_roof":
        return (
          <div className="h-4 w-4 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs">
            🏠
          </div>
        );
      case "water_feature":
        return (
          <div className="h-4 w-4 bg-blue-400 rounded-full flex items-center justify-center text-white text-xs">
            💧
          </div>
        );
      default:
        return (
          <div className="h-4 w-4 bg-gray-600 rounded-full flex items-center justify-center text-white text-xs">
            📍
          </div>
        );
    }
  };

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
                {getInterventionIcon(intervention.type)}
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
          <div className="h-4 w-4 bg-green-600 rounded-full flex items-center justify-center text-white text-xs">
            🌲
          </div>
          <span className="text-sm">Tree Placement</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs">
            🏠
          </div>
          <span className="text-sm">Green Roofs</span>
        </div>
      </div>
    </div>
  );
};

export default HeatMap;
