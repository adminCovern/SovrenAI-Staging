#!/usr/bin/env python3
"""
SOVREN AI Launcher Test Suite
Enterprise-grade testing with security validation and performance benchmarks
"""

import unittest
import tempfile
import shutil
import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Import yaml with fallback for testing
try:
    import yaml  # type: ignore
except ImportError:
    print("❌ ERROR: PyYAML is required for testing but not installed.")
    print("Please install it with: pip install PyYAML>=6.0")
    print("Or install all requirements with: pip install -r scripts/requirements.txt")
    sys.exit(1)

# Add SOVREN to Python path
SOVREN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SOVREN_ROOT))

from launch_sovren import (
    SOVRENLauncher, 
    SecurityManager, 
    HealthMonitor, 
    ServiceConfig,
    setup_logging
)

class TestSecurityManager(unittest.TestCase):
    """Test security management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.security_manager = SecurityManager()
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / 'security.yaml'
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_service_token(self):
        """Test service token generation"""
        token1 = self.security_manager.generate_service_token('test_service')
        token2 = self.security_manager.generate_service_token('test_service')
        
        # Tokens should be different for same service
        self.assertNotEqual(token1, token2)
        self.assertEqual(len(token1), 64)  # SHA256 hex length
    
    def test_validate_service_token(self):
        """Test service token validation"""
        service_name = 'test_service'
        token = self.security_manager.generate_service_token(service_name)
        
        # Valid token should pass
        self.assertTrue(self.security_manager.validate_service_token(service_name, token))
        
        # Invalid token should fail
        self.assertFalse(self.security_manager.validate_service_token(service_name, 'invalid_token'))
        
        # Non-existent service should fail
        self.assertFalse(self.security_manager.validate_service_token('non_existent', token))
    
    def test_load_allowed_ips(self):
        """Test loading allowed IPs from config"""
        # Test with valid config
        config_data = {'allowed_ips': ['192.168.1.1', '10.0.0.1']}
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        with patch.object(self.security_manager, '_load_allowed_ips') as mock_load:
            mock_load.return_value = ['192.168.1.1', '10.0.0.1']
            ips = self.security_manager._load_allowed_ips()
            self.assertEqual(ips, ['192.168.1.1', '10.0.0.1'])
        
        # Test with missing config (should return default)
        with patch('pathlib.Path.exists', return_value=False):
            ips = self.security_manager._load_allowed_ips()
            self.assertEqual(ips, ['127.0.0.1'])

class TestHealthMonitor(unittest.TestCase):
    """Test health monitoring functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.health_monitor = HealthMonitor()
        self.test_config = ServiceConfig(
            script='test_script.py',
            name='Test Service',
            port=8000,
            critical=True,
            health_check_url='http://localhost:8000/health'
        )
    
    def test_health_monitor_initialization(self):
        """Test health monitor initialization"""
        self.assertEqual(self.health_monitor.health_status, {})
        self.assertIsNone(self.health_monitor.monitoring_thread)
        self.assertFalse(self.health_monitor._stop_monitoring)
    
    def test_get_health_status(self):
        """Test getting health status"""
        # Add test health status
        self.health_monitor.health_status['test_service'] = {
            'status': 'healthy',
            'last_check': '2023-01-01T00:00:00',
            'response_time': 0.1
        }
        
        status = self.health_monitor.get_health_status()
        self.assertIn('test_service', status)
        self.assertEqual(status['test_service']['status'], 'healthy')
    
    @patch('requests.get')
    def test_http_health_check_success(self, mock_get):
        """Test successful HTTP health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.health_monitor._http_health_check('http://localhost:8000/health')
        
        self.assertIsNotNone(result)
        if result is not None:
            self.assertTrue(result['healthy'])
            self.assertEqual(result['status_code'], 200)
    
    @patch('requests.get')
    def test_http_health_check_failure(self, mock_get):
        """Test failed HTTP health check"""
        mock_get.side_effect = Exception("Connection failed")
        
        result = self.health_monitor._http_health_check('http://localhost:8000/health')
        
        self.assertIsNone(result)
    
    def test_stop_monitoring(self):
        """Test stopping health monitoring"""
        # Start monitoring
        self.health_monitor.start_monitoring({'test': self.test_config})
        
        # Stop monitoring
        self.health_monitor.stop_monitoring()
        
        self.assertTrue(self.health_monitor._stop_monitoring)

class TestSOVRENLauncher(unittest.TestCase):
    """Test SOVREN launcher functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.launcher = SOVRENLauncher()
        
        # Mock file system operations
        self.patcher1 = patch('pathlib.Path.exists', return_value=True)
        self.patcher2 = patch('pathlib.Path.mkdir')
        self.mock_exists = self.patcher1.start()
        self.mock_mkdir = self.patcher2.start()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.patcher1.stop()
        self.patcher2.stop()
    
    def test_launcher_initialization(self):
        """Test launcher initialization"""
        self.assertIsInstance(self.launcher.processes, dict)
        self.assertIsInstance(self.launcher.service_configs, dict)
        self.assertIsInstance(self.launcher.security_manager, SecurityManager)
        self.assertIsInstance(self.launcher.health_monitor, HealthMonitor)
    
    def test_load_service_configurations(self):
        """Test service configuration loading"""
        configs = self.launcher.service_configs
        
        # Check required services exist
        required_services = ['consciousness', 'bayesian', 'voice', 'api', 'mcp']
        for service in required_services:
            self.assertIn(service, configs)
            self.assertIsInstance(configs[service], ServiceConfig)
        
        # Check critical services
        critical_services = ['consciousness', 'bayesian', 'voice', 'api']
        for service in critical_services:
            self.assertTrue(configs[service].critical)
        
        # Check non-critical services
        self.assertFalse(configs['mcp'].critical)
    
    @patch('subprocess.run')
    def test_check_system_requirements(self, mock_run):
        """Test system requirements checking"""
        # Mock successful nvidia-smi
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "GPU 0: NVIDIA B200\nGPU 1: NVIDIA B200"
        mock_run.return_value = mock_result
        
        self.launcher._check_system_requirements()
        # Should not raise any exceptions
    
    @patch('subprocess.run')
    def test_check_system_requirements_no_gpu(self, mock_run):
        """Test system requirements checking without GPU"""
        # Mock failed nvidia-smi
        mock_run.side_effect = FileNotFoundError()
        
        self.launcher._check_system_requirements()
        # Should not raise any exceptions
    
    def test_validate_security_environment(self):
        """Test security environment validation"""
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            self.launcher._validate_security_environment()
            # Should not raise any exceptions
    
    def test_ensure_directory_structure(self):
        """Test directory structure creation"""
        self.launcher._ensure_directory_structure()
        
        # Check that mkdir was called for required directories
        expected_dirs = [
            '/data/sovren',
            '/data/sovren/models',
            '/data/sovren/logs',
            '/data/sovren/voice',
            '/data/sovren/config',
            '/data/sovren/temp'
        ]
        
        for dir_path in expected_dirs:
            self.mock_mkdir.assert_any_call(parents=True, exist_ok=True)
    
    @patch('socket.create_connection')
    def test_check_network_connectivity_success(self, mock_connect):
        """Test network connectivity check with success"""
        mock_connect.return_value = None
        
        self.launcher._check_network_connectivity()
        # Should not raise any exceptions
    
    @patch('socket.create_connection')
    def test_check_network_connectivity_failure(self, mock_connect):
        """Test network connectivity check with failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        self.launcher._check_network_connectivity()
        # Should not raise any exceptions
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.cpu_count')
    def test_check_resource_availability(self, mock_cpu, mock_disk, mock_memory):
        """Test resource availability checking"""
        # Mock sufficient resources
        mock_memory.return_value.available = 2 * 1024 * 1024 * 1024  # 2GB
        mock_disk.return_value.free = 20 * 1024 * 1024 * 1024  # 20GB
        mock_cpu.return_value = 8
        
        self.launcher._check_resource_availability()
        # Should not raise any exceptions
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.cpu_count')
    def test_check_resource_availability_limited(self, mock_cpu, mock_disk, mock_memory):
        """Test resource availability checking with limited resources"""
        # Mock limited resources
        mock_memory.return_value.available = 512 * 1024 * 1024  # 512MB
        mock_disk.return_value.free = 5 * 1024 * 1024 * 1024  # 5GB
        mock_cpu.return_value = 2
        
        self.launcher._check_resource_availability()
        # Should not raise any exceptions
    
    @patch('subprocess.Popen')
    def test_start_service_success(self, mock_popen):
        """Test successful service startup"""
        # Mock successful process
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Mock health check success
        with patch.object(self.launcher, '_wait_for_service_startup', return_value=True):
            result = self.launcher.start_service('consciousness')
            self.assertTrue(result)
    
    @patch('subprocess.Popen')
    def test_start_service_failure(self, mock_popen):
        """Test failed service startup"""
        # Mock failed process
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Process terminated
        mock_popen.return_value = mock_process
        
        with patch.object(self.launcher, '_wait_for_service_startup', return_value=False):
            result = self.launcher.start_service('consciousness')
            self.assertFalse(result)
    
    def test_start_service_missing_script(self):
        """Test service startup with missing script"""
        with patch('pathlib.Path.exists', return_value=False):
            result = self.launcher.start_service('consciousness')
            self.assertFalse(result)
    
    @patch.object(SOVRENLauncher, 'start_service')
    def test_start_all_services_success(self, mock_start_service):
        """Test successful startup of all services"""
        mock_start_service.return_value = True
        
        result = self.launcher.start_all_services()
        self.assertTrue(result)
        
        # Check that start_service was called for all services
        expected_calls = len(self.launcher.service_configs)
        self.assertEqual(mock_start_service.call_count, expected_calls)
    
    @patch.object(SOVRENLauncher, 'start_service')
    def test_start_all_services_critical_failure(self, mock_start_service):
        """Test startup failure with critical service"""
        def mock_start(service_key):
            return service_key != 'consciousness'  # consciousness fails
        
        mock_start_service.side_effect = mock_start
        
        with patch.object(self.launcher, 'shutdown'):
            result = self.launcher.start_all_services()
            self.assertFalse(result)
    
    def test_shutdown(self):
        """Test graceful shutdown"""
        # Mock processes
        mock_process = Mock()
        mock_process.poll.return_value = None
        self.launcher.processes['test_service'] = mock_process
        
        # Mock health monitor
        with patch.object(self.launcher.health_monitor, 'stop_monitoring'):
            self.launcher.shutdown()
            
            # Check that terminate was called
            mock_process.terminate.assert_called_once()
    
    def test_signal_handler(self):
        """Test signal handler"""
        with patch.object(self.launcher, 'shutdown'):
            with patch('sys.exit') as mock_exit:
                self.launcher.signal_handler(2, None)  # SIGINT
                
                self.launcher.shutdown.assert_called_once()
                mock_exit.assert_called_once_with(0)

class TestIntegration(unittest.TestCase):
    """Integration tests for the launcher"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.launcher = SOVRENLauncher()
    
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_launcher_lifecycle(self):
        """Test complete launcher lifecycle"""
        # Mock all external dependencies
        with patch.object(self.launcher, 'check_prerequisites', return_value=True):
            with patch.object(self.launcher, 'start_all_services', return_value=True):
                with patch.object(self.launcher, 'monitor_services'):
                    with patch.object(self.launcher, 'shutdown'):
                        result = self.launcher.run()
                        self.assertEqual(result, 0)
    
    def test_launcher_with_prerequisites_failure(self):
        """Test launcher with prerequisites failure"""
        with patch.object(self.launcher, 'check_prerequisites', return_value=False):
            result = self.launcher.run()
            self.assertEqual(result, 1)
    
    def test_launcher_with_service_startup_failure(self):
        """Test launcher with service startup failure"""
        with patch.object(self.launcher, 'check_prerequisites', return_value=True):
            with patch.object(self.launcher, 'start_all_services', return_value=False):
                with patch.object(self.launcher, 'shutdown'):
                    result = self.launcher.run()
                    self.assertEqual(result, 1)

class TestPerformance(unittest.TestCase):
    """Performance tests for the launcher"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.launcher = SOVRENLauncher()
    
    def test_service_configuration_loading_performance(self):
        """Test performance of service configuration loading"""
        start_time = time.time()
        
        # Load configurations multiple times
        for _ in range(100):
            self.launcher._load_service_configurations()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 1.0)  # Less than 1 second
    
    def test_security_token_generation_performance(self):
        """Test performance of security token generation"""
        security_manager = SecurityManager()
        
        start_time = time.time()
        
        # Generate tokens multiple times
        for i in range(1000):
            security_manager.generate_service_token(f'service_{i}')
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 1.0)  # Less than 1 second
    
    def test_health_monitor_performance(self):
        """Test performance of health monitoring"""
        health_monitor = HealthMonitor()
        test_config = ServiceConfig(
            script='test.py',
            name='Test',
            port=8000,
            critical=True,
            health_check_url='http://localhost:8000/health'
        )
        
        start_time = time.time()
        
        # Perform health checks multiple times
        for _ in range(100):
            health_monitor._check_service_health('test_service', test_config)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 5.0)  # Less than 5 seconds

def run_security_validation():
    """Run security validation tests"""
    print("🔒 Running security validation...")
    
    # Test security key strength
    from launch_sovren import SECURITY_KEY
    assert len(SECURITY_KEY) >= 32, "Security key too weak"
    
    # Test token generation security
    security_manager = SecurityManager()
    tokens = set()
    for i in range(1000):
        token = security_manager.generate_service_token(f'service_{i}')
        tokens.add(token)
    
    # All tokens should be unique
    assert len(tokens) == 1000, "Token collision detected"
    
    print("✅ Security validation passed")

def run_performance_benchmarks():
    """Run performance benchmarks"""
    print("⚡ Running performance benchmarks...")
    
    # Benchmark service configuration loading
    launcher = SOVRENLauncher()
    start_time = time.time()
    launcher._load_service_configurations()
    config_time = time.time() - start_time
    
    # Benchmark security token generation
    security_manager = SecurityManager()
    start_time = time.time()
    for i in range(1000):
        security_manager.generate_service_token(f'service_{i}')
    token_time = time.time() - start_time
    
    print(f"📊 Performance Results:")
    print(f"  Service config loading: {config_time:.4f}s")
    print(f"  Token generation (1000): {token_time:.4f}s")
    
    # Performance thresholds
    assert config_time < 0.1, f"Service config loading too slow: {config_time}s"
    assert token_time < 1.0, f"Token generation too slow: {token_time}s"
    
    print("✅ Performance benchmarks passed")

if __name__ == '__main__':
    # Run security validation
    run_security_validation()
    
    # Run performance benchmarks
    run_performance_benchmarks()
    
    # Run unit tests
    unittest.main(verbosity=2) 