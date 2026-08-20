import React, { useEffect, useState, useRef } from 'react';
import { Camera, Filter, Upload, MapPin, X, Eye, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { getSites, getFloorPlans, getLocations, getAllSessions, uploadSession, deleteSession, createIssue, addIssueComment, uploadIssuePhoto, sendIssueNotification } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useSearchParams } from 'react-router-dom';
import Viewer360 from '../components/Viewer360';
import CreateIssueModal from '../components/CreateIssueModal';
import FrameTimelineViewer from '../components/FrameTimelineViewer';
import { useSite } from '../context/SiteContext';

const CapturesPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const { selectedSiteId } = useSite();
  const [searchParams] = useSearchParams();
  const locationParam = searchParams.get('location_id');
  const highlightParam = searchParams.get('highlight');
  
  const [captures, setCaptures] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [selectedCaptureForIssue, setSelectedCaptureForIssue] = useState<any>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [filterSiteId, setFilterSiteId] = useState<string>('');
  const [highlightedCapture, setHighlightedCapture] = useState<string | null>(null);
  const [selectedFrameForIssue, setSelectedFrameForIssue] = useState<any>(null);

  // Modal states
  const [sites, setSites] = useState<any[]>([]);
  const [floorPlans, setFloorPlans] = useState<any[]>([]);
  const [locations, setLocations] = useState<any[]>([]);
  
  const [modalSiteId, setModalSiteId] = useState('');
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [selectedLocationId, setSelectedLocationId] = useState('');
  
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [capturedAt, setCapturedAt] = useState(() => new Date().toISOString().split('T')[0]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchCaptures = async () => {
    setLoading(true);
    try {
      const res = await getAllSessions(filterSiteId || undefined);
      let data = res.data;
      
      if (locationParam) {
        data = data.filter((c: any) => c.location_point_id === locationParam);
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
  }, [filterSiteId]);

  useEffect(() => {
    const hasPending = captures.some(c => c.processing_status === 'pending');
    if (hasPending) {
      const interval = setInterval(fetchCaptures, 5000);
      return () => clearInterval(interval);
    }
  }, [captures]);

  // Load sites once for both the filter and the modal
  useEffect(() => {
    getSites().then(res => {
      console.log('Fetched sites:', res.data);
      setSites(res.data);
    }).catch(console.error);
  }, []);

  console.log('Current sites state:', sites);

  const handleOpenModal = () => {
    setShowModal(true);
    if (sites.length > 0 && !modalSiteId) {
      setModalSiteId(sites[0].id);
    }
  };

  useEffect(() => {
    if (!modalSiteId) {
      setFloorPlans([]);
      setSelectedPlanId('');
      return;
    }
    getFloorPlans(modalSiteId).then(res => {
      setFloorPlans(res.data);
      if (res.data.length > 0) setSelectedPlanId(res.data[0].id);
      else setSelectedPlanId('');
    }).catch(console.error);
  }, [modalSiteId]);

  useEffect(() => {
    if (!selectedPlanId) {
      setLocations([]);
      setSelectedLocationId('');
      return;
    }
    getLocations(selectedPlanId).then(res => {
      setLocations(res.data);
      if (res.data.length > 0) setSelectedLocationId(res.data[0].id);
      else setSelectedLocationId('');
    }).catch(console.error);
  }, [selectedPlanId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      const isImage = f.type.startsWith('image/') || f.name.toLowerCase().endsWith('.jpg') || f.name.toLowerCase().endsWith('.jpeg') || f.name.toLowerCase().endsWith('.png');
      const isVideo = f.type.startsWith('video/') || f.name.toLowerCase().endsWith('.mp4') || f.name.toLowerCase().endsWith('.mov') || f.name.toLowerCase().endsWith('.webm');
      if (!isImage && !isVideo) {
        toast.error('Only JPG, PNG images and MP4, MOV videos are allowed.');
        return;
      }
      setFile(f);
    }
  };

  const handleUpload = async () => {
    if (!selectedLocationId || !file) {
      toast.error('Please select a location and choose a file');
      return;
    }
    setUploading(true);
    try {
      await uploadSession(selectedLocationId, file, notes, capturedAt);
      toast.success('Capture uploaded!');
      setShowModal(false);
      setFile(null);
      setNotes('');
      setCapturedAt(new Date().toISOString().split('T')[0]);
      fetchCaptures();
    } catch (err) {
      console.error(err);
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const [selectedSequenceData, setSelectedSequenceData] = useState<any>(null);

  const handleView360 = (e: React.MouseEvent, capture: any) => {
    e.stopPropagation();
    if (capture.frames && capture.frames.length > 0) {
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

  return (
    <div className="space-y-6 relative">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white p-6 rounded-2xl shadow-sm border border-gray-200 gap-6 mb-8">
        <div className="flex flex-col w-full sm:w-1/2 md:w-1/3">
          <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Construction Site</label>
          <div className="relative">
            <select 
              className="appearance-none w-full bg-gray-50 border border-gray-200 text-gray-900 font-bold text-lg py-3 px-4 rounded-xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 transition-all cursor-pointer shadow-sm hover:bg-white"
              value={filterSiteId || ''}
              onChange={e => setFilterSiteId(e.target.value)}
            >
              <option value="">All Sites</option>
              {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>
        <button onClick={handleOpenModal} className="btn-primary flex items-center shadow-lg hover:shadow-xl py-3 px-6 w-full sm:w-auto justify-center rounded-xl font-bold text-base transition-all hover:-translate-y-0.5">
          <Upload className="w-5 h-5 mr-2" />
          Upload Capture
        </button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-black text-gray-900 tracking-tight">Site Captures</h2>
          <p className="text-gray-500 mt-1 font-medium">Browse 360° photos and video sequences for {filterSiteId ? sites.find(s => s.id === filterSiteId)?.name : 'all sites'}.</p>
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
                {c.thumbnail_url || c.image_url ? (
                  <img src={c.thumbnail_url || c.image_url} alt="thumbnail" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 ease-in-out" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-100"><Camera className="w-8 h-8 text-gray-300" /></div>
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md animate-fade-in max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900 flex items-center">
                <Upload className="w-5 h-5 mr-2 text-brand-600" /> Upload Capture
              </h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-700 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Site</label>
                <select className="input w-full" value={modalSiteId} onChange={e => setModalSiteId(e.target.value)}>
                  {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Floor Plan</label>
                <select className="input w-full" value={selectedPlanId} onChange={e => setSelectedPlanId(e.target.value)} disabled={floorPlans.length === 0}>
                  {floorPlans.length === 0 ? <option>No plans available</option> : floorPlans.map(f => <option key={f.id} value={f.id}>{f.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location Pin</label>
                <select className="input w-full" value={selectedLocationId} onChange={e => setSelectedLocationId(e.target.value)} disabled={locations.length === 0}>
                  {locations.length === 0 ? <option>No locations available</option> : locations.map(l => <option key={l.id} value={l.id}>{l.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">360° Image (JPG/PNG)</label>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".png,.jpg,.jpeg" className="hidden" />
                <div onClick={() => fileInputRef.current?.click()} className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-brand-500 hover:bg-brand-50 transition-colors">
                  {file ? (
                    <div>
                      <p className="font-bold text-brand-600 text-sm truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  ) : (
                    <div className="text-gray-500">
                      <Camera className="w-6 h-6 mx-auto mb-1 opacity-50" />
                      <p className="text-sm">Click to browse files</p>
                    </div>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Capture Date</label>
                <input type="date" className="input w-full" value={capturedAt} onChange={e => setCapturedAt(e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
                <textarea className="input w-full text-sm" rows={2} value={notes} onChange={e => setNotes(e.target.value)} placeholder="Add any capture notes..."></textarea>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-100">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 font-bold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
              <button onClick={handleUpload} disabled={uploading || !selectedLocationId || !file} className="btn-primary px-6 py-2 shadow-md disabled:opacity-50 disabled:cursor-not-allowed">
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
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
