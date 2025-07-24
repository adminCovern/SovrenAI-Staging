import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import { Users, MessageSquare, Brain, TrendingUp, DollarSign, Building, Shield } from 'lucide-react';

export default function ShadowBoard() {
  const { currentUser } = useAuth();
  const [executives, setExecutives] = useState([]);
  const [selectedExec, setSelectedExec] = useState(null);
  const [conversation, setConversation] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadExecutives();
  }, []);

  async function loadExecutives() {
    try {
      const response = await api.get('/api/shadow-board/executives');
      setExecutives(response.data.executives);
    } catch (error) {
      console.error('Failed to load executives:', error);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage() {
    if (!message.trim() || !selectedExec) return;

    const userMessage = { type: 'user', text: message, timestamp: new Date() };
    setConversation(prev => [...prev, userMessage]);
    setMessage('');
    setSending(true);

    try {
      const response = await api.post('/user/shadow-board/consult', {
        executive_id: selectedExec.id,
        message: message
      });

      const execMessage = { 
        type: 'executive', 
        text: response.data.response, 
        timestamp: new Date(),
        executive: selectedExec.name
      };
      setConversation(prev => [...prev, execMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  }

  function selectExecutive(exec) {
    setSelectedExec(exec);
    setConversation([]);
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading Shadow Board...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Shadow Board</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Executive List */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-purple-500/20">
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-lg font-semibold text-white">C-Suite Executives</h2>
              </div>
              <div className="p-4">
                <div className="space-y-3">
                  {executives.map(exec => (
                    <ExecutiveCard
                      key={exec.id}
                      executive={exec}
                      selected={selectedExec?.id === exec.id}
                      onSelect={() => selectExecutive(exec)}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Conversation Area */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl border border-purple-500/20 h-[600px] flex flex-col">
              {selectedExec ? (
                <>
                  {/* Header */}
                  <div className="p-4 border-b border-gray-700">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-purple-600/20 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-purple-400" />
                      </div>
                      <div>
                        <h3 className="text-white font-semibold">{selectedExec.name}</h3>
                        <p className="text-gray-400 text-sm">{selectedExec.role}</p>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 p-4 overflow-y-auto space-y-4">
                    {conversation.map((msg, index) => (
                      <Message key={index} message={msg} />
                    ))}
                    {sending && (
                      <div className="flex items-center space-x-2 text-gray-400">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    )}
                  </div>

                  {/* Input */}
                  <div className="p-4 border-t border-gray-700">
                    <div className="flex space-x-3">
                      <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask your executive..."
                        className="flex-1 px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        disabled={sending}
                      />
                      <button
                        onClick={sendMessage}
                        disabled={!message.trim() || sending}
                        className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Send
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <Users className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <p>Select an executive to start consulting</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ExecutiveCard({ executive, selected, onSelect }) {
  const getIcon = (role) => {
    switch (role.toLowerCase()) {
      case 'ceo':
        return Brain;
      case 'cfo':
        return DollarSign;
      case 'cto':
        return TrendingUp;
      case 'coo':
        return Building;
      case 'cso':
        return Shield;
      default:
        return Users;
    }
  };

  const Icon = getIcon(executive.role);

  return (
    <div
      onClick={onSelect}
      className={`p-4 rounded-lg cursor-pointer transition ${
        selected ? 'bg-purple-600/20 border border-purple-500/50' : 'hover:bg-gray-700/50'
      }`}
    >
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-purple-600/20 rounded-full flex items-center justify-center">
          <Icon className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h4 className="text-white font-medium">{executive.name}</h4>
          <p className="text-gray-400 text-sm">{executive.role}</p>
          <p className="text-xs text-blue-300 mt-1">PhD Expertise: {executive.phd_expertise && executive.phd_expertise.length > 0 ? executive.phd_expertise.join(', ') : 'N/A'}</p>
        </div>
      </div>
      <p className="text-gray-300 text-xs mt-2">{executive.reasoning || 'No reasoning available.'}</p>
    </div>
  );
}

function Message({ message }) {
  const isUser = message.type === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md p-3 rounded-lg ${
        isUser 
          ? 'bg-purple-600 text-white' 
          : 'bg-gray-700 text-gray-200'
      }`}>
        <p className="text-sm">{message.text}</p>
        <p className="text-xs opacity-70 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
} 