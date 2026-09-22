import React, { useEffect, useState, useRef } from 'react';
import { Camera, Filter, Upload, MapPin, X, Eye, Trash2, Video } from 'lucide-react';
import toast from 'react-hot-toast';
import { getFloorPlans, getLocations, getAllSessions, uploadSession, deleteSession, createIssue, addIssueComment, uploadIssuePhoto, sendIssueNotification, uploadVideoIngest } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Viewer360 from '../components/Viewer360';
import CreateIssueModal from '../components/CreateIssueModal';
import CaptureUpload from '../components/CaptureUpload';
import FrameTimelineViewer from '../components/FrameTimelineViewer';
import { useSiteContext } from '../context/SiteContext';

const CapturesPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const { selectedSiteId, sites } = useSiteContext();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const locationParam = searchParams.get('location_id');
  const highlightParam = searchParams.get('highlight');
  
  const [captures, setCaptures] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [selectedCaptureForIssue, setSelectedCaptureForIssue] = useState<any>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [highlightedCapture, setHighlightedCapture] = useState<string | null>(null);
  const [selectedFrameForIssue, setSelectedFrameForIssue] = useState<any>(null);
  
  const fetchCaptures = async () => {
    if (!selectedSiteId) return;
    setLoading(true);
    try {
      const res = await getAllSessions(selectedSiteId);
      let data = res.data;
      
      if (locationParam) {
        data = data.filter((c: any) => c.location_point_id === locationParam || c.location_point_id === null);
      }
      
      setCaptures(data);

      if (highlightParam) {
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
      } else if (locationParam && data.length > 0) {
        setViewerUrl(data[0].image_url);
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
    fetchCaptures();
  }, [selectedSiteId]);

  useEffect(() => {
    const hasPending = captures.some(c => c.processing_status === 'pending');
    if (hasPending && selectedSiteId) {
      const interval = setInterval(fetchCaptures, 5000);
      return () => clearInterval(interval);
    }
  }, [captures, selectedSiteId]);

  const handleOpenModal = () => {
    setShowModal(true);
  };


  const [selectedSequenceData, setSelectedSequenceData] = useState<any>(null);

  const handleView360 = (e: React.MouseEvent, capture: any) => {
    e.stopPropagation();
    if (capture.location_label === '360° Video Sequence' || capture.location_point_id === null) {
      navigate(`/videos/${capture.id}/status`);
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
    if (window.confirm("Are you sure you want to delete this capture session?")) {
      try {
        await deleteSession(id);
        toast.success("Capture session deleted");
        fetchCaptures();
      } catch (err) {
        console.error(err);
        toast.error("Failed to delete capture session");
      }
    }
  };

  if (!selectedSiteId) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Camera className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-xl font-bold text-gray-700">No Site Selected</h2>
        <p className="text-gray-500 mt-2">Please go to the Sites page and select a site first.</p>
        <button onClick={() => navigate('/sites')} className="mt-6 btn-primary">Go to Sites</button>
      </div>
    );
  }

  return (
    <div className="space-y-6 relative">
      <div className="flex flex-col sm:flex-row justify-end items-start sm:items-center bg-white p-6 rounded-2xl shadow-sm border border-gray-200 gap-6 mb-8">
        <button onClick={handleOpenModal} className="btn-primary flex items-center shadow-lg hover:shadow-xl py-3 px-6 w-full sm:w-auto justify-center rounded-xl font-bold text-base transition-all hover:-translate-y-0.5">
          <Upload className="w-5 h-5 mr-2" />
          Upload Capture
        </button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-black text-gray-900 tracking-tight">Site Captures</h2>
          <p className="text-gray-500 mt-1 font-medium">Browse 360° photos and video sequences for {sites.find(s => s.id === selectedSiteId)?.name || 'this site'}.</p>
        </div>
        <div className="hidden sm:flex items-center bg-brand-50 text-brand-700 px-4 py-2 rounded-lg font-bold text-sm border border-brand-100 shadow-sm">
          <Camera className="w-4 h-4 mr-2 opacity-70" />
          {captures.length} {captures.length === 1 ? 'Capture' : 'Captures'} Total
        </div>
      </div>

      {captures.length === 0 && !loading ? (
        <div className="card py-16 text-center">
          <Camera className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-gray-900 mb-2">No captures yet</h3>
          <p className="text-gray-500 mb-6">Click Upload Capture to add one.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
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
                <div className="flex items-center text-sm text-gray-500 mb-1.5">
                  <MapPin className="w-4 h-4 mr-1.5 opacity-70" />
                  <span className="truncate">{c.site_name || 'Site Capture'}</span>
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

      {showModal && (
        <CaptureUpload 
          onClose={() => setShowModal(false)}
          onUploadComplete={() => {
            setShowModal(false);
            fetchCaptures();
          }}
        />
      )}

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

              // Upload marked-up image as special issue photo
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

              // Upload photos if any
              if (data.selected_photos && data.selected_photos.length > 0) {
                // Sequential upload to avoid rate limiting
                for (let i = 0; i < data.selected_photos.length; i++) {
                  const photo = data.selected_photos[i];
                  try {
                    await uploadIssuePhoto(issueId, photo);
                    // Add a small delay between uploads to be safe with quotas
                    await new Promise(resolve => setTimeout(resolve, 500));
                  } catch (photoErr) {
                    console.error(`Failed to upload ${photo.name}`, photoErr);
                    toast.error(`Failed to upload photo: ${photo.name}`);
                  }
                }
              }

              try {
                await sendIssueNotification(issueId);
                toast.success("Issue created & notification sent to contractors");
              } catch (e) {
                console.error("Failed to send notification:", e);
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
