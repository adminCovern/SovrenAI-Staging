import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { CheckCircle, XCircle, Loader, AlertTriangle } from 'lucide-react';

export default function ApplicationReview() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    loadApplications();
  }, []);

  async function loadApplications() {
    try {
      setError('');
      setLoading(true);
      const response = await api.get('/admin/applications');
      setApplications(response.data.applications);
    } catch (err) {
      setError('Failed to load applications');
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(appId, action) {
    setActionLoading(prev => ({ ...prev, [appId]: true }));
    try {
      await api.post(`/admin/applications/${appId}/${action}`);
      await loadApplications();
    } catch (err) {
      setError(`Failed to ${action} application`);
    } finally {
      setActionLoading(prev => ({ ...prev, [appId]: false }));
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-purple-400 animate-spin mr-2" />
        <span className="text-white">Loading applications...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <AlertTriangle className="w-6 h-6 text-red-400 mr-2" />
        <span className="text-red-400">{error}</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Application Review</h1>
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 border border-purple-500/20">
          {applications.length === 0 ? (
            <div className="text-gray-400 text-center">No applications to review.</div>
          ) : (
            <table className="min-w-full divide-y divide-gray-700">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Applicant</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Role</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Email</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {applications.map(app => (
                  <tr key={app.id}>
                    <td className="px-4 py-2 text-white">{app.name}</td>
                    <td className="px-4 py-2 text-white">{app.role}</td>
                    <td className="px-4 py-2 text-white">{app.email}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        app.status === 'approved' ? 'bg-green-700 text-green-300' :
                        app.status === 'rejected' ? 'bg-red-700 text-red-300' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 space-x-2">
                      <button
                        className="inline-flex items-center px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded disabled:opacity-50"
                        disabled={actionLoading[app.id] || app.status === 'approved'}
                        onClick={() => handleAction(app.id, 'approve')}
                        aria-label="Approve"
                      >
                        <CheckCircle className="w-4 h-4 mr-1" /> Approve
                      </button>
                      <button
                        className="inline-flex items-center px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded disabled:opacity-50"
                        disabled={actionLoading[app.id] || app.status === 'rejected'}
                        onClick={() => handleAction(app.id, 'reject')}
                        aria-label="Reject"
                      >
                        <XCircle className="w-4 h-4 mr-1" /> Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
} 