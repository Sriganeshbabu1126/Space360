import React, { useState } from 'react';
import { Search, Filter, X, ChevronDown, ChevronUp } from 'lucide-react';
import FilterPresetManager from './FilterPresetManager';

interface Props {
  onFilterChange: (filters: any) => void;
  sites: any[];
  contractors: any[];
  currentFilters: any;
}

export default function AdvancedFilterPanel({ onFilterChange, sites, contractors, currentFilters }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState(currentFilters);

  const statuses = ['open', 'in_review', 'pending', 'closed', 'critical'];
  const types = ['defect', 'safety_issue', 'quality_issue', 'incomplete_work', 'rework_required'];

  const handleApply = () => {
    onFilterChange(localFilters);
    setIsExpanded(false);
  };

  const handleClear = () => {
    const emptyFilters = {
      search_text: '',
      statuses: [],
      types: [],
      sites: [],
      contractors: [],
      date_start: '',
      date_end: ''
    };
    setLocalFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const toggleArrayItem = (key: string, value: string) => {
    setLocalFilters((prev: any) => {
      const current = prev[key] || [];
      const updated = current.includes(value) 
        ? current.filter((i: string) => i !== value)
        : [...current, value];
      return { ...prev, [key]: updated };
    });
  };

  const activeFilterCount = (localFilters.statuses?.length || 0) +
    (localFilters.types?.length || 0) +
    (localFilters.sites?.length || 0) +
    (localFilters.contractors?.length || 0) +
    (localFilters.date_start ? 1 : 0) +
    (localFilters.date_end ? 1 : 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col mb-6">
      {/* Search Bar & Basic Controls */}
      <div className="p-4 flex flex-col sm:flex-row gap-4 items-center border-b border-gray-100">
        <div className="relative flex-1 w-full">
          <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search issues in title, description, or comments..." 
            value={localFilters.search_text || ''}
            onChange={(e) => {
              const val = e.target.value;
              setLocalFilters((prev: any) => ({ ...prev, search_text: val }));
            }}
            onKeyDown={(e) => e.key === 'Enter' && handleApply()}
            className="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
          />
        </div>
        
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className={`flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg border transition-colors w-full sm:w-auto ${isExpanded ? 'bg-brand-50 text-brand-700 border-brand-200' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
          >
            <Filter className="w-4 h-4" />
            Filters {activeFilterCount > 0 && <span className="bg-brand-100 text-brand-700 px-1.5 py-0.5 rounded-full text-xs">{activeFilterCount}</span>}
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          <button 
            onClick={handleApply}
            className="btn-primary whitespace-nowrap py-2.5 px-6 shadow-sm"
          >
            Search
          </button>
        </div>
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="p-5 bg-gray-50/50">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Statuses */}
            <div>
              <h4 className="text-sm font-bold text-gray-900 mb-3">Status</h4>
              <div className="space-y-2">
                {statuses.map(s => (
                  <label key={s} className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                      checked={(localFilters.statuses || []).includes(s)}
                      onChange={() => toggleArrayItem('statuses', s)}
                    />
                    <span className="text-sm text-gray-700 capitalize">{s.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Types */}
            <div>
              <h4 className="text-sm font-bold text-gray-900 mb-3">Issue Type</h4>
              <div className="space-y-2">
                {types.map(t => (
                  <label key={t} className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                      checked={(localFilters.types || []).includes(t)}
                      onChange={() => toggleArrayItem('types', t)}
                    />
                    <span className="text-sm text-gray-700 capitalize">{t.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Sites & Contractors */}
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-bold text-gray-900 mb-2">Sites</h4>
                <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-md bg-white p-2 space-y-1">
                  {sites.map(site => (
                    <label key={site.id} className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="checkbox" 
                        className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                        checked={(localFilters.sites || []).includes(site.id)}
                        onChange={() => toggleArrayItem('sites', site.id)}
                      />
                      <span className="text-sm text-gray-700 truncate">{site.name}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-bold text-gray-900 mb-2">Assigned Contractors</h4>
                <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-md bg-white p-2 space-y-1">
                  {contractors.map(c => (
                    <label key={c.id} className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="checkbox" 
                        className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                        checked={(localFilters.contractors || []).includes(c.id)}
                        onChange={() => toggleArrayItem('contractors', c.id)}
                      />
                      <span className="text-sm text-gray-700 truncate">{c.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Dates & Actions */}
            <div className="flex flex-col justify-between h-full">
              <div className="space-y-4">
                <h4 className="text-sm font-bold text-gray-900 mb-2">Date Range</h4>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">From</label>
                  <input 
                    type="date" 
                    value={localFilters.date_start || ''}
                    onChange={(e) => setLocalFilters((prev: any) => ({ ...prev, date_start: e.target.value }))}
                    className="input w-full text-sm py-1.5"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">To</label>
                  <input 
                    type="date" 
                    value={localFilters.date_end || ''}
                    onChange={(e) => setLocalFilters((prev: any) => ({ ...prev, date_end: e.target.value }))}
                    className="input w-full text-sm py-1.5"
                  />
                </div>
              </div>
              
              <div className="mt-6 flex items-center justify-between pt-4 border-t border-gray-200">
                <button onClick={handleClear} className="text-sm text-gray-500 hover:text-gray-800 font-medium flex items-center">
                  <X className="w-4 h-4 mr-1" /> Clear All
                </button>
                
                <FilterPresetManager 
                  currentFilters={localFilters} 
                  onLoadPreset={(filters) => {
                    setLocalFilters(filters);
                    onFilterChange(filters);
                  }} 
                />
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
