import React, { useState, useEffect } from 'react';
import { X, Calendar, MapPin, AlertCircle, Image as ImageIcon } from 'lucide-react';
import { getContractors } from '../services/api';
import toast from 'react-hot-toast';

interface Contractor {
  id: string;
  name: string;
  company?: string;
  trade?: string;
  access_level: string;
}

interface CreateIssueModalProps {
  capture_url: string;
  captured_at: string;
  location_label: string;
  onClose: () => void;
  onSubmit: (data: any) => void;
}

const CreateIssueModal: React.FC<CreateIssueModalProps> = ({
  capture_url,
  captured_at,
  location_label,
  onClose,
  onSubmit
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [initialComment, setInitialComment] = useState('');
  
  const [contractors, setContractors] = useState<Contractor[]>([]);
  const [selectedContractors, setSelectedContractors] = useState<string[]>([]);
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContractors = async () => {
      try {
        const res = await getContractors();
        setContractors(res.data);
      } catch (error) {
        console.error("Failed to load contractors", error);
        toast.error("Failed to load contractors list");
      } finally {
        setLoading(false);
      }
    };
    fetchContractors();
  }, []);

  const handleContractorToggle = (id: string) => {
    setSelectedContractors(prev => 
      prev.includes(id) ? prev.filter(cId => cId !== id) : [...prev, id]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !initialComment.trim()) {
      toast.error('Title and Initial Comment are required');
      return;
    }
    
    onSubmit({
      title,
      description,
      initial_comment: initialComment,
      contractor_ids: selectedContractors
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl flex flex-col md:flex-row overflow-hidden animate-fade-in border border-gray-100 my-8">
        
        {/* Left Panel - Image & Context */}
        <div className="w-full md:w-5/12 bg-gray-50 flex flex-col border-r border-gray-200">
          <div className="p-5 border-b border-gray-200 bg-white">
            <h3 className="font-bold text-gray-900 flex items-center text-lg">
              <ImageIcon className="w-5 h-5 mr-2 text-brand-600" />
              Capture Reference
            </h3>
          </div>
          
          <div className="flex-1 p-5 space-y-5">
            <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm bg-gray-100 aspect-video md:aspect-square relative flex items-center justify-center">
              {capture_url ? (
                <img 
                  src={capture_url} 
                  alt="Capture context" 
                  className="absolute inset-0 w-full h-full object-cover"
                />
              ) : (
                <div className="text-gray-400 flex flex-col items-center">
                  <ImageIcon className="w-10 h-10 mb-2 opacity-50" />
                  <span className="text-sm">No image available</span>
                </div>
              )}
            </div>
            
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm space-y-3">
              <div className="flex items-start">
                <MapPin className="w-4 h-4 mr-2 text-gray-400 mt-0.5" />
                <div>
                  <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">Location</div>
                  <div className="text-sm font-semibold text-gray-900">{location_label}</div>
                </div>
              </div>
              
              <div className="flex items-start">
                <Calendar className="w-4 h-4 mr-2 text-gray-400 mt-0.5" />
                <div>
                  <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">Captured On</div>
                  <div className="text-sm font-semibold text-gray-900">
                    {new Date(captured_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right Panel - Form */}
        <div className="w-full md:w-7/12 flex flex-col bg-white">
          <div className="flex justify-between items-center px-6 py-5 border-b border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-brand-600" />
              Create Issue
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-700 hover:bg-gray-100 p-2 rounded-xl transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6">
            <form id="create-issue-form" onSubmit={handleSubmit} className="space-y-6">
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Issue Title <span className="text-red-500">*</span>
                </label>
                <input 
                  type="text" 
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Exposed wiring in ceiling"
                  className="w-full px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Description
                </label>
                <textarea 
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Provide additional details about the issue..."
                  className="w-full px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Initial Comment <span className="text-red-500">*</span>
                </label>
                <p className="text-xs text-gray-500 mb-2">This will be added as the first comment to start the discussion.</p>
                <textarea 
                  required
                  rows={2}
                  value={initialComment}
                  onChange={(e) => setInitialComment(e.target.value)}
                  placeholder="What action needs to be taken?"
                  className="w-full px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Assign Contractors
                </label>
                {loading ? (
                  <div className="text-sm text-gray-500">Loading contractors...</div>
                ) : contractors.length === 0 ? (
                  <div className="text-sm text-gray-500 italic bg-gray-50 p-3 rounded-lg border border-gray-200">No contractors found.</div>
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-xl overflow-hidden max-h-48 overflow-y-auto divide-y divide-gray-100">
                    {contractors.map(c => (
                      <label key={c.id} className="flex items-center p-3 hover:bg-brand-50 transition-colors cursor-pointer group">
                        <input 
                          type="checkbox" 
                          checked={selectedContractors.includes(c.id)}
                          onChange={() => handleContractorToggle(c.id)}
                          className="w-4 h-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500 mr-3"
                        />
                        <div>
                          <div className="text-sm font-semibold text-gray-900 group-hover:text-brand-900">{c.name}</div>
                          <div className="text-xs text-gray-500">{c.company || c.trade || 'No company listed'}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>

            </form>
          </div>
          
          <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end space-x-3 rounded-br-2xl">
            <button 
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit"
              form="create-issue-form"
              className="px-5 py-2.5 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors shadow-sm"
            >
              Create Issue
            </button>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default CreateIssueModal;
