import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getProject } from '../services/api';
import { 
  Building2, MapPin, Calendar, Clock, ArrowLeft, 
  Map, Activity, AlertCircle, CheckCircle2, ChevronRight, HardHat, Info
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSite } from '../context/SiteContext';

const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const { setSelectedSiteId } = useSite();
  
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjectDetail = async () => {
      if (!projectId) return;
      try {
        setLoading(true);
        setErrorMsg(null);
        setSelectedSiteId(projectId);
        const res = await getProject(projectId);
        setProject(res.data);
      } catch (err: any) {
        console.error('Error fetching project details', err);
        setErrorMsg(err?.response?.data?.detail || err.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchProjectDetail();
  }, [projectId, setSelectedSiteId]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-4 space-y-6">
        <div className="h-8 w-64 bg-gray-200 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="h-64 bg-gray-200 rounded-2xl animate-pulse"></div>
            <div className="h-64 bg-gray-200 rounded-2xl animate-pulse"></div>
          </div>
          <div className="h-96 bg-gray-200 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (errorMsg || !project) {
    return (
      <div className="text-center mt-20 text-gray-500">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Project not found</h2>
        <p>{errorMsg || "The project you are looking for does not exist or you don't have permission to view it."}</p>
        <button onClick={() => navigate('/')} className="mt-4 text-brand-600 hover:underline">
          Go back to Hub
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto pb-12 space-y-6">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center space-x-2 text-sm text-gray-500 mb-6">
        <Link to="/" className="hover:text-brand-600 transition-colors flex items-center">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Hub
        </Link>
        <span>/</span>
        <span className="text-gray-900 font-medium">{project.name}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Content Area (Left: 2 columns wide) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Project Header Card */}
          <div className="bg-white rounded-2xl p-6 md:p-8 border border-gray-200 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-brand-500 to-brand-300"></div>
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{project.name}</h1>
                <p className="text-gray-500 mt-2 flex items-center text-sm">
                  <MapPin className="w-4 h-4 mr-1.5 opacity-70" /> 
                  {project.location || 'No location specified'}
                </p>
              </div>
              <span className={`px-3 py-1 text-xs font-semibold uppercase tracking-wider rounded-full ${
                project.status === 'active' ? 'bg-green-100 text-green-700' : 
                project.status === 'archived' ? 'bg-gray-100 text-gray-600' : 
                'bg-yellow-100 text-yellow-700'
              }`}>
                {project.status}
              </span>
            </div>

            {project.description && (
              <div className="mt-6 bg-gray-50 p-4 rounded-xl border border-gray-100 text-gray-700 text-sm leading-relaxed flex items-start">
                <Info className="w-5 h-5 mr-3 text-brand-500 shrink-0 mt-0.5" />
                <p>{project.description}</p>
              </div>
            )}
          </div>

          {/* Floor Plans Grid */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <Map className="w-5 h-5 mr-2 text-brand-500" /> Floor Plans
              </h2>
              <button 
                onClick={() => navigate('/floor-plans')}
                className="text-sm font-medium text-brand-600 hover:text-brand-800 transition-colors"
              >
                Manage Maps
              </button>
            </div>

            {project.floor_plans && project.floor_plans.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {project.floor_plans.map((fp: any) => (
                  <div 
                    key={fp.id} 
                    onClick={() => navigate('/captures')}
                    className="border border-gray-200 rounded-xl overflow-hidden hover:border-brand-300 hover:shadow-md transition-all cursor-pointer group"
                  >
                    <div className="h-32 bg-gray-100 relative overflow-hidden">
                      {fp.image_url ? (
                        <img src={fp.image_url} alt={fp.label} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          <Map className="w-8 h-8 opacity-50" />
                        </div>
                      )}
                    </div>
                    <div className="p-4 flex justify-between items-center bg-white">
                      <span className="font-semibold text-gray-900 truncate">{fp.label}</span>
                      <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-brand-500 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <Map className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">No floor plans uploaded yet.</p>
              </div>
            )}
          </div>

          {/* Recent Issues Table */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 text-brand-500" /> Recent Issues
              </h2>
              <button 
                onClick={() => navigate('/issues')}
                className="text-sm font-medium text-brand-600 hover:text-brand-800 transition-colors"
              >
                View All Issues
              </button>
            </div>

            {project.recent_issues && project.recent_issues.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse whitespace-nowrap">
                  <thead>
                    <tr className="bg-gray-50 border-y border-gray-200 text-gray-500 text-xs uppercase tracking-wider">
                      <th className="px-4 py-3 font-semibold">Title</th>
                      <th className="px-4 py-3 font-semibold">Status</th>
                      <th className="px-4 py-3 font-semibold">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {project.recent_issues.map((issue: any) => (
                      <tr key={issue.id} className="hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => navigate('/issues')}>
                        <td className="px-4 py-3 font-medium text-gray-900 truncate max-w-[200px]">{issue.title}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold ${
                            issue.status === 'open' ? 'bg-red-100 text-red-700' :
                            issue.status === 'closed' ? 'bg-green-100 text-green-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {issue.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {new Date(issue.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-xl">
                No recent issues.
              </div>
            )}
          </div>

        </div>

        {/* Sidebar (Right: 1 column wide) */}
        <div className="space-y-6">
          
          {/* Quick Stats Card */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-5">Project Overview</h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                <div className="flex items-center text-gray-600">
                  <AlertCircle className="w-5 h-5 mr-3 text-brand-500" />
                  <span className="font-medium">Total Issues</span>
                </div>
                <span className="font-bold text-gray-900">{project.stats?.total_issues || 0}</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-red-50 rounded-xl border border-red-100">
                <div className="flex items-center text-red-700">
                  <AlertCircle className="w-5 h-5 mr-3 text-red-500" />
                  <span className="font-medium">Open Issues</span>
                </div>
                <span className="font-bold text-red-700">{project.stats?.open_issues || 0}</span>
              </div>

              <div className="flex justify-between items-center p-3 bg-green-50 rounded-xl border border-green-100">
                <div className="flex items-center text-green-700">
                  <CheckCircle2 className="w-5 h-5 mr-3 text-green-500" />
                  <span className="font-medium">Closed Issues</span>
                </div>
                <span className="font-bold text-green-700">{project.stats?.closed_issues || 0}</span>
              </div>

              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                <div className="flex items-center text-gray-600">
                  <HardHat className="w-5 h-5 mr-3 text-brand-500" />
                  <span className="font-medium">Contractors</span>
                </div>
                <span className="font-bold text-gray-900">{project.stats?.assigned_contractors || 0}</span>
              </div>
            </div>

            <div className="mt-6 pt-5 border-t border-gray-100 text-xs text-gray-500 space-y-2">
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-2" /> Created on {new Date(project.created_at).toLocaleDateString()}
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-2" /> Last active {project.last_activity_at ? new Date(project.last_activity_at).toLocaleDateString() : 'Never'}
              </div>
            </div>
          </div>

          {/* Assigned Contractors Snippet */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
             <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-900">Contractors</h2>
              <button 
                onClick={() => navigate('/members')}
                className="text-sm font-medium text-brand-600 hover:text-brand-800"
              >
                Manage
              </button>
            </div>
            
            {project.contractors && project.contractors.length > 0 ? (
              <div className="space-y-3">
                {project.contractors.slice(0, 5).map((c: any) => (
                  <div key={c.id} className="flex items-center p-2 hover:bg-gray-50 rounded-lg transition-colors">
                    <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-xs mr-3 shrink-0">
                      {c.name.substring(0, 2).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-gray-900 truncate">{c.name}</p>
                      <p className="text-xs text-gray-500 truncate">{c.trade || c.company}</p>
                    </div>
                  </div>
                ))}
                {project.contractors.length > 5 && (
                  <div className="text-center pt-2">
                    <span className="text-xs text-gray-500">+{project.contractors.length - 5} more contractors</span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic">No contractors assigned.</p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};

export default ProjectDetailPage;
