import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Sparkles, BarChart, Mic, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';
import { getAllSessions, getAuthHeaders } from '../services/api';

const AIFeaturesPage: React.FC = () => {
  const { isAIPro } = useAuth();
  const [sessions, setSessions] = useState<any[]>([]);

  useEffect(() => {
    document.title = "AI Features | Space360";
    const fetchSessions = async () => {
      try {
        const res = await getAllSessions();
        const sortedSessions = (res.data || []).sort((a: any, b: any) => 
          new Date(b.captured_at).getTime() - new Date(a.captured_at).getTime()
        );
        setSessions(sortedSessions);
      } catch (error) {
        console.error("Failed to fetch sessions", error);
      }
    };
    if (isAIPro) {
      fetchSessions();
    }
  }, [isAIPro]);

  // Change Detection State
  const [cdSessionA, setCdSessionA] = useState('');
  const [cdSessionB, setCdSessionB] = useState('');
  const [cdLoading, setCdLoading] = useState(false);
  const [cdResult, setCdResult] = useState<any>(null);

  const runChangeDetection = async () => {
    if (!cdSessionA || !cdSessionB) return;
    setCdLoading(true);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch(`http://localhost:8000/ai/change-detection?session_a_id=${cdSessionA}&session_b_id=${cdSessionB}`, {
        method: 'POST',
        headers: { ...headers }
      });
      if (!res.ok) throw new Error("Failed to detect changes");
      const data = await res.json();
      setCdResult(data);
      toast.success("Change detection complete");
    } catch (error) {
      console.error(error);
      toast.error("AI Analysis failed");
    } finally {
      setCdLoading(false);
    }
  };

  // Progress Estimation State
  const [peSession, setPeSession] = useState('');
  const [peLoading, setPeLoading] = useState(false);
  const [peResult, setPeResult] = useState<any>(null);

  const runProgressEstimation = async () => {
    if (!peSession) return;
    setPeLoading(true);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch(`http://localhost:8000/ai/progress-estimation/${peSession}`, {
        method: 'POST',
        headers: { ...headers }
      });
      if (!res.ok) throw new Error("Failed to estimate progress");
      const data = await res.json();
      setPeResult(data);
      toast.success("Progress estimated");
    } catch (error) {
      console.error(error);
      toast.error("AI Analysis failed");
    } finally {
      setPeLoading(false);
    }
  };

  if (!isAIPro) {
    return (
      <div className="card text-center py-20 bg-gradient-to-br from-indigo-50 to-blue-50">
        <Sparkles className="w-16 h-16 text-blue-500 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Upgrade to AI Pro</h2>
        <p className="text-gray-600 max-w-md mx-auto mb-8">
          Unlock advanced features like Change Detection, Progress Estimation, Voice Transcription, and Site Q&A powered by Google Gemini 2.0 Flash.
        </p>
        <button className="btn-primary px-8 py-3 text-lg rounded-full shadow-lg">Upgrade Now</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">AI Features (Powered by Gemini 2.0 Flash)</h2>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* Card 1: Change Detection */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-blue-500">
          <div className="flex items-center mb-2">
            <Sparkles className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Change Detection</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Compare two captures and let Gemini 2.0 list all visible changes.</p>
          
          <div className="space-y-4 mb-6 flex-1">
            <select className="input w-full" value={cdSessionA} onChange={e => setCdSessionA(e.target.value)}>
              <option value="">Select Base Capture (A)...</option>
              {sessions.map(s => <option key={s.id} value={s.id}>{new Date(s.captured_at).toLocaleDateString()} - {s.location_label}</option>)}
            </select>
            <select className="input w-full" value={cdSessionB} onChange={e => setCdSessionB(e.target.value)}>
              <option value="">Select New Capture (B)...</option>
              {sessions.map(s => <option key={s.id} value={s.id}>{new Date(s.captured_at).toLocaleDateString()} - {s.location_label}</option>)}
            </select>
            <button onClick={runChangeDetection} disabled={cdLoading || !cdSessionA || !cdSessionB} className="btn-primary w-full flex justify-center items-center py-2.5">
              {cdLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div> : <Sparkles className="w-4 h-4 mr-2" />}
              {cdLoading ? "Gemini is analyzing..." : "Analyse Changes"}
            </button>
          </div>

          {cdResult && (
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 animate-fade-in shadow-inner">
              <h4 className="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wider">Results</h4>
              <p className="text-sm font-semibold text-brand-700 bg-brand-50 p-3 rounded-lg border border-brand-100 mb-4">{cdResult.summary}</p>
              
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4">
                <span className="text-sm font-bold text-gray-700 block mb-2">Estimated Progress</span>
                <div className="flex items-center">
                  <div className="w-full bg-gray-200 rounded-full h-2.5 mr-3">
                    <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${cdResult.progress_percentage || 0}%` }}></div>
                  </div>
                  <span className="text-sm font-bold text-gray-900">{cdResult.progress_percentage || 0}%</span>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-sm font-bold text-gray-700 block mb-1">Identified Changes:</span>
                {(cdResult.changes || []).map((c: string, i: number) => (
                  <div key={i} className="flex items-start bg-white p-3 rounded-lg shadow-sm border border-gray-100">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 mr-2 shrink-0"></div>
                    <span className="text-sm text-gray-700">{c}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Card 2: Progress Estimation */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-green-500">
          <div className="flex items-center mb-2">
            <BarChart className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Progress Estimation</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Estimate completion % and categorize work status for a capture using AI vision.</p>
          
          <div className="space-y-4 mb-6 flex-1">
            <select className="input w-full" value={peSession} onChange={e => setPeSession(e.target.value)}>
              <option value="">Select Capture...</option>
              {sessions.map(s => <option key={s.id} value={s.id}>{new Date(s.captured_at).toLocaleDateString()} - {s.location_label}</option>)}
            </select>
            <button onClick={runProgressEstimation} disabled={peLoading || !peSession} className="btn-primary bg-green-600 hover:bg-green-700 w-full flex justify-center items-center py-2.5 shadow-md">
              {peLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div> : <BarChart className="w-4 h-4 mr-2" />}
              {peLoading ? "Gemini is analyzing..." : "Estimate Progress"}
            </button>
          </div>

          {peResult && (
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 animate-fade-in shadow-inner">
              <div className="text-center mb-6">
                <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-emerald-700">{peResult.progress_percentage || 0}%</div>
                <div className="text-sm font-semibold text-gray-500 uppercase tracking-widest mt-1">Overall Progress</div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                  <span className="text-xs font-bold text-green-700 uppercase tracking-wider mb-2 block border-b border-gray-100 pb-1">Completed</span>
                  <ul className="list-disc pl-4 text-sm text-gray-700 space-y-1">
                    {(peResult.completed || []).map((item: string, i: number) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
                
                <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                  <span className="text-xs font-bold text-yellow-700 uppercase tracking-wider mb-2 block border-b border-gray-100 pb-1">In Progress</span>
                  <ul className="list-disc pl-4 text-sm text-gray-700 space-y-1">
                    {(peResult.in_progress || []).map((item: string, i: number) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
                
                <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                  <span className="text-xs font-bold text-red-700 uppercase tracking-wider mb-2 block border-b border-gray-100 pb-1">Pending</span>
                  <ul className="list-disc pl-4 text-sm text-gray-700 space-y-1">
                    {(peResult.pending || []).map((item: string, i: number) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Card 3: Voice Note Transcription (Coming Soon) */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-purple-500 relative overflow-hidden">
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex items-center justify-center">
            <span className="bg-purple-600 text-white px-4 py-2 rounded-full font-bold shadow-lg transform -rotate-12 border-2 border-white">Coming Soon</span>
          </div>
          <div className="flex items-center mb-2">
            <Mic className="w-6 h-6 text-purple-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Voice Note Transcription</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Transcribe field voice notes and extract key information.</p>
          <div className="space-y-4 mb-6 flex-1 opacity-50">
            <input type="text" placeholder="Voice Note ID" className="input" disabled />
            <button className="btn-primary bg-purple-600 w-full flex justify-center items-center py-2.5 shadow-md" disabled>
              <Mic className="w-4 h-4 mr-2" /> Transcribe
            </button>
          </div>
        </div>

        {/* Card 4: Site Q&A (Coming Soon) */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-orange-500 relative overflow-hidden">
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex items-center justify-center">
             <span className="bg-orange-500 text-white px-4 py-2 rounded-full font-bold shadow-lg transform -rotate-12 border-2 border-white">Coming Soon</span>
          </div>
          <div className="flex items-center mb-2">
            <MessageSquare className="w-6 h-6 text-orange-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Site Q&A</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Ask questions about your site in plain English.</p>
          <div className="space-y-4 mb-6 flex-1 opacity-50">
            <input type="text" placeholder="Site ID" className="input" disabled />
            <textarea placeholder="Ask a question..." className="input h-24 resize-none" disabled />
            <button className="btn-primary bg-orange-500 w-full flex justify-center items-center py-2.5 shadow-md" disabled>
              <MessageSquare className="w-4 h-4 mr-2" /> Ask AI
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AIFeaturesPage;
