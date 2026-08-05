import React, { useEffect, useState, useRef } from 'react';
import { Camera, Filter, Upload, MapPin, X, Eye, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { getSites, getFloorPlans, getLocations, getAllSessions, uploadSession, deleteSession } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useSearchParams } from 'react-router-dom';
import Viewer360 from '../components/Viewer360';

const CapturesPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [searchParams] = useSearchParams();
  const locationParam = searchParams.get('location_id');
  
  const [captures, setCaptures] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);

  // Modal states
  const [sites, setSites] = useState<any[]>([]);
  const [floorPlans, setFloorPlans] = useState<any[]>([]);
  const [locations, setLocations] = useState<any[]>([]);
  
  const [selectedSiteId, setSelectedSiteId] = useState('');
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [selectedLocationId, setSelectedLocationId] = useState('');
  
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchCaptures = async () => {
    setLoading(true);
    try {
      const res = await getAllSessions();
      let data = res.data;
      
      if (locationParam) {
        data = data.filter((c: any) => c.location_point_id === locationParam);
        if (data.length > 0) {
          setViewerUrl(data[0].image_url);
        }
      }
      
      setCaptures(data);
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
  }, []);

  const handleOpenModal = async () => {
    setShowModal(true);
    try {
      const res = await getSites();
      setSites(res.data);
      if (res.data.length > 0) {
        setSelectedSiteId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
      toast.error('Failed to load sites');
    }
  };

  useEffect(() => {
    if (!selectedSiteId) {
      setFloorPlans([]);
      setSelectedPlanId('');
      return;
    }
    getFloorPlans(selectedSiteId).then(res => {
      setFloorPlans(res.data);
      if (res.data.length > 0) setSelectedPlanId(res.data[0].id);
      else setSelectedPlanId('');
    }).catch(console.error);
  }, [selectedSiteId]);

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
      if (f.type !== 'image/jpeg' && f.type !== 'image/png' && !f.name.toLowerCase().endsWith('.jpg') && !f.name.toLowerCase().endsWith('.jpeg') && !f.name.toLowerCase().endsWith('.png')) {
        toast.error('Only JPG and PNG files are allowed.');
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
      await uploadSession(selectedLocationId, file, notes);
      toast.success('Capture uploaded!');
      setShowModal(false);
      setFile(null);
      setNotes('');
      fetchCaptures();
    } catch (err) {
      console.error(err);
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleView360 = (e: React.MouseEvent, imageUrl: string) => {
    e.stopPropagation();
    if (imageUrl) {
      setViewerUrl(imageUrl);
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
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800">Site Captures</h2>
        <button onClick={handleOpenModal} className="btn-primary flex items-center shadow-md">
          <Upload className="w-4 h-4 mr-2" />
          Upload Capture
        </button>
      </div>

      <div className="card flex flex-wrap items-center gap-4 p-4 shadow-sm">
        <div className="flex items-center text-gray-500 mr-2">
          <Filter className="w-5 h-5 mr-2" />
          <span className="font-medium">Filter By:</span>
        </div>
        <select className="input max-w-xs flex-1 min-w-[150px]"><option>All Sites</option></select>
        <select className="input max-w-xs flex-1 min-w-[150px]"><option>All Dates</option></select>
        <select className="input max-w-xs flex-1 min-w-[150px]"><option>Any AI Status</option></select>
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
            <div key={c.id} className="card p-0 overflow-hidden cursor-pointer hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
              <div className="h-48 relative overflow-hidden bg-gray-200">
                {c.thumbnail_url || c.image_url ? (
                  <img src={c.thumbnail_url || c.image_url} alt="thumbnail" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 ease-in-out" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-100"><Camera className="w-8 h-8 text-gray-300" /></div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <button onClick={(e) => handleView360(e, c.image_url)} className="bg-white/20 backdrop-blur border border-white/50 text-white px-4 py-2 rounded-lg font-bold flex items-center shadow-lg transform scale-90 group-hover:scale-100 transition-all hover:bg-white hover:text-gray-900">
                    <Eye className="w-4 h-4 mr-2" /> View 360°
                  </button>
                </div>
              </div>
              <div className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-gray-900 truncate pr-2 text-lg">
                    {c.location_label || c.location_point_id.slice(0,8)}
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
                <p className="text-xs font-semibold text-gray-400 mt-3">{new Date(c.captured_at).toLocaleDateString()}</p>
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
                <select className="input w-full" value={selectedSiteId} onChange={e => setSelectedSiteId(e.target.value)}>
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
    </div>
  );
};

export default CapturesPage;
