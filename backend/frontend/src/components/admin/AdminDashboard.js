import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { Shield, Users, BarChart3, Activity, Loader } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    try {
      setError('');
      setLoading(true);
      const response = await api.get('/admin/dashboard');
      setStats(response.data.stats);
    } catch (err) {
      setError('Failed to load dashboard stats');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-purple-400 animate-spin mr-2" />
        <span className="text-white">Loading admin dashboard...</span>
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
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Admin Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Users" value={stats?.users || 0} icon={Users} color="purple" />
          <StatCard title="Active Sessions" value={stats?.active_sessions || 0} icon={Activity} color="blue" />
          <StatCard title="Applications" value={stats?.applications || 0} icon={BarChart3} color="green" />
          <StatCard title="System Health" value={stats?.system_health || 'OK'} icon={Shield} color="yellow" />
        </div>
        {/* Additional admin widgets can be added here */}
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }) {
  const colorClasses = {
    purple: 'bg-purple-600/20 text-purple-400 border-purple-500/20',
    blue: 'bg-blue-600/20 text-blue-400 border-blue-500/20',
    yellow: 'bg-yellow-600/20 text-yellow-400 border-yellow-500/20',
    green: 'bg-green-600/20 text-green-400 border-green-500/20'
  };
  return (
    <div className={`bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className={`w-8 h-8 ${colorClasses[color].split(' ')[1]}`} />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-gray-400 text-sm">{title}</div>
    </div>
  );
} 