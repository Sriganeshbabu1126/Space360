import React, { useState, useEffect, useMemo } from 'react';
import PannellumViewer from './PannellumViewer';

export interface PathPoint {
  id: string;
  label: string;
  timestamp_seconds: number;
  x: number; // 0.0 to 1.0 (relative to floor plan width)
  y: number; // 0.0 to 1.0 (relative to floor plan height)
}

export interface PathVideoPlayerProps {
  videoUrl: string;
  floorPlanUrl?: string;
  pathPoints: PathPoint[];
  onPointClick?: (point: PathPoint) => void;
}

export const PathVideoPlayer: React.FC<PathVideoPlayerProps> = ({
  videoUrl,
  floorPlanUrl,
  pathPoints,
  onPointClick
}) => {
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!videoElement) return;

    const handleTimeUpdate = () => setCurrentTime(videoElement.currentTime);
    const handleDurationChange = () => setDuration(videoElement.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleCanPlay = () => setLoading(false);

    videoElement.addEventListener('timeupdate', handleTimeUpdate);
    videoElement.addEventListener('durationchange', handleDurationChange);
    videoElement.addEventListener('play', handlePlay);
    videoElement.addEventListener('pause', handlePause);
    videoElement.addEventListener('canplay', handleCanPlay);

    // Initialization check if already loaded
    if (videoElement.readyState >= 3) {
      setLoading(false);
      setDuration(videoElement.duration);
    }

    return () => {
      videoElement.removeEventListener('timeupdate', handleTimeUpdate);
      videoElement.removeEventListener('durationchange', handleDurationChange);
      videoElement.removeEventListener('play', handlePlay);
      videoElement.removeEventListener('pause', handlePause);
      videoElement.removeEventListener('canplay', handleCanPlay);
    };
  }, [videoElement]);

  // Active point is the one whose timestamp is closest to current time, but <= currentTime + small threshold
  const activePoint = useMemo(() => {
    if (!pathPoints || pathPoints.length === 0) return null;
    
    const sorted = [...pathPoints].sort((a, b) => a.timestamp_seconds - b.timestamp_seconds);
    let current = sorted[0];
    
    for (let i = 0; i < sorted.length; i++) {
      // allow small threshold ahead
      if (sorted[i].timestamp_seconds <= currentTime + 0.5) {
        current = sorted[i];
      } else {
        break;
      }
    }
    return current;
  }, [currentTime, pathPoints]);

  const handleSeek = (time: number) => {
    if (videoElement) {
      videoElement.currentTime = time;
    }
  };

  const handlePointClick = (point: PathPoint) => {
    handleSeek(point.timestamp_seconds);
    if (onPointClick) {
      onPointClick(point);
    }
  };

  const togglePlay = () => {
    if (!videoElement) return;
    if (isPlaying) {
      videoElement.pause();
    } else {
      videoElement.play();
    }
  };

  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return "00:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col w-full bg-gray-900 rounded-xl overflow-hidden shadow-2xl border border-gray-800">
      {/* 360 Video Viewer */}
      <div className="relative w-full aspect-[2/1] md:aspect-video bg-black">
        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/80 z-20">
            <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
            <div className="mt-4 text-gray-300 font-medium text-sm">Loading 360 Video...</div>
          </div>
        )}
        
        <PannellumViewer 
          url={videoUrl} 
          isVideo={true} 
          onVideoCreate={(video) => setVideoElement(video)} 
        />
        
        {/* Mini Floor Plan */}
        {floorPlanUrl && (
          <div className="absolute bottom-4 right-4 w-32 h-32 md:w-48 md:h-48 bg-white rounded-lg shadow-lg border-2 border-gray-200 overflow-hidden z-10">
            <div className="relative w-full h-full">
              <img 
                src={floorPlanUrl} 
                alt="Mini Floor Plan" 
                className="w-full h-full object-contain p-2" 
              />
              {activePoint && (
                <div 
                  className="absolute w-3 h-3 md:w-4 md:h-4 bg-brand-500 border-2 border-white rounded-full shadow-md transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300"
                  style={{ 
                    left: `${activePoint.x * 100}%`, 
                    top: `${activePoint.y * 100}%` 
                  }}
                  title={activePoint.label}
                />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Timeline Controls */}
      <div className="p-4 bg-gray-900 border-t border-gray-800 flex flex-col gap-4">
        {/* Active Point Info */}
        <div className="flex items-center justify-between text-gray-300 text-sm">
          <div>
            Current Point: <span className="font-semibold text-white">{activePoint?.label || 'None'}</span>
          </div>
          <div className="font-mono text-gray-400">
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>
        </div>

        {/* Scrubber Area */}
        <div className="flex items-center gap-4">
          <button 
            onClick={togglePlay}
            className="w-10 h-10 flex-shrink-0 flex items-center justify-center bg-brand-600 hover:bg-brand-500 text-white rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-brand-400"
            disabled={loading}
          >
            {isPlaying ? (
              // Pause Icon
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 fill-current" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
            ) : (
              // Play Icon
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            )}
          </button>
          
          <div className="flex-1 relative h-12 flex flex-col justify-center">
            {/* The Invisible Native Range Input for native drag feel */}
            <input 
              type="range" 
              min={0} 
              max={duration || 100} 
              step="0.1"
              value={currentTime} 
              onChange={(e) => handleSeek(Number(e.target.value))}
              className="w-full absolute z-20 opacity-0 cursor-pointer h-full"
            />
            
            {/* Custom Track Background */}
            <div className="w-full h-2 bg-gray-700 rounded-full relative overflow-visible">
              {/* Custom Track Progress */}
              <div 
                className="absolute left-0 top-0 h-full bg-brand-500 rounded-l-full pointer-events-none" 
                style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
              />

              {/* Path Point Markers */}
              {duration > 0 && pathPoints.map(point => {
                const isActive = activePoint?.id === point.id;
                const percent = (point.timestamp_seconds / duration) * 100;
                return (
                  <div 
                    key={point.id}
                    className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 flex flex-col items-center cursor-pointer z-30 group"
                    style={{ left: `${percent}%` }}
                    onClick={() => handlePointClick(point)}
                  >
                    <div className={`w-4 h-4 rounded-full border-2 transition-all hover:scale-125 hover:bg-brand-400 ${isActive ? 'bg-brand-400 border-white scale-125' : 'bg-gray-400 border-gray-800'}`} />
                    <div className={`text-[10px] mt-2 whitespace-nowrap px-2 py-0.5 rounded shadow-lg transition-all opacity-0 group-hover:opacity-100 group-hover:-translate-y-1 absolute top-full ${isActive ? 'opacity-100 text-white font-bold bg-brand-600/90' : 'text-gray-200 bg-gray-800/90'}`}>
                      {point.label} ({formatTime(point.timestamp_seconds)})
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PathVideoPlayer;
