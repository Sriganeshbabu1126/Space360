import React, { useState, useEffect } from 'react';
import Viewer360 from '../components/Viewer360';
import { getAllSessions } from '../services/api';
import { Link2, Link2Off } from 'lucide-react';
import toast from 'react-hot-toast';

const ComparePage: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionAId, setSessionAId] = useState<string>('');
  const [sessionBId, setSessionBId] = useState<string>('');
  
  const [isSynced, setIsSynced] = useState(true);
  const [viewState, setViewState] = useState({ pitch: 0, yaw: 0, hfov: 100 });
  const [activeViewer, setActiveViewer] = useState<'A' | 'B' | null>(null);

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

  const handleViewChangeA = (pitch: number, yaw: number, hfov: number) => {
    if (!isSynced) return;
    setActiveViewer('A');
    setViewState({ pitch, yaw, hfov });
  };

  const handleViewChangeB = (pitch: number, yaw: number, hfov: number) => {
    if (!isSynced) return;
    setActiveViewer('B');
    setViewState({ pitch, yaw, hfov });
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
                  ? 'bg-brand-100 text-brand-700 hover:bg-brand-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
        </div>
      </div>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-black relative">
        {!sessionA && !sessionB && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400 z-10 bg-gray-50">
            Please select captures to compare.
          </div>
        )}
        
        {/* Left Viewer */}
        <div className="flex-1 relative flex flex-col border-b lg:border-b-0 lg:border-r border-gray-700">
          {sessionA ? (
            <>
              <div className="absolute top-4 left-4 z-20 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm shadow-md pointer-events-none">
                {new Date(sessionA.captured_at).toLocaleDateString()} - {sessionA.location_label}
              </div>
              <Viewer360 
                id="viewer-a" 
                imageUrl={sessionA.image_url} 
                onViewChange={handleViewChangeA}
                syncPitch={isSynced && activeViewer === 'B' ? viewState.pitch : undefined}
                syncYaw={isSynced && activeViewer === 'B' ? viewState.yaw : undefined}
                syncHfov={isSynced && activeViewer === 'B' ? viewState.hfov : undefined}
              />
            </>
          ) : (
             <div className="flex-1 bg-gray-900 flex items-center justify-center text-gray-500">Left view not selected</div>
          )}
        </div>

        {/* Right Viewer */}
        <div className="flex-1 relative flex flex-col">
          {sessionB ? (
            <>
              <div className="absolute top-4 left-4 z-20 bg-black/60 text-white px-3 py-1 rounded-md text-sm font-medium backdrop-blur-sm shadow-md pointer-events-none">
                {new Date(sessionB.captured_at).toLocaleDateString()} - {sessionB.location_label}
              </div>
              <Viewer360 
                id="viewer-b" 
                imageUrl={sessionB.image_url} 
                onViewChange={handleViewChangeB}
                syncPitch={isSynced && activeViewer === 'A' ? viewState.pitch : undefined}
                syncYaw={isSynced && activeViewer === 'A' ? viewState.yaw : undefined}
                syncHfov={isSynced && activeViewer === 'A' ? viewState.hfov : undefined}
              />
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
