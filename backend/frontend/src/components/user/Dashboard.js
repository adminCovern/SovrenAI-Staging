import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import {
  Brain, Activity, TrendingUp, Users, Clock, Zap,
  Phone, MessageSquare, BarChart3, Shield, LogOut
} from 'lucide-react';

export default function Dashboard() {
  const { currentUser, logout } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    
    // Set up real-time updates
    const interval = setInterval(loadDashboardData, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  async function loadDashboardData() {
    try {
      const response = await api.get('/user/dashboard');
      setMetrics(response.data.metrics);
      setActivities(response.data.recent_activity);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading your sovereign dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900">
      {/* Header */}
      <header className="bg-gray-900/50 backdrop-blur-xl border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Brain className="w-8 h-8 text-purple-400 mr-3" />
              <h1 className="text-xl font-bold text-white">SOVREN AI</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">Welcome, {currentUser?.name}</span>
              <button
                onClick={logout}
                className="text-gray-400 hover:text-white transition"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Decisions Today"
            value={metrics?.decisions_today || 0}
            icon={Brain}
            trend="+12%"
            color="purple"
          />
          <MetricCard
            title="Active Operations"
            value={metrics?.active_operations || 0}
            icon={Activity}
            trend="+5%"
            color="blue"
          />
          <MetricCard
            title="Processing Power"
            value={metrics?.processing_power || '0%'}
            icon={Zap}
            color="yellow"
          />
          <MetricCard
            title="Scenarios Evaluated"
            value={(metrics?.scenarios_evaluated || 0).toLocaleString()}
            icon={BarChart3}
            trend="+18%"
            color="green"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <QuickActionCard
            title="Voice Command"
            description="Interact with SOVREN using natural voice"
            icon={Phone}
            link="/voice"
            color="purple"
          />
          <QuickActionCard
            title="Shadow Board"
            description="Consult your virtual C-Suite executives"
            icon={Users}
            link="/shadow-board"
            color="blue"
          />
          <QuickActionCard
            title="Time Machine"
            description="Analyze temporal patterns and predictions"
            icon={Clock}
            link="/time-machine"
            color="green"
          />
        </div>

        {/* SOVREN Score */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 mb-8 border border-purple-500/20">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white">Your SOVREN Score</h2>
            <Link to="/score" className="text-purple-400 hover:text-purple-300 text-sm">
              View Details →
            </Link>
          </div>
          
          <div className="flex items-center">
            <div className="text-5xl font-bold text-purple-400">
              {currentUser?.sovren_score || 425}
            </div>
            <div className="ml-4">
              <div className="text-green-400 text-sm">+15 from last week</div>
              <div className="text-gray-400 text-sm">Industry avg: 380</div>
            </div>
          </div>
          
          <div className="mt-4 bg-gray-700/30 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-purple-500 to-purple-400 h-full transition-all duration-1000"
              style={{ width: `${(currentUser?.sovren_score || 425) / 10}%` }}
            />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
          <h2 className="text-xl font-bold text-white mb-4">Recent Activity</h2>
          
          <div className="space-y-3">
            {activities.map((activity, index) => (
              <ActivityItem key={index} activity={activity} />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, trend, color }) {
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
        {trend && (
          <span className="text-green-400 text-sm">{trend}</span>
        )}
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-gray-400 text-sm">{title}</div>
    </div>
  );
}

function QuickActionCard({ title, description, icon: Icon, link, color }) {
  const colorClasses = {
    purple: 'hover:border-purple-400',
    blue: 'hover:border-blue-400',
    green: 'hover:border-green-400'
  };

  return (
    <Link
      to={link}
      className={`bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700 ${colorClasses[color]} transition-all duration-200 block`}
    >
      <Icon className="w-10 h-10 text-gray-400 mb-3" />
      <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </Link>
  );
}

function ActivityItem({ activity }) {
  const getActivityIcon = (action) => {
    switch (action) {
      case 'decision_made':
        return Brain;
      case 'voice_interaction':
        return Phone;
      case 'shadow_board_consultation':
        return Users;
      default:
        return Activity;
    }
  };

  const Icon = getActivityIcon(activity.action);

  return (
    <div className="flex items-center space-x-3 text-sm">
      <Icon className="w-4 h-4 text-gray-500" />
      <span className="text-gray-300 flex-1">{activity.action.replace('_', ' ')}</span>
      <span className="text-gray-500">{new Date(activity.timestamp).toLocaleTimeString()}</span>
    </div>
  );
} 