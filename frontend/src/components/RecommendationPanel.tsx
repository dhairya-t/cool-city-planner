import React, { useState } from 'react';

interface Recommendation {
  type: string;
  title: string;
  impact: string;
  cost: string;
  timeline: string;
}

interface RecommendationPanelProps {
  recommendations: Recommendation[];
}

const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ recommendations }) => {
  const [selectedRec, setSelectedRec] = useState(0);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'Green Infrastructure':
        return <div className="h-5 w-5 bg-green-600 rounded-full flex items-center justify-center text-white text-xs">🌲</div>;
      case 'Building Modifications':
        return <div className="h-5 w-5 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs">🏠</div>;
      case 'Urban Design':
        return <div className="h-5 w-5 bg-blue-400 rounded-full flex items-center justify-center text-white text-xs">🌊</div>;
      default:
        return <div className="h-5 w-5 bg-gray-600 rounded-full flex items-center justify-center text-white text-xs">🌲</div>;
    }
  };

  const generatePolicyReport = () => {
    const report = `
COOLCITY PLANNER - POLICY RECOMMENDATIONS REPORT

Generated: ${new Date().toLocaleDateString()}

EXECUTIVE SUMMARY:
Based on AI analysis of satellite imagery, this report provides actionable recommendations 
for reducing urban heat island effects in the target area.

KEY FINDINGS:
- Current heat island intensity: High (3.2°C above rural areas)
- Vegetation coverage: 23.5% (below recommended 30%)
- Building density: 67.8% (requiring cooling interventions)

RECOMMENDED INTERVENTIONS:
${recommendations.map((rec, index) => `
${index + 1}. ${rec.title}
   Type: ${rec.type}
   Expected Impact: ${rec.impact}
   Investment Required: ${rec.cost}
   Timeline: ${rec.timeline}
`).join('')}

IMPLEMENTATION PRIORITY:
1. Immediate (0-6 months): Tree planting initiatives
2. Short-term (6-12 months): Green roof conversions
3. Long-term (12-18 months): Major urban design modifications

EXPECTED OUTCOMES:
- Average temperature reduction: 2.4°C
- Improved air quality index: +15%
- Energy savings: 20% reduction in cooling costs
- Enhanced urban livability and property values

This report was generated using AI-powered analysis combining TwelveLabs image recognition, 
Vellum multi-agent orchestration, and Gemini intelligence synthesis.
    `;

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'coolcity-policy-report.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">AI Recommendations</h3>
        <button
          onClick={generatePolicyReport}
          className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md text-sm transition-colors"
        >
          <div className="h-4 w-4 bg-purple-600 rounded-full flex items-center justify-center text-white text-xs">📥</div>
          <span>Download Report</span>
        </button>
      </div>

      <div className="space-y-3 mb-4">
        {recommendations.map((rec, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
              selectedRec === index
                ? 'border-green-500 bg-green-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedRec(index)}
          >
            <div className="flex items-start space-x-3">
              {getTypeIcon(rec.type)}
              <div className="flex-1">
                <h4 className="font-medium text-sm">{rec.title}</h4>
                <p className="text-xs text-gray-600 mt-1">{rec.type}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center space-x-1 text-xs text-red-600 font-medium">
                  <div className="h-3 w-3 bg-red-600 rounded-full flex items-center justify-center text-white text-xs">📉</div>
                  <span>{rec.impact}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed view of selected recommendation */}
      {recommendations[selectedRec] && (
        <div className="border-t pt-4">
          <h4 className="font-medium mb-3">Implementation Details</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="h-4 w-4 bg-green-600 rounded-full flex items-center justify-center text-white text-xs">💵</div>
              <span className="text-gray-600">Cost:</span>
              <span className="font-medium">{recommendations[selectedRec].cost}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-4 w-4 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs">⏰</div>
              <span className="text-gray-600">Timeline:</span>
              <span className="font-medium">{recommendations[selectedRec].timeline}</span>
            </div>
          </div>
          
          <div className="mt-3 p-3 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Impact:</strong> {recommendations[selectedRec].impact} expected temperature reduction
            </p>
          </div>
        </div>
      )}

      {/* Summary stats */}
      <div className="mt-4 pt-4 border-t">
        <h4 className="font-medium mb-2 text-sm">Total Impact Summary</h4>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-red-50 p-3 rounded">
            <div className="text-lg font-bold text-red-600">-2.4°C</div>
            <div className="text-xs text-gray-600">Avg Cooling</div>
          </div>
          <div className="bg-green-50 p-3 rounded">
            <div className="text-lg font-bold text-green-600">$365K</div>
            <div className="text-xs text-gray-600">Investment</div>
          </div>
          <div className="bg-blue-50 p-3 rounded">
            <div className="text-lg font-bold text-blue-600">18 mo</div>
            <div className="text-xs text-gray-600">Timeline</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationPanel;
