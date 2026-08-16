import React, { useEffect, useState } from 'react';
import { getDashboardStats, getDashboardTimeline } from '../services/api';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, CheckCircle, Clock, AlertTriangle, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const STATUS_COLORS = {
  open: '#3b82f6', // blue
  in_review: '#f59e0b', // amber
  pending: '#f97316', // orange
  closed: '#22c55e', // green
  critical: '#ef4444' // red
};

const TYPE_COLORS = [
  '#8b5cf6', '#ec4899', '#14b8a6', '#f43f5e', '#84cc16'
];

const DashboardPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, timelineRes] = await Promise.all([
        getDashboardStats(),
        getDashboardTimeline()
      ]);
      setStats(statsRes.data);
      setTimeline(timelineRes.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchDashboardData();
    }
  }, [isAdmin]);

  if (!isAdmin) {
    return <Navigate to="/" />;
  }

  if (loading || !stats) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  const statusData = [
    { name: 'Open', value: stats.open_issues, color: STATUS_COLORS.open },
    { name: 'In Review', value: stats.in_review, color: STATUS_COLORS.in_review },
    { name: 'Pending', value: stats.pending, color: STATUS_COLORS.pending },
    { name: 'Closed', value: stats.closed, color: STATUS_COLORS.closed },
    { name: 'Critical', value: stats.critical, color: STATUS_COLORS.critical },
  ].filter(d => d.value > 0);

  const typeData = Object.entries(stats.by_type || {}).map(([key, value], index) => ({
    name: key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
    count: value,
    fill: TYPE_COLORS[index % TYPE_COLORS.length]
  }));

  const workloadData = Object.entries(stats.by_contractor || {}).map(([email, count]) => ({
    email,
    count: count as number,
    percent: stats.total_issues > 0 ? Math.round((count as number / stats.total_issues) * 100) : 0
  })).sort((a, b) => b.count - a.count);

  return (
    <div className="max-w-7xl mx-auto pb-12 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Project Dashboard</h1>
        <button onClick={fetchDashboardData} className="px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 min-h-[44px]">
          Refresh Data
        </button>
      </div>

      {/* Row 1: Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg mr-4">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Issues</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_issues}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center">
          <div className="p-3 bg-red-100 text-red-600 rounded-lg mr-4">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Open Issues</p>
            <p className="text-2xl font-bold text-red-600">{stats.open_issues}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center">
          <div className="p-3 bg-green-100 text-green-600 rounded-lg mr-4">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Closed Issues</p>
            <p className="text-2xl font-bold text-green-600">{stats.closed}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center">
          <div className="p-3 bg-orange-100 text-orange-600 rounded-lg mr-4">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Critical Issues</p>
            <p className="text-2xl font-bold text-orange-600">{stats.critical}</p>
          </div>
        </div>
      </div>

      {/* Row 2: Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Status Breakdown</h2>
          <div className="h-64">
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={statusData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">No data available</div>
            )}
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Issues by Type</h2>
          <div className="h-64">
            {typeData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 12}} />
                  <Tooltip />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">No data available</div>
            )}
          </div>
        </div>
      </div>

      {/* Row 3: Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-bold text-gray-900">Contractor Workload</h2>
          </div>
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3">Contractor</th>
                  <th className="px-4 py-3">Assigned Issues</th>
                  <th className="px-4 py-3">% of Total</th>
                </tr>
              </thead>
              <tbody>
                {workloadData.map((w, i) => (
                  <tr key={i} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{w.email}</td>
                    <td className="px-4 py-3">{w.count}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center">
                        <span className="w-8">{w.percent}%</span>
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden ml-2">
                          <div className="h-full bg-brand-500" style={{ width: `${w.percent}%` }}></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
                {workloadData.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-4 py-8 text-center text-gray-500">No contractors assigned</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-bold text-gray-900">Recent Issues</h2>
          </div>
          <div className="divide-y divide-gray-100 flex-1 overflow-y-auto max-h-80">
            {timeline.map(issue => (
              <div key={issue.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start mb-1">
                  <h3 className="font-semibold text-gray-900 truncate pr-4">{issue.title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    issue.status === 'open' ? 'bg-blue-100 text-blue-700' :
                    issue.status === 'closed' ? 'bg-green-100 text-green-700' :
                    issue.status === 'critical' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {issue.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center text-xs text-gray-500">
                  <span className="capitalize mr-2 bg-gray-100 px-1.5 py-0.5 rounded">{issue.issue_type.replace('_', ' ')}</span>
                  <Clock className="w-3 h-3 mr-1" />
                  {new Date(issue.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
            {timeline.length === 0 && (
              <div className="p-8 text-center text-gray-500">No issues found</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
