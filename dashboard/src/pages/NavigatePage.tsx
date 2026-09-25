import React, { useState, useEffect } from 'react';
import { useSiteContext } from '../context/SiteContext';
import { getAllSessions } from '../services/api';
import ComparePathOverlay from '../components/ComparePathOverlay';
import PannellumViewer from '../components/PannellumViewer';
import Viewer360 from '../components/Viewer360';

const NavigatePage: React.FC = () => {
  const { selectedSiteId, selectedFloorPlanId, sites } = useSiteContext();
  const [sessions, setSessions] = useState<any[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [floorPlanImage, setFloorPlanImage] = useState<string>('');
  const [floorPlansMap, setFloorPlansMap] = useState<Record<string, string>>({});
  
  // "toggle button for video/image" -> viewMode state
  const [viewMode, setViewMode] = useState<'video' | 'image'>('video');

  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);

  useEffect(() => {
    document.title = "Navigate | Space360";
    if (selectedSiteId) {
      import('../services/api').then(({ getFloorPlans }) => {
        getFloorPlans(selectedSiteId).then(res => {
          const map: Record<string, string> = {};
          res.data.forEach((fp: any) => {
            map[fp.id] = fp.name;
          });
          setFloorPlansMap(map);
        }).catch(console.error);
      });

      getAllSessions(selectedSiteId).then(res => {
        // Filter to only video captures that actually have a URL or are still processing
        const videoCaptures = res.data.filter((c: any) => 
          (c.location_label === '360° Video Sequence' || c.video_url != null || (c.frames && c.frames.length > 0)) &&
          (c.video_url != null || c.processing_status === 'pending')
        );
        let sorted = videoCaptures.sort((a: any, b: any) => new Date(b.captured_at).getTime() - new Date(a.captured_at).getTime());
        
        setSessions(sorted);
      }).catch(console.error);
    }
  }, [selectedSiteId, selectedFloorPlanId]);

  useEffect(() => {
    if (selectedFloorPlanId) {
      import('../services/api').then(({ getFloorPlan }) => {
        getFloorPlan(selectedFloorPlanId).then(res => {
          setFloorPlanImage(res.data.image_url || '');
        }).catch(console.error);
      });
    } else {
      setFloorPlanImage('');
    }
  }, [selectedFloorPlanId]);

  const selectedSession = sessions.find(s => s.id === selectedSessionId);
  const frames = selectedSession?.frames || [];
  const currentFrame = frames[currentFrameIndex];
  
  const isVideo = selectedSession?.video_url != null && viewMode === 'video';

  return (
    <div className="h-full flex flex-col p-4 md:p-8 max-w-[1600px] mx-auto animate-fade-in">
      <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Navigate 360° Inspection</h1>
          <p className="text-gray-600">Select an uploaded video capture to navigate.</p>
        </div>
        
        <div className="flex bg-gray-100 p-1 rounded-lg border border-gray-200 shadow-inner">
          <button
            onClick={() => setViewMode('video')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              viewMode === 'video' 
                ? 'bg-white text-brand-700 shadow shadow-gray-200/50' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Video Mode
          </button>
          <button
            onClick={() => setViewMode('image')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              viewMode === 'image' 
                ? 'bg-white text-brand-700 shadow shadow-gray-200/50' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Image Mode
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6 z-10 flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-semibold text-gray-700 mb-1">Select Uploaded Video</label>
          <select 
            className="input w-full" 
            value={selectedSessionId} 
            onChange={e => setSelectedSessionId(e.target.value)}
          >
            <option value="">Select a video capture...</option>
            {sessions.map(s => {
              const siteName = sites.find(site => site.id === selectedSiteId)?.name || 'Project';
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
      </div>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row gap-6 bg-gray-50 rounded-xl p-4 border border-gray-200">
        {!selectedSession ? (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-lg bg-white rounded-lg border border-dashed border-gray-300">
            Please select a video capture to navigate.
          </div>
        ) : (
          <>
            {/* Viewer Panel */}
            <div className="flex-1 bg-black rounded-lg overflow-hidden shadow-inner relative flex flex-col">
              {viewMode === 'video' && selectedSession.video_url ? (
                 <div className="flex-1 relative">
                    <PannellumViewer url={selectedSession.video_url} isVideo={true} />
                 </div>
              ) : viewMode === 'image' && currentFrame ? (
                 <div className="flex-1 relative">
                    <Viewer360 imageUrl={currentFrame.frame_url} />
                    <div className="absolute bottom-4 left-0 right-0 px-4">
                      <input 
                        type="range" 
                        min="0" 
                        max={Math.max(0, frames.length - 1)} 
                        value={currentFrameIndex}
                        onChange={(e) => setCurrentFrameIndex(parseInt(e.target.value))}
                        className="w-full accent-brand-500"
                      />
                    </div>
                 </div>
              ) : (
                 <div className="flex-1 flex items-center justify-center text-gray-400 bg-gray-900">
                    No compatible media found for the selected mode.
                 </div>
              )}
            </div>
            
            {/* Floor Plan Panel */}
            <div className="w-full lg:w-1/3 bg-white rounded-lg overflow-hidden border border-gray-200 shadow-sm relative">
              <div className="absolute inset-0 p-2">
                <ComparePathOverlay 
                  selectedPath={selectedSession}
                  floorPlanImage={floorPlanImage}
                  currentVideoTime={currentFrame?.timestamp_seconds || 0}
                  onPathPointClick={(ts) => {
                    const idx = frames.findIndex((f: any) => f.timestamp_seconds >= ts);
                    if (idx >= 0) setCurrentFrameIndex(idx);
                  }}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default NavigatePage;
