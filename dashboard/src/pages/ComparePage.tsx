import React, { useState, useEffect } from 'react';
import CompareViewer from '../components/CompareViewer';
import { useAuth } from '../context/AuthContext';
import { Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

const ComparePage: React.FC = () => {
  const { isAIPro } = useAuth();
  const [sites, setSites] = useState<any[]>([]);
  const [selectedSite, setSelectedSite] = useState('');
  
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionA, setSessionA] = useState<any>(null);
  const [sessionB, setSessionB] = useState<any>(null);
  
  const [isDetecting, setIsDetecting] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);

  useEffect(() => {
    document.title = "Compare | Space360";
    setSites([{ id: '1', name: 'Downtown Highrise' }]);
    
    // Mock sessions for demonstration
    const mockSessions = [
      { id: 's1', imageUrl: 'https://pannellum.org/images/alma.jpg', captured_at: '2023-10-01T10:00:00Z', location_label: 'Level 1 Center' },
      { id: 's2', imageUrl: 'https://pannellum.org/images/cerro-toco-0.jpg', captured_at: '2023-10-15T14:30:00Z', location_label: 'Level 1 Center' }
    ];
    setSessions(mockSessions);
    setSessionA(mockSessions[0]);
    setSessionB(mockSessions[1]);
  }, []);

  const handleRunAI = async () => {
    if (!sessionA || !sessionB) return;
    setIsDetecting(true);
    try {
      // Mock API call delay
      setTimeout(() => {
        setAiResult({
          summary: "Significant structural progress detected since last capture.",
          progress_indicator: "on_track",
          changes: [
            { description: "Concrete pillars poured", category: "structural", significance: "high" },
            { description: "HVAC ducting installed in ceiling", category: "mechanical", significance: "medium" }
          ]
        });
        toast.success("AI Change Detection completed");
        setIsDetecting(false);
      }, 2000);
      
    } catch (error) {
      toast.error('AI analysis failed');
      setIsDetecting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Select Location to Compare</h2>
        <div className="flex space-x-4">
          <select className="input max-w-xs" value={selectedSite} onChange={e => setSelectedSite(e.target.value)}>
            <option value="">Select Site...</option>
            {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        
        <div className="mt-6 flex space-x-4 overflow-x-auto pb-2">
          {sessions.map(s => (
            <div key={s.id} 
                 className={`min-w-[120px] p-2 border-2 rounded-lg cursor-pointer transition-colors ${
                   sessionA?.id === s.id ? 'border-brand-500 bg-brand-50' :
                   sessionB?.id === s.id ? 'border-gray-500 bg-gray-50' : 'border-transparent hover:border-brand-300'
                 }`}
                 onClick={() => {
                   if (sessionA?.id === s.id) setSessionA(null);
                   else if (sessionB?.id === s.id) setSessionB(null);
                   else if (!sessionA) setSessionA(s);
                   else setSessionB(s);
                 }}>
              <div className="h-16 bg-gray-200 rounded mb-2 overflow-hidden shadow-sm">
                <img src={s.imageUrl} className="object-cover w-full h-full" alt="thumb" />
              </div>
              <p className="text-xs font-medium text-center">{new Date(s.captured_at).toLocaleDateString()}</p>
              <div className="flex justify-center space-x-1 mt-1">
                {sessionA?.id === s.id && <span className="bg-brand-600 text-white text-[10px] px-1.5 rounded">A</span>}
                {sessionB?.id === s.id && <span className="bg-gray-600 text-white text-[10px] px-1.5 rounded">B</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {sessionA && sessionB && (
        <div className="space-y-6 animate-fade-in">
          <div className="card p-0 overflow-hidden shadow-lg border-gray-200 rounded-xl">
             <CompareViewer sessionA={sessionA} sessionB={sessionB} />
          </div>

          {isAIPro && (
            <div className="flex justify-center">
              <button 
                onClick={handleRunAI} 
                disabled={isDetecting}
                className="btn-primary flex items-center px-6 py-3 text-lg rounded-full shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:hover:translate-y-0"
              >
                <Sparkles className={`w-5 h-5 mr-2 ${isDetecting ? 'animate-spin' : ''}`} />
                {isDetecting ? 'Analyzing changes...' : 'Run AI Change Detection'}
              </button>
            </div>
          )}

          {aiResult && (
            <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100 shadow-sm rounded-xl">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <Sparkles className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">AI Analysis Results</h3>
              </div>
              <p className="text-gray-700 font-medium mb-6 text-lg">{aiResult.summary}</p>
              
              <div className="space-y-3">
                {aiResult.changes.map((change: any, i: number) => (
                  <div key={i} className="flex items-start bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                    <span className={`mt-0.5 px-2.5 py-1 text-xs font-bold rounded-full mr-4 shadow-sm border ${
                      change.significance === 'high' ? 'bg-red-50 text-red-700 border-red-200' :
                      change.significance === 'medium' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                      'bg-green-50 text-green-700 border-green-200'
                    }`}>
                      {change.category.toUpperCase()}
                    </span>
                    <p className="text-gray-800 text-sm leading-relaxed">{change.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ComparePage;
