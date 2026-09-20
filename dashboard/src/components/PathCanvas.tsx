import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuid } from 'uuid';
import toast from 'react-hot-toast';

export interface PathPoint {
  id?: string;
  x_percent: number;
  y_percent: number;
  sequence_order: number;
  label: string;
  capture_id?: string;
  video_job_id?: string;
  timestamp_seconds?: number;
}

interface PathCanvasProps {
  floorPlanId: string;
  siteId: string;
  imageWidth: number;
  imageHeight: number;
  onPointClick: (point: PathPoint, updatePoint: (pt: PathPoint) => void) => void;
}

export const PathCanvas: React.FC<PathCanvasProps> = ({ floorPlanId, siteId, imageWidth, imageHeight, onPointClick }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [points, setPoints] = useState<PathPoint[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [pathName, setPathName] = useState("Inspection Path 1");
  const [existingPaths, setExistingPaths] = useState<any[]>([]);
  const [selectedPathId, setSelectedPathId] = useState<string | null>(null);

  useEffect(() => {
    fetchExistingPaths();
  }, [floorPlanId]);

  const fetchExistingPaths = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/paths?floor_plan_id=${floorPlanId}`, {
        headers: { Authorization: `Bearer test-token` }
      });
      setExistingPaths(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    redrawCanvas();
  }, [points, existingPaths, selectedPathId, imageWidth, imageHeight]);

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (!isDrawing) {
      // Check if we clicked an existing point
      const clickedPoint = points.find(p => {
        const px = (p.x_percent / 100) * rect.width;
        const py = (p.y_percent / 100) * rect.height;
        return Math.sqrt(Math.pow(px - x, 2) + Math.pow(py - y, 2)) < 15;
      });

      if (clickedPoint) {
        onPointClick(clickedPoint, (updatedPoint) => {
          setPoints(pts => pts.map(p => p.sequence_order === updatedPoint.sequence_order ? updatedPoint : p));
        });
      }
      return;
    }

    const x_percent = (x / rect.width) * 100;
    const y_percent = (y / rect.height) * 100;

    const newPoint: PathPoint = {
      x_percent,
      y_percent,
      sequence_order: points.length + 1,
      label: `Point ${points.length + 1}`
    };
    setPoints([...points, newPoint]);
  };

  const redrawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw existing paths
    existingPaths.forEach(path => {
      if (path.id === selectedPathId || !isDrawing) {
        drawPath(ctx, path.points, canvas.width, canvas.height, true);
      }
    });

    // Draw current drawing path
    if (isDrawing || points.length > 0) {
      drawPath(ctx, points, canvas.width, canvas.height, false);
    }
  };

  const drawPath = (ctx: CanvasRenderingContext2D, pathPoints: PathPoint[], width: number, height: number, isExisting: boolean) => {
    if (pathPoints.length === 0) return;

    ctx.beginPath();
    ctx.strokeStyle = isExisting ? 'rgba(100, 100, 100, 0.5)' : '#3b82f6';
    ctx.lineWidth = 3;

    pathPoints.forEach((p, i) => {
      const px = (p.x_percent / 100) * width;
      const py = (p.y_percent / 100) * height;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.stroke();

    pathPoints.forEach((p) => {
      const px = (p.x_percent / 100) * width;
      const py = (p.y_percent / 100) * height;

      ctx.beginPath();
      ctx.arc(px, py, 12, 0, 2 * Math.PI);
      
      if (p.video_job_id) {
        ctx.fillStyle = '#3b82f6'; // blue for video
      } else if (p.capture_id) {
        ctx.fillStyle = '#10b981'; // green for capture
      } else {
        ctx.fillStyle = isExisting ? '#9ca3af' : '#ef4444'; // gray or red
      }
      
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = '#ffffff';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(p.sequence_order.toString(), px, py);
    });
  };

  const savePath = async () => {
    if (points.length === 0) return;
    try {
      await axios.post('http://localhost:8000/api/paths', {
        name: pathName,
        site_id: siteId,
        floor_plan_id: floorPlanId,
        points: points
      }, {
        headers: { Authorization: `Bearer test-token` }
      });
      toast.success("Path saved!");
      setPoints([]);
      setIsDrawing(false);
      fetchExistingPaths();
    } catch (e) {
      toast.error("Failed to save path");
    }
  };

  return (
    <div className="absolute inset-0 z-10 pointer-events-none">
      <div className="pointer-events-auto absolute top-4 left-4 bg-white/90 backdrop-blur p-2 rounded-lg shadow-lg flex gap-2">
        <button
          onClick={() => setIsDrawing(!isDrawing)}
          className={`px-3 py-1.5 rounded text-sm font-medium ${isDrawing ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          {isDrawing ? "Stop Drawing" : "Draw New Path"}
        </button>
        {isDrawing && (
          <>
            <input 
              type="text" 
              value={pathName} 
              onChange={e => setPathName(e.target.value)} 
              className="text-sm border rounded px-2"
            />
            <button onClick={savePath} className="px-3 py-1.5 bg-blue-500 text-white rounded text-sm font-medium">
              Save Path
            </button>
            <button onClick={() => setPoints([])} className="px-3 py-1.5 bg-gray-500 text-white rounded text-sm font-medium">
              Clear
            </button>
          </>
        )}
      </div>
      <canvas
        ref={canvasRef}
        width={imageWidth}
        height={imageHeight}
        onClick={handleCanvasClick}
        className="pointer-events-auto cursor-crosshair w-full h-full"
      />
    </div>
  );
};
