import React, { useEffect, useState } from 'react';
import { Camera, Filter, Upload, MapPin } from 'lucide-react';

const CapturesPage: React.FC = () => {
  const [captures, setCaptures] = useState<any[]>([]);

  useEffect(() => {
    document.title = "Captures | Space360";
    setCaptures([
      { id: '1', site: 'Downtown Highrise', location: 'Level 1 Center', date: 'Oct 15, 2023', ai_status: 'done', thumb: 'https://pannellum.org/images/alma.jpg' },
      { id: '2', site: 'Downtown Highrise', location: 'Level 2 North', date: 'Oct 16, 2023', ai_status: 'processing', thumb: 'https://pannellum.org/images/cerro-toco-0.jpg' },
      { id: '3', site: 'Westside Mall', location: 'Atrium', date: 'Oct 17, 2023', ai_status: 'pending', thumb: 'https://pannellum.org/images/jfk.jpg' }
    ]);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800">Site Captures</h2>
        <button className="btn-primary flex items-center shadow-md">
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

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {captures.map(c => (
          <div key={c.id} className="card p-0 overflow-hidden cursor-pointer hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
            <div className="h-48 relative overflow-hidden bg-gray-200">
              <img src={c.thumb} alt="thumbnail" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 ease-in-out" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <Camera className="w-10 h-10 text-white drop-shadow-md transform scale-50 group-hover:scale-100 transition-transform duration-300" />
              </div>
            </div>
            <div className="p-5">
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-bold text-gray-900 truncate pr-2 text-lg">{c.location}</h3>
                <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-md shadow-sm border ${
                  c.ai_status === 'done' ? 'bg-green-50 text-green-700 border-green-200' :
                  c.ai_status === 'processing' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                  'bg-gray-50 text-gray-700 border-gray-200'
                }`}>
                  {c.ai_status}
                </span>
              </div>
              <div className="flex items-center text-sm text-gray-500 mb-1.5">
                <MapPin className="w-4 h-4 mr-1.5 opacity-70" />
                <span className="truncate">{c.site}</span>
              </div>
              <p className="text-xs font-semibold text-gray-400 mt-3">{c.date}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CapturesPage;
