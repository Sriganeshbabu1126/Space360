import React, { useEffect, useRef, useState } from 'react';

declare global {
  interface Window {
    pannellum: any;
    videojs: any; // Requires video.js plugin
  }
}

interface PannellumViewerProps {
  url: string;
  isVideo?: boolean;
  onVideoCreate?: (video: HTMLVideoElement) => void;
}

const PannellumViewer: React.FC<PannellumViewerProps> = ({ url, isVideo = true, onVideoCreate }) => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const pannellumInstance = useRef<any>(null);
  const videoId = 'pannellum-video-' + Math.random().toString(36).substr(2, 9);

  useEffect(() => {
    if (viewerRef.current && window.pannellum) {
      if (isVideo) {
        // Pannellum video configuration using Video.js plugin if available
        // or passing video element if supported directly.
        // Pannellum doesn't have a direct `video: true` boolean that magically works
        // without the videojs plugin or dynamic plugin.
        // Wait, some forks or newer versions just use `type: 'video'` or similar?
        // Let's implement the standard way, or we can just pass the config.
        let config: any = {
          type: 'equirectangular',
          autoLoad: true,
          compass: false,
          showFullscreenCtrl: false,
        };

        if (isVideo) {
          const videoElement = document.createElement('video');
          videoElement.src = url;
          videoElement.crossOrigin = 'anonymous';
          videoElement.muted = true; // Auto-play policies usually require muting
          videoElement.loop = true;
          videoElement.onerror = (e) => {
            console.error("Video load error", e);
          };
          
          videoElement.onloadeddata = () => {
            if (onVideoCreate) {
              onVideoCreate(videoElement);
            }
            config.dynamic = true;
            config.panorama = videoElement;
            if (viewerRef.current) {
              pannellumInstance.current = window.pannellum.viewer(viewerRef.current, config);
            }
            videoElement.play().catch(e => console.error("Autoplay prevented:", e));
          };
        } else {
          config.panorama = url;
          pannellumInstance.current = window.pannellum.viewer(viewerRef.current, config);
        }
      }
    }

    return () => {
      if (pannellumInstance.current) {
        try {
          pannellumInstance.current.destroy();
        } catch (e) {
          console.error("Error destroying pannellum instance", e);
        }
      }
    };
  }, [url, isVideo]);

  return (
    <div className="relative w-full h-full bg-black">
      <div ref={viewerRef} className="w-full h-full"></div>
    </div>
  );
};

export default PannellumViewer;
