import React, { useState, useEffect } from 'react';
import { collection, query, where, orderBy, limit, getDocs } from 'firebase/firestore';
import { db } from '../services/firebase';
import { useAuth } from '../context/AuthContext';

const AuditLogsPage: React.FC = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterAction, setFilterAction] = useState('');
  const [filterUser, setFilterUser] = useState('');

  useEffect(() => {
    fetchAuditLogs();
  }, [filterAction, filterUser]);

  // Example simple RBAC check
  if (user?.email !== 'wincadsg@gmail.com') {
    return <div className="p-6 text-red-600 font-bold">Access Denied. Admin only.</div>;
  }
  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      let q = query(
        collection(db, 'audit_logs'),
        orderBy('timestamp', 'desc'),
        limit(100)
      );

      if (filterAction) {
        q = query(q, where('action', '==', filterAction));
      }
      if (filterUser) {
        q = query(q, where('user_id', '==', filterUser));
      }

      const snapshot = await getDocs(q);
      const data = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setLogs(data);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Audit Logs</h1>
      
      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <input
          type="text"
          placeholder="Filter by user email"
          value={filterUser}
          onChange={(e) => setFilterUser(e.target.value)}
          className="border p-2 rounded"
        />
        <select
          value={filterAction}
          onChange={(e) => setFilterAction(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="">All Actions</option>
          <option value="POST_SITES">Create Site</option>
          <option value="POST_VIDEOS">Upload Video</option>
          <option value="POST_ISSUES">Create Issue</option>
          <option value="LOGIN">Login</option>
        </select>
        <button onClick={fetchAuditLogs} className="bg-blue-600 text-white px-4 py-2 rounded">
          Refresh
        </button>
      </div>

      {/* Table */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="overflow-x-auto bg-white rounded shadow">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100 text-left">
                <th className="border p-3">Timestamp</th>
                <th className="border p-3">User</th>
                <th className="border p-3">Action</th>
                <th className="border p-3">Resource</th>
                <th className="border p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50 border-b">
                  <td className="p-3 whitespace-nowrap">
                    {log.timestamp?.toDate ? new Date(log.timestamp.toDate()).toLocaleString() : String(log.timestamp)}
                  </td>
                  <td className="p-3">{log.user_id}</td>
                  <td className="p-3">{log.action}</td>
                  <td className="p-3">{log.resource_name}</td>
                  <td className="p-3">
                    <span className={log.status === 'SUCCESS' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-4 text-center text-gray-500">No logs found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AuditLogsPage;
