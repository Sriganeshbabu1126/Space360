import React, { useEffect, useState } from 'react';
import { Route as RouteIcon, ChevronDown, Check, Loader2 } from 'lucide-react';
import { getPaths } from '../services/api';
import toast from 'react-hot-toast';

interface PathSelectorProps {
  siteId: string;
  onPathSelected: (path: any) => void;
  selectedPathId?: string;
}

const PathSelector: React.FC<PathSelectorProps> = ({ siteId, onPathSelected, selectedPathId }) => {
  const [paths, setPaths] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!siteId) return;
    
    let isMounted = true;
    const fetchPaths = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await getPaths(siteId);
        if (isMounted) {
          setPaths(res.data);
          
          // Auto-select if selectedPathId is provided and exists in paths
          if (selectedPathId && res.data.length > 0) {
             const preselect = res.data.find((p: any) => p.id === selectedPathId);
             if (preselect) {
                // optional: call onPathSelected but might cause loop if not handled carefully
             }
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error("Failed to load paths", err);
          setError("Failed to load paths");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    
    fetchPaths();
    
    return () => { isMounted = false; };
  }, [siteId]);

  const selectedPath = paths.find(p => p.id === selectedPathId);

  return (
    <div className="relative w-72">
      <div 
        className="flex items-center justify-between w-full px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm cursor-pointer hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center overflow-hidden">
          <RouteIcon className="w-5 h-5 mr-3 text-brand-600 shrink-0" />
          <div className="flex flex-col truncate">
            <span className="text-sm font-semibold text-gray-900 truncate">
              {selectedPath ? selectedPath.name : "Select Inspection Path"}
            </span>
            <span className="text-xs text-gray-500">
              {selectedPath ? `${selectedPath.points?.length || 0} points` : (loading ? "Loading..." : `${paths.length} paths available`)}
            </span>
          </div>
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'transform rotate-180' : ''}`} />
      </div>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-xl max-h-96 overflow-y-auto animate-fade-in custom-scrollbar">
          {loading ? (
            <div className="flex items-center justify-center py-6 text-gray-500">
              <Loader2 className="w-6 h-6 animate-spin mr-2" />
              <span className="text-sm">Loading paths...</span>
            </div>
          ) : error ? (
            <div className="py-4 px-4 text-sm text-red-500 text-center">{error}</div>
          ) : paths.length === 0 ? (
            <div className="py-8 px-4 text-center flex flex-col items-center">
               <RouteIcon className="w-8 h-8 text-gray-300 mb-2" />
               <p className="text-sm font-medium text-gray-900">No paths found</p>
               <p className="text-xs text-gray-500 mt-1">Create an inspection path first.</p>
            </div>
          ) : (
            <ul className="py-1">
              {/* Option to clear selection */}
              <li 
                className="flex items-center px-4 py-3 cursor-pointer hover:bg-gray-50 text-gray-700 transition-colors border-b border-gray-100"
                onClick={() => {
                  onPathSelected(null);
                  setIsOpen(false);
                }}
              >
                <span className="text-sm italic">Clear Selection</span>
              </li>
              
              {paths.map(path => (
                <li 
                  key={path.id}
                  className={`flex items-center justify-between px-4 py-3 cursor-pointer transition-colors ${
                    selectedPathId === path.id ? 'bg-brand-50 hover:bg-brand-100' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => {
                    onPathSelected(path);
                    setIsOpen(false);
                  }}
                >
                  <div className="flex flex-col">
                    <span className={`text-sm font-medium ${selectedPathId === path.id ? 'text-brand-700' : 'text-gray-900'}`}>
                      {path.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {path.points?.length || 0} points
                    </span>
                  </div>
                  {selectedPathId === path.id && (
                    <Check className="w-5 h-5 text-brand-600" />
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default PathSelector;
