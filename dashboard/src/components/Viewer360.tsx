declare global {
  interface Window {
    pannellum: any;
  }
}

import React, { useEffect, useRef, useState } from 'react';

interface Viewer360Props {
  id: string;
  imageUrl: string;
  heading?: number;
  height?: string;
  onViewChange?: (pitch: number, yaw: number, hfov: number) => void;
  syncPitch?: number;
  syncYaw?: number;
  syncHfov?: number;
}

const Viewer360: React.FC<Viewer360Props> = ({
  id, imageUrl, heading = 0, height = '400px',
  onViewChange, syncPitch, syncYaw, syncHfov
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<any>(null);
  const [loaded, setLoaded] = useState(false);
  const isUpdatingRef = useRef(false);

  useEffect(() => {
    const loadPannellum = () => {
      if (!window.pannellum) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css';
        document.head.appendChild(link);

        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js';
        script.onload = initViewer;
        document.head.appendChild(script);
      } else {
        initViewer();
      }
    };

    const initViewer = () => {
      if (!containerRef.current) return;
      
      if (viewerRef.current) {
        viewerRef.current.destroy();
      }

      viewerRef.current = window.pannellum.viewer(containerRef.current, {
        type: 'equirectangular',
        panorama: imageUrl,
        yaw: heading,
        autoLoad: true,
        showControls: false,
      });

      viewerRef.current.on('load', () => setLoaded(true));
      viewerRef.current.on('mouseup', handleViewChange);
      viewerRef.current.on('touchend', handleViewChange);
      viewerRef.current.on('zoom', handleViewChange);
      viewerRef.current.on('mousedown', () => { isUpdatingRef.current = true; });
    };

    loadPannellum();

    return () => {
      if (viewerRef.current) {
        try { viewerRef.current.destroy(); } catch(e) {}
      }
    };
  }, [imageUrl, heading]);

  useEffect(() => {
    const v = viewerRef.current;
    if (v && !isUpdatingRef.current) {
      if (syncPitch !== undefined) v.setPitch(syncPitch, false);
      if (syncYaw !== undefined) v.setYaw(syncYaw, false);
      if (syncHfov !== undefined) v.setHfov(syncHfov, false);
    }
  }, [syncPitch, syncYaw, syncHfov]);

  const handleViewChange = () => {
    isUpdatingRef.current = false;
    if (onViewChange && viewerRef.current) {
      onViewChange(
        viewerRef.current.getPitch(),
        viewerRef.current.getYaw(),
        viewerRef.current.getHfov()
      );
    }
  };

  useEffect(() => {
    const handleWheel = () => handleViewChange();
    const el = containerRef.current;
    if (el) {
      el.addEventListener('wheel', handleWheel);
      return () => el.removeEventListener('wheel', handleWheel);
    }
  }, []);

  return (
    <div className="relative overflow-hidden w-full" style={{ height }}>
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
        </div>
      )}
      <div ref={containerRef} className="w-full h-full" id={id}></div>
    </div>
  );
};

export default Viewer360;
