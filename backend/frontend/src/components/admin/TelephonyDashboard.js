import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { Phone, Activity, Loader } from 'lucide-react';

export default function TelephonyDashboard() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCalls();
  }, []);

  async function loadCalls() {
    try {
      setError('');
      setLoading(true);
      const response = await api.get('/admin/telephony');
      setCalls(response.data.calls);
    } catch (err) {
      setError('Failed to load telephony data');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-purple-400 animate-spin mr-2" />
        <span className="text-white">Loading telephony data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <span className="text-red-400">{error}</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Telephony Dashboard</h1>
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 border border-purple-500/20">
          <div className="space-y-4">
            {calls.map(call => (
              <CallRow key={call.id} call={call} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function CallRow({ call }) {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
      <div className="flex items-center space-x-3">
        <Phone className="w-6 h-6 text-purple-400" />
        <div>
          <div className="text-white font-medium">{call.caller}</div>
          <div className="text-gray-400 text-sm">{call.time}</div>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <Activity className="w-5 h-5 text-blue-400" />
        <span className="text-sm text-blue-400">{call.status}</span>
      </div>
    </div>
  );
} 