import React, { useState, useEffect } from 'react';
import { Camera as CameraIcon, Wifi, Upload, Info } from 'lucide-react';
import toast from 'react-hot-toast';
import { 
  checkCameraConnection, 
  getCameraInfo, 
  takeAndDownload, 
  CameraInfo 
} from '../services/camera';
import { uploadSession } from '../services/api';

const CameraPanel: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [camInfo, setCamInfo] = useState<CameraInfo | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState('');
  
  const [capturing, setCapturing] = useState(false);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  const [uploading, setUploading] = useState(false);

  // Cleanup object URL on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const isConnected = await checkCameraConnection();
      if (isConnected) {
        setConnected(true);
        const info = await getCameraInfo();
        setCamInfo(info);
        toast.success(`Connected to ${info.model}`);
      } else {
        toast.error('Could not connect to camera. Check WiFi.');
        setConnected(false);
      }
    } catch (error) {
      toast.error('Connection error.');
      setConnected(false);
    }
    setConnecting(false);
  };

  const handleCapture = async () => {
    setCapturing(true);
    setCapturedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    try {
      toast('Taking picture... Please wait', { icon: '📸' });
      const file = await takeAndDownload();
      setCapturedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      toast.success('Picture captured successfully!');
    } catch (error) {
      toast.error('Capture failed. Please try again.');
    }
    setCapturing(false);
  };

  const handleUpload = async () => {
    if (!capturedFile) return;
    setUploading(true);
    try {
      await uploadSession(selectedLocationId, capturedFile, 'LG-R105');
      toast.success('Uploaded to Space360!');
      setCapturedFile(null);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    } catch (error) {
      toast.error('Upload failed.');
    }
    setUploading(false);
  };

  return (
    <div className="card max-w-md mx-auto bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden p-0">
      <div className="bg-gray-900 text-white p-5 flex justify-between items-center">
        <h2 className="text-xl font-bold flex items-center">
          <CameraIcon className="w-6 h-6 mr-2" />
          Camera Control
        </h2>
        <div className="flex items-center space-x-2 bg-gray-800 px-3 py-1.5 rounded-full border border-gray-700">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Status</span>
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'}`}></div>
        </div>
      </div>
      
      <div className="p-6 space-y-6">
        <button 
          onClick={handleConnect} 
          disabled={connecting}
          className="w-full flex items-center justify-center py-3 px-4 bg-gray-50 hover:bg-gray-100 text-gray-800 font-bold rounded-xl transition-colors border border-gray-200 shadow-sm"
        >
          {connecting ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-800 mr-2"></div> : <Wifi className="w-5 h-5 mr-2 text-gray-600" />}
          {connected ? 'Reconnect' : 'Connect to LG 360 CAM'}
        </button>

        {camInfo && (
          <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl flex items-start space-x-3 text-sm text-blue-900 shadow-inner">
            <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-base">{camInfo.manufacturer} {camInfo.model}</p>
              <p className="text-blue-700/80 font-medium">Firmware: {camInfo.firmwareVersion} • SN: {camInfo.serialNumber}</p>
            </div>
          </div>
        )}

        <button 
          onClick={handleCapture}
          disabled={!connected || capturing || uploading}
          className="w-full flex flex-col items-center justify-center py-8 px-4 bg-brand-600 hover:bg-brand-700 text-white rounded-2xl shadow-xl hover:-translate-y-1 transition-all disabled:opacity-50 disabled:hover:translate-y-0 disabled:cursor-not-allowed group"
        >
          {capturing ? (
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-white/30 border-t-white mb-3"></div>
          ) : (
            <CameraIcon className="w-12 h-12 mb-3 drop-shadow-md group-hover:scale-110 transition-transform" />
          )}
          <span className="font-black text-xl uppercase tracking-widest">Capture 360°</span>
        </button>

        {previewUrl && (
          <div className="space-y-4 animate-fade-in border-t-2 border-gray-100 pt-6 mt-6">
            <h3 className="font-bold text-gray-800 flex justify-between items-center text-sm uppercase tracking-wide">
              Capture Preview
              <span className="text-xs font-semibold bg-brand-100 text-brand-800 px-2.5 py-1 rounded-full normal-case tracking-normal">{capturedFile?.name}</span>
            </h3>
            <div className="relative h-48 bg-gray-200 rounded-xl overflow-hidden shadow-inner border border-gray-200">
              <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
            </div>
            
            <input
              type="text"
              placeholder="Enter Location ID"
              value={selectedLocationId}
              onChange={(e) => setSelectedLocationId(e.target.value)}
              className="input w-full mb-2"
            />
            <button 
              onClick={handleUpload}
              disabled={uploading}
              className="w-full flex items-center justify-center py-3.5 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-md transition-colors disabled:opacity-70"
            >
              {uploading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              ) : (
                <Upload className="w-5 h-5 mr-2" />
              )}
              Upload to Space360
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraPanel;
