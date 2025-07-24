#!/usr/bin/env python3
"""
SOVREN AI Launcher - Dependency Installation Script
Automatically installs all required dependencies for enterprise deployment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install all required dependencies"""
    print("🚀 Installing SOVREN AI Launcher dependencies...")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    requirements_file = script_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ ERROR: Requirements file not found at {requirements_file}")
        return False
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r {requirements_file}", "Installing dependencies"):
        return False
    
    return True

def verify_installation():
    """Verify that all critical dependencies are installed"""
    print("🔍 Verifying installation...")
    
    critical_packages = [
        'psutil',
        'PyYAML', 
        'requests',
        'cryptography'
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r scripts/requirements.txt")
        return False
    
    print("✅ All critical dependencies are installed")
    return True

def setup_environment():
    """Set up environment variables and directories"""
    print("🔧 Setting up environment...")
    
    # Create required directories
    required_dirs = [
        '/data/sovren',
        '/data/sovren/models',
        '/data/sovren/logs',
        '/data/sovren/voice',
        '/data/sovren/config',
        '/data/sovren/temp'
    ]
    
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")
        except PermissionError:
            print(f"⚠️  Warning: Cannot create {dir_path} (permission denied)")
            print(f"   You may need to run: sudo mkdir -p {dir_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create {dir_path}: {e}")
    
    # Set default environment variables if not already set
    env_vars = {
        'SOVREN_ENV': 'production',
        'SOVREN_LOG_LEVEL': 'INFO'
    }
    
    for var, default_value in env_vars.items():
        if not os.environ.get(var):
            print(f"ℹ️  Setting {var}={default_value}")
            os.environ[var] = default_value
    
    return True

def main():
    """Main installation function"""
    print("=" * 60)
    print("SOVREN AI Launcher - Dependency Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Verification failed. Please install missing packages.")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n⚠️  Environment setup had warnings. Please check above.")
    
    print("\n" + "=" * 60)
    print("✅ SOVREN AI Launcher installation completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set your security key: export SOVREN_SECURITY_KEY='your-secure-key'")
    print("2. Run the launcher: python scripts/launch_sovren.py")
    print("3. Check the documentation: cat scripts/README.md")
    print("\nFor enterprise deployment, see the README.md for detailed instructions.")

if __name__ == "__main__":
    main() 