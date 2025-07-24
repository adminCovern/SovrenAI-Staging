import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import { Users, Zap, Activity, Target, Brain, Shield, Play, Pause, Settings } from 'lucide-react';

export default function AgentBattalion() {
  const { currentUser } = useAuth();
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deploying, setDeploying] = useState(false);

  useEffect(() => {
    loadAgents();
  }, []);

  async function loadAgents() {
    try {
      const response = await api.get('/api/agents/status');
      // Use the new API structure
      setAgents(response.data.agents.profiles || []);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setLoading(false);
    }
  }

  async function deployAgent(agentId) {
    try {
      setDeploying(true);
      await api.post(`/user/agents/${agentId}/deploy`);
      await loadAgents(); // Reload to get updated status
    } catch (error) {
      console.error('Failed to deploy agent:', error);
    } finally {
      setDeploying(false);
    }
  }

  async function pauseAgent(agentId) {
    try {
      await api.post(`/user/agents/${agentId}/pause`);
      await loadAgents();
    } catch (error) {
      console.error('Failed to pause agent:', error);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading Agent Battalion...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Agent Battalion</h1>
        
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Active Agents"
            value={agents.filter(a => a.status === 'active').length}
            icon={Users}
            color="purple"
          />
          <StatCard
            title="Total Operations"
            value={agents.reduce((sum, a) => sum + (a.operations || 0), 0)}
            icon={Activity}
            color="blue"
          />
          <StatCard
            title="Success Rate"
            value={`${Math.round(agents.reduce((sum, a) => sum + (a.success_rate || 0), 0) / agents.length)}%`}
            icon={Target}
            color="green"
          />
          <StatCard
            title="Processing Power"
            value={`${agents.filter(a => a.status === 'active').length * 25}%`}
            icon={Zap}
            color="yellow"
          />
        </div>

        {/* Agent Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {agents.map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              selected={selectedAgent?.id === agent.id}
              onSelect={() => setSelectedAgent(agent)}
              onDeploy={() => deployAgent(agent.id)}
              onPause={() => pauseAgent(agent.id)}
              deploying={deploying}
            />
          ))}
        </div>

        {/* Agent Details */}
        {selectedAgent && (
          <div className="mt-8 bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-purple-500/20">
            <h2 className="text-xl font-bold text-white mb-4">Agent Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">{selectedAgent.name}</h3>
                <p className="text-gray-400 mb-4">{selectedAgent.reasoning || 'No reasoning available.'}</p>
                
                <div className="space-y-3">
                  <DetailItem label="Status" value={selectedAgent.status} />
                  <DetailItem label="Operations" value={selectedAgent.operations} />
                  <DetailItem label="Success Rate" value={`${selectedAgent.success_rate}%`} />
                  <DetailItem label="Last Active" value={selectedAgent.last_active} />
                  <DetailItem label="PhD Expertise" value={selectedAgent.phd_expertise && selectedAgent.phd_expertise.length > 0 ? selectedAgent.phd_expertise.join(', ') : 'N/A'} />
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Recent Activity</h3>
                <div className="space-y-2">
                  {selectedAgent.recent_activity?.map((activity, index) => (
                    <ActivityItem key={index} activity={activity} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
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

function AgentCard({ agent, selected, onSelect, onDeploy, onPause, deploying }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'text-green-400';
      case 'paused':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'strategic':
        return Brain;
      case 'tactical':
        return Target;
      case 'defensive':
        return Shield;
      default:
        return Users;
    }
  };

  const Icon = getIcon(agent.type);

  return (
    <div
      onClick={onSelect}
      className={`bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border border-gray-700 cursor-pointer transition ${
        selected ? 'border-purple-500' : 'hover:border-gray-600'
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Icon className="w-8 h-8 text-purple-400" />
          <div>
            <h3 className="text-white font-semibold">{agent.name}</h3>
            <p className="text-gray-400 text-sm">{agent.type}</p>
            <p className="text-xs text-blue-300 mt-1">PhD Expertise: {agent.phd_expertise && agent.phd_expertise.length > 0 ? agent.phd_expertise.join(', ') : 'N/A'}</p>
          </div>
        </div>
        <div className={`text-sm ${getStatusColor(agent.status)}`}>{agent.status}</div>
      </div>
      <p className="text-gray-300 text-sm mb-4">{agent.reasoning || 'No reasoning available.'}</p>
      
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          {agent.operations} operations
        </div>
        <div className="flex space-x-2">
          {agent.status === 'active' ? (
            <button
              onClick={(e) => { e.stopPropagation(); onPause(); }}
              className="p-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg transition"
            >
              <Pause className="w-4 h-4 text-white" />
            </button>
          ) : (
            <button
              onClick={(e) => { e.stopPropagation(); onDeploy(); }}
              disabled={deploying}
              className="p-2 bg-green-600 hover:bg-green-700 rounded-lg transition disabled:opacity-50"
            >
              <Play className="w-4 h-4 text-white" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}:</span>
      <span className="text-white">{value}</span>
    </div>
  );
}

function ActivityItem({ activity }) {
  return (
    <div className="flex items-center space-x-3 text-sm">
      <Activity className="w-4 h-4 text-gray-500" />
      <span className="text-gray-300 flex-1">{activity.description}</span>
      <span className="text-gray-500">{activity.timestamp}</span>
    </div>
  );
} 