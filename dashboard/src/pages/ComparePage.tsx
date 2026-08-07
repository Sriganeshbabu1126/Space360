import React, { useState, useEffect, useRef } from 'react';
import { getAllSessions } from '../services/api';
import { Link2, Link2Off, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import { jsPDF } from 'jspdf';

declare global {
  interface Window {
    pannellum: any;
  }
}

const ComparePage: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionAId, setSessionAId] = useState<string>('');
  const [sessionBId, setSessionBId] = useState<string>('');
  const [isSynced, setIsSynced] = useState(true);

  const viewerARef = useRef<HTMLDivElement>(null);
  const viewerBRef = useRef<HTMLDivElement>(null);
  const pannellumA = useRef<any>(null);
  const pannellumB = useRef<any>(null);
  const activeViewer = useRef<'A' | 'B' | null>(null);

  useEffect(() => {
    document.title = "Compare | Space360";
    
    const fetchSessions = async () => {
      try {
        const res = await getAllSessions();
        const sortedSessions = (res.data || []).sort((a: any, b: any) => 
          new Date(b.captured_at).getTime() - new Date(a.captured_at).getTime()
        );
        setSessions(sortedSessions);
        
        if (sortedSessions.length > 0) {
          setSessionAId(sortedSessions[0].id);
          if (sortedSessions.length > 1) {
            setSessionBId(sortedSessions[1].id);
          }
        }
      } catch (error) {
        console.error("Failed to fetch sessions for compare", error);
        toast.error("Failed to load captures");
      }
    };
    
    fetchSessions();
  }, []);

  const sessionA = sessions.find(s => s.id === sessionAId);
  const sessionB = sessions.find(s => s.id === sessionBId);

  // Initialize Viewer A
  useEffect(() => {
    if (sessionA && viewerARef.current && window.pannellum) {
      pannellumA.current = window.pannellum.viewer(viewerARef.current, {
        type: 'equirectangular',
        panorama: sessionA.image_url,
        autoLoad: true,
        compass: false,
        showFullscreenCtrl: false,
      });
    }
    return () => {
      if (pannellumA.current) {
        pannellumA.current.destroy();
        pannellumA.current = null;
      }
    };
  }, [sessionA]);

  // Initialize Viewer B
  useEffect(() => {
    if (sessionB && viewerBRef.current && window.pannellum) {
      pannellumB.current = window.pannellum.viewer(viewerBRef.current, {
        type: 'equirectangular',
        panorama: sessionB.image_url,
        autoLoad: true,
        compass: false,
        showFullscreenCtrl: false,
      });
    }
    return () => {
      if (pannellumB.current) {
        pannellumB.current.destroy();
        pannellumB.current = null;
      }
    };
  }, [sessionB]);

  // Sync Loop
  useEffect(() => {
    let syncInterval: any;
    if (isSynced) {
      syncInterval = setInterval(() => {
        if (!pannellumA.current || !pannellumB.current) return;

        if (activeViewer.current === 'A') {
          pannellumB.current.setPitch(pannellumA.current.getPitch(), false);
          pannellumB.current.setYaw(pannellumA.current.getYaw(), false);
          pannellumB.current.setHfov(pannellumA.current.getHfov(), false);
        } else if (activeViewer.current === 'B') {
          pannellumA.current.setPitch(pannellumB.current.getPitch(), false);
          pannellumA.current.setYaw(pannellumB.current.getYaw(), false);
          pannellumA.current.setHfov(pannellumB.current.getHfov(), false);
        }
      }, 1000 / 60); // 60fps
    }
    
    return () => {
      if (syncInterval) clearInterval(syncInterval);
    };
  }, [isSynced]);

  const onViewerAInteract = () => { activeViewer.current = 'A'; };
  const onViewerBInteract = () => { activeViewer.current = 'B'; };

  const fetchImageAsBase64 = async (url: string) => {
    const res = await fetch(url);
    const blob = await res.blob();
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const [exporting, setExporting] = useState(false);
  const handleExportPDF = async () => {
    if (!sessionA || !sessionB) {
      toast.error("Please select both captures to export.");
      return;
    }
    setExporting(true);
    toast.loading("Generating PDF...", { id: 'pdf-toast' });
    try {
      const doc = new jsPDF();
      const margin = 20;
      let y = margin;
      
      // Title & Meta
      doc.setFontSize(22);
      doc.text("Site Comparison Report", margin, y);
      y += 10;
      
      doc.setFontSize(12);
      doc.setTextColor(100);
      doc.text(`Site: ${sessionA.site_name || 'N/A'}`, margin, y);
      y += 6;
      doc.text(`Location: ${sessionA.location_label || 'N/A'}`, margin, y);
      y += 15;
      
      // Images
      const imgWidth = 80;
      const imgHeight = 40;
      
      try {
        const urlA = sessionA.thumbnail_url || sessionA.image_url;
        const urlB = sessionB.thumbnail_url || sessionB.image_url;
        const b64A = await fetchImageAsBase64(urlA);
        const b64B = await fetchImageAsBase64(urlB);
        
        doc.addImage(b64A, "JPEG", margin, y, imgWidth, imgHeight);
        doc.addImage(b64B, "JPEG", margin + imgWidth + 10, y, imgWidth, imgHeight);
        y += imgHeight + 8;
        
        // Dates
        doc.setFontSize(10);
        doc.setTextColor(0);
        doc.text(`Before: ${new Date(sessionA.captured_at).toLocaleDateString()}`, margin, y);
        doc.text(`After: ${new Date(sessionB.captured_at).toLocaleDateString()}`, margin + imgWidth + 10, y);
        y += 15;
      } catch (err) {
        console.error("Failed to embed images", err);
        doc.text("[Image Failed to Load]", margin, y);
        y += 15;
      }
      
      // Summary
      doc.setFontSize(14);
      doc.text("AI Summary", margin, y);
      y += 8;
      
      doc.setFontSize(11);
      doc.setTextColor(80);
      const summaryText = "This is a placeholder for the AI summary. Changes identified during the comparison will be listed here once the AI feature is re-enabled.";
      const lines = doc.splitTextToSize(summaryText, 170);
      doc.text(lines, margin, y);
      
      doc.save(`Space360_Report_${sessionA.location_point_id.slice(0, 8)}.pdf`);
      toast.success("PDF Exported!", { id: 'pdf-toast' });
    } catch (error) {
      console.error(error);
      toast.error("Failed to export PDF", { id: 'pdf-toast' });
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-100px)]">
      <div className="card shrink-0 flex items-center justify-between">
        <div className="flex space-x-6 items-end w-full">
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-1">Left Viewer (A)</label>
            <select 
              className="input w-full" 
              value={sessionAId} 
              onChange={e => setSessionAId(e.target.value)}
            >
              <option value="">Select a capture...</option>
              {sessions.map(s => (
                <option key={s.id} value={s.id}>
                  {new Date(s.captured_at).toLocaleDateString()} - {s.location_label || s.location_point_id.slice(0, 8)} ({s.site_name || 'Site'})
                </option>
              ))}
            </select>
          </div>
          
          <div className="shrink-0 pb-1">
            <button
              onClick={() => setIsSynced(!isSynced)}
              className={`flex items-center px-4 py-2 rounded-full font-medium transition-colors ${
                isSynced 
                  ? 'bg-blue-100 text-blue-700 border-2 border-blue-500 shadow-sm hover:bg-blue-200' 
                  : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
              }`}
            >
              {isSynced ? (
                <><Link2 className="w-5 h-5 mr-2" /> Synced</>
              ) : (
                <><Link2Off className="w-5 h-5 mr-2" /> Not Synced</>
              )}
            </button>
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-1">Right Viewer (B)</label>
            <select 
              className="input w-full" 
              value={sessionBId} 
              onChange={e => setSessionBId(e.target.value)}
            >
              <option value="">Select a capture...</option>
              {sessions.map(s => (
                <option key={s.id} value={s.id}>
                  {new Date(s.captured_at).toLocaleDateString()} - {s.location_label || s.location_point_id.slice(0, 8)} ({s.site_name || 'Site'})
                </option>
              ))}
            </select>
          </div>

          <div className="shrink-0 pb-1 pl-4 border-l border-gray-200">
            <button
              onClick={handleExportPDF}
              disabled={exporting || !sessionA || !sessionB}
              className="flex items-center px-4 py-2 rounded-full font-medium transition-colors bg-brand-600 text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
            >
              <Download className="w-4 h-4 mr-2" /> {exporting ? "Exporting..." : "Export PDF"}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-black relative">
        {!sessionA && !sessionB && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400 z-10 bg-gray-50">
            Please select captures to compare.
          </div>
        )}
        
        {/* Left Viewer */}
        <div 
          className="flex-1 relative flex flex-col border-b lg:border-b-0 lg:border-r border-gray-700"
          onPointerDownCapture={onViewerAInteract}
          onWheelCapture={onViewerAInteract}
        >
          {sessionA ? (
            <>
              <div className="absolute top-4 left-4 z-20 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm shadow-md pointer-events-none">
                {new Date(sessionA.captured_at).toLocaleDateString()} - {sessionA.location_label}
              </div>
              <div ref={viewerARef} className="w-full h-full"></div>
            </>
          ) : (
             <div className="flex-1 bg-gray-900 flex items-center justify-center text-gray-500">Left view not selected</div>
          )}
        </div>

        {/* Right Viewer */}
        <div 
          className="flex-1 relative flex flex-col"
          onPointerDownCapture={onViewerBInteract}
          onWheelCapture={onViewerBInteract}
        >
          {sessionB ? (
            <>
              <div className="absolute top-4 left-4 z-20 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm shadow-md pointer-events-none">
                {new Date(sessionB.captured_at).toLocaleDateString()} - {sessionB.location_label}
              </div>
              <div ref={viewerBRef} className="w-full h-full"></div>
            </>
          ) : (
            <div className="flex-1 bg-gray-900 flex items-center justify-center text-gray-500">Right view not selected</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComparePage;
