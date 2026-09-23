import React, { useEffect, useState } from 'react';
import { Camera, Upload, MapPin, X, Eye, Trash2, Video } from 'lucide-react';
import toast from 'react-hot-toast';
import { getAllSessions, deleteSession, createIssue, addIssueComment, uploadIssuePhoto, sendIssueNotification } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Viewer360 from '../components/Viewer360';
import CreateIssueModal from '../components/CreateIssueModal';
import CaptureUpload from '../components/CaptureUpload';
import FrameTimelineViewer from '../components/FrameTimelineViewer';
import { useSiteContext } from '../context/SiteContext';

const CapturesPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const { selectedSiteId, selectedFloorPlanId } = useSiteContext();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const highlightParam = searchParams.get('highlight');
  
  const [captures, setCaptures] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'view' | 'upload'>('view');
  
  // Issue Modal State
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [selectedCaptureForIssue, setSelectedCaptureForIssue] = useState<any>(null);
  const [selectedFrameForIssue, setSelectedFrameForIssue] = useState<any>(null);
  
  // Viewer State
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [selectedSequenceData, setSelectedSequenceData] = useState<any>(null);
  const [highlightedCapture, setHighlightedCapture] = useState<string | null>(null);
  
  const fetchCaptures = async () => {
    if (!selectedSiteId) return;
    setLoading(true);
    try {
      const res = await getAllSessions(selectedSiteId);
      let data = res.data;
      
      // Filter by floor plan if one is selected
      if (selectedFloorPlanId) {
        data = data.filter((c: any) => c.floor_plan_id === selectedFloorPlanId || c.location_point_id === selectedFloorPlanId);
        // Note: Actual filtering might depend on backend schema. If location_point_id is floor_plan_id, adjust accordingly.
      }
      
      setCaptures(data);

      if (highlightParam && activeTab === 'view') {
        setHighlightedCapture(highlightParam);
        const capture = data.find((c: any) => c.id === highlightParam);
        if (capture) {
          setViewerUrl(capture.image_url);
          setTimeout(() => {
            const el = document.getElementById(`capture-${highlightParam}`);
            if (el) {
              el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }, 500);
        }
      }
    } catch (err) {
      console.error(err);
      toast.error('Failed to load captures');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    document.title = "Captures | Space360";
    if (activeTab === 'view') {
      fetchCaptures();
    }
  }, [selectedSiteId, selectedFloorPlanId, activeTab]);

  useEffect(() => {
    const hasPending = captures.some(c => c.processing_status === 'pending');
    if (hasPending && selectedSiteId && activeTab === 'view') {
      const interval = setInterval(fetchCaptures, 5000);
      return () => clearInterval(interval);
    }
  }, [captures, selectedSiteId, activeTab]);

  const handleView360 = (e: React.MouseEvent, capture: any) => {
    e.stopPropagation();
    if (capture.location_label === '360° Video Sequence' || capture.location_point_id === null) {
      navigate(`/projects/${selectedSiteId}/videos/${capture.id}/status`);
    } else if (capture.frames && capture.frames.length > 0) {
      setSelectedSequenceData(capture);
    } else if (capture.image_url) {
      setViewerUrl(capture.image_url);
    } else {
      toast.error('No image available for this capture');
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this capture?")) {
      try {
        await deleteSession(id);
        toast.success("Capture deleted");
        fetchCaptures();
      } catch (err) {
        console.error(err);
        toast.error("Failed to delete capture");
      }
    }
  };

  if (!selectedSiteId) return null;

  return (
    <div className="space-y-6 relative h-full flex flex-col">
      {/* Tabs */}
      <div className="flex space-x-1 bg-white p-1 rounded-xl shadow-sm border border-gray-100 max-w-sm mb-4">
        <button
          onClick={() => setActiveTab('view')}
          className={`flex-1 flex items-center justify-center py-2.5 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'view' ? 'bg-brand-50 text-brand-700 shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Camera className="w-4 h-4 mr-2" /> Existing Captures
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 flex items-center justify-center py-2.5 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'upload' ? 'bg-brand-50 text-brand-700 shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Upload className="w-4 h-4 mr-2" /> Upload New
        </button>
      </div>

      {activeTab === 'upload' ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex-1 p-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Upload Capture to Floor Plan</h2>
            {!selectedFloorPlanId ? (
              <div className="p-4 bg-yellow-50 text-yellow-700 rounded-lg border border-yellow-200 mb-6">
                Please select a Floor Plan from the top menu before uploading a capture.
              </div>
            ) : (
              <CaptureUpload 
                onClose={() => setActiveTab('view')}
                onUploadComplete={() => {
                  toast.success("Upload completed successfully!");
                  setActiveTab('view');
                }}
              />
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col">
          {!selectedFloorPlanId && (
            <div className="p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 mb-6 flex items-center">
              <MapPin className="w-5 h-5 mr-3 shrink-0" />
              Showing captures for ALL floor plans. Select a Floor Plan above to filter.
            </div>
          )}

          {captures.length === 0 && !loading ? (
            <div className="card py-16 text-center">
              <Camera className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-gray-900 mb-2">No captures found</h3>
              <p className="text-gray-500 mb-6">Try uploading a new capture to this floor plan.</p>
              <button onClick={() => setActiveTab('upload')} className="btn-primary inline-flex">
                <Upload className="w-4 h-4 mr-2" /> Upload Capture
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
              {captures.map(c => (
                <div id={`capture-${c.id}`} key={c.id} className={`card p-0 overflow-hidden cursor-pointer hover:shadow-xl transition-all duration-300 group hover:-translate-y-1 ${highlightedCapture === c.id ? 'ring-4 ring-brand-500 shadow-xl' : ''}`}>
                  <div className="h-48 relative overflow-hidden bg-gray-200">
                    {c.location_point_id === null ? (
                      <div className="w-full h-full flex flex-col items-center justify-center bg-indigo-50 border border-indigo-100">
                        <Video className="w-12 h-12 text-indigo-500 mb-2" />
                        <span className="bg-indigo-600 text-white text-[10px] font-bold px-2 py-1 rounded">360° VIDEO</span>
                        <span className="mt-2 text-[10px] font-medium text-indigo-500 uppercase tracking-wider bg-white px-2 py-0.5 rounded shadow-sm border border-indigo-100">
                          {c.processing_status || 'queued'}
                        </span>
                      </div>
                    ) : c.thumbnail_url || c.image_url ? (
                      <img src={c.thumbnail_url || c.image_url} alt="thumbnail" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 ease-in-out" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gray-100">
                        <Camera className="w-8 h-8 text-gray-300" />
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      {c.processing_status === 'pending' ? (
                        <div className="bg-black/70 backdrop-blur text-white px-4 py-2 rounded-lg font-bold flex items-center shadow-lg">
                          <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span> Processing...
                        </div>
                      ) : (
                        <button onClick={(e) => handleView360(e, c)} className="bg-white/20 backdrop-blur border border-white/50 text-white px-4 py-2 rounded-lg font-bold flex items-center shadow-lg transform scale-90 group-hover:scale-100 transition-all hover:bg-white hover:text-gray-900">
                          <Eye className="w-4 h-4 mr-2" /> {c.frames?.length > 0 ? 'View Sequence' : 'View 360°'}
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-bold text-gray-900 truncate pr-2 text-lg">
                        {c.location_label || c.location_point_id?.slice(0,8) || 'Unknown'}
                      </h3>
                      <div className="flex items-center gap-2">
                        {isAdmin && (
                          <button 
                            onClick={(e) => handleDeleteSession(e, c.id)}
                            className="text-red-500 hover:bg-red-50 p-1.5 rounded-lg transition-colors"
                            title="Delete Capture"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                        <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-md shadow-sm border ${
                          c.ai_status === 'done' ? 'bg-green-50 text-green-700 border-green-200' :
                          c.ai_status === 'processing' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                          'bg-gray-50 text-gray-700 border-gray-200'
                        }`}>
                          {c.ai_status || 'pending'}
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between items-end mt-3">
                      <p className="text-xs font-semibold text-gray-400">{new Date(c.captured_at).toLocaleDateString()}</p>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedCaptureForIssue(c);
                          setShowIssueModal(true);
                        }}
                        className="text-xs font-bold text-brand-600 hover:text-brand-700 border border-brand-200 hover:bg-brand-50 px-2 py-1 rounded transition-colors"
                      >
                        + Issue
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Viewers & Modals */}
      {viewerUrl && (
        <Viewer360 imageUrl={viewerUrl} onClose={() => setViewerUrl(null)} />
      )}

      {selectedSequenceData && (
        <div className="fixed inset-0 z-40 bg-white flex flex-col pt-16">
          <div className="absolute top-4 right-4 z-50">
            <button onClick={() => { setSelectedSequenceData(null); setSelectedFrameForIssue(null); }} className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors shadow-sm">
              <X className="w-6 h-6 text-gray-700" />
            </button>
          </div>
          <div className="flex-1 overflow-auto p-6 max-w-7xl mx-auto w-full">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Video Sequence Frames</h2>
            <FrameTimelineViewer 
              frames={selectedSequenceData.frames} 
              selectedFrameId={selectedFrameForIssue?.id}
              onSelectFrame={(frame) => {
                setSelectedFrameForIssue(frame);
                setViewerUrl(frame.frame_url);
              }}
            />
            
            <div className="mt-8 pt-8 border-t border-gray-200">
              <h3 className="text-xl font-bold mb-4">Create Issue from Frame</h3>
              {selectedFrameForIssue ? (
                <button 
                  onClick={() => {
                    setSelectedCaptureForIssue(selectedSequenceData);
                    setShowIssueModal(true);
                  }}
                  className="btn-primary"
                >
                  Log Issue at Frame {selectedFrameForIssue.frame_number} ({selectedFrameForIssue.timestamp_seconds}s)
                </button>
              ) : (
                <p className="text-gray-500">Please select a frame above to log an issue at a specific timestamp.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {showIssueModal && selectedCaptureForIssue && (
        <CreateIssueModal
          captureData={{
            id: selectedCaptureForIssue.id,
            image_url: selectedFrameForIssue ? selectedFrameForIssue.frame_url : selectedCaptureForIssue.image_url,
            captured_at: selectedCaptureForIssue.captured_at,
            location_name: selectedCaptureForIssue.location_label || selectedCaptureForIssue.location_point_id,
            frame_a_id: selectedFrameForIssue ? selectedFrameForIssue.id : undefined,
            frame_timestamp: selectedFrameForIssue ? selectedFrameForIssue.timestamp_seconds : undefined,
          }}
          captureId={selectedCaptureForIssue.id}
          onClose={() => {
            setShowIssueModal(false);
            setSelectedCaptureForIssue(null);
            setSelectedFrameForIssue(null);
          }}
          onSubmit={async (data) => {
            try {
              const payload = {
                title: data.title,
                description: data.description,
                issue_type: data.issue_type,
                location_id: selectedCaptureForIssue.location_point_id,
                session_a_id: selectedCaptureForIssue.id,
                frame_a_id: selectedFrameForIssue ? selectedFrameForIssue.id : undefined,
                contractor_ids: data.contractor_ids
              };
              const res = await createIssue(payload);
              const issueId = res.data.id;
              
              if (data.initial_comment) {
                await addIssueComment(issueId, data.initial_comment);
              }

              if (data.markup_image_url) {
                try {
                  const blob = await fetch(data.markup_image_url).then(r => r.blob());
                  const file = new File([blob], 'markup-annotation.png', { type: 'image/png' });
                  await uploadIssuePhoto(issueId, file);
                } catch (error) {
                  console.error('Failed to save markup', error);
                  toast.error('Failed to save markup photo');
                }
              }

              if (data.selected_photos && data.selected_photos.length > 0) {
                for (let i = 0; i < data.selected_photos.length; i++) {
                  const photo = data.selected_photos[i];
                  try {
                    await uploadIssuePhoto(issueId, photo);
                    await new Promise(resolve => setTimeout(resolve, 500));
                  } catch (photoErr) {
                    console.error(`Failed to upload ${photo.name}`, photoErr);
                  }
                }
              }

              try {
                await sendIssueNotification(issueId);
                toast.success("Issue created & notification sent to contractors");
              } catch (e) {
                toast.success("Issue created successfully (Notifications failed)");
              }
              
              setShowIssueModal(false);
              setSelectedCaptureForIssue(null);
            } catch (err) {
              console.error(err);
              toast.error("Failed to create issue");
            }
          }}
        />
      )}
    </div>
  );
};

export default CapturesPage;
