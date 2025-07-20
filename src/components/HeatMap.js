import React, { useEffect, useRef } from 'react';
import { MapPin, TreePine, Home, Droplets } from 'lucide-react';

const HeatMap = ({ imageUrl, interventions }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (imageUrl && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        canvas.width = 600;
        canvas.height = 400;
        
        // Draw the original image
        ctx.drawImage(img, 0, 0, 600, 400);
        
        // Add heat overlay (simulated heat islands)
        ctx.globalAlpha = 0.4;
        
        // Hot spots (red areas)
        const hotSpots = [
          { x: 200, y: 150, intensity: 0.8 },
          { x: 400, y: 200, intensity: 0.7 },
          { x: 150, y: 300, intensity: 0.6 }
        ];
        
        hotSpots.forEach(spot => {
          const gradient = ctx.createRadialGradient(spot.x, spot.y, 0, spot.x, spot.y, 60);
          gradient.addColorStop(0, `rgba(255, 0, 0, ${spot.intensity})`);
          gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
          ctx.fillStyle = gradient;
          ctx.fillRect(spot.x - 60, spot.y - 60, 120, 120);
        });
        
        // Cool spots (blue/green areas)
        const coolSpots = [
          { x: 100, y: 100, intensity: 0.5 },
          { x: 500, y: 300, intensity: 0.6 }
        ];
        
        coolSpots.forEach(spot => {
          const gradient = ctx.createRadialGradient(spot.x, spot.y, 0, spot.x, spot.y, 50);
          gradient.addColorStop(0, `rgba(0, 255, 0, ${spot.intensity})`);
          gradient.addColorStop(1, 'rgba(0, 255, 0, 0)');
          ctx.fillStyle = gradient;
          ctx.fillRect(spot.x - 50, spot.y - 50, 100, 100);
        });
        
        ctx.globalAlpha = 1.0;
      };
      
      img.src = imageUrl;
    }
  }, [imageUrl]);

  const getInterventionIcon = (type) => {
    switch (type) {
      case 'tree':
        return <TreePine className="h-4 w-4 text-green-600" />;
      case 'green_roof':
        return <Home className="h-4 w-4 text-blue-600" />;
      case 'water_feature':
        return <Droplets className="h-4 w-4 text-blue-400" />;
      default:
        return <MapPin className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Heat Map Analysis</h3>
      
      <div className="relative">
        <canvas
          ref={canvasRef}
          className="w-full h-auto rounded-lg border"
          style={{ maxHeight: '400px' }}
        />
        
        {/* Intervention markers overlay */}
        <div className="absolute inset-0">
          {interventions.map((intervention, index) => (
            <div
              key={intervention.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-full p-2 shadow-lg border-2 border-gray-200 cursor-pointer hover:scale-110 transition-transform"
              style={{
                left: `${20 + index * 15}%`,
                top: `${30 + index * 10}%`
              }}
              title={`${intervention.type}: ${intervention.impact}°C impact`}
            >
              {getInterventionIcon(intervention.type)}
            </div>
          ))}
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
          <TreePine className="h-4 w-4 text-green-600" />
          <span className="text-sm">Tree Placement</span>
        </div>
        <div className="flex items-center space-x-2">
          <Home className="h-4 w-4 text-blue-600" />
          <span className="text-sm">Green Roofs</span>
        </div>
      </div>
    </div>
  );
};

export default HeatMap;
