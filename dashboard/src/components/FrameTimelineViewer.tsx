import React, { useState } from 'react';
import { Eye, Video } from 'lucide-react';
import Viewer360 from './Viewer360';

interface FrameTimelineViewerProps {
  frames: any[];
  onSelectFrame?: (frame: any) => void;
  selectedFrameId?: string;
  className?: string;
}

const FrameTimelineViewer: React.FC<FrameTimelineViewerProps> = ({ frames, onSelectFrame, selectedFrameId, className = '' }) => {
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);

  if (!frames || frames.length === 0) return null;

  return (
    <div className={`w-full bg-gray-50 border border-gray-200 rounded-xl p-4 ${className}`}>
      <div className="flex items-center text-gray-700 font-bold mb-3">
        <Video className="w-5 h-5 mr-2 text-brand-500" />
        Video Sequence ({frames.length} frames)
      </div>
      
      <div className="flex overflow-x-auto gap-3 pb-2 snap-x">
        {frames.map((frame, idx) => (
          <div 
            key={frame.id} 
            onClick={() => onSelectFrame ? onSelectFrame(frame) : setViewerUrl(frame.frame_url)}
            className={`
              relative flex-shrink-0 w-24 h-24 rounded-lg overflow-hidden cursor-pointer snap-start
              border-2 transition-all hover:scale-105
              ${selectedFrameId === frame.id ? 'border-brand-500 ring-2 ring-brand-200' : 'border-transparent hover:border-brand-300'}
            `}
          >
            <img 
              src={frame.frame_url} 
              alt={`Frame ${frame.frame_number}`} 
              className="w-full h-full object-cover bg-gray-200" 
            />
            <div className="absolute bottom-0 inset-x-0 bg-black/60 text-white text-[10px] font-bold text-center py-1">
              {frame.timestamp_seconds}s
            </div>
          </div>
        ))}
      </div>

      {viewerUrl && (
        <div className="fixed inset-0 z-50 bg-black/90 flex flex-col items-center justify-center">
          <div className="absolute top-4 right-4 z-50">
            <button 
              onClick={() => setViewerUrl(null)}
              className="bg-white text-gray-900 px-4 py-2 rounded-lg font-bold shadow-lg"
            >
              Close 360° View
            </button>
          </div>
          <div className="w-full h-[80vh] max-w-6xl relative">
            <Viewer360 imageUrl={viewerUrl} />
          </div>
        </div>
      )}
    </div>
  );
};

export default FrameTimelineViewer;
