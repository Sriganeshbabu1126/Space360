import React, { useEffect, useState } from 'react';
import { Building2, Camera, Clock, AlertTriangle } from 'lucide-react';
import { getSites } from '../services/api';

const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    sites: 0,
    captures: 0,
    pendingJobs: 0,
    issues: 0
  });

  useEffect(() => {
    document.title = "Dashboard | Space360";
    const fetchStats = async () => {
      try {
        const res = await getSites();
        const siteCount = res.data.length || 0;
        setStats({
          sites: siteCount,
          captures: 0,
          pendingJobs: 0,
          issues: 0
        });
      } catch (error) {
        console.error("Failed to fetch dashboard stats", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Space360 Dashboard</h2>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Stat Cards */}
        <div className="card flex items-center">
          <div className="p-3 rounded-full bg-blue-50 text-blue-600 mr-4">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Sites</p>
            {loading ? (
              <div className="h-6 w-12 bg-gray-200 rounded animate-pulse mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold text-gray-900">{stats.sites}</p>
            )}
          </div>
        </div>

        <div className="card flex items-center">
          <div className="p-3 rounded-full bg-green-50 text-green-600 mr-4">
            <Camera className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Captures</p>
            {loading ? (
              <div className="h-6 w-12 bg-gray-200 rounded animate-pulse mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold text-gray-900">{stats.captures}</p>
            )}
          </div>
        </div>

        <div className="card flex items-center">
          <div className="p-3 rounded-full bg-yellow-50 text-yellow-600 mr-4">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Pending AI Jobs</p>
            {loading ? (
              <div className="h-6 w-12 bg-gray-200 rounded animate-pulse mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold text-gray-900">{stats.pendingJobs}</p>
            )}
          </div>
        </div>

        <div className="card flex items-center">
          <div className="p-3 rounded-full bg-red-50 text-red-600 mr-4">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Issues Flagged</p>
            {loading ? (
              <div className="h-6 w-12 bg-gray-200 rounded animate-pulse mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold text-gray-900">{stats.issues}</p>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Captures</h3>
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="text-center py-10 text-gray-500">
            No recent captures found. Start by uploading a floor plan and adding captures.
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
