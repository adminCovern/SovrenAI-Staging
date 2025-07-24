import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import { Clock, TrendingUp, TrendingDown, BarChart3, Loader } from 'lucide-react';

export default function TimeMachine() {
  const { currentUser } = useAuth();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPredictions();
  }, []);

  async function loadPredictions() {
    try {
      setError('');
      setLoading(true);
      const response = await api.get('/user/time-machine');
      setPredictions(response.data.predictions);
    } catch (err) {
      setError('Failed to load predictions');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-purple-400 animate-spin mr-2" />
        <span className="text-white">Loading time machine predictions...</span>
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
        <h1 className="text-3xl font-bold text-white mb-8">Time Machine</h1>
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 border border-purple-500/20 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Temporal Predictions</h2>
          <div className="space-y-6">
            {predictions.map((prediction, idx) => (
              <PredictionCard key={idx} prediction={prediction} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function PredictionCard({ prediction }) {
  const isPositive = prediction.trend === 'up';
  return (
    <div className="p-6 bg-gray-700/30 rounded-xl border border-gray-600 flex items-center space-x-4">
      <div className="flex-shrink-0">
        {isPositive ? (
          <TrendingUp className="w-8 h-8 text-green-400" />
        ) : (
          <TrendingDown className="w-8 h-8 text-red-400" />
        )}
      </div>
      <div className="flex-1">
        <div className="text-lg text-white font-semibold mb-1">{prediction.title}</div>
        <div className="text-gray-300 text-sm mb-2">{prediction.description}</div>
        <div className="flex items-center space-x-2 text-xs">
          <Clock className="w-4 h-4 text-purple-400" />
          <span className="text-gray-400">{prediction.date}</span>
        </div>
      </div>
      <div className="flex flex-col items-end">
        <span className={`font-bold text-xl ${isPositive ? 'text-green-400' : 'text-red-400'}`}>{prediction.value}</span>
        <span className="text-gray-400 text-xs">{prediction.metric}</span>
      </div>
    </div>
  );
} 