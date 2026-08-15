import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  AlertCircle, Plus, Search, Filter, Trash2, X, 
  MapPin, CheckCircle2, Circle, Clock, MessageSquare, Users, Send, Eye
} from 'lucide-react';
import toast from 'react-hot-toast';
import { 
  getIssues, deleteIssue, updateIssue, getContractors, 
  assignContractorToIssue, unassignContractorFromIssue,
  getIssueComments, addIssueComment, getIssue
} from '../services/api';
import { useAuth } from '../context/AuthContext';
import PhotoGallery, { IssuePhoto } from '../components/PhotoGallery';

interface Contractor {
  id: string;
  name: string;
  access_level: string;
}

interface IssueAssignment {
  id: string;
  contractor_id: string;
  contractor: Contractor;
}

interface IssueComment {
  id: string;
  author: string;
  comment_text: string;
  created_at: string;
}

interface Issue {
  id: string;
  title: string;
  description: string;
  status: string;
  issue_type: string;
  location_id: string;
  location_name?: string;
  session_a_id: string;
  session_b_id: string;
  created_by: string;
  created_at: string;
  assignments: IssueAssignment[];
  photos?: IssuePhoto[];
}

const statusConfig: Record<string, { label: string, color: string, icon: React.FC<any> }> = {
  open: { label: 'Open', color: 'bg-blue-100 text-blue-800 border-blue-200', icon: Circle },
  in_review: { label: 'In Review', color: 'bg-orange-100 text-orange-800 border-orange-200', icon: Clock },
  pending: { label: 'Pending', color: 'bg-purple-100 text-purple-800 border-purple-200', icon: Clock },
  critical: { label: 'Critical', color: 'bg-red-100 text-red-800 border-red-200', icon: AlertCircle },
  closed: { label: 'Closed', color: 'bg-gray-100 text-gray-800 border-gray-200', icon: CheckCircle2 },
};

const issueTypeLabels: Record<string, string> = {
  defect: 'Defect',
  safety_issue: 'Safety Issue',
  quality_issue: 'Quality Issue',
  incomplete_work: 'Incomplete Work',
  rework_required: 'Rework Required'
};

const IssuesPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAdmin, user } = useAuth();
  
  const [issues, setIssues] = useState<Issue[]>([]);
  const [contractors, setContractors] = useState<Contractor[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('');
  const [filterLocation, setFilterLocation] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [comments, setComments] = useState<IssueComment[]>([]);
  const [newComment, setNewComment] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [issuesRes, contractorsRes] = await Promise.all([
        getIssues(filterStatus || undefined),
        getContractors()
      ]);
      setIssues(issuesRes.data);
      setContractors(contractorsRes.data);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filterStatus]);

  const loadComments = async (issueId: string) => {
    try {
      const res = await getIssueComments(issueId);
      setComments(res.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load comments');
    }
  };

  const handleRowClick = async (issue: Issue) => {
    setSelectedIssue(issue);
    setComments([]);
    loadComments(issue.id);
    try {
      const res = await getIssue(issue.id);
      setSelectedIssue(res.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load full issue details');
    }
  };

  // Extract unique locations from issues for the filter dropdown
  const uniqueLocations = useMemo(() => {
    const locs = issues
      .filter(i => i.location_id && i.location_name)
      .map(i => ({ id: i.location_id, name: i.location_name as string }));
    
    // Deduplicate by id
    const unique = Array.from(new Map(locs.map(l => [l.id, l])).values());
    return unique.sort((a, b) => a.name.localeCompare(b.name));
  }, [issues]);

  const filteredIssues = useMemo(() => {
    let result = issues;
    if (filterType) {
      result = result.filter(i => i.issue_type === filterType);
    }
    if (filterLocation) {
      result = result.filter(i => i.location_id === filterLocation);
    }
    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      result = result.filter(i => 
        i.title.toLowerCase().includes(lower) || 
        (i.description && i.description.toLowerCase().includes(lower))
      );
    }
    return result;
  }, [issues, searchTerm, filterType, filterLocation]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this issue?')) {
      try {
        await deleteIssue(id);
        toast.success('Issue deleted');
        fetchData();
      } catch (error) {
        console.error(error);
        toast.error('Failed to delete issue');
      }
    }
  };

  const handleStatusChange = async (issueId: string, newStatus: string) => {
    try {
      await updateIssue(issueId, { status: newStatus });
      toast.success('Status updated');
      fetchData();
      if (selectedIssue && selectedIssue.id === issueId) {
        setSelectedIssue({ ...selectedIssue, status: newStatus });
      }
    } catch (error: any) {
      console.error(error);
      toast.error(error.response?.data?.detail || 'Failed to update status. Check permissions.');
    }
  };

  const handleTypeChange = async (issueId: string, newType: string) => {
    try {
      await updateIssue(issueId, { issue_type: newType });
      toast.success('Issue type updated');
      fetchData();
      if (selectedIssue && selectedIssue.id === issueId) {
        setSelectedIssue({ ...selectedIssue, issue_type: newType });
      }
    } catch (error: any) {
      console.error(error);
      toast.error(error.response?.data?.detail || 'Failed to update issue type.');
    }
  };

  const handleAssign = async (contractorId: string) => {
    if (!selectedIssue) return;
    try {
      await assignContractorToIssue(selectedIssue.id, contractorId);
      toast.success('Contractor assigned');
      fetchData();
      const res = await getIssue(selectedIssue.id);
      setSelectedIssue(res.data);
    } catch (error) {
      console.error(error);
      toast.error('Failed to assign contractor');
    }
  };

  const handleUnassign = async (contractorId: string) => {
    if (!selectedIssue) return;
    try {
      await unassignContractorFromIssue(selectedIssue.id, contractorId);
      toast.success('Contractor unassigned');
      fetchData();
      // Optimistic update
      setSelectedIssue({
        ...selectedIssue, 
        assignments: selectedIssue.assignments.filter(a => a.contractor_id !== contractorId)
      });
    } catch (error) {
      console.error(error);
      toast.error('Failed to unassign contractor');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedIssue) return;
    try {
      await addIssueComment(selectedIssue.id, newComment);
      setNewComment('');
      toast.success('Comment added');
      loadComments(selectedIssue.id);
    } catch (error) {
      console.error(error);
      toast.error('Failed to post comment');
    }
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 shrink-0 space-y-4">
        {/* Row 1: Header & Primary Action */}
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <AlertCircle className="w-6 h-6 mr-3 text-brand-600" />
            Issues
          </h2>
          <button onClick={() => navigate('/captures')} className="btn-primary flex items-center py-2 px-4 text-sm whitespace-nowrap shadow-sm">
            <Plus className="w-4 h-4 mr-1.5" />
            Create Issue
          </button>
        </div>
        
        {/* Row 2: Search & Filters */}
        <div className="flex flex-col sm:flex-row gap-4 items-end sm:items-center">
          {/* Search */}
          <div className="relative flex-1 w-full sm:w-auto">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search issues..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>
          
          {/* Filters */}
          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-500 flex items-center">
                <Filter className="w-4 h-4 mr-1" /> Status:
              </span>
              <select 
                value={filterStatus} 
                onChange={(e) => setFilterStatus(e.target.value)}
                className="input py-1.5 text-sm w-full sm:w-32"
              >
                <option value="">All</option>
                <option value="open">Open</option>
                <option value="in_review">In Review</option>
                <option value="closed">Closed</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-500">Location:</span>
              <select 
                value={filterLocation} 
                onChange={(e) => setFilterLocation(e.target.value)}
                className="input py-1.5 text-sm w-full sm:w-40"
              >
                <option value="">All Locations</option>
                {uniqueLocations.map(loc => (
                  <option key={loc.id} value={loc.id}>{loc.name}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-500">Type:</span>
              <select 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
                className="input py-1.5 text-sm w-full sm:w-40"
              >
                <option value="">All</option>
                <option value="defect">Defect</option>
                <option value="safety_issue">Safety Issue</option>
                <option value="quality_issue">Quality Issue</option>
                <option value="incomplete_work">Incomplete Work</option>
                <option value="rework_required">Rework Required</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
        {loading ? (
          <div className="p-12 text-center text-gray-500 m-auto">Loading issues...</div>
        ) : filteredIssues.length === 0 ? (
          <div className="p-16 text-center m-auto">
            <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-gray-900 mb-2">No issues found</h3>
            <p className="text-gray-500">Try adjusting your filters or create a new issue.</p>
          </div>
        ) : (
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead className="sticky top-0 bg-gray-50 z-10">
                <tr className="border-b border-gray-200 text-gray-600 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Type</th>
                  <th className="px-6 py-4 font-semibold">Title</th>
                  <th className="px-6 py-4 font-semibold">Location / Description</th>
                  <th className="px-6 py-4 font-semibold">Assigned To</th>
                  <th className="px-6 py-4 font-semibold">Created Date</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredIssues.map(issue => {
                  const conf = statusConfig[issue.status] || statusConfig.open;
                  const StatusIcon = conf.icon;
                  return (
                    <tr 
                      key={issue.id} 
                      onClick={() => handleRowClick(issue)}
                      className="hover:bg-gray-50 transition-colors cursor-pointer group"
                    >
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${conf.color}`}>
                          <StatusIcon className="w-3.5 h-3.5 mr-1.5" />
                          {conf.label}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full text-xs font-semibold tracking-wider">
                          {issueTypeLabels[issue.issue_type] || issue.issue_type || 'Defect'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-semibold text-gray-900 truncate max-w-[200px]">{issue.title}</div>
                        <div className="text-xs text-gray-400 mt-1">By: {issue.created_by.split('@')[0]}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center text-sm text-gray-700 font-medium mb-1">
                          <MapPin className="w-3.5 h-3.5 mr-1 text-gray-400" /> 
                          {issue.location_name || 'No location'}
                        </div>
                        <div className="text-sm text-gray-500 truncate max-w-[250px]">
                          {issue.description || 'No description provided.'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {issue.assignments.length > 0 ? (
                          <div className="flex -space-x-2 overflow-hidden">
                            {issue.assignments.map(a => (
                              <div key={a.id} className="inline-block w-8 h-8 rounded-full ring-2 ring-white bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-bold" title={a.contractor?.name}>
                                {a.contractor?.name.substring(0,2).toUpperCase() || '?'}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-400 text-sm italic">Unassigned</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-500 text-sm">
                        {new Date(issue.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end">
                          <button 
                            onClick={(e) => handleDelete(e, issue.id)} 
                            className="text-gray-400 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100" 
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedIssue && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden animate-fade-in border border-gray-100">
            
            <div className="flex justify-between items-start px-6 py-5 border-b border-gray-100 bg-gray-50/50">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{selectedIssue.title}</h3>
                <div className="flex items-center space-x-3 text-sm">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full font-semibold border ${statusConfig[selectedIssue.status]?.color || statusConfig.open.color}`}>
                    {statusConfig[selectedIssue.status]?.label || 'Open'}
                  </span>
                  <span className="text-gray-400">|</span>
                  <span className="text-gray-600 flex items-center gap-1">
                    <MapPin className="w-4 h-4 text-gray-500" />
                    <span className="text-sm font-medium">{selectedIssue.location_name || 'No location'}</span>
                  </span>
                  <span className="text-gray-400">|</span>
                  <span className="text-gray-500">{new Date(selectedIssue.created_at).toLocaleDateString()}</span>
                </div>
                
                {selectedIssue.session_a_id && (
                  <div className="mt-5">
                    <button
                      onClick={() => {
                        const captureId = selectedIssue.session_a_id;
                        setSelectedIssue(null);
                        navigate(`/captures?highlight=${captureId}`);
                      }}
                      className="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 text-sm font-medium transition-colors shadow-sm flex items-center"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View 360° Capture
                    </button>
                  </div>
                )}
              </div>
              <button onClick={() => setSelectedIssue(null)} className="text-gray-400 hover:text-gray-700 hover:bg-gray-200 p-2 rounded-xl transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 flex flex-col md:flex-row gap-8">
              {/* Left Column (Info & Comments) */}
              <div className="flex-1 space-y-8">
                {/* Description */}
                <div>
                  <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3 flex items-center">
                    <MessageSquare className="w-4 h-4 mr-2 text-gray-400" /> Description
                  </h4>
                  <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
                    {selectedIssue.description || <span className="text-gray-400 italic">No description provided.</span>}
                  </div>
                </div>

                {/* Comments Section */}
                <div className="pt-4 border-t border-gray-100">
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Comments & Activity</h4>
                    {comments.length > 0 && (
                      <span className="bg-gray-100 text-gray-600 px-2.5 py-0.5 rounded-full text-xs font-semibold">
                        {comments.length} Comment{comments.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-4 mb-4 max-h-80 overflow-y-auto pr-2">
                    {comments.length === 0 ? (
                      <div className="text-center py-6 text-gray-500">
                        <p className="text-sm">No comments yet. Add the first one!</p>
                      </div>
                    ) : (
                      [...comments].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()).map(c => (
                        <div key={c.id} className="border-l-2 border-brand-300 pl-4 pb-2">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-xs shrink-0">
                              {c.author.substring(0, 1).toUpperCase()}
                            </div>
                            <span className="font-medium text-sm text-gray-900">
                              {c.author.split('@')[0]}
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(c.created_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 whitespace-pre-wrap">{c.comment_text}</p>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddComment()}
                      placeholder="Add a comment..."
                      className="input flex-1 py-2 text-sm"
                    />
                    <button onClick={handleAddComment} className="btn-primary p-2 shadow-sm rounded-lg">
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Evidence Photos Section */}
                <div className="pt-6 mt-6 border-t border-gray-100">
                  <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4">Evidence Photos</h4>
                  <PhotoGallery 
                    photos={selectedIssue.photos || []} 
                    issueTitle={selectedIssue.title || 'Issue'} 
                  />
                </div>
              </div>

              {/* Right Column (Sidebar Controls) */}
              <div className="w-full md:w-64 space-y-6">
                
                {/* Status Change */}
                <div className="bg-brand-50 p-4 rounded-xl border border-brand-100">
                  <h4 className="text-sm font-bold text-brand-900 mb-2">Update Status</h4>
                  <select 
                    value={selectedIssue.status} 
                    onChange={(e) => handleStatusChange(selectedIssue.id, e.target.value)}
                    className="input py-1.5 text-sm font-semibold border-brand-200 focus:ring-brand-500 w-full"
                  >
                    <option value="open">Open</option>
                    <option value="in_review">In Review</option>
                    {isAdmin && <option value="pending">Pending</option>}
                    {isAdmin && <option value="critical">Critical</option>}
                    {isAdmin && <option value="closed">Closed</option>}
                  </select>
                </div>

                {/* Issue Type Change */}
                <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                  <h4 className="text-sm font-bold text-gray-900 mb-2">Issue Type</h4>
                  <select 
                    value={selectedIssue.issue_type || 'defect'} 
                    onChange={(e) => handleTypeChange(selectedIssue.id, e.target.value)}
                    disabled={!isAdmin}
                    className="input py-1.5 text-sm w-full disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    <option value="defect">Defect</option>
                    <option value="safety_issue">Safety Issue</option>
                    <option value="quality_issue">Quality Issue</option>
                    <option value="incomplete_work">Incomplete Work</option>
                    <option value="rework_required">Rework Required</option>
                  </select>
                </div>

                {/* Assignees */}
                <div>
                  <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3 flex items-center">
                    <Users className="w-4 h-4 mr-2 text-gray-400" /> Assignees
                  </h4>
                  
                  <div className="space-y-2">
                    {selectedIssue.assignments.length === 0 ? (
                      <div className="text-sm text-gray-500 italic">No assignees.</div>
                    ) : (
                      selectedIssue.assignments.map(a => (
                        <div key={a.id} className="flex items-center justify-between bg-white border border-gray-200 p-2 rounded-lg shadow-sm">
                          <div className="flex items-center">
                            <div className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-xs mr-2">
                              {a.contractor?.name.substring(0,2).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-semibold text-gray-900 text-xs">{a.contractor?.name}</div>
                            </div>
                          </div>
                          {isAdmin && (
                            <button 
                              onClick={() => handleUnassign(a.contractor_id)}
                              className="text-red-500 hover:text-red-700 p-1"
                              title="Unassign"
                            >
                              <X className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      ))
                    )}
                  </div>

                  {/* Add Assignee Dropdown */}
                  {isAdmin && (
                    <div className="mt-3">
                      <select 
                        onChange={(e) => {
                          if (e.target.value) {
                            handleAssign(e.target.value);
                            e.target.value = '';
                          }
                        }}
                        className="input py-1.5 text-sm w-full"
                        defaultValue=""
                      >
                        <option value="" disabled>+ Assign Contractor</option>
                        {contractors.filter(c => !selectedIssue.assignments.find(a => a.contractor_id === c.id)).map(c => (
                          <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
                
                {/* Context Links (Sessions) */}
                <div className="pt-4 border-t border-gray-100 space-y-2">
                   <button className="w-full py-2 px-4 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center justify-center transition-colors">
                     View Session A
                   </button>
                   {selectedIssue.session_b_id && (
                     <button className="w-full py-2 px-4 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center justify-center transition-colors">
                       View Session B
                     </button>
                   )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IssuesPage;
