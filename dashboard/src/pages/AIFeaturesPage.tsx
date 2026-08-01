import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Sparkles, BarChart, Mic, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';
import StatusBadge from '../components/StatusBadge';
import ProgressBar from '../components/ProgressBar';

const AIFeaturesPage: React.FC = () => {
  const { isAIPro } = useAuth();

  useEffect(() => {
    document.title = "AI Features | Space360";
  }, []);

  const [cdSessionA, setCdSessionA] = useState('');
  const [cdSessionB, setCdSessionB] = useState('');
  const [cdLoading, setCdLoading] = useState(false);
  const [cdResult, setCdResult] = useState<any>(null);

  const runChangeDetection = () => {
    setCdLoading(true);
    setTimeout(() => {
      setCdResult({
        summary: "Detected new HVAC and drywall progress.",
        changes: [
          { category: 'mechanical', significance: 'high', desc: 'HVAC ducts installed' },
          { category: 'finishing', significance: 'medium', desc: 'Drywall framing started' },
          { category: 'safety', significance: 'low', desc: 'Scaffolding removed in zone 2' }
        ]
      });
      setCdLoading(false);
      toast.success("Change detection complete");
    }, 1500);
  };

  const [peSession, setPeSession] = useState('');
  const [peLoading, setPeLoading] = useState(false);
  const [peResult, setPeResult] = useState<any>(null);

  const runProgressEstimation = () => {
    setPeLoading(true);
    setTimeout(() => {
      setPeResult({
        overall: 65,
        stage: 'mep',
        summary: "MEP rough-ins are progressing on schedule.",
        zones: [
          { label: 'Framing', value: 100 },
          { label: 'Electrical', value: 80 },
          { label: 'Plumbing', value: 60 },
          { label: 'Drywall', value: 20 }
        ]
      });
      setPeLoading(false);
      toast.success("Progress estimated");
    }, 1500);
  };

  const [vnId, setVnId] = useState('');
  const [vnLoading, setVnLoading] = useState(false);
  const [vnResult, setVnResult] = useState<any>(null);

  const runTranscription = () => {
    setVnLoading(true);
    setTimeout(() => {
      setVnResult({
        transcript: "The electrical wiring in the north corridor is delayed due to missing materials. We need the conduit delivery by tomorrow to stay on schedule.",
        tags: [
          { type: 'issues', text: 'Delayed wiring' },
          { type: 'materials', text: 'Missing conduit' },
          { type: 'action items', text: 'Check delivery tomorrow' }
        ]
      });
      setVnLoading(false);
      toast.success("Transcription complete");
    }, 1500);
  };

  const getTagColor = (type: string) => {
    if (type === 'issues') return 'bg-red-100 text-red-800 border-red-200';
    if (type === 'materials') return 'bg-blue-100 text-blue-800 border-blue-200';
    if (type === 'trades') return 'bg-purple-100 text-purple-800 border-purple-200';
    if (type === 'action items') return 'bg-green-100 text-green-800 border-green-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const [qaSite, setQaSite] = useState('');
  const [qaQuestion, setQaQuestion] = useState('');
  const [qaLoading, setQaLoading] = useState(false);
  const [qaResult, setQaResult] = useState<any>(null);

  const runAskAI = () => {
    setQaLoading(true);
    setTimeout(() => {
      setQaResult({
        answer: "Based on the recent captures, the foundation work is complete in Zone A, but still pending in Zone B.",
        confidence: 'high',
        sessions: ['Session #1042', 'Session #1043']
      });
      setQaLoading(false);
      toast.success("AI responded");
    }, 1500);
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
      <h2 className="text-2xl font-bold text-gray-800">AI Features</h2>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* Card 1 */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-blue-500">
          <div className="flex items-center mb-2">
            <Sparkles className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Change Detection</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Compare two captures and detect what changed on site.</p>
          
          <div className="space-y-4 mb-6 flex-1">
            <input type="text" placeholder="Session A ID" className="input" value={cdSessionA} onChange={e => setCdSessionA(e.target.value)} />
            <input type="text" placeholder="Session B ID" className="input" value={cdSessionB} onChange={e => setCdSessionB(e.target.value)} />
            <button onClick={runChangeDetection} disabled={cdLoading || !cdSessionA || !cdSessionB} className="btn-primary w-full flex justify-center items-center py-2.5">
              {cdLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div> : <Sparkles className="w-4 h-4 mr-2" />}
              Detect Changes
            </button>
          </div>

          {cdResult && (
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 animate-fade-in shadow-inner">
              <h4 className="font-semibold text-gray-800 mb-4 text-sm uppercase tracking-wider">Results</h4>
              <div className="space-y-3 mb-4">
                {cdResult.changes.map((c: any, i: number) => (
                  <div key={i} className="flex flex-col bg-white p-3.5 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex space-x-2 mb-2">
                      <StatusBadge status={c.category} type="category" />
                      <StatusBadge status={c.significance} type="significance" />
                    </div>
                    <span className="text-sm text-gray-700 font-medium">{c.desc}</span>
                  </div>
                ))}
              </div>
              <p className="text-sm font-semibold text-brand-700 bg-brand-50 p-3 rounded-lg border border-brand-100">{cdResult.summary}</p>
            </div>
          )}
        </div>

        {/* Card 2 */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-green-500">
          <div className="flex items-center mb-2">
            <BarChart className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Progress Estimation</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Estimate completion % for a capture using AI vision.</p>
          
          <div className="space-y-4 mb-6 flex-1">
            <input type="text" placeholder="Session ID" className="input" value={peSession} onChange={e => setPeSession(e.target.value)} />
            <button onClick={runProgressEstimation} disabled={peLoading || !peSession} className="btn-primary bg-green-600 hover:bg-green-700 w-full flex justify-center items-center py-2.5 shadow-md">
              {peLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div> : <BarChart className="w-4 h-4 mr-2" />}
              Estimate Progress
            </button>
          </div>

          {peResult && (
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 text-center animate-fade-in shadow-inner">
              <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-emerald-700 mb-2">{peResult.overall}%</div>
              <div className="mb-6"><StatusBadge status={peResult.stage} type="stage" /></div>
              <div className="text-left space-y-2 mb-5 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                {peResult.zones.map((z: any, i: number) => (
                  <ProgressBar key={i} label={z.label} value={z.value} colorClass="bg-green-500" />
                ))}
              </div>
              <p className="text-sm font-semibold text-green-700 bg-green-50 p-3 rounded-lg border border-green-100">{peResult.summary}</p>
            </div>
          )}
        </div>

        {/* Card 3 */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-purple-500">
          <div className="flex items-center mb-2">
            <Mic className="w-6 h-6 text-purple-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Voice Note Transcription</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Transcribe field voice notes and extract key information.</p>
          
          <div className="space-y-4 mb-6 flex-1">
            <input type="text" placeholder="Voice Note ID" className="input" value={vnId} onChange={e => setVnId(e.target.value)} />
            <button onClick={runTranscription} disabled={vnLoading || !vnId} className="btn-primary bg-purple-600 hover:bg-purple-700 w-full flex justify-center items-center py-2.5 shadow-md">
              {vnLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div> : <Mic className="w-4 h-4 mr-2" />}
              Transcribe
            </button>
          </div>

          {vnResult && (
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 animate-fade-in shadow-inner">
              <div className="bg-white p-4 rounded-lg border border-gray-200 text-sm text-gray-800 italic mb-5 leading-relaxed shadow-sm">
                "{vnResult.transcript}"
              </div>
              <div className="flex flex-wrap gap-2">
                {vnResult.tags.map((t: any, i: number) => (
                  <span key={i} className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wide rounded-full border shadow-sm ${getTagColor(t.type)}`}>
                    {t.text}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Card 4 */}
        <div className="card flex flex-col shadow-md border-t-4 border-t-orange-500">
          <div className="flex items-center mb-2">
            <MessageSquare className="w-6 h-6 text-orange-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Site Q&A</h3>
          </div>
          <p className="text-sm text-gray-500 mb-6">Ask questions about your site in plain English.</p>
          
          <div className="space-y-4 mb-6 flex-1">
            <input type="text" placeholder="Site ID" className="input" value={qaSite} onChange={e => setQaSite(e.target.value)} />
            <textarea placeholder="Ask a question..." className="input h-24 resize-none" value={qaQuestion} onChange={e => setQaQuestion(e.target.value)} />
            <button onClick={runAskAI} disabled={qaLoading || !qaSite || !qaQuestion} className="btn-primary bg-orange-500 hover:bg-orange-600 w-full flex justify-center items-center py-2.5 shadow-md">
              {qaLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div> : <MessageSquare className="w-4 h-4 mr-2" />}
              Ask AI
            </button>
          </div>

          {qaResult && (
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 animate-fade-in shadow-inner flex flex-col">
              <div className="flex justify-between items-start mb-4">
                <StatusBadge status={qaResult.confidence} type="significance" />
              </div>
              <p className="text-xl font-semibold text-gray-800 mb-5 leading-snug">{qaResult.answer}</p>
              <div className="text-xs text-gray-500 bg-white p-3 rounded-lg border border-gray-200 mt-auto shadow-sm">
                <span className="font-bold text-gray-700 block mb-2 uppercase tracking-wide">Relevant Sessions:</span>
                <div className="flex flex-wrap gap-2">
                  {qaResult.sessions.map((s: string, i: number) => (
                    <span key={i} className="bg-gray-100 text-gray-600 px-2 py-1 rounded font-medium border border-gray-200">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default AIFeaturesPage;
