#!/usr/bin/env python3
"""
Unit tests for SOVREN AI Consciousness Engine
Tests all critical functionality for production deployment
"""

import unittest
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import torch
import numpy as np

# Import the consciousness engine
from consciousness_engine import (
    BayesianConsciousnessEngine,
    ConsciousnessPacket,
    Universe,
    ConsciousnessState,
    ValidationError,
    SecurityError
)

class TestConsciousnessPacket(unittest.TestCase):
    """Test ConsciousnessPacket validation and security"""
    
    def test_valid_packet_creation(self):
        """Test valid packet creation"""
        packet = ConsciousnessPacket(
            packet_id="test_001",
            timestamp=time.time(),
            source="api",
            data={"test": "data"},
            priority=5,
            universes_required=3
        )
        self.assertEqual(packet.packet_id, "test_001")
        self.assertEqual(packet.source, "api")
    
    def test_invalid_packet_id(self):
        """Test invalid packet_id validation"""
        with self.assertRaises(ValidationError):
            ConsciousnessPacket(
                packet_id="",
                timestamp=time.time(),
                source="api",
                data={"test": "data"}
            )
    
    def test_invalid_source(self):
        """Test invalid source validation"""
        with self.assertRaises(ValidationError):
            ConsciousnessPacket(
                packet_id="test_001",
                timestamp=time.time(),
                source="invalid_source",
                data={"test": "data"}
            )
    
    def test_invalid_priority(self):
        """Test invalid priority validation"""
        with self.assertRaises(ValidationError):
            ConsciousnessPacket(
                packet_id="test_001",
                timestamp=time.time(),
                source="api",
                data={"test": "data"},
                priority=15
            )
    
    def test_invalid_universes_required(self):
        """Test invalid universes_required validation"""
        with self.assertRaises(ValidationError):
            ConsciousnessPacket(
                packet_id="test_001",
                timestamp=time.time(),
                source="api",
                data={"test": "data"},
                universes_required=25
            )
    
    def test_invalid_gpu_affinity(self):
        """Test invalid gpu_affinity validation"""
        with self.assertRaises(ValidationError):
            ConsciousnessPacket(
                packet_id="test_001",
                timestamp=time.time(),
                source="api",
                data={"test": "data"},
                gpu_affinity=[10]  # Invalid GPU ID
            )

class TestBayesianConsciousnessEngine(unittest.TestCase):
    """Test BayesianConsciousnessEngine functionality"""
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    @patch('torch.distributed.init_process_group')
    def setUp(self, mock_dist_init, mock_get_props, mock_cuda_available):
        """Set up test environment with mocked CUDA"""
        mock_cuda_available.return_value = True
        mock_get_props.return_value = Mock(
            name="NVIDIA B200",
            total_memory=183 * 1024**3  # 183GB
        )
        mock_dist_init.return_value = None
        
        # Create temporary config
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False)
        config_data = {
            'secret_key': 'test_secret_key_12345',
            'rate_limit': 100,
            'max_universes': 5,
            'timeout_seconds': 10
        }
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
        
        # Initialize engine with mocked components
        with patch('consciousness_engine.BayesianNetwork') as mock_network:
            mock_network.return_value = Mock()
            self.engine = BayesianConsciousnessEngine(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'engine'):
            self.engine.shutdown()
        if hasattr(self, 'temp_config'):
            os.unlink(self.temp_config.name)
    
    def test_config_loading(self):
        """Test configuration loading"""
        self.assertIsNotNone(self.engine.config)
        self.assertEqual(self.engine.config['rate_limit'], 100)
        self.assertEqual(self.engine.config['max_universes'], 5)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Should allow requests within limit
        for _ in range(50):
            self.assertTrue(self.engine._check_rate_limit())
        
        # Should block when limit exceeded
        for _ in range(100):
            self.engine._check_rate_limit()
        
        self.assertFalse(self.engine._check_rate_limit())
    
    def test_packet_security_validation(self):
        """Test packet security validation"""
        packet = ConsciousnessPacket(
            packet_id="test_001",
            timestamp=time.time(),
            source="api",
            data={"test": "data"},
            auth_token=None
        )
        
        # Should pass without auth token
        self.assertTrue(self.engine._validate_packet_security(packet))
    
    def test_packet_security_validation_with_auth(self):
        """Test packet security validation with authentication"""
        timestamp = time.time()
        packet_id = "test_001"
        
        # Generate valid auth token
        expected_token = self.engine._generate_auth_token(packet_id, timestamp)
        
        packet = ConsciousnessPacket(
            packet_id=packet_id,
            timestamp=timestamp,
            source="api",
            data={"test": "data"},
            auth_token=expected_token
        )
        
        # Should pass with valid auth token
        self.assertTrue(self.engine._validate_packet_security(packet))
    
    def test_packet_security_validation_invalid_auth(self):
        """Test packet security validation with invalid auth"""
        packet = ConsciousnessPacket(
            packet_id="test_001",
            timestamp=time.time(),
            source="api",
            data={"test": "data"},
            auth_token="invalid_token"
        )
        
        # Should fail with invalid auth token
        with self.assertRaises(SecurityError):
            self.engine._validate_packet_security(packet)
    
    def test_large_data_rejection(self):
        """Test rejection of oversized data"""
        large_data = {"data": "x" * (1024 * 1024 + 1)}  # > 1MB
        
        packet = ConsciousnessPacket(
            packet_id="test_001",
            timestamp=time.time(),
            source="api",
            data=large_data
        )
        
        # Should reject oversized data
        with self.assertRaises(ValidationError):
            self.engine._validate_packet_security(packet)
    
    @patch('consciousness_engine.BayesianNetwork')
    def test_universe_spawning(self, mock_network):
        """Test parallel universe spawning"""
        mock_network.return_value = Mock()
        
        packet = ConsciousnessPacket(
            packet_id="test_001",
            timestamp=time.time(),
            source="api",
            data={"test": "data"},
            universes_required=3
        )
        
        universes = self.engine._spawn_universes(packet)
        
        self.assertEqual(len(universes), 3)
        for universe in universes:
            self.assertIsInstance(universe, Universe)
            self.assertIn(universe.gpu_assignment, range(8))
    
    def test_system_status(self):
        """Test system status reporting"""
        status = self.engine.get_system_status()
        
        self.assertIn('state', status)
        self.assertIn('uptime_seconds', status)
        self.assertIn('metrics', status)
        self.assertIn('gpu_memory_usage', status)
        self.assertIsInstance(status['total_memory_tb'], float)
    
    def test_consciousness_proof_generation(self):
        """Test consciousness proof generation"""
        decision_data = {
            'decision': {'action': 'proceed'},
            'confidence': 0.85,
            'universes_explored': 3
        }
        
        proof = self.engine.generate_consciousness_proof(decision_data)
        
        self.assertIn('proof', proof)
        self.assertIn('proof_data', proof)
        self.assertIn('verification_method', proof)
        self.assertIn('timestamp', proof)
        self.assertEqual(proof['verification_method'], 'sha512')

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    @patch('torch.cuda.is_available')
    def test_gpu_unavailable(self, mock_cuda_available):
        """Test handling when GPUs are unavailable"""
        mock_cuda_available.return_value = False
        
        with self.assertRaises(RuntimeError):
            BayesianConsciousnessEngine()
    
    def test_invalid_config_file(self):
        """Test handling of invalid config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid json content")
            f.flush()
            
            # Should not crash, should use defaults
            engine = BayesianConsciousnessEngine(f.name)
            self.assertIsNotNone(engine.config)
            
            os.unlink(f.name)

class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    @patch('torch.distributed.init_process_group')
    def test_processing_latency(self, mock_dist_init, mock_get_props, mock_cuda_available):
        """Test processing latency"""
        mock_cuda_available.return_value = True
        mock_get_props.return_value = Mock(
            name="NVIDIA B200",
            total_memory=183 * 1024**3
        )
        mock_dist_init.return_value = None
        
        with patch('consciousness_engine.BayesianNetwork') as mock_network:
            mock_network.return_value = Mock()
            engine = BayesianConsciousnessEngine()
            
            packet = ConsciousnessPacket(
                packet_id="perf_test",
                timestamp=time.time(),
                source="api",
                data={"test": "performance"},
                universes_required=2
            )
            
            start_time = time.time()
            result = engine.process_decision(packet)
            processing_time = time.time() - start_time
            
            # Should complete within reasonable time
            self.assertLess(processing_time, 5.0)  # 5 seconds max
            self.assertIn('processing_time_ms', result)
            
            engine.shutdown()

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2) 