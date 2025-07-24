import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { Shield, BarChart3, Loader } from 'lucide-react';

export default function SystemMonitoring() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMetrics();
  }, []);

  async function loadMetrics() {
    try {
      setError('');
      setLoading(true);
      const response = await api.get('/admin/monitoring');
      setMetrics(response.data.metrics);
    } catch (err) {
      setError('Failed to load system metrics');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-purple-400 animate-spin mr-2" />
        <span className="text-white">Loading system metrics...</span>
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
        <h1 className="text-3xl font-bold text-white mb-8">System Monitoring</h1>
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 border border-purple-500/20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <MetricCard label="CPU Usage" value={metrics?.cpu_usage} />
            <MetricCard label="Memory Usage" value={metrics?.memory_usage} />
            <MetricCard label="Disk Space" value={metrics?.disk_space} />
            <MetricCard label="Network" value={metrics?.network} />
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="p-6 bg-gray-700/30 rounded-xl border border-gray-600 flex flex-col items-center">
      <BarChart3 className="w-8 h-8 text-purple-400 mb-2" />
      <div className="text-lg text-white font-semibold mb-1">{label}</div>
      <div className="text-2xl text-green-400 font-bold">{value}</div>
    </div>
  );
} 