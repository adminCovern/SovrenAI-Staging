import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import { Brain, TrendingUp, TrendingDown, Target, Award, Activity } from 'lucide-react';

export default function SovrenScore() {
  const { currentUser } = useAuth();
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScoreData();
  }, []);

  async function loadScoreData() {
    try {
      const response = await api.get('/user/score');
      setScoreData(response.data);
    } catch (error) {
      console.error('Failed to load score data:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading your SOVREN score...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">SOVREN Score Analytics</h1>
        
        {/* Main Score Display */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 mb-8 border border-purple-500/20">
          <div className="text-center">
            <div className="text-8xl font-bold text-purple-400 mb-4">
              {currentUser?.sovren_score || 425}
            </div>
            <div className="text-xl text-gray-300 mb-2">Your Sovereignty Score</div>
            <div className="flex items-center justify-center space-x-4 text-sm">
              <div className="flex items-center text-green-400">
                <TrendingUp className="w-4 h-4 mr-1" />
                +15 from last week
              </div>
              <div className="text-gray-400">Industry avg: 380</div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-8 bg-gray-700/30 rounded-full h-4 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-purple-500 to-purple-400 h-full transition-all duration-1000"
              style={{ width: `${(currentUser?.sovren_score || 425) / 10}%` }}
            />
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <ScoreCategory
            title="Decision Quality"
            score={scoreData?.decision_quality || 85}
            icon={Brain}
            color="purple"
          />
          <ScoreCategory
            title="Strategic Thinking"
            score={scoreData?.strategic_thinking || 78}
            icon={Target}
            color="blue"
          />
          <ScoreCategory
            title="Risk Management"
            score={scoreData?.risk_management || 92}
            icon={Award}
            color="green"
          />
        </div>

        {/* Historical Trends */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 mb-8 border border-purple-500/20">
          <h2 className="text-xl font-bold text-white mb-4">Score History</h2>
          <div className="space-y-4">
            {scoreData?.history?.map((entry, index) => (
              <HistoryEntry key={index} entry={entry} />
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
          <h2 className="text-xl font-bold text-white mb-4">Recommendations</h2>
          <div className="space-y-4">
            {scoreData?.recommendations?.map((rec, index) => (
              <Recommendation key={index} recommendation={rec} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ScoreCategory({ title, score, icon: Icon, color }) {
  const colorClasses = {
    purple: 'bg-purple-600/20 text-purple-400 border-purple-500/20',
    blue: 'bg-blue-600/20 text-blue-400 border-blue-500/20',
    green: 'bg-green-600/20 text-green-400 border-green-500/20'
  };

  return (
    <div className={`bg-gray-800/50 backdrop-blur-xl rounded-xl p-6 border ${colorClasses[color]}`}>
      <div className="flex items-center mb-4">
        <Icon className={`w-8 h-8 ${colorClasses[color].split(' ')[1]} mr-3`} />
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      <div className="text-3xl font-bold text-white mb-2">{score}</div>
      <div className="text-gray-400 text-sm">out of 100</div>
    </div>
  );
}

function HistoryEntry({ entry }) {
  const isPositive = entry.change > 0;
  
  return (
    <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
      <div className="flex items-center space-x-4">
        <div className="text-gray-300">{entry.date}</div>
        <div className="text-white font-medium">{entry.score}</div>
      </div>
      <div className={`flex items-center ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
        {isPositive ? (
          <TrendingUp className="w-4 h-4 mr-1" />
        ) : (
          <TrendingDown className="w-4 h-4 mr-1" />
        )}
        <span>{Math.abs(entry.change)}</span>
      </div>
    </div>
  );
}

function Recommendation({ recommendation }) {
  return (
    <div className="flex items-start space-x-3 p-4 bg-gray-700/30 rounded-lg">
      <Activity className="w-5 h-5 text-purple-400 mt-1" />
      <div>
        <h4 className="text-white font-medium mb-1">{recommendation.title}</h4>
        <p className="text-gray-300 text-sm">{recommendation.description}</p>
      </div>
    </div>
  );
} 