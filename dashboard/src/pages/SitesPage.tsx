import React, { useEffect, useState } from 'react';
import { getSites, createSite } from '../services/api';
import { MapPin, Plus, X } from 'lucide-react';
import toast from 'react-hot-toast';

const SitesPage: React.FC = () => {
  const [sites, setSites] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newSiteName, setNewSiteName] = useState('');
  const [newSiteAddress, setNewSiteAddress] = useState('');

  const fetchSites = async () => {
    try {
      setLoading(true);
      const res = await getSites();
      setSites(res.data);
    } catch (error) {
      toast.error('Failed to load sites');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    document.title = "Sites | Space360";
    fetchSites();
  }, []);

  const handleCreateSite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSiteName.trim()) return;
    
    try {
      await createSite({ name: newSiteName, address: newSiteAddress });
      toast.success('Site created successfully');
      setIsModalOpen(false);
      setNewSiteName('');
      setNewSiteAddress('');
      fetchSites();
    } catch (error) {
      toast.error('Failed to create site');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">All Construction Sites</h2>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Site
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="card h-48 animate-pulse bg-gray-100 border-none"></div>
          ))}
        </div>
      ) : sites.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <p className="text-gray-500 mb-4">No sites found. Create your first site to get started.</p>
          <button onClick={() => setIsModalOpen(true)} className="btn-primary">Create Site</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sites.map(site => (
            <div key={site.id} className="card hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-medium text-gray-900 truncate pr-2">{site.name}</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  site.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {site.status || 'Active'}
                </span>
              </div>
              
              {site.address && (
                <div className="flex items-start text-gray-500 text-sm mb-6">
                  <MapPin className="w-4 h-4 mr-1 mt-0.5 flex-shrink-0" />
                  <p className="line-clamp-2">{site.address}</p>
                </div>
              )}
              
              <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center">
                <span className="text-sm text-gray-500">0 Captures</span>
                <button className="text-brand-600 hover:text-brand-800 text-sm font-medium">View &rarr;</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true" onClick={() => setIsModalOpen(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex justify-between items-center mb-5">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Create New Site</h3>
                  <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-500">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <form onSubmit={handleCreateSite}>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Site Name</label>
                      <input 
                        type="text" 
                        required 
                        className="input" 
                        placeholder="e.g. Downtown Highrise"
                        value={newSiteName}
                        onChange={(e) => setNewSiteName(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                      <input 
                        type="text" 
                        className="input" 
                        placeholder="e.g. 123 Main St, City"
                        value={newSiteAddress}
                        onChange={(e) => setNewSiteAddress(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="mt-6 flex justify-end space-x-3">
                    <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      Create
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SitesPage;
