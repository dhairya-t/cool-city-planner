import React from 'react';
import { Thermometer, TreePine, Building, Activity } from 'lucide-react';

const AnalysisResults = ({ data }) => {
  const metrics = [
    {
      icon: <Thermometer className="h-6 w-6 text-red-500" />,
      label: 'Heat Island Intensity',
      value: `${data.heatIslandIntensity}°C`,
      description: 'Above rural baseline',
      color: 'red'
    },
    {
      icon: <TreePine className="h-6 w-6 text-green-500" />,
      label: 'Vegetation Coverage',
      value: `${data.vegetationCoverage}%`,
      description: 'Current green space',
      color: 'green'
    },
    {
      icon: <Building className="h-6 w-6 text-blue-500" />,
      label: 'Building Density',
      value: `${data.buildingDensity}%`,
      description: 'Urban development',
      color: 'blue'
    },
    {
      icon: <Activity className="h-6 w-6 text-orange-500" />,
      label: 'Surface Temperature',
      value: `${data.surfaceTemperature}°C`,
      description: 'Current average',
      color: 'orange'
    }
  ];

  const getStatusColor = (metric) => {
    switch (metric.label) {
      case 'Heat Island Intensity':
        return parseFloat(metric.value) > 3 ? 'text-red-600 bg-red-50' : 'text-yellow-600 bg-yellow-50';
      case 'Vegetation Coverage':
        return parseFloat(metric.value) < 30 ? 'text-red-600 bg-red-50' : 'text-green-600 bg-green-50';
      case 'Building Density':
        return parseFloat(metric.value) > 60 ? 'text-orange-600 bg-orange-50' : 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              {metric.icon}
              <div>
                <h3 className="font-medium text-gray-900 text-sm">{metric.label}</h3>
                <p className="text-xs text-gray-500 mt-1">{metric.description}</p>
              </div>
            </div>
          </div>
          
          <div className="mt-3">
            <div className={`inline-flex items-center px-2.5 py-1.5 rounded-full text-sm font-medium ${getStatusColor(metric)}`}>
              {metric.value}
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  metric.color === 'red' ? 'bg-red-500' :
                  metric.color === 'green' ? 'bg-green-500' :
                  metric.color === 'blue' ? 'bg-blue-500' :
                  'bg-orange-500'
                }`}
                style={{
                  width: `${
                    metric.label === 'Heat Island Intensity' ? Math.min(parseFloat(metric.value) * 25, 100) :
                    metric.label === 'Surface Temperature' ? Math.min(parseFloat(metric.value) * 2, 100) :
                    parseFloat(metric.value)
                  }%`
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
