import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { Users, CheckCircle, XCircle, Loader } from 'lucide-react';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      setError('');
      setLoading(true);
      const response = await api.get('/admin/users');
      setUsers(response.data.users);
    } catch (err) {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-purple-400 animate-spin mr-2" />
        <span className="text-white">Loading users...</span>
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
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">User Management</h1>
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 border border-purple-500/20">
          <div className="space-y-4">
            {users.map(user => (
              <UserRow key={user.id} user={user} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function UserRow({ user }) {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
      <div className="flex items-center space-x-3">
        <Users className="w-6 h-6 text-purple-400" />
        <div>
          <div className="text-white font-medium">{user.name}</div>
          <div className="text-gray-400 text-sm">{user.email}</div>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        {user.status === 'active' ? (
          <CheckCircle className="w-5 h-5 text-green-400" />
        ) : (
          <XCircle className="w-5 h-5 text-red-400" />
        )}
        <span className={`text-sm ${user.status === 'active' ? 'text-green-400' : 'text-red-400'}`}>{user.status}</span>
      </div>
    </div>
  );
} 