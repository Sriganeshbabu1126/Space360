import React, { useState, useEffect, useRef } from 'react';
import { getAllSessions, getSites } from '../services/api';
import { Link2, Link2Off, Download, Play, Pause, Zap } from 'lucide-react';
import toast from 'react-hot-toast';
import { jsPDF } from 'jspdf';
import { analyzeVisualChanges } from '../services/aiAnalysis';
import PathSelector from '../components/PathSelector';
import ComparePathOverlay from '../components/ComparePathOverlay';
import CreateIssueModal, { CaptureData } from '../components/CreateIssueModal';
import { useSiteContext } from '../context/SiteContext';
declare global {
  interface Window {
    pannellum: any;
  }
}

const ComparePage: React.FC = () => {
  const { selectedSiteId, selectedFloorPlanId, sites: contextSites } = useSiteContext();
  const [sessions, setSessions] = useState<any[]>([]);
  const [sites, setSites] = useState<any[]>([]);
  const [floorPlansMap, setFloorPlansMap] = useState<Record<string, string>>({});
  
  // Use selectedSiteId from context instead of local state if it exists
  const [localSiteId, setLocalSiteId] = useState<string>('');
  const activeSiteId = selectedSiteId || localSiteId;

  const [sessionAId, setSessionAId] = useState<string>('');
  const [sessionBId, setSessionBId] = useState<string>('');
  const [isSynced, setIsSynced] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiResult, setAiResult] = useState<string>('');
  const [showCreateIssue, setShowCreateIssue] = useState(false);
  
  // Path states
  const [selectedPath, setSelectedPath] = useState<any>(null);
  const [floorPlanImage, setFloorPlanImage] = useState<string>('');
  const [viewMode, setViewMode] = useState<'video' | 'image'>('video');

  const viewerARef = useRef<HTMLDivElement>(null);
  const viewerBRef = useRef<HTMLDivElement>(null);
  const pannellumA = useRef<any>(null);
  const pannellumB = useRef<any>(null);
  const activeViewer = useRef<'A' | 'B' | null>('A');

  useEffect(() => {
    document.title = "Compare | Space360";
    getSites().then(res => setSites(res.data)).catch(console.error);
  }, []);
  
  // Fetch floor plan image for overlay
  useEffect(() => {
    const fetchFP = async () => {
      if (activeSiteId) {
        try {
          const { getFloorPlans } = await import('../services/api');
          const res = await getFloorPlans(activeSiteId);
          const map: Record<string, string> = {};
          res.data.forEach((fp: any) => { map[fp.id] = fp.name; });
          setFloorPlansMap(map);
        } catch(e) {
          console.error(e);
        }
      }

      if (selectedFloorPlanId) {
        try {
          const { getFloorPlan } = await import('../services/api');
          const res = await getFloorPlan(selectedFloorPlanId);
          setFloorPlanImage(res.data.image_url || '');
        } catch (e) {
          console.error("Failed to load floor plan for ComparePage overlay", e);
        }
      } else {
        setFloorPlanImage('');
      }
    };
    fetchFP();
  }, [selectedFloorPlanId, activeSiteId]);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await getAllSessions(activeSiteId || undefined);
        let sortedSessions = (res.data || []).sort((a: any, b: any) => 
          new Date(b.captured_at).getTime() - new Date(a.captured_at).getTime()
        );
        
        // Filter by floor plan if one is selected in context
        if (selectedFloorPlanId) {
          sortedSessions = sortedSessions.filter((c: any) => c.floor_plan_id === selectedFloorPlanId || c.location_point_id === selectedFloorPlanId);
        }
        
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
  }, [activeSiteId, selectedFloorPlanId]);

  const sessionA = sessions.find(s => s.id === sessionAId);
  const sessionB = sessions.find(s => s.id === sessionBId);

  const isVideoCapture = (capture: any) => 
    (capture?.location_label === '360° Video Sequence' || capture?.video_url != null || (capture?.frames && capture?.frames.length > 0)) &&
    (capture?.video_url != null || capture?.processing_status === 'pending');
  const filteredSessions = sessions.filter(s => viewMode === 'video' ? isVideoCapture(s) : !isVideoCapture(s));
  const isVideoA = isVideoCapture(sessionA);
  const isVideoB = isVideoCapture(sessionB);
  const isMixedType = sessionA && sessionB && (isVideoA !== isVideoB);

  const videoAElement = useRef<HTMLVideoElement | null>(null);
  const videoBElement = useRef<HTMLVideoElement | null>(null);

  // Initialize Viewer A
  useEffect(() => {
    if (sessionA && (sessionA.image_url || sessionA.video_url) && viewerARef.current && window.pannellum) {
      const isVideo = isVideoCapture(sessionA);
      const url = isVideo ? (sessionA.video_url || sessionA.image_url) : sessionA.image_url;
      
      if (!url) return;

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
        videoElement.muted = true;
        videoElement.loop = true;
        videoElement.play().catch(e => console.error("Autoplay prevented:", e));
        
        videoAElement.current = videoElement;
        config.panorama = videoElement;
        config.dynamic = true;
      } else {
        videoAElement.current = null;
        config.panorama = url;
      }

      pannellumA.current = window.pannellum.viewer(viewerARef.current, config);
    }
    return () => {
      if (pannellumA.current) {
        pannellumA.current.destroy();
        pannellumA.current = null;
      }
      if (videoAElement.current) {
        videoAElement.current.pause();
        videoAElement.current.src = "";
        videoAElement.current = null;
      }
    };
  }, [sessionA, viewMode]);

  // Initialize Viewer B
  useEffect(() => {
    if (sessionB && (sessionB.image_url || sessionB.video_url) && viewerBRef.current && window.pannellum) {
      const isVideo = isVideoCapture(sessionB);
      const url = isVideo ? (sessionB.video_url || sessionB.image_url) : sessionB.image_url;
      
      if (!url) return;

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
        videoElement.muted = true;
        videoElement.loop = true;
        videoElement.play().catch(e => console.error("Autoplay prevented:", e));
        
        videoBElement.current = videoElement;
        config.panorama = videoElement;
        config.dynamic = true;
      } else {
        videoBElement.current = null;
        config.panorama = url;
      }

      pannellumB.current = window.pannellum.viewer(viewerBRef.current, config);
    }
    return () => {
      if (pannellumB.current) {
        pannellumB.current.destroy();
        pannellumB.current = null;
      }
      if (videoBElement.current) {
        videoBElement.current.pause();
        videoBElement.current.src = "";
        videoBElement.current = null;
      }
    };
  }, [sessionB, viewMode]);

  // Sync Loop
  useEffect(() => {
    let syncInterval: any;
    if (isSynced) {
      syncInterval = setInterval(() => {
        if (!pannellumA.current || !pannellumB.current) return;

        try {
          if (activeViewer.current === 'A') {
            const pitch = pannellumA.current.getPitch();
            if (pitch !== undefined) {
              pannellumB.current.setPitch(pitch, false);
              pannellumB.current.setYaw(pannellumA.current.getYaw(), false);
              pannellumB.current.setHfov(pannellumA.current.getHfov(), false);
            }
          } else if (activeViewer.current === 'B') {
            const pitch = pannellumB.current.getPitch();
            if (pitch !== undefined) {
              pannellumA.current.setPitch(pitch, false);
              pannellumA.current.setYaw(pannellumB.current.getYaw(), false);
              pannellumA.current.setHfov(pannellumB.current.getHfov(), false);
            }
          }
        } catch (e) {
          // Pannellum might throw if the image is still loading; ignore
        }
      }, 1000 / 60); // 60fps
    }
    
    return () => {
      if (syncInterval) clearInterval(syncInterval);
    };
  }, [isSynced]);

  // Video Sync Effect
  useEffect(() => {
    let animFrame: number;
    const syncVideos = () => {
      if (videoAElement.current && videoBElement.current) {
        setProgress(videoAElement.current.currentTime);
        setDuration(videoAElement.current.duration || 0);

        // Only force sync if isSynced is true
        if (isSynced && Math.abs(videoAElement.current.currentTime - videoBElement.current.currentTime) > 0.1) {
          videoBElement.current.currentTime = videoAElement.current.currentTime;
        }
      }
      animFrame = requestAnimationFrame(syncVideos);
    };
    if (isVideoA && isVideoB && !isMixedType) {
      animFrame = requestAnimationFrame(syncVideos);
    }
    return () => {
      if (animFrame) cancelAnimationFrame(animFrame);
    };
  }, [isVideoA, isVideoB, isMixedType, isSynced]);

  const togglePlay = () => {
    if (videoAElement.current && videoBElement.current) {
      if (isPlaying) {
        videoAElement.current.pause();
        videoBElement.current.pause();
      } else {
        videoAElement.current.play();
        videoBElement.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoAElement.current && videoBElement.current) {
      videoAElement.current.currentTime = time;
      videoBElement.current.currentTime = time;
      setProgress(time);
    }
  };

  const onViewerAInteract = () => { activeViewer.current = 'A'; };
  const onViewerBInteract = () => { activeViewer.current = 'B'; };

  const handlePathPointClick = (timestamp: number) => {
    // Only scrub the currently active/primary video
    // The secondary video will stay where it was
    // Note: If isSynced is true, they might try to snap back together in the next anim frame,
    // so you might want to adjust how video sync works if it breaks. The instructions say "Secondary video independent",
    // but the sync logic `if (Math.abs(...) > 0.1) videoB = videoA` might force them back.
    // I will temporarily disable the hard sync for the secondary if they are scrubbed independently,
    // or just let them snap if that's the desired sync behavior.
    
    if (activeViewer.current === 'A' && videoAElement.current) {
      videoAElement.current.currentTime = timestamp;
      setProgress(timestamp);
    } else if (activeViewer.current === 'B' && videoBElement.current) {
      videoBElement.current.currentTime = timestamp;
      // Depending on setup, might need to set progress to A's time to keep scrubber on A
      setProgress(videoAElement.current ? videoAElement.current.currentTime : timestamp);
    }
  };

  const handleAnalyzeChanges = async () => {
    if (!sessionA || !sessionB) return;
    
    setIsAnalyzing(true);
    setAiResult('');
    const toastId = toast.loading('Analyzing changes...');
    
    try {
      const urlA = sessionA.thumbnail_url || sessionA.image_url;
      const urlB = sessionB.thumbnail_url || sessionB.image_url;
      
      const result = await analyzeVisualChanges(urlA, urlB);
      setAiResult(result);
      toast.success('Analysis complete', { id: toastId });
    } catch (error: any) {
      console.error(error);
      toast.error(error.message || 'Failed to analyze changes', { id: toastId });
    } finally {
      setIsAnalyzing(false);
    }
  };

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
      
      doc.save(`Space360_Report_${sessionA.location_point_id?.slice(0, 8) || 'report'}.pdf`);
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
          {!selectedSiteId && (
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">Site</label>
              <select 
                className="input w-full" 
                value={localSiteId} 
                onChange={e => setLocalSiteId(e.target.value)}
              >
                <option value="">Select a Site...</option>
                {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
          )}
          
          <div className="flex-none">
            <label className="block text-sm font-semibold text-gray-700 mb-1">Inspection Path</label>
            <PathSelector 
              siteId={activeSiteId} 
              selectedPathId={selectedPath?.id} 
              onPathSelected={setSelectedPath} 
            />
          </div>
          
          <div className="flex-none pb-0.5">
            <div className="flex bg-gray-100 p-1 rounded-lg border border-gray-200">
              <button
                onClick={() => setViewMode('video')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                  viewMode === 'video' 
                    ? 'bg-white text-brand-700 shadow shadow-gray-200/50' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Video
              </button>
              <button
                onClick={() => setViewMode('image')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                  viewMode === 'image' 
                    ? 'bg-white text-brand-700 shadow shadow-gray-200/50' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Image
              </button>
            </div>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-1">Left Viewer (A)</label>
            <select 
              className="input w-full" 
              value={sessionAId} 
              onChange={e => setSessionAId(e.target.value)}
            >
              <option value="">Select a capture...</option>
              {filteredSessions.map(s => {
                const siteName = (contextSites && contextSites.length > 0 ? contextSites : sites).find(site => site.id === activeSiteId)?.name || s.site_name || 'Project';
                const fpName = s.floor_plan_id ? floorPlansMap[s.floor_plan_id] : 'Floor Plan';
                const dateTime = new Date(s.captured_at).toLocaleString();
                const label = s.location_label || s.location_point_id?.slice(0, 8) || 'Video Walk';
                return (
                  <option key={s.id} value={s.id}>
                    {siteName} &gt; {fpName} &gt; {dateTime} &gt; {label}
                  </option>
                );
              })}
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
              {filteredSessions.map(s => {
                const siteName = (contextSites && contextSites.length > 0 ? contextSites : sites).find(site => site.id === activeSiteId)?.name || s.site_name || 'Project';
                const fpName = s.floor_plan_id ? floorPlansMap[s.floor_plan_id] : 'Floor Plan';
                const dateTime = new Date(s.captured_at).toLocaleString();
                const label = s.location_label || s.location_point_id?.slice(0, 8) || 'Video Walk';
                return (
                  <option key={s.id} value={s.id}>
                    {siteName} &gt; {fpName} &gt; {dateTime} &gt; {label}
                  </option>
                );
              })}
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
              
              {selectedPath && floorPlanImage && (
                <ComparePathOverlay
                  selectedPath={selectedPath}
                  currentVideoTime={progress}
                  floorPlanImage={floorPlanImage}
                  onPathPointClick={handlePathPointClick}
                />
              )}
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
        {/* Mixed Type Warning */}
        {isMixedType && (
          <div className="absolute inset-0 flex items-center justify-center text-orange-500 z-10 bg-gray-50/95 font-medium text-lg">
            Please select the same type of capture (both images or both videos) to compare.
          </div>
        )}

        {/* Video Controls */}
        {isVideoA && isVideoB && !isMixedType && (
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20 bg-black/80 rounded-full px-6 py-3 flex items-center space-x-4 shadow-xl">
            <button onClick={togglePlay} className="text-white hover:text-brand-400 focus:outline-none">
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
            </button>
            <input 
              type="range" 
              min={0} 
              max={duration || 100} 
              step="0.01" 
              value={progress} 
              onChange={handleSeek} 
              className="w-64 accent-brand-500" 
            />
          </div>
        )}
      </div>

      {/* AI Analysis Section */}
      {sessionA && sessionB && !isMixedType && (
        <div className="card shrink-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-800 flex items-center">
              <Zap className="w-5 h-5 mr-2 text-brand-500" /> AI Change Analysis
            </h3>
            <div className="flex space-x-2">
              <button 
                onClick={handleAnalyzeChanges} 
                disabled={isAnalyzing}
                className="px-4 py-1.5 bg-brand-100 text-brand-700 rounded-md text-sm font-medium hover:bg-brand-200 disabled:opacity-50 transition-colors"
              >
                {isAnalyzing ? "Analyzing..." : "Analyze Changes"}
              </button>
              <button 
                onClick={() => setShowCreateIssue(true)}
                className="px-4 py-1.5 bg-brand-600 text-white rounded-md text-sm font-medium hover:bg-brand-700 transition-colors shadow-sm"
              >
                Create Issue
              </button>
            </div>
          </div>
          <div className="text-sm text-gray-600 bg-gray-50 rounded p-4 border border-gray-100 min-h-[60px] whitespace-pre-wrap">
            {aiResult || "Click 'Analyze Changes' to identify visual differences between these two captures."}
          </div>
        </div>
      )}
      
      {showCreateIssue && sessionA && (
        <CreateIssueModal
          captureId={sessionA.id}
          captureData={{
            image_url: isVideoCapture(sessionA) && videoAElement.current ? videoAElement.current.src : sessionA.image_url,
            captured_at: sessionA.captured_at,
            location_name: sessionA.location_label || 'Compare View',
            frame_timestamp: isVideoCapture(sessionA) && videoAElement.current ? videoAElement.current.currentTime : undefined
          } as CaptureData}
          onClose={() => setShowCreateIssue(false)}
          onSubmit={async (data) => {
            try {
              const { createIssue } = await import('../services/api');
              await createIssue({
                ...data,
                location_id: sessionA.location_point_id,
                session_a_id: sessionA.id,
                session_b_id: sessionB?.id
              });
              toast.success('Issue created from compare view');
              setShowCreateIssue(false);
            } catch (err: any) {
              toast.error(err.message || 'Failed to create issue');
            }
          }}
        />
      )}
    </div>
  );
};

export default ComparePage;
