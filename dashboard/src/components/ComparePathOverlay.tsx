import React, { useRef, useState, useEffect, useMemo } from 'react';

interface Point {
  x: number; // percentage 0-100
  y: number; // percentage 0-100
  timestamp: number;
}

interface Path {
  id: string;
  points: Point[];
  floorPlanId: string;
}

interface ComparePathOverlayProps {
  selectedPath: Path | null;
  currentVideoTime: number;
  floorPlanImage: string;
  videoWidth?: number;
  videoHeight?: number;
  onPathPointClick: (timestamp: number) => void;
}

const ComparePathOverlay: React.FC<ComparePathOverlayProps> = ({
  selectedPath,
  currentVideoTime,
  floorPlanImage,
  onPathPointClick
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // View transform state
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  // Track hovered point
  const [hoveredPoint, setHoveredPoint] = useState<Point | null>(null);

  const pathPoints = selectedPath?.points || [];

  // Auto-zoom logic
  useEffect(() => {
    if (pathPoints.length === 0) return;
    
    // Find nearest point
    const points = pathPoints;
    let nearest = points[0];
    let minDiff = Math.abs(currentVideoTime - nearest.timestamp);
    
    for (const pt of points) {
      const diff = Math.abs(currentVideoTime - pt.timestamp);
      if (diff < minDiff) {
        minDiff = diff;
        nearest = pt;
      }
    }

    if (!isDragging) {
      // Auto center on nearest point if we have many points
      if (points.length > 50) {
        const targetScale = 2.5; // Zoom in
        setScale(targetScale);
        // Center the point (pt.x, pt.y are 0-100)
        setPan({
          x: 50 - nearest.x, // shift so nearest.x is at 50%
          y: 50 - nearest.y
        });
      } else {
        // Less points, fit to view
        setScale(1);
        setPan({ x: 0, y: 0 });
      }
    }
  }, [currentVideoTime, selectedPath, isDragging]);

  // Handle Wheel Zoom
  const handleWheel = (e: React.WheelEvent) => {
    if (pathPoints.length < 50) return;
    e.preventDefault();
    const zoomFactor = -e.deltaY * 0.005;
    setScale(prev => Math.min(Math.max(1, prev + zoomFactor), 5));
  };

  // Handle Drag/Pan
  const handlePointerDown = (e: React.PointerEvent) => {
    if (scale <= 1) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging) return;
    const dx = (e.clientX - dragStart.x) / (containerRef.current?.clientWidth || 1000) * 100;
    const dy = (e.clientY - dragStart.y) / (containerRef.current?.clientHeight || 1000) * 100;
    setPan(prev => ({ x: prev.x + dx, y: prev.y + dy }));
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  const currentPointIndex = useMemo(() => {
    if (pathPoints.length === 0) return -1;
    let idx = 0;
    let minDiff = Math.abs(currentVideoTime - pathPoints[0].timestamp);
    pathPoints.forEach((pt: any, i: number) => {
      const diff = Math.abs(currentVideoTime - pt.timestamp);
      if (diff < minDiff) {
        minDiff = diff;
        idx = i;
      }
    });
    return idx;
  }, [pathPoints, currentVideoTime]);

  if (!floorPlanImage) return null;

  return (
    <div className="absolute bottom-4 left-4 w-64 h-64 bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl rounded-xl overflow-hidden z-30 flex flex-col group transition-all duration-300 hover:w-96 hover:h-96">
      <div className="bg-black/60 px-3 py-1.5 flex justify-between items-center text-xs text-white shrink-0">
        <span className="font-semibold tracking-wide">Floor Plan Map</span>
        <div className="flex gap-2">
          {scale > 1 && (
            <button 
              onClick={() => { setScale(1); setPan({x:0, y:0}); }}
              className="hover:text-brand-300 transition-colors"
            >
              Reset View
            </button>
          )}
          <span className="opacity-60">{pathPoints.length} pts</span>
        </div>
      </div>
      
      <div 
        ref={containerRef}
        className="relative flex-1 overflow-hidden cursor-grab active:cursor-grabbing touch-none"
        onWheel={handleWheel}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      >
        <div 
          className="absolute inset-0 w-full h-full origin-center transition-transform"
          style={{ 
            transform: `scale(${scale}) translate(${pan.x}%, ${pan.y}%)`,
            transitionDuration: isDragging ? '0ms' : '300ms',
            transitionTimingFunction: 'cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        >
          {/* Floor plan background */}
          <img 
            src={floorPlanImage} 
            alt="Floor Plan Overlay" 
            className="w-full h-full object-contain opacity-80"
            draggable={false}
          />

          {/* Path Line */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none">
             {pathPoints.length > 1 && (
                <polyline 
                  points={pathPoints.map((p: any) => `${p.x}%,${p.y}%`).join(' ')}
                  fill="none"
                  stroke="rgba(99, 102, 241, 0.5)"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                />
             )}
          </svg>

          {/* Path Points */}
          {pathPoints.map((pt: any, i: number) => {
            const isCurrent = i === currentPointIndex;
            return (
              <div
                key={i}
                className="absolute w-4 h-4 -ml-2 -mt-2 rounded-full cursor-pointer transition-all duration-200 shadow-sm"
                style={{ 
                  left: `${pt.x}%`, 
                  top: `${pt.y}%`,
                  backgroundColor: isCurrent ? '#10B981' : '#6366F1', // Emerald for current, Indigo for normal
                  transform: isCurrent ? 'scale(1.5)' : 'scale(1)',
                  zIndex: isCurrent ? 10 : 1,
                  border: '2px solid white'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  onPathPointClick(pt.timestamp);
                }}
                onMouseEnter={() => setHoveredPoint(pt)}
                onMouseLeave={() => setHoveredPoint(null)}
              >
                {isCurrent && (
                  <div className="absolute inset-0 rounded-full border-2 border-emerald-400 animate-ping opacity-75"></div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Tooltip */}
        {hoveredPoint && (
          <div 
            className="absolute z-50 bg-gray-900 text-white text-[10px] font-bold px-2 py-1 rounded shadow-lg pointer-events-none whitespace-nowrap transform -translate-x-1/2 -translate-y-full mt-[-8px]"
            style={{ 
               left: `calc(50% + ${((hoveredPoint.x - 50 + pan.x) * scale)}%)`,
               top: `calc(50% + ${((hoveredPoint.y - 50 + pan.y) * scale)}%)` 
            }}
          >
            {Math.floor(hoveredPoint.timestamp / 60)}:{(Math.floor(hoveredPoint.timestamp) % 60).toString().padStart(2, '0')}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparePathOverlay;
