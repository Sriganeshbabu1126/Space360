import React, { useEffect, useState } from 'react';
import { useParams, Outlet, useNavigate } from 'react-router-dom';
import { useSite } from '../context/SiteContext';
import FloorPlanSelector from '../components/FloorPlanSelector';
import FloorPlanUpload from '../components/FloorPlanUpload';

const ProjectDashboard: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { selectedSiteId, setSelectedSiteId, sites, loading } = useSite();
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    // If the projectId in URL doesn't match context, update context
    if (projectId && projectId !== selectedSiteId) {
      setSelectedSiteId(projectId);
    }
  }, [projectId, selectedSiteId, setSelectedSiteId]);

  // Handle case where project is invalid or not loaded yet
  if (loading) {
    return <div className="p-8 text-gray-500">Loading project...</div>;
  }

  const currentSite = sites.find(s => s.id === projectId);

  if (!currentSite && !loading) {
    return (
      <div className="p-8">
        <h2 className="text-xl font-bold text-red-600 mb-4">Project Not Found</h2>
        <p className="text-gray-600 mb-4">The project you are looking for does not exist or you don't have access.</p>
        <button 
          onClick={() => navigate('/')}
          className="bg-brand-600 text-white px-4 py-2 rounded-lg"
        >
          Return to Home
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Project Header Context Area */}
      <div className="bg-white border-b border-gray-200 p-4 md:px-8 mb-6 rounded-xl shadow-sm flex flex-col md:flex-row md:items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {currentSite?.name}
          </h1>
          <div className="max-w-md flex space-x-4 items-end">
            <div className="flex-1">
              <FloorPlanSelector />
            </div>
            <button 
              onClick={() => setShowUpload(!showUpload)}
              className="mb-6 btn-secondary whitespace-nowrap h-10 px-4"
            >
              {showUpload ? 'Cancel Upload' : 'Upload Floor Plan'}
            </button>
          </div>
        </div>
      </div>
      
      {showUpload && (
        <div className="px-4 md:px-8">
           <FloorPlanUpload onUploadSuccess={() => { setShowUpload(false); window.location.reload(); }} />
        </div>
      )}

      {/* Feature Content Area (Nested Routes) */}
      <div className="flex-1">
        <Outlet />
      </div>
    </div>
  );
};

export default ProjectDashboard;
