#!/usr/bin/env python3
"""
Test script for SOVREN AI MCP Server
"""

import sys
import os
import importlib.util

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dynamically import mpc_server.py.py as mpc_server
spec = importlib.util.spec_from_file_location("mpc_server", os.path.join(os.path.dirname(__file__), "mpc_server.py.py"))
if spec is None or spec.loader is None:
    raise ImportError("Could not load mpc_server.py.py module")
mpc_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mpc_server)

SOVRENLatencyMCPServer = mpc_server.SOVRENLatencyMCPServer
B200OptimizedLatencyEngine = mpc_server.B200OptimizedLatencyEngine

def test_server_initialization():
    """Test server initialization"""
    print("Testing server initialization...")
    
    try:
        server = SOVRENLatencyMCPServer(host="127.0.0.1", port=9999)
        print("✓ Server initialized successfully")
        
        # Test optimization engine
        engine = B200OptimizedLatencyEngine()
        print("✓ Optimization engine initialized successfully")
        
        # Test basic functionality
        state = engine.analyze_current_state()
        print(f"✓ System state analysis: {len(state)} components analyzed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_tool_registration():
    """Test tool registration"""
    print("\nTesting tool registration...")
    
    try:
        server = SOVRENLatencyMCPServer()
        
        # Check if tools are registered
        expected_tools = [
            'analyze_system_state',
            'optimize_resource_allocation',
            'optimize_gpu_placement',
            'optimize_numa_affinity',
            'monitor_latency_realtime',
            'optimize_session_handling',
            'optimize_model_performance',
            'run_latency_benchmark',
            'configure_autoscaling'
        ]
        
        for tool_name in expected_tools:
            if tool_name in server.tools:
                print(f"✓ Tool '{tool_name}' registered")
            else:
                print(f"✗ Tool '{tool_name}' not found")
                return False
                
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_optimization_engine():
    """Test optimization engine functionality"""
    print("\nTesting optimization engine...")
    
    try:
        engine = B200OptimizedLatencyEngine()
        
        # Test resource usage
        usage = engine._get_resource_usage()
        print(f"✓ Resource usage analysis: {len(usage)} components")
        
        # Test bottleneck identification
        bottlenecks = engine._identify_bottlenecks()
        print(f"✓ Bottleneck identification: {len(bottlenecks)} bottlenecks found")
        
        # Test GPU managers
        for i in range(8):
            gpu_manager = engine.gpu_managers[i]
            memory = gpu_manager.get_used_memory()
            load = gpu_manager.get_load()
            print(f"✓ GPU {i}: {memory:.1f}GB used, {load:.1f}% load")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_server_methods():
    """Test server methods"""
    print("\nTesting server methods...")
    
    try:
        server = SOVRENLatencyMCPServer()
        
        # Test latency monitoring
        latency_data = server._handle_latency_monitoring({'window_seconds': 60})
        print(f"✓ Latency monitoring: {len(latency_data)} metrics")
        
        # Test system analysis
        analysis = server._handle_analyze_system({'deep_analysis': False})
        print(f"✓ System analysis: {len(analysis)} components")
        
        # Test session optimization
        session_opt = server._handle_session_optimization({'current_sessions': 25})
        print(f"✓ Session optimization: {len(session_opt)} optimizations")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SOVREN AI MCP Server - Test Suite")
    print("=" * 60)
    
    tests = [
        test_server_initialization,
        test_tool_registration,
        test_optimization_engine,
        test_server_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Server is ready for deployment.")
        return 0
    else:
        print("✗ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main()) 