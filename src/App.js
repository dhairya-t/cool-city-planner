import React, { useState, useRef } from 'react';
import { Upload, MapPin, Thermometer, TreePine, FileText, Zap } from 'lucide-react';
import HeatMap from './components/HeatMap';
import RecommendationPanel from './components/RecommendationPanel';
import AnalysisResults from './components/AnalysisResults';
import './App.css';

function App() {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target.result);
        setAnalysisComplete(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate AI analysis process
    setTimeout(() => {
      const mockData = {
        heatIslandIntensity: 3.2,
        vegetationCoverage: 23.5,
        buildingDensity: 67.8,
        surfaceTemperature: 28.7,
        recommendations: [
          {
            type: 'Green Infrastructure',
            title: 'Plant 150 Trees Along Main Corridor',
            impact: '2.3°C temperature reduction',
            cost: '$45,000',
            timeline: '6 months'
          },
          {
            type: 'Building Modifications',
            title: 'Convert 5 Rooftops to Green Roofs',
            impact: '1.8°C local cooling',
            cost: '$120,000',
            timeline: '12 months'
          },
          {
            type: 'Urban Design',
            title: 'Create Cooling Corridors with Water Features',
            impact: '3.1°C corridor cooling',
            cost: '$200,000',
            timeline: '18 months'
          }
        ],
        interventions: [
          { id: 1, lat: 40.7128, lng: -74.0060, type: 'tree', impact: 2.3 },
          { id: 2, lat: 40.7130, lng: -74.0058, type: 'green_roof', impact: 1.8 },
          { id: 3, lat: 40.7125, lng: -74.0062, type: 'water_feature', impact: 3.1 }
        ]
      };
      
      setAnalysisData(mockData);
      setIsAnalyzing(false);
      setAnalysisComplete(true);
    }, 3000);
  };

  const resetAnalysis = () => {
    setUploadedImage(null);
    setAnalysisComplete(false);
    setAnalysisData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b-2 border-green-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <Thermometer className="h-8 w-8 text-green-600" />
            <h1 className="text-3xl font-bold text-gray-900">CoolCity Planner</h1>
            <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
              AI-Powered Urban Climate Analysis
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!uploadedImage && (
          <div className="text-center">
            <div className="max-w-md mx-auto">
              <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
                <Upload className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold mb-4">Upload Satellite Imagery</h2>
                <p className="text-gray-600 mb-6">
                  Upload satellite or drone footage of your target urban area to begin AI-powered climate analysis
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
                >
                  Choose Image
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-white p-4 rounded-lg shadow">
                  <MapPin className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                  <p className="text-sm font-medium">Urban Mapping</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <Thermometer className="h-8 w-8 text-red-500 mx-auto mb-2" />
                  <p className="text-sm font-medium">Heat Analysis</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <TreePine className="h-8 w-8 text-green-500 mx-auto mb-2" />
                  <p className="text-sm font-medium">Green Solutions</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <FileText className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                  <p className="text-sm font-medium">Policy Reports</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {uploadedImage && !analysisComplete && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Satellite Image Analysis</h2>
                <button
                  onClick={resetAnalysis}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Upload Different Image
                </button>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <img
                    src={uploadedImage}
                    alt="Uploaded satellite imagery"
                    className="w-full h-64 object-cover rounded-lg"
                  />
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">AI Analysis Pipeline</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <Zap className="h-5 w-5 text-blue-500" />
                      <span className="text-sm">TwelveLabs Video Understanding</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Zap className="h-5 w-5 text-purple-500" />
                      <span className="text-sm">Vellum Multi-Agent Processing</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Zap className="h-5 w-5 text-green-500" />
                      <span className="text-sm">OpenAI Intelligence Synthesis</span>
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
                      'Start AI Analysis'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {analysisComplete && analysisData && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
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
                imageUrl={uploadedImage} 
                interventions={analysisData.interventions}
              />
              <RecommendationPanel recommendations={analysisData.recommendations} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
