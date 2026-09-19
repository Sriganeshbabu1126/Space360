import React from 'react';
import { Upload } from 'lucide-react';

const VideoUploadPage: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Video</h1>
        <p className="text-gray-500 mt-1 font-medium">Upload new video sequences to process.</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <Upload className="w-12 h-12 text-brand-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900">Upload new video</h3>
        <p className="text-gray-500 mt-2">Drag and drop your video file here.</p>
      </div>
    </div>
  );
};

export default VideoUploadPage;
