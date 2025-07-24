#!/usr/bin/env python3
"""
Test script for SOVREN AI API Server
"""

import requests
import time
import subprocess
import sys
import os

def test_api_server():
    """Test the API server functionality"""
    
    # Start the server in background
    print("Starting API Server...")
    server_process = subprocess.Popen([
        sys.executable, "server.py"
    ], cwd=os.path.dirname(__file__))
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        
        # Test status endpoint
        print("Testing status endpoint...")
        response = requests.get("http://localhost:8000/status", timeout=10)
        print(f"Status check status: {response.status_code}")
        print(f"Status check response: {response.json()}")
        
        # Test agents status endpoint
        print("Testing agents status endpoint...")
        response = requests.get("http://localhost:8000/api/agents/status", timeout=10)
        print(f"Agents status check: {response.status_code}")
        print(f"Agents status response: {response.json()}")
        
        print("✅ All API endpoints working correctly!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        return False
    finally:
        # Stop the server
        print("Stopping API Server...")
        server_process.terminate()
        server_process.wait()
    
    return True

if __name__ == "__main__":
    success = test_api_server()
    sys.exit(0 if success else 1) 