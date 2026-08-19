import React, { useEffect, useState, useRef } from 'react';
import { Upload, Eye, MapPin, Plus, List, Map, FileText, Camera, Check, X, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { getSites, getFloorPlans, getLocations, uploadFloorPlan, createLocation, deleteFloorPlan } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useSite } from '../context/SiteContext';

const FloorPlansPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const { selectedSiteId, setSelectedSiteId } = useSite();
  const navigate = useNavigate();
  const [sites, setSites] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<any>(null);
  
  const [isAddingPin, setIsAddingPin] = useState(false);
  const [pins, setPins] = useState<any[]>([]);
  const [pendingPin, setPendingPin] = useState<{x: number, y: number} | null>(null);
  const [pinLabel, setPinLabel] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadLabel, setUploadLabel] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    document.title = "Floor Plans | Space360";
    const fetchSites = async () => {
      try {
        const res = await getSites();
        setSites(res.data);
        if (res.data.length > 0 && !selectedSiteId) {
          setSelectedSiteId(res.data[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchSites();
  }, []);

  useEffect(() => {
    if (!selectedSiteId) return;
    const fetchPlans = async () => {
      setLoading(true);
      try {
        const res = await getFloorPlans(selectedSiteId);
        setPlans(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPlans();
  }, [selectedSiteId]);

  const openPlan = async (plan: any) => {
    setSelectedPlan(plan);
    try {
      const res = await getLocations(plan.id);
      setPins(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
    if (!isAddingPin || !imageRef.current || pendingPin) return;
    
    const rect = imageRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    setPendingPin({ x, y });
    setPinLabel("");
  };

  const handleConfirmPin = async () => {
    if (!pendingPin || !pinLabel.trim() || !selectedPlan) return;
    try {
      await createLocation(selectedPlan.id, {
        label: pinLabel.trim(),
        pin_x: pendingPin.x,
        pin_y: pendingPin.y
      });
      toast.success("Location pin added");
      setPendingPin(null);
      setPinLabel("");
      setIsAddingPin(false);
      
      const res = await getLocations(selectedPlan.id);
      setPins(res.data);
    } catch (error) {
      toast.error("Failed to add pin");
      console.error(error);
    }
  };

  const handleDeletePlan = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this floor plan and all its pins?")) {
      try {
        await deleteFloorPlan(id);
        toast.success("Floor plan deleted");
        if (selectedSiteId) {
          getFloorPlans(selectedSiteId).then(res => setPlans(res.data)).catch(console.error);
        }
      } catch (err) {
        console.error(err);
        toast.error("Failed to delete floor plan");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File selected:', e.target.files?.[0]);
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        toast.error('PDFs are not supported. Please upload a JPG or PNG image.');
        return;
      }
      setUploadFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      console.log('File dropped:', file);
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        toast.error('PDFs are not supported. Please upload a JPG or PNG image.');
        return;
      }
      setUploadFile(file);
      console.log('uploadFile state set');
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadLabel || !selectedSiteId) {
      toast.error('Please fill in all fields');
      return;
    }
    try {
      setUploading(true);
      await uploadFloorPlan(selectedSiteId, uploadLabel, uploadFile);
      toast.success('Floor plan uploaded successfully!');
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadLabel('');
      // Refresh list
      const fp = await getFloorPlans(selectedSiteId);
      setPlans(fp.data);
    } catch (error) {
      toast.error('Upload failed. Please try again.');
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  if (selectedPlan) {
    return (
      <div className="space-y-4 h-full flex flex-col">
        <div className="flex justify-between items-center bg-white p-5 rounded-2xl shadow-sm border border-gray-200">
          <div>
            <button onClick={() => setSelectedPlan(null)} className="text-sm font-bold text-brand-600 hover:text-brand-800 transition-colors mb-1 uppercase tracking-wide">&larr; Back to Floor Plans</button>
            <h2 className="text-3xl font-black text-gray-900">{selectedPlan.label}</h2>
          </div>
          <button 
            onClick={() => {
              if (isAddingPin) {
                setIsAddingPin(false);
                setPendingPin(null);
              } else {
                setIsAddingPin(true);
              }
            }} 
            disabled={selectedPlan.image_url?.toLowerCase().endsWith('.pdf')}
            className={`flex items-center px-5 py-2.5 rounded-xl font-bold transition-all shadow-sm ${
              selectedPlan.image_url?.toLowerCase().endsWith('.pdf') ? 'bg-gray-100 text-gray-400 cursor-not-allowed' :
              isAddingPin ? 'bg-red-500 text-white hover:bg-red-600 shadow-red-200' : 'bg-brand-100 text-brand-700 hover:bg-brand-200 hover:-translate-y-0.5'
            }`}
          >
            {isAddingPin ? 'Cancel Pin Placement' : <><Plus className="w-5 h-5 mr-2" /> Add Location Pin</>}
          </button>
        </div>

        <div className="flex-1 card p-4 bg-gray-50 flex flex-col lg:flex-row items-stretch justify-center overflow-hidden gap-4">
          <div className="flex-1 relative inline-block max-w-full max-h-full border-4 border-white shadow-2xl rounded-2xl overflow-hidden bg-white">
            {selectedPlan.image_url?.toLowerCase().endsWith('.pdf') ? (
              <div className="flex flex-col items-center justify-center h-full bg-gray-50 min-h-[500px] w-full">
                <FileText className="w-20 h-20 text-brand-500 mb-4" />
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{selectedPlan.label}</h3>
                <p className="text-gray-500 mb-6">This floor plan is a PDF document.</p>
                <a href={selectedPlan.image_url} target="_blank" rel="noopener noreferrer" className="btn-primary px-6 py-3 shadow-md inline-flex items-center">
                  <Eye className="w-5 h-5 mr-2" /> Open PDF
                </a>
              </div>
            ) : (
              <img 
                ref={imageRef}
                src={selectedPlan.image_url} 
                alt="Floor Plan" 
                className={`w-full h-full object-contain transition-opacity duration-300 ${isAddingPin ? 'cursor-crosshair opacity-80' : 'cursor-default'}`}
                onClick={handleImageClick}
              />
            )}
            
            {isAddingPin && !pendingPin && !selectedPlan.image_url?.toLowerCase().endsWith('.pdf') && (
              <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur text-white px-4 py-2 rounded-full text-sm font-bold animate-pulse z-20 shadow-lg pointer-events-none">
                Click anywhere on the map to place a pin
              </div>
            )}

            {pendingPin && (
              <div 
                className="absolute transform -translate-x-1/2 -translate-y-1/2 z-30"
                style={{ left: `${pendingPin.x}%`, top: `${pendingPin.y}%` }}
              >
                <div className="relative">
                  <div className="w-8 h-8 bg-brand-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white animate-bounce">
                    <Plus className="w-4 h-4 text-white" />
                  </div>
                  <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 bg-white rounded-xl shadow-xl p-3 w-48 animate-fade-in border border-gray-100 z-40">
                    <input 
                      type="text" 
                      autoFocus
                      placeholder="e.g. Entrance"
                      value={pinLabel}
                      onChange={(e) => setPinLabel(e.target.value)}
                      className="input text-sm mb-2 w-full"
                      onKeyDown={(e) => e.key === 'Enter' && handleConfirmPin()}
                    />
                    <div className="flex gap-2">
                      <button onClick={handleConfirmPin} className="flex-1 bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold py-1.5 rounded-lg flex justify-center items-center transition-colors">
                        <Check className="w-3 h-3 mr-1" /> Save
                      </button>
                      <button onClick={() => setPendingPin(null)} className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-1.5 rounded-lg flex justify-center items-center transition-colors">
                        <X className="w-3 h-3 mr-1" /> Cancel
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {pins.map((pin, index) => (
              <div 
                key={pin.id} 
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer transition-transform ${isAddingPin ? 'pointer-events-none opacity-50' : 'hover:scale-110 z-10'}`}
                style={{ left: `${pin.pin_x}%`, top: `${pin.pin_y}%` }}
              >
                <div className="relative flex flex-col items-center">
                  <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center shadow-lg border-2 border-white font-bold text-sm">
                    {index + 1}
                  </div>
                  
                  <div className="absolute top-full mt-2 opacity-0 group-hover:opacity-100 transition-all duration-200 bg-white rounded-xl p-3 shadow-xl border border-gray-100 z-20 pointer-events-none group-hover:pointer-events-auto min-w-[150px]">
                    <div className="text-sm font-bold text-gray-900 mb-1 text-center">{pin.label}</div>
                    <div className="w-full bg-gray-100 h-px mb-2"></div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/captures?location_id=${pin.id}`);
                      }}
                      className="w-full bg-brand-50 hover:bg-brand-100 text-brand-700 text-xs font-bold py-2 rounded-lg flex justify-center items-center transition-colors"
                    >
                      <Camera className="w-3 h-3 mr-1.5" /> View Captures
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Optional Sidebar for Location List */}
          <div className="hidden xl:flex w-72 bg-white rounded-2xl shadow-sm border border-gray-200 flex-col overflow-hidden">
            <div className="bg-gray-50 p-4 border-b border-gray-200 flex items-center">
              <List className="w-5 h-5 text-gray-500 mr-2" />
              <h3 className="font-bold text-gray-800">Locations ({pins.length})</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {pins.map((pin, index) => (
                <div key={pin.id} className="p-3 hover:bg-brand-50 rounded-lg cursor-pointer transition-colors border border-transparent hover:border-brand-100 flex items-center text-sm font-medium text-gray-700 group">
                  <div className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 flex-shrink-0">
                    {index + 1}
                  </div>
                  <span className="flex-1 truncate">{pin.label}</span>
                  <button onClick={() => navigate(`/captures?location_id=${pin.id}`)} className="text-brand-600 hover:text-brand-800 p-1 opacity-0 group-hover:opacity-100 transition-opacity" title="View Captures">
                    <Camera className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white p-6 rounded-2xl shadow-sm border border-gray-200 gap-6 mb-8">
        <div className="flex flex-col w-full sm:w-1/2 md:w-1/3">
          <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Construction Site</label>
          <div className="relative">
            <select 
              className="appearance-none w-full bg-gray-50 border border-gray-200 text-gray-900 font-bold text-lg py-3 px-4 rounded-xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 transition-all cursor-pointer shadow-sm hover:bg-white"
              value={selectedSiteId || ''}
              onChange={(e) => setSelectedSiteId(e.target.value)}
            >
              {sites.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>
        <button onClick={() => setShowUploadModal(true)} className="btn-primary flex items-center shadow-lg hover:shadow-xl py-3 px-6 w-full sm:w-auto justify-center rounded-xl font-bold text-base transition-all hover:-translate-y-0.5">
          <Upload className="w-5 h-5 mr-2" />
          Upload Floor Plan
        </button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-black text-gray-900 tracking-tight">Floor Plans</h2>
          <p className="text-gray-500 mt-1 font-medium">Manage interactive maps and location pins for {sites.find(s => s.id === selectedSiteId)?.name || 'this site'}.</p>
        </div>
        <div className="hidden sm:flex items-center bg-brand-50 text-brand-700 px-4 py-2 rounded-lg font-bold text-sm border border-brand-100 shadow-sm">
          <Map className="w-4 h-4 mr-2 opacity-70" />
          {plans.length} {plans.length === 1 ? 'Plan' : 'Plans'} Total
        </div>
      </div>

      {plans.length === 0 && !loading ? (
        <div className="card py-16 text-center">
          <Map className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-gray-900 mb-2">No floor plans yet</h3>
          <p className="text-gray-500 mb-6">Upload your first floor plan to get started</p>
          <button onClick={() => setShowUploadModal(true)} className="btn-primary px-6 py-2.5">Upload Floor Plan</button>
        </div>
      ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {plans.map(p => (
          <div key={p.id} className="card p-0 overflow-hidden group hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-gray-200">
            <div className="h-56 bg-gray-200 relative border-b border-gray-100 overflow-hidden">
              {p.image_url?.toLowerCase().endsWith('.pdf') ? (
                <div className="flex items-center justify-center h-full bg-gray-100">
                  <div className="text-center">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">PDF Document</p>
                  </div>
                </div>
              ) : (
                <img src={p.image_url} alt={p.label} className="w-full h-full object-cover opacity-90 group-hover:scale-105 group-hover:opacity-100 transition-all duration-500" />
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="absolute top-4 right-4 bg-white/95 backdrop-blur text-gray-900 text-xs font-black px-3 py-1.5 rounded-lg shadow-sm flex items-center uppercase tracking-wider">
                <MapPin className="w-3 h-3 mr-1.5 text-brand-600" />
                Pins
              </div>
            </div>
            <div className="p-5 flex justify-between items-center bg-white">
              <h3 className="font-black text-gray-900 text-xl">{p.label}</h3>
              <div className="flex items-center gap-2">
                {isAdmin && (
                  <button 
                    onClick={(e) => handleDeletePlan(e, p.id)} 
                    className="flex items-center justify-center p-2 text-red-500 hover:text-white bg-red-50 hover:bg-red-500 rounded-lg transition-colors shadow-sm"
                    title="Delete Floor Plan"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <button onClick={() => openPlan(p)} className="flex items-center text-sm font-bold text-brand-700 hover:text-white bg-brand-50 hover:bg-brand-600 px-4 py-2 rounded-lg transition-colors shadow-sm">
                  <Eye className="w-4 h-4 mr-2" /> View Map
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md animate-fade-in">
            <div className="flex items-center mb-6">
              <Upload className="w-6 h-6 text-brand-600 mr-2" />
              <h3 className="text-2xl font-bold text-gray-900">Upload Floor Plan</h3>
            </div>
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Label (e.g. Level 1)
                </label>
                <input
                  type="text"
                  value={uploadLabel}
                  onChange={(e) => {
                    console.log('Label changed:', e.target.value);
                    setUploadLabel(e.target.value);
                  }}
                  placeholder="Level name..."
                  className="input w-full mb-4"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  File (JPG/PNG only (required for pin placement))
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".png,.jpg,.jpeg"
                  className="hidden"
                />
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  className={`border-2 border-dashed rounded-lg p-8 
                    text-center cursor-pointer transition-colors
                    ${isDragging 
                      ? 'border-brand-500 bg-brand-50' 
                      : 'border-gray-300 hover:border-brand-400 hover:bg-gray-50'}`}
                >
                  {uploadFile ? (
                    <div>
                      <p className="text-brand-600 font-medium">
                        {uploadFile.name}
                      </p>
                      <p className="text-gray-500 text-sm mt-1">
                        {(uploadFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <p className="text-gray-400 text-xs mt-2">
                        Click to change file
                      </p>
                    </div>
                  ) : (
                    <div>
                      <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600">
                        Click to browse or drag and drop
                      </p>
                      <p className="text-gray-400 text-sm mt-1">
                        PNG, JPG up to 50MB
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-3 mt-6 pt-5 border-t border-gray-100">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadFile(null);
                  setUploadLabel('');
                }}
                className="px-5 py-2.5 font-bold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={!uploadFile || uploading}
                className="btn-primary px-6 py-2.5 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : 'Upload Plan'}
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Debug: file={uploadFile ? uploadFile.name : 'none'} 
              | label={uploadLabel || 'empty'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FloorPlansPage;
