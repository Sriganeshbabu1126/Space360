import React, { useState, useEffect, useMemo } from 'react';
import { Users, Plus, Edit2, Trash2, X, Search, ChevronDown, ChevronUp } from 'lucide-react';
import toast from 'react-hot-toast';
import { getContractors, createContractor, updateContractor, deleteContractor } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Contractor {
  id: string;
  name: string;
  company: string;
  trade: string;
  designation: string;
  contact: string;
  access_level: string;
  created_at: string;
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
    access_level: 'view_only'
  });

  const fetchContractors = async () => {
    try {
      const res = await getContractors();
      setContractors(res.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load contractors');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchContractors();
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
        access_level: contractor.access_level
      });
    } else {
      setEditingId(null);
      setFormData({
        name: '',
        company: '',
        trade: '',
        designation: '',
        contact: '',
        access_level: 'view_only'
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
      fetchContractors();
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
        fetchContractors();
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

      {/* Modal remains largely the same with refined styling */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-fade-in border border-gray-100">
            <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingId ? 'Edit Project Member' : 'Add Project Member'}
              </h3>
              <button onClick={handleCloseModal} className="text-gray-400 hover:text-gray-700 hover:bg-gray-100 p-1.5 rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-5">
              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
                  <input required name="name" value={formData.name} onChange={handleChange} className="input w-full" placeholder="John Doe" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Company</label>
                  <input required name="company" value={formData.company} onChange={handleChange} className="input w-full" placeholder="Acme Corp" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Trade</label>
                  <input required name="trade" value={formData.trade} onChange={handleChange} className="input w-full" placeholder="Electrical" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Role / Designation</label>
                  <input required name="designation" value={formData.designation} onChange={handleChange} className="input w-full" placeholder="Site Manager" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Contact (Email or Phone)</label>
                <input required name="contact" value={formData.contact} onChange={handleChange} className="input w-full" placeholder="john@example.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Access Level</label>
                <select name="access_level" value={formData.access_level} onChange={handleChange} className="input w-full">
                  <option value="view_only">Project Member (View Only)</option>
                  <option value="comment_and_change_status">Issue Editor (Comment & Change Status)</option>
                  <option value="create_issue">Issue Creator (Create Issues)</option>
                  <option value="close_and_review">Project Admin (Close & Review)</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-6">
                <button type="button" onClick={handleCloseModal} className="px-5 py-2 font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-6 py-2 shadow-md">
                  {editingId ? 'Save Changes' : 'Add Member'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectMembersPage;
