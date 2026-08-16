import React, { useState, useEffect, useMemo } from 'react';
import { Users, Plus, Edit2, Trash2, X, Search, ChevronDown, ChevronUp, User as UserIcon, Building2, Briefcase, Mail, ShieldAlert, CheckCircle2, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';
import { getContractors, createContractor, updateContractor, deleteContractor, getSites } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Site {
  id: string;
  name: string;
}

interface Contractor {
  id: string;
  name: string;
  company: string;
  trade: string;
  designation: string;
  contact: string;
  access_level: string;
  created_at: string;
  sites?: Site[];
}

const accessLevelMap: Record<string, string> = {
  view_only: 'Project Member',
  comment_and_change_status: 'Issue Editor',
  create_issue: 'Issue Creator',
  close_and_review: 'Project Admin'
};

const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
};

const getColorClass = (name: string) => {
  const colors = [
    'bg-red-100 text-red-700', 'bg-blue-100 text-blue-700', 
    'bg-green-100 text-green-700', 'bg-yellow-100 text-yellow-700', 
    'bg-purple-100 text-purple-700', 'bg-pink-100 text-pink-700',
    'bg-indigo-100 text-indigo-700', 'bg-teal-100 text-teal-700'
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
};

const maskContact = (contact: string) => {
  if (!contact) return '-';
  if (contact.includes('@')) {
    const [local, domain] = contact.split('@');
    return `${local}@${domain.charAt(0)}...`;
  }
  return contact.length > 4 ? `${contact.slice(0, 4)}...` : contact;
};

const isEmail = (contact: string) => contact?.includes('@');

const ProjectMembersPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [contractors, setContractors] = useState<Contractor[]>([]);
  const [allSites, setAllSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: keyof Contractor; direction: 'asc' | 'desc' } | null>(null);

  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    trade: '',
    designation: '',
    contact: '',
    access_level: 'view_only',
    site_ids: [] as string[]
  });

  const fetchData = async () => {
    try {
      const [res, sitesRes] = await Promise.all([
        getContractors(),
        getSites()
      ]);
      setContractors(res.data);
      setAllSites(sitesRes.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchData();
    }
  }, [isAdmin]);

  const handleSort = (key: keyof Contractor) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const filteredAndSorted = useMemo(() => {
    let result = [...contractors];

    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      result = result.filter(c => 
        c.name.toLowerCase().includes(lower) || 
        (c.contact && c.contact.toLowerCase().includes(lower)) ||
        (c.company && c.company.toLowerCase().includes(lower))
      );
    }

    if (sortConfig) {
      result.sort((a, b) => {
        const aValue = a[sortConfig.key] || '';
        const bValue = b[sortConfig.key] || '';
        if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [contractors, searchTerm, sortConfig]);


  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-700">Access Denied</h2>
          <p className="text-gray-500 mt-2">Only administrators can access this page.</p>
        </div>
      </div>
    );
  }

  const handleOpenModal = (contractor?: Contractor) => {
    if (contractor) {
      setEditingId(contractor.id);
      setFormData({
        name: contractor.name,
        company: contractor.company,
        trade: contractor.trade,
        designation: contractor.designation,
        contact: contractor.contact,
        access_level: contractor.access_level,
        site_ids: contractor.sites ? contractor.sites.map(s => s.id) : []
      });
    } else {
      setEditingId(null);
      setFormData({
        name: '',
        company: '',
        trade: '',
        designation: '',
        contact: '',
        access_level: 'view_only',
        site_ids: []
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSiteChange = (siteId: string) => {
    setFormData(prev => {
      const isSelected = prev.site_ids.includes(siteId);
      if (isSelected) {
        return { ...prev, site_ids: prev.site_ids.filter(id => id !== siteId) };
      } else {
        return { ...prev, site_ids: [...prev.site_ids, siteId] };
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateContractor(editingId, formData);
        toast.success('Member updated successfully');
      } else {
        await createContractor(formData);
        toast.success('Member added successfully');
      }
      handleCloseModal();
      fetchData();
    } catch (err) {
      console.error(err);
      toast.error('Failed to save member');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to remove this member?')) {
      try {
        await deleteContractor(id);
        toast.success('Member removed');
        fetchData();
      } catch (err) {
        console.error(err);
        toast.error('Failed to remove member');
      }
    }
  };

  const SortIcon = ({ columnKey }: { columnKey: string }) => {
    if (sortConfig?.key === columnKey) {
      return sortConfig.direction === 'asc' ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />;
    }
    return <ChevronDown className="w-4 h-4 ml-1 opacity-20 group-hover:opacity-100" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Project Members</h2>
        
        <div className="flex items-center gap-4 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search members..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow"
            />
          </div>
          <button onClick={() => handleOpenModal()} className="btn-primary flex items-center shadow-md whitespace-nowrap">
            <Plus className="w-4 h-4 mr-2" />
            Add Member
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-500">Loading members...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-semibold cursor-pointer group select-none" onClick={() => handleSort('name')}>
                    <div className="flex items-center">Name <SortIcon columnKey="name" /></div>
                  </th>
                  <th className="px-6 py-4 font-semibold cursor-pointer group select-none" onClick={() => handleSort('contact')}>
                    <div className="flex items-center">Email <SortIcon columnKey="contact" /></div>
                  </th>
                  <th className="px-6 py-4 font-semibold">Phone</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold cursor-pointer group select-none" onClick={() => handleSort('company')}>
                    <div className="flex items-center">Company <SortIcon columnKey="company" /></div>
                  </th>
                  <th className="px-6 py-4 font-semibold cursor-pointer group select-none" onClick={() => handleSort('designation')}>
                    <div className="flex items-center">Role <SortIcon columnKey="designation" /></div>
                  </th>
                  <th className="px-6 py-4 font-semibold cursor-pointer group select-none" onClick={() => handleSort('access_level')}>
                    <div className="flex items-center">Access Level <SortIcon columnKey="access_level" /></div>
                  </th>
                  <th className="px-6 py-4 font-semibold">Assigned Sites</th>
                  <th className="px-6 py-4 font-semibold cursor-pointer group select-none" onClick={() => handleSort('created_at')}>
                    <div className="flex items-center">Added On <SortIcon columnKey="created_at" /></div>
                  </th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredAndSorted.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-6 py-12 text-center text-gray-500">
                      No project members found matching your search.
                    </td>
                  </tr>
                ) : (
                  filteredAndSorted.map(c => (
                    <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm ${getColorClass(c.name)}`}>
                            {getInitials(c.name)}
                          </div>
                          <span className="ml-3 font-semibold text-gray-900">{c.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {isEmail(c.contact) ? maskContact(c.contact) : '-'}
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {!isEmail(c.contact) ? maskContact(c.contact) : '-'}
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                          Active
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-700 text-sm">{c.company || '-'}</td>
                      <td className="px-6 py-4 text-gray-700 text-sm">{c.designation || '-'}</td>
                      <td className="px-6 py-4 text-gray-700 text-sm font-medium">
                        {accessLevelMap[c.access_level] || c.access_level}
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {c.sites && c.sites.length > 0 
                          ? c.sites.map(s => s.name).join(', ') 
                          : <span className="text-gray-400 italic">None</span>}
                      </td>
                      <td className="px-6 py-4 text-gray-500 text-sm">
                        {c.created_at ? new Date(c.created_at).toLocaleDateString() : '-'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button onClick={() => handleOpenModal(c)} className="text-gray-400 hover:text-brand-600 p-1.5 rounded-lg hover:bg-brand-50 transition-colors" title="Edit">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleDelete(c.id)} className="text-gray-400 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 transition-colors" title="Delete">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modern, Premium Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-md p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-fade-in flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="flex justify-between items-center px-8 py-6 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white shrink-0">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center text-brand-600">
                  <UserIcon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 tracking-tight">
                    {editingId ? 'Edit Project Member' : 'Add Project Member'}
                  </h3>
                  <p className="text-sm text-gray-500 font-medium mt-0.5">
                    {editingId ? 'Update member details and permissions' : 'Invite a new member and assign sites'}
                  </p>
                </div>
              </div>
              <button 
                onClick={handleCloseModal} 
                className="text-gray-400 hover:text-gray-700 hover:bg-gray-100 p-2 rounded-xl transition-all duration-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body (Scrollable) */}
            <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-8 py-6 space-y-8">
              
              {/* Profile Details Section */}
              <div className="space-y-5">
                <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Profile Details</h4>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <UserIcon className="w-4 h-4 mr-1.5 text-gray-400" /> Full Name
                    </label>
                    <input 
                      required name="name" value={formData.name} onChange={handleChange} 
                      className="w-full bg-gray-50 border border-gray-200 text-gray-900 rounded-xl px-4 py-2.5 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all" 
                      placeholder="e.g. Jane Doe" 
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <Building2 className="w-4 h-4 mr-1.5 text-gray-400" /> Company
                    </label>
                    <input 
                      required name="company" value={formData.company} onChange={handleChange} 
                      className="w-full bg-gray-50 border border-gray-200 text-gray-900 rounded-xl px-4 py-2.5 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all" 
                      placeholder="e.g. Acme Construction" 
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <Briefcase className="w-4 h-4 mr-1.5 text-gray-400" /> Trade
                    </label>
                    <input 
                      required name="trade" value={formData.trade} onChange={handleChange} 
                      className="w-full bg-gray-50 border border-gray-200 text-gray-900 rounded-xl px-4 py-2.5 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all" 
                      placeholder="e.g. Electrical" 
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <UserIcon className="w-4 h-4 mr-1.5 text-gray-400" /> Role / Designation
                    </label>
                    <input 
                      required name="designation" value={formData.designation} onChange={handleChange} 
                      className="w-full bg-gray-50 border border-gray-200 text-gray-900 rounded-xl px-4 py-2.5 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all" 
                      placeholder="e.g. Site Supervisor" 
                    />
                  </div>
                  <div className="space-y-1.5 sm:col-span-2">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <Mail className="w-4 h-4 mr-1.5 text-gray-400" /> Contact Email or Phone
                    </label>
                    <input 
                      required name="contact" value={formData.contact} onChange={handleChange} 
                      className="w-full bg-gray-50 border border-gray-200 text-gray-900 rounded-xl px-4 py-2.5 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all" 
                      placeholder="jane.doe@example.com" 
                    />
                  </div>
                </div>
              </div>

              {/* Permissions Section */}
              <div className="space-y-5 pt-4 border-t border-gray-100">
                <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Access & Permissions</h4>
                
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-gray-700 flex items-center">
                    <ShieldAlert className="w-4 h-4 mr-1.5 text-gray-400" /> System Access Level
                  </label>
                  <div className="relative">
                    <select 
                      name="access_level" value={formData.access_level} onChange={handleChange} 
                      className="w-full appearance-none bg-gray-50 border border-gray-200 text-gray-900 rounded-xl pl-4 pr-10 py-2.5 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 font-medium transition-all cursor-pointer"
                    >
                      <option value="view_only">Project Member (View Only)</option>
                      <option value="comment_and_change_status">Issue Editor (Comment & Change Status)</option>
                      <option value="create_issue">Issue Creator (Create Issues)</option>
                      <option value="close_and_review">Project Admin (Close & Review)</option>
                    </select>
                    <ChevronDown className="w-5 h-5 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="text-sm font-semibold text-gray-700 flex items-center">
                    <MapPin className="w-4 h-4 mr-1.5 text-gray-400" /> Assigned Sites
                  </label>
                  <p className="text-sm text-gray-500">Select which sites this member can access. They will only see issues and captures for these sites.</p>
                  
                  {allSites.length === 0 ? (
                    <div className="p-4 bg-gray-50 border border-gray-200 rounded-xl text-center text-gray-500 text-sm">
                      No sites available in the system.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-64 overflow-y-auto pr-2 pb-2 custom-scrollbar">
                      {allSites.map(site => {
                        const isSelected = formData.site_ids.includes(site.id);
                        return (
                          <div 
                            key={site.id} 
                            onClick={() => handleSiteChange(site.id)}
                            className={`group flex items-center p-3 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                              isSelected 
                                ? 'border-brand-500 bg-brand-50' 
                                : 'border-gray-100 bg-white hover:border-brand-200 hover:bg-gray-50'
                            }`}
                          >
                            <div className={`flex-shrink-0 w-5 h-5 rounded flex items-center justify-center mr-3 transition-colors ${
                              isSelected ? 'bg-brand-500 text-white' : 'border-2 border-gray-300 group-hover:border-brand-400'
                            }`}>
                              {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className={`text-sm font-semibold truncate ${isSelected ? 'text-brand-900' : 'text-gray-700'}`}>
                                {site.name}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>

            </form>

            {/* Modal Footer */}
            <div className="px-8 py-5 border-t border-gray-100 bg-gray-50/50 flex justify-end gap-3 shrink-0">
              <button 
                type="button" 
                onClick={handleCloseModal} 
                className="px-6 py-2.5 font-semibold text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all duration-200"
              >
                Cancel
              </button>
              <button 
                onClick={handleSubmit}
                className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-xl shadow-lg shadow-brand-500/30 transform hover:-translate-y-0.5 transition-all duration-200"
              >
                {editingId ? 'Save Changes' : 'Add Member'}
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectMembersPage;
