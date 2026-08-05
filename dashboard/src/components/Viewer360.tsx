import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface Viewer360Props {
  imageUrl: string;
  onClose: () => void;
}

declare global {
  interface Window {
    pannellum: any;
  }
}

const Viewer360: React.FC<Viewer360Props> = ({ imageUrl, onClose }) => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const pannellumInstance = useRef<any>(null);

  useEffect(() => {
    if (viewerRef.current && window.pannellum) {
      pannellumInstance.current = window.pannellum.viewer(viewerRef.current, {
        type: 'equirectangular',
        panorama: imageUrl,
        autoLoad: true,
        compass: false,
        showFullscreenCtrl: false,
      });
    }

    return () => {
      if (pannellumInstance.current) {
        pannellumInstance.current.destroy();
      }
    };
  }, [imageUrl]);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black animate-fade-in">
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 z-[101] bg-black/50 hover:bg-black/80 text-white p-3 rounded-full transition-colors"
      >
        <X className="w-6 h-6" />
      </button>
      <div ref={viewerRef} className="w-full h-full"></div>
    </div>
  );
};

export default Viewer360;
