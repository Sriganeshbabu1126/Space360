import React, { useState, useEffect, useRef } from 'react';
import { X, Calendar, MapPin, AlertCircle, Image as ImageIcon, Trash2 } from 'lucide-react';
import { getContractors } from '../services/api';
import toast from 'react-hot-toast';
import ImageMarkupCanvas from './ImageMarkupCanvas';
import Viewer360 from './Viewer360';
import { Camera } from 'lucide-react';

interface Contractor {
  id: string;
  name: string;
  company?: string;
  trade?: string;
  access_level: string;
}

export interface CaptureData {
  id: string;
  image_url: string;
  captured_at: string;
  location_name: string;
  frame_a_id?: string;
  frame_timestamp?: number;
}

interface CreateIssueModalProps {
  captureData: CaptureData;
  captureId: string;
  onClose: () => void;
  onSubmit: (data: any) => void;
}

const CreateIssueModal: React.FC<CreateIssueModalProps> = ({
  captureData,
  captureId,
  onClose,
  onSubmit
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [issueType, setIssueType] = useState('defect');
  const [initialComment, setInitialComment] = useState('');
  
  const [contractors, setContractors] = useState<Contractor[]>([]);
  const [selectedContractors, setSelectedContractors] = useState<string[]>([]);
  
  const [selectedPhotos, setSelectedPhotos] = useState<File[]>([]);
  const photoInputRef = useRef<HTMLInputElement>(null);
  
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [markupImageUrl, setMarkupImageUrl] = useState<string | null>(null);
  const [showMarkupEditor, setShowMarkupEditor] = useState(false);
  const [showClipCapture, setShowClipCapture] = useState(false);
  const [clipImageUrl, setClipImageUrl] = useState<string | null>(null);

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

  const handlePhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      const validFiles = newFiles.filter(f => {
        if (f.size > 5 * 1024 * 1024) {
          toast.error(`${f.name} exceeds 5MB limit`);
          return false;
        }
        if (!f.type.includes('image/jpeg') && !f.type.includes('image/png')) {
          toast.error(`${f.name} is not a valid JPG/PNG`);
          return false;
        }
        return true;
      });
      setSelectedPhotos(prev => [...prev, ...validFiles]);
    }
  };

  const removePhoto = (index: number) => {
    setSelectedPhotos(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !initialComment.trim()) {
      toast.error('Title and Initial Comment are required');
      return;
    }
    
    setIsSubmitting(true);
    try {
      await onSubmit({
        title,
        description,
        issue_type: issueType,
        initial_comment: initialComment,
        contractor_ids: selectedContractors,
        selected_photos: selectedPhotos,
        markup_image_url: markupImageUrl
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const viewer360Ref = useRef<any>(null);

  const handleCaptureView = async () => {
    try {
      if (viewer360Ref.current) {
        const dataUrl = await viewer360Ref.current.captureSnapshot();
        if (dataUrl) {
          setClipImageUrl(dataUrl);
          setShowClipCapture(false);
          setShowMarkupEditor(true);
          return;
        }
      }
      toast.error("Could not capture view");
    } catch (error) {
      console.error(error);
      toast.error("Failed to capture screen");
    }
  };

  return (
    <>
      <div 
        className="fixed inset-0 flex items-center justify-center bg-black"
        style={{ 
          zIndex: showClipCapture ? 60 : -1,
          opacity: showClipCapture ? 1 : 0,
          pointerEvents: showClipCapture ? 'auto' : 'none',
          visibility: showClipCapture ? 'visible' : 'hidden'
        }}
      >
        <div className="w-full h-full relative flex flex-col">
          <div className="flex justify-between items-center px-6 py-4 bg-gradient-to-b from-black/80 to-transparent absolute top-0 left-0 right-0 z-10">
            <h2 className="text-xl font-bold text-white flex items-center drop-shadow-md">
              <Camera className="w-5 h-5 mr-2" />
              Frame Your Shot
            </h2>
            <button onClick={() => setShowClipCapture(false)} className="text-white/80 hover:text-white bg-black/40 hover:bg-black/60 p-2 rounded-xl transition-colors backdrop-blur-sm">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 w-full h-full flex flex-col">
            <Viewer360 
              ref={viewer360Ref}
              imageUrl={captureData.image_url} 
              id="clip-viewer" 
            />
          </div>

          <div className="absolute bottom-10 left-0 right-0 flex justify-center z-10 pointer-events-none">
            <button
              onClick={handleCaptureView}
              className="pointer-events-auto px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-full font-bold shadow-[0_0_20px_rgba(0,0,0,0.3)] transition-transform hover:scale-105 flex items-center gap-2 border border-white/20"
            >
              <Camera className="w-5 h-5" />
              📸 Capture This View & Markup
            </button>
          </div>
        </div>
      </div>

      {showMarkupEditor && (
        <div className="fixed inset-0 z-[60] bg-zinc-950 flex flex-col">
          <div className="flex-1 overflow-hidden relative w-full h-full bg-zinc-950">
            <ImageMarkupCanvas
              imageUrl={clipImageUrl || captureData.image_url}
              onSaveMarkup={(markupUrl) => {
                setMarkupImageUrl(markupUrl);
                setShowMarkupEditor(false);
              }}
              onClose={() => setShowMarkupEditor(false)}
            />
          </div>
        </div>
      )}

      <div 
        className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-sm md:p-4 md:overflow-y-auto"
        style={{ display: (showClipCapture || showMarkupEditor) ? 'none' : 'flex' }}
      >
      <div className="bg-white w-full h-full md:h-auto md:rounded-2xl shadow-2xl md:max-w-4xl flex flex-col md:flex-row overflow-hidden animate-fade-in md:border md:border-gray-100 md:my-8 relative">
        
        {/* Mobile Header with Close Button */}
        <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white shrink-0">
          <h2 className="text-lg font-bold text-gray-900">Create Issue</h2>
          <button onClick={onClose} className="p-2 -mr-2 text-gray-400 hover:text-gray-600 rounded-full min-h-[44px] min-w-[44px] flex items-center justify-center">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Left Panel - Image & Context */}
        <div className="w-full md:w-5/12 bg-gray-50 flex flex-col md:border-r border-b md:border-b-0 border-gray-200 shrink-0">
          <div className="hidden md:flex p-5 border-b border-gray-200 bg-white items-center">
            <h3 className="font-bold text-gray-900 flex items-center text-lg">
              <ImageIcon className="w-5 h-5 mr-2 text-brand-600" />
              Capture Reference
            </h3>
          </div>
          
          <div className="flex-1 p-4 md:p-5 space-y-4 md:space-y-5">
            <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm bg-gray-100 aspect-video relative flex items-center justify-center">
              {captureData.image_url ? (
                <img 
                  src={captureData.image_url} 
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
            
            {!markupImageUrl ? (
              <button
                type="button"
                onClick={() => {
                  setShowClipCapture(true);
                  // Force a resize event after a slight delay so Pannellum recalculates its container bounds
                  setTimeout(() => window.dispatchEvent(new Event('resize')), 100);
                }}
                className="w-full py-3 md:py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 text-sm font-medium shadow-sm transition-colors flex items-center justify-center min-h-[44px]"
              >
                ✏️ Markup Image (Optional)
              </button>
            ) : (
              <div className="relative rounded-xl overflow-hidden border-2 border-brand-500 shadow-md">
                <div className="absolute top-0 left-0 bg-brand-500 text-white text-xs px-2 py-1 font-bold rounded-br-lg z-10">
                  Marked Up
                </div>
                <img src={markupImageUrl} alt="Marked up" className="w-full h-auto" />
                <button
                  type="button"
                  onClick={() => setMarkupImageUrl(null)}
                  className="absolute top-2 right-2 bg-black/60 hover:bg-red-500 text-white p-1.5 rounded-full transition-colors backdrop-blur-sm min-h-[44px] min-w-[44px] flex items-center justify-center"
                  title="Remove Markup"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
            
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Location Context</h4>
              <div className="flex items-center text-sm font-medium text-gray-800">
                <MapPin className="w-4 h-4 mr-2 text-brand-500 shrink-0" />
                {captureData.location_name}
              </div>
              <div className="flex items-center text-sm text-gray-600 mt-2">
                <Calendar className="w-4 h-4 mr-2 text-gray-400 shrink-0" />
                {new Date(captureData.captured_at).toLocaleString()}
              </div>
              {captureData.frame_timestamp !== undefined && (
                <div className="text-sm text-brand-600 font-bold flex items-center mt-1">
                  <Camera className="w-3 h-3 mr-1" />
                  Frame at {captureData.frame_timestamp}s
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Right Panel - Form Fields */}
        <div className="w-full md:w-7/12 flex flex-col bg-white overflow-hidden">
          <div className="hidden md:flex justify-between items-center p-5 border-b border-gray-100 bg-white shrink-0">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-brand-600" />
              Log New Issue
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-100 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-white">
            <form id="create-issue-form" onSubmit={handleSubmit} className="space-y-5">
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Issue Title <span className="text-red-500">*</span>
                </label>
                <input 
                  type="text" 
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Scratched drywall near entrance"
                  className="w-full px-4 py-3 md:py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow min-h-[44px]"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Issue Type <span className="text-red-500">*</span>
                  </label>
                  <select 
                    value={issueType}
                    onChange={(e) => setIssueType(e.target.value)}
                    className="w-full px-4 py-3 md:py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 bg-white min-h-[44px]"
                  >
                    <option value="defect">Defect</option>
                    <option value="safety_issue">Safety Issue</option>
                    <option value="quality_issue">Quality Issue</option>
                    <option value="incomplete_work">Incomplete Work</option>
                    <option value="rework_required">Rework Required</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Description (Optional)
                </label>
                <textarea 
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Provide additional details..."
                  className="w-full px-4 py-3 md:py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Evidence Photos (Optional)
                </label>
                <input 
                  type="file" 
                  multiple 
                  accept=".jpg,.jpeg,.png"
                  ref={photoInputRef}
                  onChange={handlePhotoSelect}
                  className="hidden" 
                />
                <button 
                  type="button" 
                  onClick={() => photoInputRef.current?.click()}
                  className="w-full py-3 md:py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:text-brand-600 hover:border-brand-500 hover:bg-brand-50 transition-colors flex items-center justify-center text-sm font-medium min-h-[44px]"
                >
                  <ImageIcon className="w-5 h-5 md:w-4 md:h-4 mr-2" />
                  + Add Photo
                </button>
                
                {selectedPhotos.length > 0 && (
                  <div className="mt-3 flex gap-3 md:gap-2 overflow-x-auto pb-2 snap-x">
                    {selectedPhotos.map((photo, idx) => (
                      <div key={idx} className="relative shrink-0 snap-start">
                        <img 
                          src={URL.createObjectURL(photo)} 
                          alt="Preview" 
                          className="w-20 h-20 md:w-16 md:h-16 object-cover rounded-lg border border-gray-200"
                        />
                        <button 
                          type="button"
                          onClick={() => removePhoto(idx)}
                          className="absolute -top-2 -right-2 md:-top-1.5 md:-right-1.5 bg-red-500 text-white rounded-full p-1.5 hover:bg-red-600 shadow-sm min-h-[32px] min-w-[32px] flex items-center justify-center"
                        >
                          <X className="w-3 h-3 md:w-3 md:h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
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
                  className="w-full px-4 py-3 md:py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow resize-none"
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
                      <label key={c.id} className="flex items-center p-3 hover:bg-brand-50 transition-colors cursor-pointer group min-h-[44px]">
                        <input 
                          type="checkbox" 
                          checked={selectedContractors.includes(c.id)}
                          onChange={() => handleContractorToggle(c.id)}
                          className="w-5 h-5 md:w-4 md:h-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500 mr-3"
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
          
          <div className="p-4 md:px-6 md:py-4 border-t border-gray-100 bg-gray-50 flex flex-col-reverse md:flex-row justify-end md:space-x-3 md:rounded-br-2xl shrink-0 gap-3 md:gap-0 mt-auto">
            <button 
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="w-full md:w-auto px-5 py-3 md:py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 min-h-[44px]"
            >
              Cancel
            </button>
            <button 
              type="submit"
              form="create-issue-form"
              disabled={isSubmitting}
              className="w-full md:w-auto px-5 py-3 md:py-2.5 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors shadow-sm disabled:opacity-50 flex items-center justify-center min-h-[44px]"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Uploading...
                </>
              ) : (
                'Create Issue'
              )}
            </button>
          </div>
          
        </div>
      </div>
    </div>
    </>
  );
};

export default CreateIssueModal;
