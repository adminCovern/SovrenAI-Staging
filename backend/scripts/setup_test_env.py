#!/usr/bin/env python3
"""
SOVREN AI Launcher - Test Environment Setup
Ensures all testing dependencies are properly installed
"""

import subprocess
import sys
import os
from pathlib import Path

def check_test_dependencies():
    """Check if all testing dependencies are available"""
    print("🔍 Checking test dependencies...")
    
    test_dependencies = [
        ('unittest', None),  # Built-in
        ('tempfile', None),   # Built-in
        ('shutil', None),     # Built-in
        ('os', None),         # Built-in
        ('sys', None),        # Built-in
        ('time', None),       # Built-in
        ('threading', None),  # Built-in
        ('subprocess', None), # Built-in
        ('pathlib', None),    # Built-in
        ('json', None),       # Built-in
        ('yaml', 'PyYAML'),   # External
        ('unittest.mock', None),  # Built-in
        ('psutil', 'psutil'),     # External
        ('requests', 'requests'), # External
    ]
    
    missing_deps = []
    
    for module, package in test_dependencies:
        try:
            if module == 'unittest.mock':
                import unittest.mock
            else:
                __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            print(f"❌ {module} not available")
            if package:
                missing_deps.append(package)
    
    return missing_deps

def install_missing_dependencies(missing_deps):
    """Install missing testing dependencies"""
    if not missing_deps:
        print("✅ All test dependencies are available")
        return True
    
    print(f"🔧 Installing missing dependencies: {', '.join(missing_deps)}")
    
    for package in missing_deps:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def verify_test_imports():
    """Verify that all test imports work correctly"""
    print("🔍 Verifying test imports...")
    
    try:
        # Test importing the main launcher
        from launch_sovren import SOVRENLauncher, SecurityManager, HealthMonitor, ServiceConfig
        print("✅ Main launcher imports successful")
        
        # Test importing test utilities
        import unittest
        import tempfile
        import shutil
        import yaml
        import json
        from unittest.mock import Mock, patch
        print("✅ Test utility imports successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import verification failed: {e}")
        return False

def setup_test_directories():
    """Set up test directories"""
    print("🔧 Setting up test directories...")
    
    test_dirs = [
        "scripts/typings",
        "scripts/test_output",
        "scripts/test_logs"
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path}")
    
    # Create __init__.py for typings if it doesn't exist
    init_file = Path("scripts/typings/__init__.py")
    if not init_file.exists():
        init_file.touch()
        print("✅ Created scripts/typings/__init__.py")

def run_test_validation():
    """Run basic test validation"""
    print("🔍 Running test validation...")
    
    try:
        # Test basic functionality
        from launch_sovren import SOVRENLauncher
        launcher = SOVRENLauncher()
        
        # Test security manager
        from launch_sovren import SecurityManager
        security = SecurityManager()
        token = security.generate_service_token('test')
        
        # Test health monitor
        from launch_sovren import HealthMonitor
        monitor = HealthMonitor()
        
        print("✅ Basic functionality tests passed")
        return True
    except Exception as e:
        print(f"❌ Test validation failed: {e}")
        return False

def main():
    """Main test environment setup function"""
    print("🔧 SOVREN AI Launcher - Test Environment Setup")
    print("=" * 60)
    
    # Check dependencies
    missing_deps = check_test_dependencies()
    
    # Install missing dependencies
    if missing_deps:
        if not install_missing_dependencies(missing_deps):
            print("❌ Failed to install missing dependencies")
            sys.exit(1)
    
    # Setup directories
    setup_test_directories()
    
    # Verify imports
    if not verify_test_imports():
        print("❌ Import verification failed")
        sys.exit(1)
    
    # Run test validation
    if not run_test_validation():
        print("❌ Test validation failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Test environment setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run tests with:")
    print("  python scripts/test_launch_sovren.py")
    print("  python -m pytest scripts/test_launch_sovren.py")
    print("  python scripts/check_types.py")

if __name__ == "__main__":
    main() 