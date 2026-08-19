import React, { useState, useEffect } from 'react';
import { Bookmark, Star, Trash2, Check, Plus, X } from 'lucide-react';
import toast from 'react-hot-toast';

export interface FilterPreset {
  id: string;
  name: string;
  filters: any;
  isFavorite: boolean;
  lastUsedAt: string;
}

interface Props {
  currentFilters: any;
  onLoadPreset: (filters: any) => void;
}

export default function FilterPresetManager({ currentFilters, onLoadPreset }: Props) {
  const [presets, setPresets] = useState<FilterPreset[]>([]);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('space360_filter_presets');
    if (saved) {
      try {
        setPresets(JSON.parse(saved));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  const savePresets = (newPresets: FilterPreset[]) => {
    setPresets(newPresets);
    localStorage.setItem('space360_filter_presets', JSON.stringify(newPresets));
  };

  const handleSavePreset = () => {
    if (!presetName.trim()) {
      toast.error('Preset name is required');
      return;
    }
    
    const newPreset: FilterPreset = {
      id: Date.now().toString(),
      name: presetName.trim(),
      filters: currentFilters,
      isFavorite: false,
      lastUsedAt: new Date().toISOString()
    };
    
    savePresets([...presets, newPreset]);
    setPresetName('');
    setShowSaveModal(false);
    toast.success('Preset saved');
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Delete this preset?')) {
      savePresets(presets.filter(p => p.id !== id));
      toast.success('Preset deleted');
    }
  };

  const handleToggleFavorite = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    savePresets(presets.map(p => p.id === id ? { ...p, isFavorite: !p.isFavorite } : p));
  };

  const handleApply = (preset: FilterPreset) => {
    savePresets(presets.map(p => p.id === preset.id ? { ...p, lastUsedAt: new Date().toISOString() } : p));
    onLoadPreset(preset.filters);
    setIsOpen(false);
    toast.success(`Applied preset: ${preset.name}`);
  };

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        <Bookmark className="w-4 h-4 text-brand-600" />
        Presets
      </button>

      {isOpen && (
        <div className="absolute right-0 z-50 w-64 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg">
          <div className="p-3 border-b border-gray-100 flex justify-between items-center">
            <h3 className="text-sm font-bold text-gray-900">Saved Presets</h3>
            <button 
              onClick={() => setShowSaveModal(true)}
              className="text-xs text-brand-600 hover:text-brand-800 flex items-center font-medium"
            >
              <Plus className="w-3 h-3 mr-0.5" /> Save Current
            </button>
          </div>
          
          <div className="max-h-60 overflow-y-auto p-2">
            {presets.length === 0 ? (
              <div className="text-center py-4 text-sm text-gray-500 italic">No presets saved.</div>
            ) : (
              <div className="space-y-1">
                {presets.sort((a, b) => (b.isFavorite ? 1 : 0) - (a.isFavorite ? 1 : 0)).map(preset => (
                  <div 
                    key={preset.id}
                    onClick={() => handleApply(preset)}
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer group transition-colors"
                  >
                    <div className="flex items-center gap-2 overflow-hidden">
                      <button 
                        onClick={(e) => handleToggleFavorite(preset.id, e)}
                        className={`shrink-0 ${preset.isFavorite ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-400'}`}
                      >
                        <Star className="w-4 h-4 fill-current" />
                      </button>
                      <span className="text-sm font-medium text-gray-700 truncate">{preset.name}</span>
                    </div>
                    <button 
                      onClick={(e) => handleDelete(preset.id, e)}
                      className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {showSaveModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm overflow-hidden animate-fade-in">
            <div className="flex justify-between items-center p-4 border-b border-gray-100 bg-gray-50">
              <h3 className="font-bold text-gray-900">Save Filter Preset</h3>
              <button onClick={() => setShowSaveModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Preset Name</label>
                <input 
                  type="text" 
                  value={presetName}
                  onChange={(e) => setPresetName(e.target.value)}
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && handleSavePreset()}
                  className="input w-full"
                  placeholder="e.g., Critical Safety Issues"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button onClick={() => setShowSaveModal(false)} className="btn-secondary">Cancel</button>
                <button onClick={handleSavePreset} className="btn-primary flex items-center">
                  <Check className="w-4 h-4 mr-1.5" /> Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
