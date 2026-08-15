import React, { useRef, useEffect, useState } from 'react';
import { ArrowUpRight, Type, Cloud, Undo, Trash2, Check, X } from 'lucide-react';

interface ImageMarkupCanvasProps {
  imageUrl: string;
  onSaveMarkup: (canvasDataUrl: string) => void;
  onClose: () => void;
}

type Tool = 'arrow' | 'text' | 'cloud';

const ImageMarkupCanvas: React.FC<ImageMarkupCanvasProps> = ({ imageUrl, onSaveMarkup, onClose }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [tool, setTool] = useState<Tool>('arrow');
  const [color, setColor] = useState('#ef4444');
  const [lineWidth, setLineWidth] = useState(4);
  const [isDrawing, setIsDrawing] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  
  const [baseImage, setBaseImage] = useState<HTMLImageElement | null>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const img = new Image();
    if (!imageUrl.startsWith('data:')) {
      img.crossOrigin = "anonymous";
    }
    img.onload = () => {
      setBaseImage(img);
      initCanvas(img);
    };
    img.src = imageUrl;
    
    const handleResize = () => {
      if (img.complete) initCanvas(img);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [imageUrl]);

  const initCanvas = (img: HTMLImageElement) => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    
    // Add generous padding so the image doesn't get covered by our new floating UI
    const maxWidth = container.clientWidth - 240; // 120px padding on each side
    const maxHeight = container.clientHeight - 120; // 60px padding on top/bottom
    
    const scale = Math.min(maxWidth / img.width, maxHeight / img.height, 1);
    const canvasWidth = img.width * scale;
    const canvasHeight = img.height * scale;
    
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    setCanvasSize({ width: canvasWidth, height: canvasHeight });
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
    
    // Save initial state if history is empty
    setHistory(prev => prev.length === 0 ? [canvas.toDataURL()] : prev);
    
    // If we have history, restore the latest state instead of just the image
    setHistory(prev => {
      if (prev.length > 0) {
        restoreState(prev[prev.length - 1], canvas, ctx);
      }
      return prev;
    });
  };

  const saveState = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      setHistory(prev => [...prev, canvas.toDataURL()]);
    }
  };

  const restoreState = (dataUrl: string, canvasObj?: HTMLCanvasElement, ctxObj?: CanvasRenderingContext2D) => {
    const canvas = canvasObj || canvasRef.current;
    const ctx = ctxObj || canvas?.getContext('2d');
    if (!canvas || !ctx) return;
    
    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = dataUrl;
  };

  const handleUndo = () => {
    if (history.length > 1) {
      const newHistory = [...history];
      newHistory.pop(); // Remove current
      setHistory(newHistory);
      restoreState(newHistory[newHistory.length - 1]);
    }
  };

  const handleClear = () => {
    if (window.confirm("Clear all annotations?")) {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (!canvas || !ctx || !baseImage) return;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);
      
      const newInitialState = canvas.toDataURL();
      setHistory([newInitialState]);
    }
  };

  const getPos = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    
    let clientX, clientY;
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = (e as React.MouseEvent).clientX;
      clientY = (e as React.MouseEvent).clientY;
    }
    
    // Crucial: scale DOM coordinates to internal canvas resolution
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  };

  const drawArrow = (ctx: CanvasRenderingContext2D, fromx: number, fromy: number, tox: number, toy: number) => {
    const headlen = lineWidth * 4; 
    const dx = tox - fromx;
    const dy = toy - fromy;
    const angle = Math.atan2(dy, dx);
    
    ctx.beginPath();
    ctx.moveTo(fromx, fromy);
    ctx.lineTo(tox, toy);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(tox, toy);
    ctx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
    ctx.lineTo(tox, toy);
    ctx.fillStyle = color;
    ctx.fill();
  };

  const drawCloud = (ctx: CanvasRenderingContext2D, startX: number, startY: number, endX: number, endY: number) => {
    const x = Math.min(startX, endX);
    const y = Math.min(startY, endY);
    const w = Math.abs(endX - startX);
    const h = Math.abs(endY - startY);
    
    if (w < 10 || h < 10) return;

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    
    ctx.moveTo(x + w*0.1, y + h*0.2);
    ctx.bezierCurveTo(x + w*0.05, y, x + w*0.3, y - h*0.1, x + w*0.5, y + h*0.05);
    ctx.bezierCurveTo(x + w*0.7, y - h*0.1, x + w*0.95, y, x + w*0.9, y + h*0.2);
    ctx.bezierCurveTo(x + w*1.1, y + h*0.3, x + w*1.1, y + h*0.7, x + w*0.9, y + h*0.8);
    ctx.bezierCurveTo(x + w*0.95, y + h*1, x + w*0.7, y + h*1.1, x + w*0.5, y + h*0.95);
    ctx.bezierCurveTo(x + w*0.3, y + h*1.1, x + w*0.05, y + h*1, x + w*0.1, y + h*0.8);
    ctx.bezierCurveTo(x - w*0.1, y + h*0.7, x - w*0.1, y + h*0.3, x + w*0.1, y + h*0.2);
    
    ctx.stroke();
  };

  const handlePointerDown = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Check if we are clicking on a tool or something else outside
    if ((e.target as HTMLElement).tagName !== 'CANVAS') {
      return;
    }
    
    const pos = getPos(e);
    setStartPos(pos);
    
    if (tool === 'text') {
      // Use window.prompt for a bulletproof cross-device text entry method.
      // This bypasses all mobile keyboard / React rendering lifecycle issues!
      // setTimeout is used to prevent the prompt from blocking the mousedown event loop causing UI freezes.
      setTimeout(() => {
        const text = window.prompt("Enter text to add:");
        if (text && text.trim()) {
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.fillStyle = color;
            ctx.font = `bold ${lineWidth * 6 + 12}px sans-serif`;
            ctx.textBaseline = 'middle';
            ctx.fillText(text, pos.x, pos.y);
            saveState();
          }
        }
      }, 10);
    } else {
      setIsDrawing(true);
    }
  };

  const handlePointerMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx || history.length === 0) return;
    
    const pos = getPos(e);
    
    // Restore the canvas to the state before this stroke started
    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      
      // Draw the current shape on top
      if (tool === 'arrow') {
        drawArrow(ctx, startPos.x, startPos.y, pos.x, pos.y);
      } else if (tool === 'cloud') {
        drawCloud(ctx, startPos.x, startPos.y, pos.x, pos.y);
      }
    };
    img.src = history[history.length - 1];
  };

  const handlePointerUp = () => {
    if (!isDrawing) return;
    setIsDrawing(false);
    saveState();
  };

  const PRESET_COLORS = [
    '#facc15', // Neon Yellow
    '#3b82f6', // Electric Blue
    '#ef4444', // Safety Red
    '#22c55e', // Vibrant Green
    '#ffffff', // Stark White
    '#000000', // Black
  ];

  const PRESET_SIZES = [2, 4, 8];

  return (
    <div className="w-full h-full bg-zinc-950 relative overflow-hidden" ref={containerRef}>
      
      {/* Top Floating Action Bar */}
      <div className="absolute top-6 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2 px-4 py-2 bg-zinc-900/90 backdrop-blur-md border border-white/10 rounded-full shadow-2xl">
        <button 
          onClick={handleUndo} 
          disabled={history.length <= 1}
          className="flex items-center gap-2 px-3 py-2 text-zinc-400 hover:text-white hover:bg-white/10 rounded-full transition-colors disabled:opacity-40 disabled:hover:bg-transparent text-sm font-medium"
        >
          <Undo className="w-4 h-4" /> Undo
        </button>
        <button 
          onClick={handleClear}
          disabled={history.length <= 1}
          className="flex items-center gap-2 px-3 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-full transition-colors disabled:opacity-40 disabled:hover:bg-transparent text-sm font-medium"
        >
          <Trash2 className="w-4 h-4" /> Clear
        </button>
        
        <div className="w-px h-6 bg-white/10 mx-2" />
        
        <button 
          onClick={onClose}
          className="px-4 py-2 text-zinc-400 hover:text-white font-medium text-sm transition-colors rounded-full hover:bg-white/10"
        >
          Cancel
        </button>
        <button 
          onClick={() => {
            if (canvasRef.current) {
              onSaveMarkup(canvasRef.current.toDataURL('image/png'));
            }
          }}
          className="px-6 py-2 bg-brand-500 hover:bg-brand-400 text-white rounded-full font-bold text-sm transition-transform hover:scale-105 shadow-[0_0_15px_rgba(14,165,233,0.3)] flex items-center gap-2"
        >
          <Check className="w-4 h-4" /> Save
        </button>
      </div>

      {/* Left Floating Tool Dock */}
      <div className="absolute left-6 top-1/2 -translate-y-1/2 z-20 flex flex-col items-center gap-3 px-3 py-4 bg-zinc-900/90 backdrop-blur-md border border-white/10 rounded-3xl shadow-2xl">
        <button 
          onClick={() => setTool('arrow')} 
          className={`p-3 rounded-2xl transition-all ${tool === 'arrow' ? 'bg-brand-500 text-white shadow-[0_0_15px_rgba(14,165,233,0.4)] scale-110' : 'text-zinc-400 hover:bg-white/10 hover:text-white'}`}
          title="Arrow"
        >
          <ArrowUpRight className="w-6 h-6" />
        </button>
        <button 
          onClick={() => setTool('cloud')} 
          className={`p-3 rounded-2xl transition-all ${tool === 'cloud' ? 'bg-brand-500 text-white shadow-[0_0_15px_rgba(14,165,233,0.4)] scale-110' : 'text-zinc-400 hover:bg-white/10 hover:text-white'}`}
          title="Cloud"
        >
          <Cloud className="w-6 h-6" />
        </button>
        <button 
          onClick={() => setTool('text')} 
          className={`p-3 rounded-2xl transition-all ${tool === 'text' ? 'bg-brand-500 text-white shadow-[0_0_15px_rgba(14,165,233,0.4)] scale-110' : 'text-zinc-400 hover:bg-white/10 hover:text-white'}`}
          title="Text"
        >
          <Type className="w-6 h-6" />
        </button>
      </div>

      {/* Context Menu (Color & Size) */}
      <div className="absolute left-[88px] top-1/2 -translate-y-1/2 z-20 flex flex-col items-center gap-5 px-3 py-5 bg-zinc-900/90 backdrop-blur-md border border-white/10 rounded-3xl shadow-2xl transition-all duration-300">
        <div className="flex flex-col gap-3">
          {PRESET_COLORS.map(c => (
            <button 
              key={c}
              onClick={() => setColor(c)}
              className={`w-8 h-8 rounded-full border-2 transition-all hover:scale-110 ${color === c ? 'border-white scale-110 shadow-[0_0_10px_rgba(255,255,255,0.3)]' : 'border-transparent'}`}
              style={{ backgroundColor: c }}
              title={c}
            />
          ))}
        </div>
        <div className="w-full h-px bg-white/10" />
        <div className="flex flex-col gap-4 items-center py-2">
          {PRESET_SIZES.map(size => (
            <button 
              key={size}
              onClick={() => setLineWidth(size)}
              className={`rounded-full transition-all flex items-center justify-center ${lineWidth === size ? 'bg-zinc-700 ring-2 ring-brand-500' : 'hover:bg-zinc-800'}`}
              style={{ width: 32, height: 32 }}
              title={`Size ${size}`}
            >
              <div 
                className="bg-zinc-300 rounded-full" 
                style={{ width: size + 4, height: size + 4, backgroundColor: lineWidth === size ? '#0ea5e9' : '#d4d4d8' }} 
              />
            </button>
          ))}
        </div>
      </div>

      {/* Canvas Area */}
      <div className="w-full h-full flex justify-center items-center p-4 sm:p-12 cursor-crosshair">
        <div className="relative inline-flex">
          <canvas
            ref={canvasRef}
            onMouseDown={handlePointerDown}
            onMouseMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onMouseLeave={handlePointerUp}
            onTouchStart={handlePointerDown}
            onTouchMove={handlePointerMove}
            onTouchEnd={handlePointerUp}
            className="shadow-2xl select-none max-w-full rounded-md object-contain"
            style={{ touchAction: 'none' }}
          />
        </div>
      </div>
    </div>
  );
};

export default ImageMarkupCanvas;
