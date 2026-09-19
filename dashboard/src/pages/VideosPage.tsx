import React from 'react';
import { Camera } from 'lucide-react';
import { useSiteContext } from '../context/SiteContext';

const VideosPage: React.FC = () => {
  const { selectedSiteId, sites } = useSiteContext();

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Videos Gallery</h1>
          <p className="text-gray-500 mt-1 font-medium">Browse video sequences for {sites.find(s => s.id === selectedSiteId)?.name || 'this site'}.</p>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <Camera className="w-12 h-12 text-brand-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900">No videos yet</h3>
        <p className="text-gray-500 mt-2">Videos for this site will appear here.</p>
      </div>
    </div>
  );
};

export default VideosPage;
