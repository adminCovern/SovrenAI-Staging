import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import AdminRoute from './components/AdminRoute';

// User Components
import Login from './components/user/Login';
import Dashboard from './components/user/Dashboard';
import VoiceInterface from './components/user/VoiceInterface';
import SovrenScore from './components/user/SovrenScore';
import ShadowBoard from './components/user/ShadowBoard';
import AgentBattalion from './components/user/AgentBattalion';
import TimeMachine from './components/user/TimeMachine';

// Admin Components
import AdminLogin from './components/admin/AdminLogin';
import AdminDashboard from './components/admin/AdminDashboard';
import ApplicationReview from './components/admin/ApplicationReview';
import BetaUserManagement from './components/admin/BetaUserManagement';
import UserManagement from './components/admin/UserManagement';
import TelephonyDashboard from './components/admin/TelephonyDashboard';
import SystemMonitoring from './components/admin/SystemMonitoring';

// Styles
import './styles/main.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Login />} />
            <Route path="/admin" element={<AdminLogin />} />
            
            {/* User Routes (Protected) */}
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/voice" element={<PrivateRoute><VoiceInterface /></PrivateRoute>} />
            <Route path="/score" element={<PrivateRoute><SovrenScore /></PrivateRoute>} />
            <Route path="/shadow-board" element={<PrivateRoute><ShadowBoard /></PrivateRoute>} />
            <Route path="/agents" element={<PrivateRoute><AgentBattalion /></PrivateRoute>} />
            <Route path="/time-machine" element={<PrivateRoute><TimeMachine /></PrivateRoute>} />
            
            {/* Admin Routes (Protected + Admin) */}
            <Route path="/admin/dashboard" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
            <Route path="/admin/applications" element={<AdminRoute><ApplicationReview /></AdminRoute>} />
            <Route path="/admin/beta" element={<AdminRoute><BetaUserManagement /></AdminRoute>} />
            <Route path="/admin/users" element={<AdminRoute><UserManagement /></AdminRoute>} />
            <Route path="/admin/telephony" element={<AdminRoute><TelephonyDashboard /></AdminRoute>} />
            <Route path="/admin/monitoring" element={<AdminRoute><SystemMonitoring /></AdminRoute>} />
            
            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;