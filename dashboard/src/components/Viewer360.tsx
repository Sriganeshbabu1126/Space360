import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface Viewer360Props {
  imageUrl: string;
  onClose?: () => void;
  id?: string;
  height?: string;
  onViewChange?: (pitch: number, yaw: number, hfov: number) => void;
  syncPitch?: number;
  syncYaw?: number;
  syncHfov?: number;
}

declare global {
  interface Window {
    pannellum: any;
  }
}

const Viewer360: React.FC<Viewer360Props> = ({ 
  imageUrl, 
  onClose,
  id,
  height,
  onViewChange,
  syncPitch,
  syncYaw,
  syncHfov
}) => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const pannellumInstance = useRef<any>(null);

  useEffect(() => {
    if (viewerRef.current && window.pannellum) {
      const config: any = {
        type: 'equirectangular',
        panorama: imageUrl,
        autoLoad: true,
        compass: false,
        showFullscreenCtrl: false,
      };

      if (syncPitch !== undefined) config.pitch = syncPitch;
      if (syncYaw !== undefined) config.yaw = syncYaw;
      if (syncHfov !== undefined) config.hfov = syncHfov;

      pannellumInstance.current = window.pannellum.viewer(viewerRef.current, config);

      if (onViewChange) {
        pannellumInstance.current.on('viewchange', () => {
          onViewChange(
            pannellumInstance.current.getPitch(),
            pannellumInstance.current.getYaw(),
            pannellumInstance.current.getHfov()
          );
        });
      }
    }

    return () => {
      if (pannellumInstance.current) {
        pannellumInstance.current.destroy();
      }
    };
  }, [imageUrl]); // Intentionally only depend on imageUrl to avoid re-mounting

  useEffect(() => {
    if (pannellumInstance.current) {
      if (syncPitch !== undefined) pannellumInstance.current.setPitch(syncPitch, false);
      if (syncYaw !== undefined) pannellumInstance.current.setYaw(syncYaw, false);
      if (syncHfov !== undefined) pannellumInstance.current.setHfov(syncHfov, false);
    }
  }, [syncPitch, syncYaw, syncHfov]);

  return (
    <div 
      id={id} 
      className={onClose 
        ? "fixed inset-0 z-[100] flex items-center justify-center bg-black animate-fade-in"
        : "relative w-full flex-1 bg-black"}
    >
      {onClose && (
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 z-[101] bg-black/50 hover:bg-black/80 text-white p-3 rounded-full transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      )}
      <div ref={viewerRef} className="w-full" style={{ height: height || '100%' }}></div>
    </div>
  );
};

export default Viewer360;
