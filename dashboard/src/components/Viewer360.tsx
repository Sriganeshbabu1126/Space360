import React, { useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { X } from 'lucide-react';

declare global {
  interface Window {
    pannellum: any;
  }
}

interface Viewer360Props {
  imageUrl: string;
  onViewChange?: (pitch: number, yaw: number, hfov: number) => void;
  syncPitch?: number;
  syncYaw?: number;
  syncHfov?: number;
  onClose?: () => void;
  height?: string | number;
  id?: string;
}

export interface Viewer360Handle {
  captureSnapshot: () => Promise<string | null>;
}

const Viewer360 = forwardRef<Viewer360Handle, Viewer360Props>(({
  imageUrl,
  onViewChange,
  syncPitch,
  syncYaw,
  syncHfov,
  onClose,
  height,
  id
}, ref) => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const pannellumInstance = useRef<any>(null);

  useImperativeHandle(ref, () => ({
    captureSnapshot: () => {
      return new Promise((resolve) => {
        if (!pannellumInstance.current || !viewerRef.current) {
          resolve(null);
          return;
        }
        
        try {
          const canvas = viewerRef.current.querySelector('canvas') as HTMLCanvasElement;
          if (!canvas) {
            resolve(null);
            return;
          }
          
          if (typeof pannellumInstance.current.getRenderer === 'function') {
            const renderer = pannellumInstance.current.getRenderer();
            if (renderer) {
              try {
                // In pannellum, renderer.render takes (pitch, yaw, hfov, params) in RADIANS!
                // getPitch/getYaw/getHfov return DEGREES!
                const toRad = Math.PI / 180;
                renderer.render(
                  pannellumInstance.current.getPitch() * toRad,
                  pannellumInstance.current.getYaw() * toRad,
                  pannellumInstance.current.getHfov() * toRad,
                  { "returnImage": false }
                );
                
                const dataUrl = canvas.toDataURL('image/png');
                resolve(dataUrl);
                return;
              } catch (e) {
                console.error("Renderer sync draw failed, falling back to rAF", e);
              }
            }
          }
          
          // Fallback: Force a redraw by slightly adjusting pitch
          const p = pannellumInstance.current.getPitch();
          pannellumInstance.current.setPitch(p + 0.0001);
          pannellumInstance.current.setPitch(p);
          
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              try {
                const dataUrl = canvas.toDataURL('image/png');
                resolve(dataUrl);
              } catch (e) {
                console.error(e);
                resolve(null);
              }
            });
          });
        } catch (error) {
          console.error("Failed to capture Viewer360 snapshot:", error);
          resolve(null);
        }
      });
    }
  }));

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
        try {
          pannellumInstance.current.destroy();
        } catch (e) {
          console.error("Error destroying pannellum instance", e);
        }
      }
    };
  }, [imageUrl]);

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
});

export default Viewer360;
