import React, { useEffect, useState, useRef } from 'react';
import { Upload, Eye, MapPin, Plus, List } from 'lucide-react';
import toast from 'react-hot-toast';

const FloorPlansPage: React.FC = () => {
  const [plans, setPlans] = useState<any[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<any>(null);
  
  const [isAddingPin, setIsAddingPin] = useState(false);
  const [pins, setPins] = useState<any[]>([]);
  
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    document.title = "Floor Plans | Space360";
    setPlans([
      { id: '1', label: 'Level 1', thumb: 'https://images.unsplash.com/photo-1598418042571-085e8d91240c?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', pinCount: 4 },
      { id: '2', label: 'Level 2', thumb: 'https://images.unsplash.com/photo-1598418042571-085e8d91240c?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', pinCount: 2 }
    ]);
  }, []);

  const openPlan = (plan: any) => {
    setSelectedPlan(plan);
    setPins([
      { id: 'p1', label: 'Lobby', x: 25, y: 40 },
      { id: 'p2', label: 'Elevator Bank', x: 50, y: 50 }
    ]);
  };

  const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
    if (!isAddingPin || !imageRef.current) return;
    
    const rect = imageRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    const label = prompt("Enter location label for this pin:");
    if (label) {
      setPins([...pins, { id: Date.now().toString(), label, x, y }]);
      toast.success("Location pin added");
    }
    setIsAddingPin(false);
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
            onClick={() => setIsAddingPin(!isAddingPin)} 
            className={`flex items-center px-5 py-2.5 rounded-xl font-bold transition-all shadow-sm ${
              isAddingPin ? 'bg-red-500 text-white hover:bg-red-600 shadow-red-200' : 'bg-brand-100 text-brand-700 hover:bg-brand-200 hover:-translate-y-0.5'
            }`}
          >
            {isAddingPin ? 'Cancel Pin Placement' : <><Plus className="w-5 h-5 mr-2" /> Add Location Pin</>}
          </button>
        </div>

        <div className="flex-1 card p-4 bg-gray-50 flex flex-col lg:flex-row items-stretch justify-center overflow-hidden gap-4">
          <div className="flex-1 relative inline-block max-w-full max-h-full border-4 border-white shadow-2xl rounded-2xl overflow-hidden bg-white">
            <img 
              ref={imageRef}
              src={selectedPlan.thumb} 
              alt="Floor Plan" 
              className={`w-full h-full object-cover transition-opacity duration-300 ${isAddingPin ? 'cursor-crosshair opacity-80' : 'cursor-default'}`}
              onClick={handleImageClick}
            />
            
            {isAddingPin && (
              <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur text-white px-4 py-2 rounded-full text-sm font-bold animate-pulse z-20 shadow-lg pointer-events-none">
                Click anywhere on the map to place a pin
              </div>
            )}

            {pins.map(pin => (
              <div 
                key={pin.id} 
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer transition-transform ${isAddingPin ? 'pointer-events-none opacity-50' : 'hover:scale-110 z-10'}`}
                style={{ left: `${pin.x}%`, top: `${pin.y}%` }}
                onClick={() => { if(!isAddingPin) toast('Opening timeline for ' + pin.label, { icon: '🕒' }) }}
              >
                <div className="relative flex flex-col items-center">
                  <div className="w-4 h-4 bg-white rounded-full absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 shadow-inner"></div>
                  <MapPin className="w-10 h-10 text-brand-600 drop-shadow-xl filter" strokeWidth={1.5} />
                  
                  <div className="absolute top-full mt-2 opacity-0 group-hover:opacity-100 transition-all duration-200 bg-gray-900/90 backdrop-blur text-white text-xs font-bold px-3 py-1.5 rounded-lg whitespace-nowrap z-20 shadow-xl border border-gray-700 pointer-events-none">
                    {pin.label}
                    <div className="w-2 h-2 bg-gray-900/90 absolute bottom-full left-1/2 -translate-x-1/2 rotate-45 border-t border-l border-gray-700"></div>
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
              {pins.map(pin => (
                <div key={pin.id} className="p-3 hover:bg-brand-50 rounded-lg cursor-pointer transition-colors border border-transparent hover:border-brand-100 flex items-center text-sm font-medium text-gray-700">
                  <MapPin className="w-4 h-4 text-brand-500 mr-3" />
                  {pin.label}
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
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white p-5 rounded-2xl shadow-sm border border-gray-200 gap-4">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-black text-gray-900">Floor Plans</h2>
          <select className="input min-w-[200px] bg-gray-50 font-medium"><option>Downtown Highrise</option></select>
        </div>
        <button onClick={() => setShowUploadModal(true)} className="btn-primary flex items-center shadow-md py-2.5">
          <Upload className="w-5 h-5 mr-2" />
          Upload Floor Plan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {plans.map(p => (
          <div key={p.id} className="card p-0 overflow-hidden group hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-gray-200">
            <div className="h-56 bg-gray-200 relative border-b border-gray-100 overflow-hidden">
              <img src={p.thumb} alt={p.label} className="w-full h-full object-cover opacity-90 group-hover:scale-105 group-hover:opacity-100 transition-all duration-500" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="absolute top-4 right-4 bg-white/95 backdrop-blur text-gray-900 text-xs font-black px-3 py-1.5 rounded-lg shadow-sm flex items-center uppercase tracking-wider">
                <MapPin className="w-3 h-3 mr-1.5 text-brand-600" />
                {p.pinCount} Pins
              </div>
            </div>
            <div className="p-5 flex justify-between items-center bg-white">
              <h3 className="font-black text-gray-900 text-xl">{p.label}</h3>
              <button onClick={() => openPlan(p)} className="flex items-center text-sm font-bold text-brand-700 hover:text-white bg-brand-50 hover:bg-brand-600 px-4 py-2 rounded-lg transition-colors shadow-sm">
                <Eye className="w-4 h-4 mr-2" /> View Map
              </button>
            </div>
          </div>
        ))}
      </div>

      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md animate-fade-in">
            <div className="flex items-center mb-6">
              <Upload className="w-6 h-6 text-brand-600 mr-2" />
              <h3 className="text-2xl font-bold text-gray-900">Upload Floor Plan</h3>
            </div>
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-1.5">Label <span className="font-normal text-gray-400">(e.g. Level 1)</span></label>
                <input type="text" className="input bg-gray-50 font-medium" placeholder="Level name..." />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-1.5">File <span className="font-normal text-gray-400">(PNG/JPG/PDF)</span></label>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer group">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2 group-hover:text-brand-500 transition-colors" />
                  <input type="file" className="block w-full text-sm text-gray-500 file:hidden cursor-pointer" />
                  <span className="text-sm font-medium text-brand-600">Click to browse</span> or drag and drop
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-8 pt-5 border-t border-gray-100">
              <button onClick={() => setShowUploadModal(false)} className="px-5 py-2.5 font-bold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
              <button onClick={() => { setShowUploadModal(false); toast.success("Floor plan uploaded") }} className="btn-primary px-6 py-2.5 shadow-md">Upload Plan</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FloorPlansPage;
