import React, { useState, useEffect, useMemo } from 'react';
import { Users, Plus, Trash2, X, Search, ChevronDown, ChevronUp, User as UserIcon, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { getProjectMembers, getCompanyUsers, addProjectMember, removeProjectMember } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useSiteContext } from '../context/SiteContext';

interface Member {
  id: string; // The user ID
  name: string;
  contact: string; // email
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
  return name ? name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : '??';
};

const getColorClass = (name: string) => {
  const colors = [
    'bg-red-100 text-red-700', 'bg-blue-100 text-blue-700', 
    'bg-green-100 text-green-700', 'bg-yellow-100 text-yellow-700', 
    'bg-purple-100 text-purple-700', 'bg-pink-100 text-pink-700',
    'bg-indigo-100 text-indigo-700', 'bg-teal-100 text-teal-700'
  ];
  let hash = 0;
  if (!name) return colors[0];
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
};

const ProjectMembersPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const { selectedSiteId, tenantId } = useSiteContext();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchTerm, setSearchTerm] = useState('');
  
  // Add Member Modal State
  const [showModal, setShowModal] = useState(false);
  const [companyUsers, setCompanyUsers] = useState<Member[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [selectedAccessLevel, setSelectedAccessLevel] = useState('view_only');
  const [loadingUsers, setLoadingUsers] = useState(false);

  const fetchMembers = async () => {
    if (!selectedSiteId) return;
    try {
      setLoading(true);
      const res = await getProjectMembers(selectedSiteId);
      setMembers(res.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load project members');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [selectedSiteId]);

  const filteredMembers = useMemo(() => {
    let result = [...members];
    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      result = result.filter(m => 
        (m.name && m.name.toLowerCase().includes(lower)) || 
        (m.contact && m.contact.toLowerCase().includes(lower))
      );
    }
    return result;
  }, [members, searchTerm]);

  const handleOpenAddModal = async () => {
    if (!tenantId) {
      toast.error("Tenant information missing for this project.");
      return;
    }
    setShowModal(true);
    setLoadingUsers(true);
    try {
      const res = await getCompanyUsers(tenantId);
      // Filter out users who are already in the project
      const existingIds = new Set(members.map(m => m.id));
      const unassigned = res.data.filter((u: any) => !existingIds.has(u.id));
      setCompanyUsers(unassigned);
      if (unassigned.length > 0) {
        setSelectedUserId(unassigned[0].id);
      }
    } catch (err) {
      console.error(err);
      toast.error("Failed to load company users");
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserId || !selectedSiteId) return;
    try {
      await addProjectMember(selectedSiteId, {
        user_id: selectedUserId,
        access_level: selectedAccessLevel
      });
      toast.success("Member added to project");
      setShowModal(false);
      fetchMembers();
    } catch (err) {
      console.error(err);
      toast.error("Failed to add member to project");
    }
  };

  const handleDelete = async (id: string) => {
    if (!selectedSiteId) return;
    if (window.confirm('Are you sure you want to remove this member from the project?')) {
      try {
        await removeProjectMember(selectedSiteId, id);
        toast.success('Member removed');
        fetchMembers();
      } catch (err) {
        console.error(err);
        toast.error('Failed to remove member');
      }
    }
  };

  if (!selectedSiteId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-700">No Project Selected</h2>
          <p className="text-gray-500 mt-2">Please select a project to view its members.</p>
        </div>
      </div>
    );
  }

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
          {isAdmin && (
            <button onClick={handleOpenAddModal} className="btn-primary flex items-center shadow-md whitespace-nowrap">
              <Plus className="w-4 h-4 mr-2" />
              Add Member
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-500">Loading project members...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-semibold">Name</th>
                  <th className="px-6 py-4 font-semibold">Email</th>
                  <th className="px-6 py-4 font-semibold">Access Level</th>
                  <th className="px-6 py-4 font-semibold">Added On</th>
                  {isAdmin && <th className="px-6 py-4 font-semibold text-right">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredMembers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      No project members found.
                    </td>
                  </tr>
                ) : (
                  filteredMembers.map(c => (
                    <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm ${getColorClass(c.name)}`}>
                            {getInitials(c.name)}
                          </div>
                          <span className="ml-3 font-semibold text-gray-900">{c.name || 'Unknown'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {c.contact || '-'}
                      </td>
                      <td className="px-6 py-4 text-gray-700 text-sm font-medium">
                        {accessLevelMap[c.access_level] || c.access_level}
                      </td>
                      <td className="px-6 py-4 text-gray-500 text-sm">
                        {c.created_at ? new Date(c.created_at).toLocaleDateString() : '-'}
                      </td>
                      {isAdmin && (
                        <td className="px-6 py-4 text-right">
                          <button onClick={() => handleDelete(c.id)} className="text-gray-400 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 transition-colors" title="Remove from Project">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Member Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-md p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-fade-in flex flex-col">
            <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100 bg-gray-50">
              <h3 className="text-xl font-bold text-gray-900">Add Project Member</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleAddSubmit} className="p-6 space-y-6">
              {loadingUsers ? (
                <p className="text-gray-500 text-center py-4">Loading available company users...</p>
              ) : companyUsers.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-gray-500">All company users are already assigned to this project.</p>
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Select User</label>
                    <select 
                      value={selectedUserId}
                      onChange={e => setSelectedUserId(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2"
                      required
                    >
                      <option value="" disabled>Select a user</option>
                      {companyUsers.map(u => (
                         <option key={u.id} value={u.id}>{u.name} ({u.contact})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Project Role</label>
                    <select 
                      value={selectedAccessLevel}
                      onChange={e => setSelectedAccessLevel(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2"
                    >
                      <option value="view_only">Project Member (View Only)</option>
                      <option value="comment_and_change_status">Issue Editor (Comment & Change Status)</option>
                      <option value="create_issue">Issue Creator (Create Issues)</option>
                      <option value="close_and_review">Project Admin (Close & Review)</option>
                    </select>
                  </div>
                  <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                    <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
                    <button type="submit" className="btn-primary">Add to Project</button>
                  </div>
                </>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectMembersPage;
