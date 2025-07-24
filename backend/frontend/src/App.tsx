import React, { useEffect } fromreact;
import { BrowserRouter as Router, Routes, Route, Navigate } fromreact-router-dom';
import LivingInterface from '@/components/LivingInterface';
import consciousnessWebSocket from '@/services/consciousnessWebSocket';
import '@/styles/LivingInterface.css';

const App: React.FC = () => {
  useEffect(() => {
    // Initialize consciousness connection on app start
    consciousnessWebSocket.requestConsciousnessUpdate();
    consciousnessWebSocket.requestGPUStatus();
    consciousnessWebSocket.requestShadowBoardUpdate();
    consciousnessWebSocket.requestTimeMachineUpdate();

    // Cleanup on unmount
    return () => {
      consciousnessWebSocket.disconnect();
    };
  },);

  return (
    <Router>
      <div className="app>
        <Routes>
          {/* Main Living Interface Route */}
          <Route path="/ element={<LivingInterface />} />
          
          {/* Consciousness Routes */}
          <Route path="/consciousness element={<LivingInterface />} />
          <Route path="/neural-core element={<LivingInterface />} />
          <Route path="/shadow-board element={<LivingInterface />} />
          <Route path="/time-machine element={<LivingInterface />} />
          <Route path="/voice element={<LivingInterface />} />
          
          {/* Catch all - redirect to main interface */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App; 