import React, { useState } from 'react';
import Viewer360 from './Viewer360';

interface SessionInfo {
  imageUrl: string;
  captured_at: string;
  location_label: string;
}

interface CompareViewerProps {
  sessionA: SessionInfo;
  sessionB: SessionInfo;
}

const CompareViewer: React.FC<CompareViewerProps> = ({ sessionA, sessionB }) => {
  const [viewState, setViewState] = useState({ pitch: 0, yaw: 0, hfov: 100 });
  const [activeViewer, setActiveViewer] = useState<'A' | 'B' | null>(null);

  const handleViewChangeA = (pitch: number, yaw: number, hfov: number) => {
    setActiveViewer('A');
    setViewState({ pitch, yaw, hfov });
  };

  const handleViewChangeB = (pitch: number, yaw: number, hfov: number) => {
    setActiveViewer('B');
    setViewState({ pitch, yaw, hfov });
  };

  return (
    <div className="flex flex-col lg:flex-row w-full bg-black">
      <div className="flex-1 flex flex-col border-b lg:border-b-0 lg:border-r border-gray-700">
        <div className="bg-brand-900 text-white px-4 py-2 flex justify-between items-center text-sm shadow-sm z-20">
          <span className="font-semibold px-2 py-0.5 bg-brand-800 rounded">Session A</span>
          <span className="opacity-90">{new Date(sessionA.captured_at).toLocaleDateString()} - {sessionA.location_label}</span>
        </div>
        <Viewer360 
          id="viewer-a" 
          imageUrl={sessionA.imageUrl} 
          height="500px"
          onViewChange={handleViewChangeA}
          syncPitch={activeViewer === 'B' ? viewState.pitch : undefined}
          syncYaw={activeViewer === 'B' ? viewState.yaw : undefined}
          syncHfov={activeViewer === 'B' ? viewState.hfov : undefined}
        />
      </div>

      <div className="flex-1 flex flex-col">
        <div className="bg-gray-800 text-white px-4 py-2 flex justify-between items-center text-sm shadow-sm z-20">
          <span className="font-semibold px-2 py-0.5 bg-gray-700 rounded">Session B</span>
          <span className="opacity-90">{new Date(sessionB.captured_at).toLocaleDateString()} - {sessionB.location_label}</span>
        </div>
        <Viewer360 
          id="viewer-b" 
          imageUrl={sessionB.imageUrl} 
          height="500px"
          onViewChange={handleViewChangeB}
          syncPitch={activeViewer === 'A' ? viewState.pitch : undefined}
          syncYaw={activeViewer === 'A' ? viewState.yaw : undefined}
          syncHfov={activeViewer === 'A' ? viewState.hfov : undefined}
        />
      </div>
    </div>
  );
};

export default CompareViewer;
