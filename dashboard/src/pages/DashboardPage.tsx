import React, { useEffect, useState } from 'react';
import { Building2, Camera, Clock, AlertTriangle, MapPin } from 'lucide-react';
import { getSites, getAllSessions, getAllFloorPlans, getAllLocations } from '../services/api';

const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [recentCaptures, setRecentCaptures] = useState<any[]>([]);
  const [stats, setStats] = useState({
    sites: 0,
    captures: 0,
    floorPlans: 0,
    pins: 0
  });

  useEffect(() => {
    document.title = "Dashboard | Space360";
    
    const fetchDashboardData = async () => {
      try {
        const [sitesRes, sessionsRes, plansRes, locsRes] = await Promise.all([
          getSites(),
          getAllSessions(),
          getAllFloorPlans(),
          getAllLocations()
        ]);

        const sessions = sessionsRes.data || [];
        setStats({
          sites: sitesRes.data?.length || 0,
          captures: sessions.length,
          floorPlans: plansRes.data?.length || 0,
          pins: locsRes.data?.length || 0
        });

        // Get 3 most recent captures (assuming they are ordered by date desc in API)
        setRecentCaptures(sessions.slice(0, 3));
      } catch (error) {
        console.error("Failed to fetch dashboard stats", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
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
          <div className="p-3 rounded-full bg-indigo-50 text-indigo-600 mr-4">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Floor Plans</p>
            {loading ? (
              <div className="h-6 w-12 bg-gray-200 rounded animate-pulse mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold text-gray-900">{stats.floorPlans}</p>
            )}
          </div>
        </div>

        <div className="card flex items-center">
          <div className="p-3 rounded-full bg-purple-50 text-purple-600 mr-4">
            <MapPin className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Pins</p>
            {loading ? (
              <div className="h-6 w-12 bg-gray-200 rounded animate-pulse mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold text-gray-900">{stats.pins}</p>
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
        ) : recentCaptures.length === 0 ? (
          <div className="text-center py-10 text-gray-500">
            No recent captures found. Start by uploading a floor plan and adding captures.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentCaptures.map(c => (
              <div key={c.id} className="border border-gray-100 rounded-lg p-3 hover:shadow-md transition-shadow flex items-center space-x-4">
                <div className="w-16 h-16 bg-gray-100 rounded-md overflow-hidden flex-shrink-0">
                  {c.thumbnail_url || c.image_url ? (
                    <img src={c.thumbnail_url || c.image_url} alt="capture" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <Camera className="w-6 h-6" />
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-gray-900 truncate">
                    {c.location_label || c.location_point_id.slice(0, 8)}
                  </p>
                  <p className="text-xs text-gray-500 truncate mt-0.5">
                    {c.site_name || 'Site Capture'}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(c.captured_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
