#!/usr/bin/env python3
"""
Test suite for SOVREN Enterprise MCP Server
Comprehensive testing for B200-optimized latency engine and MCP server
"""

import asyncio
import json
import socket
import threading
import time
import unittest
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock

import pytest
import jwt
import time

class TestB200OptimizedLatencyEngine:
    """Test suite for B200-optimized latency engine"""
    
    def setUp(self):
        """Set up test environment"""
        from scripts.enterprise_mcp_server import B200OptimizedLatencyEngine
        self.engine = B200OptimizedLatencyEngine()
    
    def test_initialization(self):
        """Test engine initialization"""
        assert self.engine is not None
        assert hasattr(self.engine, 'hardware')
        assert hasattr(self.engine, 'workload')
        assert hasattr(self.engine, 'gpu_managers')
    
    def test_analyze_current_state(self):
        """Test current state analysis"""
        state = self.engine.analyze_current_state()
        assert isinstance(state, dict)
        assert 'timestamp' in state
        assert 'resource_usage' in state
        assert 'latency_profile' in state
        assert 'bottlenecks' in state
        assert 'optimization_opportunities' in state
    
    def test_gpu_memory_manager(self):
        """Test GPU memory manager functionality"""
        from scripts.enterprise_mcp_server import GPUMemoryManager
        
        manager = GPUMemoryManager(gpu_id=0, total_memory_gb=80.0)
        
        # Test allocation
        assert manager.allocate(10.0, "test_component") == True
        assert manager.get_used_memory() == 10.0
        assert manager.get_load() == 12.5  # 10/80 * 100
        
        # Test over-allocation
        assert manager.allocate(100.0, "large_component") == False
        assert manager.get_used_memory() == 10.0  # Should not change
    
    def test_optimization_strategies(self):
        """Test optimization strategy application"""
        # Test GPU load balancing
        result = self.engine._optimize_gpu_load_balancing("whisper")
        assert isinstance(result, dict)
        assert 'strategy' in result
        assert 'action' in result
        assert 'expected_improvement' in result
        
        # Test NUMA affinity
        result = self.engine._optimize_numa_affinity("styletts2")
        assert isinstance(result, dict)
        assert 'strategy' in result
        assert 'action' in result
        assert 'expected_improvement' in result
    
    def test_batch_coalescing(self):
        """Test batch coalescing optimization"""
        result = self.engine._optimize_batch_coalescing("mixtral")
        assert isinstance(result, dict)
        assert result['strategy'] == 'batch_coalescing'
        assert 'whisper' in result['action']
    
    def test_memory_prefetch(self):
        """Test memory prefetch optimization"""
        result = self.engine._optimize_memory_prefetch("whisper")
        assert isinstance(result, dict)
        assert result['strategy'] == 'memory_prefetch'
    
    def test_kernel_fusion(self):
        """Test kernel fusion optimization"""
        result = self.engine._optimize_kernel_fusion("styletts2")
        assert isinstance(result, dict)
        assert result['strategy'] == 'kernel_fusion'
    
    def test_latency_profile(self):
        """Test latency profile retrieval"""
        profile = self.engine._get_latency_profile()
        assert isinstance(profile, dict)
        assert 'whisper' in profile
        assert 'styletts2' in profile
        assert 'mixtral' in profile
        assert all(isinstance(v, (int, float)) for v in profile.values())
    
    def test_bottleneck_identification(self):
        """Test bottleneck identification"""
        bottlenecks = self.engine._identify_bottlenecks()
        assert isinstance(bottlenecks, list)
    
    def test_applicable_strategies(self):
        """Test strategy applicability"""
        strategies = self.engine._get_applicable_strategies("whisper")
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all(isinstance(s, str) for s in strategies)
    
    def test_memory_bandwidth_measurement(self):
        """Test memory bandwidth measurement"""
        bandwidth = self.engine._measure_memory_bandwidth()
        assert isinstance(bandwidth, (int, float))
        assert bandwidth > 0
    
    def test_gpu_utilization(self):
        """Test GPU utilization tracking"""
        for gpu_id in range(8):  # 8 B200 GPUs
            utilization = self.engine._get_gpu_utilization(gpu_id)
            assert isinstance(utilization, (int, float))
            assert 0 <= utilization <= 100


class TestSOVRENLatencyMCPServer:
    """Test suite for SOVREN MCP server"""
    
    def setUp(self):
        """Set up test environment"""
        from scripts.enterprise_mcp_server import SOVRENLatencyMCPServer
        self.server = SOVRENLatencyMCPServer(host="127.0.0.1", port=9999)
    
    def test_server_initialization(self):
        """Test server initialization"""
        assert self.server is not None
        assert self.server.host == "127.0.0.1"
        assert self.server.port == 9999
        assert hasattr(self.server, 'performance_tracker')
        assert hasattr(self.server, 'latency_engine')
    
    def test_model_optimization_handling(self):
        """Test model optimization request handling"""
        request = {
            'model': 'whisper',
            'optimization_level': 'moderate'
        }
        
        result = self.server._handle_model_optimization(request)
        assert isinstance(result, dict)
        assert 'model' in result
        assert 'optimization_level' in result
        assert 'configuration' in result
        assert 'expected_latency_reduction' in result
        assert 'quality_impact' in result
    
    def test_unknown_model_handling(self):
        """Test handling of unknown model requests"""
        request = {
            'model': 'unknown_model',
            'optimization_level': 'moderate'
        }
        
        result = self.server._handle_model_optimization(request)
        assert isinstance(result, dict)
        assert 'error' in result
        assert 'Unknown model' in result['error']
    
    def test_optimization_levels(self):
        """Test all optimization levels for each model"""
        models = ['whisper', 'styletts2', 'mixtral']
        levels = ['conservative', 'moderate', 'aggressive']
        
        for model in models:
            for level in levels:
                request = {
                    'model': model,
                    'optimization_level': level
                }
                
                result = self.server._handle_model_optimization(request)
                assert isinstance(result, dict)
                assert result['model'] == model
                assert result['optimization_level'] == level
                assert 'configuration' in result
    
    def test_session_calculation(self):
        """Test session calculation methods"""
        max_sessions = self.server._calculate_max_sessions()
        optimal_sessions = self.server._calculate_optimal_sessions()
        
        assert isinstance(max_sessions, int)
        assert isinstance(optimal_sessions, int)
        assert max_sessions > 0
        assert optimal_sessions > 0
        assert optimal_sessions <= max_sessions
    
    def test_latency_estimation(self):
        """Test latency estimation with allocation plans"""
        allocation_plan = {
            'whisper': {'resource_ratio': 1.0},
            'styletts2': {'resource_ratio': 0.8},
            'mixtral': {'resource_ratio': 1.2}
        }
        
        estimated_latency = self.server._estimate_latency(allocation_plan)
        assert isinstance(estimated_latency, (int, float))
        assert estimated_latency > 0
    
    def test_apply_model_optimization(self):
        """Test model optimization application"""
        config = {
            'batch_size': 2,
            'beam_size': 3,
            'model_variant': 'large-v3'
        }
        
        result = self.server._apply_model_optimization("whisper", config)
        assert isinstance(result, dict)
        assert result['model'] == "whisper"
        assert result['applied_config'] == config
        assert result['status'] == 'applied'
        assert 'timestamp' in result


class TestPerformanceTracker:
    """Test suite for performance tracking"""
    
    def setUp(self):
        """Set up test environment"""
        from scripts.enterprise_mcp_server import PerformanceTracker
        self.tracker = PerformanceTracker()
    
    def test_metric_recording(self):
        """Test metric recording functionality"""
        self.tracker.record_metric("whisper", "latency", 150.0)
        self.tracker.record_metric("whisper", "throughput", 10.5)
        
        # Verify metrics were recorded
        assert "whisper" in self.tracker.metrics
        assert "latency" in self.tracker.metrics["whisper"]
        assert "throughput" in self.tracker.metrics["whisper"]
    
    def test_metrics_retrieval(self):
        """Test metrics retrieval for time window"""
        # Record some metrics
        self.tracker.record_metric("styletts2", "latency", 100.0)
        self.tracker.record_metric("styletts2", "latency", 95.0)
        self.tracker.record_metric("styletts2", "latency", 105.0)
        
        # Get metrics for recent window
        metrics = self.tracker.get_metrics("styletts2", 10)
        
        assert isinstance(metrics, dict)
        assert 'latency_current' in metrics
        assert 'latency_avg' in metrics
        assert 'latency_p95' in metrics
        assert 'latency_p99' in metrics
        
        # Verify values are reasonable
        assert metrics['latency_current'] == 105.0
        assert 95.0 <= metrics['latency_avg'] <= 105.0
    
    def test_empty_metrics(self):
        """Test handling of empty metrics"""
        metrics = self.tracker.get_metrics("nonexistent", 10)
        assert isinstance(metrics, dict)
        assert len(metrics) == 0
    
    def test_concurrent_access(self):
        """Test concurrent access to performance tracker"""
        import threading
        
        def record_metrics():
            for i in range(10):
                self.tracker.record_metric("test", "value", float(i))
                time.sleep(0.001)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=record_metrics)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no data corruption
        metrics = self.tracker.get_metrics("test", 10)
        assert isinstance(metrics, dict)


class TestHardwareConfiguration:
    """Test suite for hardware configuration"""
    
    def test_hardware_config_structure(self):
        """Test hardware configuration structure"""
        from scripts.enterprise_mcp_server import HARDWARE_CONFIG
        
        assert isinstance(HARDWARE_CONFIG, dict)
        assert 'cpu' in HARDWARE_CONFIG
        assert 'memory' in HARDWARE_CONFIG
        assert 'gpu' in HARDWARE_CONFIG
        assert 'storage' in HARDWARE_CONFIG
        assert 'network' in HARDWARE_CONFIG
    
    def test_cpu_configuration(self):
        """Test CPU configuration values"""
        from scripts.enterprise_mcp_server import HARDWARE_CONFIG
        
        cpu_config = HARDWARE_CONFIG['cpu']
        assert cpu_config['sockets'] == 2
        assert cpu_config['cores_per_socket'] == 144
        assert cpu_config['total_cores'] == 288
        assert cpu_config['total_threads'] == 576
        assert cpu_config['numa_nodes'] == 6
        assert cpu_config['l3_cache_mb'] == 864
        assert cpu_config['avx512'] == True
        assert cpu_config['amx'] == True
    
    def test_memory_configuration(self):
        """Test memory configuration values"""
        from scripts.enterprise_mcp_server import HARDWARE_CONFIG
        
        memory_config = HARDWARE_CONFIG['memory']
        assert memory_config['total_gb'] == 2355
        assert memory_config['dimms'] == 24
        assert memory_config['speed_mts'] == 6400
        assert memory_config['channels'] == 16
        assert len(memory_config['numa_distribution']) == 6
    
    def test_gpu_configuration(self):
        """Test GPU configuration values"""
        from scripts.enterprise_mcp_server import HARDWARE_CONFIG
        
        gpu_config = HARDWARE_CONFIG['gpu']
        assert gpu_config['count'] == 8
        assert gpu_config['model'] == 'NVIDIA B200'
        assert gpu_config['memory_per_gpu_gb'] == 80
        assert gpu_config['total_memory_gb'] == 640
        assert gpu_config['pcie_gen'] == 5
        assert gpu_config['bandwidth_gbps'] == 128
        assert gpu_config['fp8_tflops'] == 20000
        assert gpu_config['fp16_tflops'] == 10000
        assert gpu_config['no_nvlink'] == True
    
    def test_storage_configuration(self):
        """Test storage configuration values"""
        from scripts.enterprise_mcp_server import HARDWARE_CONFIG
        
        storage_config = HARDWARE_CONFIG['storage']
        assert storage_config['drives'] == 4
        assert storage_config['drive_capacity_tb'] == 7.68
        assert storage_config['total_capacity_tb'] == 30.72
        assert storage_config['type'] == 'NVMe'
        assert storage_config['read_gbps'] == 6.8
        assert storage_config['write_gbps'] == 4.0
        assert storage_config['iops'] == 1500000
    
    def test_network_configuration(self):
        """Test network configuration values"""
        from scripts.enterprise_mcp_server import HARDWARE_CONFIG
        
        network_config = HARDWARE_CONFIG['network']
        assert network_config['primary_nic'] == 'Mellanox ConnectX-6 Dx'
        assert network_config['speed_gbps'] == 100
        assert network_config['secondary_nic'] == 'Intel X710'
        assert network_config['secondary_speed_gbps'] == 10
        assert network_config['rdma_capable'] == True


class TestSOVRENWorkload:
    """Test suite for SOVREN workload configuration"""
    
    def test_workload_structure(self):
        """Test workload configuration structure"""
        from scripts.enterprise_mcp_server import SOVREN_WORKLOAD
        
        assert isinstance(SOVREN_WORKLOAD, dict)
        assert 'models' in SOVREN_WORKLOAD
        assert 'agents' in SOVREN_WORKLOAD
        assert 'services' in SOVREN_WORKLOAD
        assert 'targets' in SOVREN_WORKLOAD
    
    def test_model_configurations(self):
        """Test AI model configurations"""
        from scripts.enterprise_mcp_server import SOVREN_WORKLOAD
        
        models = SOVREN_WORKLOAD['models']
        assert 'whisper_large_v3' in models
        assert 'styletts2' in models
        assert 'mixtral_8x7b_4bit' in models
        
        # Test Whisper configuration
        whisper_config = models['whisper_large_v3']
        assert whisper_config['gpu_memory_gb'] == 15
        assert whisper_config['cpu_cores'] == 8
        assert whisper_config['ram_gb'] == 16
        assert whisper_config['target_latency_ms'] == 150
        assert whisper_config['batch_size'] == 1
        assert len(whisper_config['gpu_assignment']) == 2
        
        # Test StyleTTS2 configuration
        styletts2_config = models['styletts2']
        assert styletts2_config['gpu_memory_gb'] == 8
        assert styletts2_config['cpu_cores'] == 4
        assert styletts2_config['ram_gb'] == 8
        assert styletts2_config['target_latency_ms'] == 100
        assert styletts2_config['batch_size'] == 1
        assert len(styletts2_config['gpu_assignment']) == 2
        
        # Test Mixtral configuration
        mixtral_config = models['mixtral_8x7b_4bit']
        assert mixtral_config['gpu_memory_gb'] == 24
        assert mixtral_config['cpu_cores'] == 16
        assert mixtral_config['ram_gb'] == 32
        assert mixtral_config['target_latency_ms'] == 90
        assert mixtral_config['tokens_per_second'] == 50
        assert len(mixtral_config['gpu_assignment']) == 4
    
    def test_agent_configurations(self):
        """Test agent battalion configurations"""
        from scripts.enterprise_mcp_server import SOVREN_WORKLOAD
        
        agents = SOVREN_WORKLOAD['agents']
        expected_agents = ['STRIKE', 'INTEL', 'OPS', 'SENTINEL', 'COMMAND']
        
        for agent_name in expected_agents:
            assert agent_name in agents
            agent_config = agents[agent_name]
            assert 'cpu_cores' in agent_config
            assert 'ram_gb' in agent_config
            assert 'gpu_memory_gb' in agent_config
            assert 'latency_requirement_ms' in agent_config
    
    def test_service_configurations(self):
        """Test system service configurations"""
        from scripts.enterprise_mcp_server import SOVREN_WORKLOAD
        
        services = SOVREN_WORKLOAD['services']
        expected_services = ['bayesian_engine', 'freeswitch', 'time_machine', 'kill_bill']
        
        for service_name in expected_services:
            assert service_name in services
            service_config = services[service_name]
            assert 'cpu_cores' in service_config
            assert 'ram_gb' in service_config
            assert 'latency_requirement_ms' in service_config
    
    def test_target_metrics(self):
        """Test target performance metrics"""
        from scripts.enterprise_mcp_server import SOVREN_WORKLOAD
        
        targets = SOVREN_WORKLOAD['targets']
        assert targets['concurrent_sessions'] == 50
        assert targets['total_round_trip_ms'] == 400
        assert targets['peak_sessions'] == 100
        assert targets['uptime_percent'] == 99.99


def run_tests():
    """Run all test suites"""
    print("=" * 80)
    print("SOVREN Enterprise MCP Server Test Suite")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestB200OptimizedLatencyEngine,
        TestSOVRENLatencyMCPServer,
        TestPerformanceTracker,
        TestHardwareConfiguration,
        TestSOVRENWorkload
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 