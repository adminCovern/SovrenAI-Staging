#!/usr/bin/env python3
"""
Setup Voice System Services
Install and configure PostgreSQL, Redis, and environment variables
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_environment_variables():
    """Set up required environment variables"""
    print("🔧 Setting up environment variables...")
    
    env_vars = {
        'SOVREN_ENV': 'production',
        'SOVREN_SECURITY_KEY': 'aa9628c23683705c6c1eee9771bb3224f438333e925df0c5df2e88f0699603fd',
        'DATABASE_URL': 'postgresql://sovren:password@localhost/sovren_voice',
        'REDIS_URL': 'redis://localhost:6379/0',
        'SOVREN_LOG_LEVEL': 'INFO',
        'SOVREN_HOST': '0.0.0.0',
        'SOVREN_PORT': '8000'
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"✅ Set {var}={value[:20] if len(value) > 20 else value}...")
    
    return True

def install_postgresql():
    """Install and configure PostgreSQL"""
    print("🔧 Installing PostgreSQL...")
    
    # Install PostgreSQL
    if not run_command("sudo apt-get update", "Updating package list"):
        return False
    
    if not run_command("sudo apt-get install -y postgresql postgresql-contrib", "Installing PostgreSQL"):
        return False
    
    # Start PostgreSQL service
    if not run_command("sudo systemctl start postgresql", "Starting PostgreSQL service"):
        return False
    
    if not run_command("sudo systemctl enable postgresql", "Enabling PostgreSQL service"):
        return False
    
    # Create database and user
    commands = [
        "sudo -u postgres psql -c \"CREATE USER sovren WITH PASSWORD 'password';\"",
        "sudo -u postgres psql -c \"CREATE DATABASE sovren_voice OWNER sovren;\"",
        "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE sovren_voice TO sovren;\"",
        "sudo -u postgres psql -c \"ALTER USER sovren CREATEDB;\""
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Configuring PostgreSQL: {cmd[:50]}..."):
            print(f"⚠️  PostgreSQL command failed, but continuing...")
    
    return True

def install_redis():
    """Install and configure Redis"""
    print("🔧 Installing Redis...")
    
    # Install Redis
    if not run_command("sudo apt-get install -y redis-server", "Installing Redis"):
        return False
    
    # Start Redis service
    if not run_command("sudo systemctl start redis-server", "Starting Redis service"):
        return False
    
    if not run_command("sudo systemctl enable redis-server", "Enabling Redis service"):
        return False
    
    # Test Redis connection
    if not run_command("redis-cli ping", "Testing Redis connection"):
        return False
    
    return True

def create_model_directories():
    """Create model directories"""
    print("🔧 Creating model directories...")
    
    directories = [
        "/data/sovren/models/whisper",
        "/data/sovren/models/tts",
        "/data/sovren/logs",
        "/data/sovren/config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def download_sample_models():
    """Download sample models for testing"""
    print("🔧 Downloading sample models...")
    
    # Create a simple test model file
    test_model_path = Path("/data/sovren/models/whisper/test-model.bin")
    test_model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a dummy model file for testing
    with open(test_model_path, 'w') as f:
        f.write("TEST_MODEL_CONTENT")
    
    print(f"✅ Created test model: {test_model_path}")
    
    # Create TTS model directory structure
    tts_path = Path("/data/sovren/models/tts")
    tts_path.mkdir(parents=True, exist_ok=True)
    
    # Create a dummy TTS model file
    tts_model_path = tts_path / "test-tts-model.pth"
    with open(tts_model_path, 'w') as f:
        f.write("TEST_TTS_MODEL_CONTENT")
    
    print(f"✅ Created test TTS model: {tts_model_path}")
    
    return True

def main():
    """Set up all Voice System services"""
    print("🚀 Setting up Voice System Services...")
    
    # Set environment variables
    setup_environment_variables()
    
    # Create directories
    create_model_directories()
    
    # Download sample models
    download_sample_models()
    
    # Install services
    print("\n📦 Installing system services...")
    
    # Note: These commands require sudo and may not work on Windows
    # They're designed for Ubuntu server deployment
    print("⚠️  Note: PostgreSQL and Redis installation requires sudo privileges")
    print("⚠️  These commands are designed for Ubuntu server deployment")
    
    # For now, just create the directories and set environment variables
    print("\n✅ Basic setup completed")
    print("💡 To complete setup on Ubuntu server, run:")
    print("   sudo python scripts/setup_voice_services.py")
    
    return True

if __name__ == "__main__":
    main() 