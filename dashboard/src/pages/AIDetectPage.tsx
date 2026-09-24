import React from 'react';
import { Bot, Upload, RefreshCw, Layers } from 'lucide-react';
import { useSite } from '../context/SiteContext';

const AIDetectPage: React.FC = () => {
  const { selectedSiteId } = useSite();

  if (!selectedSiteId) return null;

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl shadow-sm text-white p-8 relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-white/20 text-white text-xs font-bold uppercase tracking-wide mb-4">
            <Bot className="w-4 h-4 mr-2" /> Beta Feature
          </div>
          <h1 className="text-3xl font-bold mb-4">AI Visual Change Detection</h1>
          <p className="text-indigo-100 text-lg mb-6">
            Automatically analyze structural changes, missing components, or safety hazards between two different capture sessions using our advanced AI engine.
          </p>
          <div className="inline-block bg-white/10 backdrop-blur border border-white/20 rounded-lg px-4 py-2 font-medium">
            Coming Soon: Q4 Release
          </div>
        </div>
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-white/5 skew-x-12 transform origin-top translate-x-12" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 opacity-60 pointer-events-none grayscale">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-gray-100 text-gray-400 rounded-full flex items-center justify-center mb-4">
            <Upload className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">1. Select Captures</h3>
          <p className="text-gray-500 text-sm">Choose a baseline capture and a recent capture to compare.</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-indigo-50 text-indigo-400 rounded-full flex items-center justify-center mb-4">
            <RefreshCw className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">2. Run AI Analysis</h3>
          <p className="text-gray-500 text-sm">Our neural network analyzes the differences in 3D space.</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-purple-50 text-purple-400 rounded-full flex items-center justify-center mb-4">
            <Layers className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">3. Review Annotations</h3>
          <p className="text-gray-500 text-sm">View auto-generated bounding boxes for deviations and missing items.</p>
        </div>
      </div>
    </div>
  );
};

export default AIDetectPage;
