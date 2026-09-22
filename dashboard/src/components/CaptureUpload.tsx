import React, { useState, useRef, useEffect } from 'react';
import { Upload, Camera, X, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';
import { useSiteContext } from '../context/SiteContext';
import { uploadSession, uploadVideoIngest } from '../services/api';
import axios from 'axios';

interface CaptureUploadProps {
  onClose: () => void;
  onUploadComplete: () => void;
}

const CaptureUpload: React.FC<CaptureUploadProps> = ({ onClose, onUploadComplete }) => {
  const { selectedSiteId, sites } = useSiteContext();
  const [file, setFile] = useState<File | null>(null);
  const [isVideo, setIsVideo] = useState(false);
  
  const [floorPlans, setFloorPlans] = useState<any[]>([]);
  const [pins, setPins] = useState<any[]>([]);
  const [selectedPinId, setSelectedPinId] = useState('');
  const [notes, setNotes] = useState('');
  const [capturedAt, setCapturedAt] = useState(() => new Date().toISOString().split('T')[0]);
  
  const [loadingPins, setLoadingPins] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedJobId, setUploadedJobId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (file && selectedSiteId) {
      // Auto-load floor plan & pins after file selection
      const fetchPins = async () => {
        setLoadingPins(true);
        try {
          // Fetch inspection points for the selected site
          const res = await axios.get(`/api/sites/${selectedSiteId}/inspection-points`);
          setPins(res.data);
          if (res.data.length > 0) {
            setSelectedPinId(res.data[0].id);
          }
        } catch (err) {
          console.error('Failed to load pins', err);
          toast.error('Failed to load locations');
        } finally {
          setLoadingPins(false);
        }
      };
      fetchPins();
    }
  }, [file, selectedSiteId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      const videoExts = ['.mp4', '.mov', '.webm', '.insv'];
      const imgExts = ['.jpg', '.jpeg', '.png'];
      const name = f.name.toLowerCase();
      
      const isVid = videoExts.some(ext => name.endsWith(ext)) || f.type.startsWith('video/');
      const isImg = imgExts.some(ext => name.endsWith(ext)) || f.type.startsWith('image/');
      
      if (!isVid && !isImg) {
        toast.error('Invalid file type');
        return;
      }
      
      setIsVideo(isVid);
      setFile(f);
      setUploadProgress(0);
      setUploadedJobId(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedSiteId) {
      toast.error('No project selected');
      return;
    }
    if (!file) {
      toast.error('Please select a file');
      return;
    }
    if (!selectedPinId) {
      toast.error('Please select a starting location');
      return;
    }

    setUploading(true);
    try {
      if (isVideo) {
        const res = await uploadVideoIngest(selectedSiteId, selectedPinId, file, (progressEvent) => {
          if (progressEvent.total) {
            setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
          }
        });
        if (res.data && res.data.job_id) {
          setUploadedJobId(res.data.job_id);
          toast.success('Video uploaded successfully!');
        } else {
          throw new Error('Upload failed: No job ID returned');
        }
      } else {
        await uploadSession(selectedPinId, file, notes, capturedAt);
        toast.success('Capture uploaded!');
        onUploadComplete();
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md animate-fade-in max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-gray-900 flex items-center">
            <Upload className="w-5 h-5 mr-2 text-brand-600" /> Upload Capture
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {!uploadedJobId ? (
          <div className="space-y-4">
            {!file ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select File (360° Image or Video)</label>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".png,.jpg,.jpeg,.mp4,.mov,.webm,.insv" className="hidden" />
                <div onClick={() => fileInputRef.current?.click()} className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-brand-500 hover:bg-brand-50 transition-colors">
                  <Upload className="w-10 h-10 mx-auto mb-3 text-brand-400" />
                  <p className="font-bold text-brand-600 mb-1">Click to browse files</p>
                  <p className="text-xs text-gray-500">Supports JPG, PNG, MP4, INSV</p>
                </div>
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between bg-brand-50 p-3 rounded-lg border border-brand-100 mb-6">
                  <div className="flex items-center truncate">
                    {isVideo ? <Upload className="w-5 h-5 text-brand-500 mr-2 shrink-0" /> : <Camera className="w-5 h-5 text-brand-500 mr-2 shrink-0" />}
                    <div className="truncate">
                      <p className="text-sm font-bold text-gray-900 truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <button onClick={() => setFile(null)} className="text-gray-400 hover:text-red-500 p-1" disabled={uploading}>
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {loadingPins ? (
                  <div className="text-center py-4 text-sm text-gray-500">Loading locations...</div>
                ) : (
                  <>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Select starting location</label>
                      <select className="input w-full" value={selectedPinId} onChange={e => setSelectedPinId(e.target.value)} disabled={pins.length === 0 || uploading}>
                        {pins.length === 0 ? <option value="">No locations available</option> : pins.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
                      </select>
                    </div>
                    
                    {!isVideo && (
                      <>
                        <div className="mb-4">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Capture Date</label>
                          <input type="date" className="input w-full" value={capturedAt} onChange={e => setCapturedAt(e.target.value)} disabled={uploading} />
                        </div>
                        <div className="mb-4">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
                          <textarea className="input w-full text-sm" rows={2} value={notes} onChange={e => setNotes(e.target.value)} placeholder="Add any capture notes..." disabled={uploading}></textarea>
                        </div>
                      </>
                    )}
                  </>
                )}

                {uploading && isVideo && (
                  <div className="mb-4">
                    <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-brand-500 transition-all duration-300" style={{ width: `${uploadProgress}%` }}></div>
                    </div>
                    <p className="text-xs text-gray-500 text-center mt-1">Uploading... {uploadProgress}%</p>
                  </div>
                )}
                
                <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-100">
                  <button onClick={onClose} disabled={uploading} className="px-4 py-2 font-bold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50">Cancel</button>
                  <button onClick={handleUpload} disabled={uploading || !selectedPinId || loadingPins} className="btn-primary px-6 py-2 shadow-md disabled:opacity-50 disabled:cursor-not-allowed">
                    {uploading ? 'Uploading...' : `Upload ${isVideo ? 'Video' : 'Image'}`}
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800 flex flex-col items-center">
            <p className="font-bold text-lg mb-1">✅ Video uploaded!</p>
            <p className="mb-3">Job ID: {uploadedJobId}</p>
            <a href={`/videos/${uploadedJobId}/status`} className="text-brand-600 hover:text-brand-800 underline font-semibold mb-4 text-center block">Track progress</a>
            
            <button onClick={onUploadComplete} className="btn-primary px-8 py-2 font-bold w-full max-w-xs mx-auto">
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaptureUpload;
