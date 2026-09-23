import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects } from '../services/api';
import { 
  Building2, Plus, Search, MapPin, Activity, 
  AlertCircle, CheckCircle2, Folder, Clock, Calendar
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSiteContext } from '../context/SiteContext';

interface ProjectStats {
  total_issues: number;
  open_issues: number;
  critical_issues: number;
  closed_issues: number;
  total_floor_plans: number;
  total_captures: number;
  assigned_contractors: number;
}

interface Project {
  id: string;
  name: string;
  location?: string;
  status: string;
  description?: string;
  stats: ProjectStats;
  last_activity_at?: string;
  created_at: string;
}

const HomePage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'archived'>('all');
  const [search, setSearch] = useState('');
  
  const { isAdmin, user } = useAuth();
  const { setSelectedSiteId } = useSiteContext();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const res = await getProjects();
        setProjects(res.data);
      } catch (err) {
        console.error('Error fetching projects', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const filteredProjects = useMemo(() => {
    let result = projects;
    if (filter !== 'all') {
      result = result.filter(p => p.status === filter);
    }
    if (search) {
      const s = search.toLowerCase();
      result = result.filter(p => 
        p.name.toLowerCase().includes(s) || 
        (p.location && p.location.toLowerCase().includes(s))
      );
    }
    return result;
  }, [projects, filter, search]);

  const handleProjectClick = (project: Project) => {
    setSelectedSiteId(project.id);
    navigate(`/projects/${project.id}/captures`);
  };

  // Calculate global stats
  const globalStats = useMemo(() => {
    return projects.reduce((acc, p) => ({
      total_active: acc.total_active + (p.status === 'active' ? 1 : 0),
      total_issues: acc.total_issues + p.stats.open_issues,
      total_captures: acc.total_captures + p.stats.total_captures
    }), { total_active: 0, total_issues: 0, total_captures: 0 });
  }, [projects]);

  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header with Greeting */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 bg-gradient-to-r from-brand-900 to-brand-700 p-8 rounded-3xl text-white shadow-lg overflow-hidden relative">
        <div className="absolute top-0 right-0 -mt-16 -mr-16 opacity-10">
          <Building2 className="w-64 h-64" />
        </div>
        <div className="relative z-10">
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">
            {greeting}, {user?.email?.split('@')[0] || 'User'}!
          </h1>
          <p className="text-brand-100 text-lg opacity-90 max-w-xl">
            Here's what's happening across your construction sites today.
          </p>
        </div>
        {isAdmin && (
          <button onClick={() => navigate('/sites')} className="relative z-10 bg-white text-brand-900 hover:bg-brand-50 px-6 py-3 rounded-xl font-bold flex items-center transition-all shadow-xl hover:shadow-2xl transform hover:-translate-y-0.5">
            <Plus className="w-5 h-5 mr-2" />
            New Project
          </button>
        )}
      </div>

      {/* Global Stats Row */}
      {!loading && projects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center">
            <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mr-4">
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <div className="text-sm text-gray-500 font-medium">Active Projects</div>
              <div className="text-3xl font-bold text-gray-900">{globalStats.total_active}</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center">
            <div className="w-14 h-14 bg-orange-50 text-orange-600 rounded-2xl flex items-center justify-center mr-4">
              <AlertCircle className="w-7 h-7" />
            </div>
            <div>
              <div className="text-sm text-gray-500 font-medium">Global Open Issues</div>
              <div className="text-3xl font-bold text-gray-900">{globalStats.total_issues}</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center">
            <div className="w-14 h-14 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center mr-4">
              <Activity className="w-7 h-7" />
            </div>
            <div>
              <div className="text-sm text-gray-500 font-medium">Total Captures</div>
              <div className="text-3xl font-bold text-gray-900">{globalStats.total_captures}</div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
        <div className="flex space-x-1 w-full sm:w-auto p-1 bg-gray-200/50 rounded-xl">
          {(['all', 'active', 'archived'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-5 py-2.5 text-sm font-bold rounded-lg capitalize transition-all ${
                filter === f 
                  ? 'bg-white text-brand-700 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects by name or location..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 transition-shadow shadow-sm"
          />
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="bg-white rounded-2xl h-64 animate-pulse border border-gray-100 shadow-sm"></div>
          ))}
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300">
          <Folder className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">No projects found</h3>
          <p className="text-gray-500 max-w-sm mx-auto mt-2">Try adjusting your filters or search query to find what you're looking for.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProjects.map(project => (
            <div 
              key={project.id}
              onClick={() => handleProjectClick(project)}
              className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-xl hover:border-brand-300 transition-all duration-300 cursor-pointer group flex flex-col"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-brand-50 rounded-xl flex items-center justify-center text-brand-600 group-hover:scale-110 group-hover:bg-brand-600 group-hover:text-white transition-all duration-300">
                  <Building2 className="w-6 h-6" />
                </div>
                <span className={`px-2.5 py-1 text-xs font-semibold uppercase tracking-wider rounded-full ${
                  project.status === 'active' ? 'bg-green-100 text-green-700' : 
                  project.status === 'archived' ? 'bg-gray-100 text-gray-600' : 
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {project.status}
                </span>
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-brand-700 transition-colors line-clamp-1">{project.name}</h3>
              <p className="text-sm text-gray-500 mt-1.5 flex items-center">
                <MapPin className="w-4 h-4 mr-1 opacity-70" /> {project.location || 'No location specified'}
              </p>

              <div className="mt-6 pt-5 border-t border-gray-100 grid grid-cols-2 gap-y-4 gap-x-2">
                <div className="flex flex-col">
                  <span className="text-xs text-gray-500 uppercase font-semibold tracking-wider flex items-center">
                    <AlertCircle className="w-3.5 h-3.5 mr-1" /> Open
                  </span>
                  <span className={`text-lg font-bold mt-0.5 ${project.stats.critical_issues > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                    {project.stats.open_issues}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-500 uppercase font-semibold tracking-wider flex items-center">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Closed
                  </span>
                  <span className="text-lg font-bold text-gray-900 mt-0.5">{project.stats.closed_issues}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-500 uppercase font-semibold tracking-wider flex items-center">
                    <Activity className="w-3.5 h-3.5 mr-1" /> Floor Plans
                  </span>
                  <span className="text-lg font-bold text-gray-900 mt-0.5">{project.stats.total_floor_plans}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-500 uppercase font-semibold tracking-wider flex items-center">
                    <Calendar className="w-3.5 h-3.5 mr-1" /> Created
                  </span>
                  <span className="text-sm font-semibold text-gray-900 mt-1">
                    {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              
              <div className="mt-auto pt-6">
                <div className="flex items-center text-xs text-gray-400 font-medium">
                  <Clock className="w-3.5 h-3.5 mr-1.5" /> 
                  {project.last_activity_at 
                    ? `Last active ${new Date(project.last_activity_at).toLocaleDateString()}` 
                    : 'No recent activity'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HomePage;
