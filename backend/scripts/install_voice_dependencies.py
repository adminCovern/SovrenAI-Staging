#!/usr/bin/env python3
"""
Install Voice System Dependencies
Quick installation of required packages for production
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

def main():
    """Install Voice System dependencies"""
    print("🚀 Installing Voice System Dependencies...")
    
    # Core dependencies that are essential for startup
    core_deps = [
        "numpy>=1.24.0",
        "torch>=2.0.0",
        "torchaudio>=2.0.0", 
        "aiohttp>=3.9.0",
        "websockets>=12.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "redis>=5.0.0",
        "pydantic>=2.0.0",
        "cryptography>=41.0.0",
        "prometheus-client>=0.18.0",
        "psutil>=5.9.0"
    ]
    
    # Install core dependencies
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep} - continuing...")
    
    # Optional dependencies that can be installed later
    optional_deps = [
        "soundfile>=0.12.1",
        "librosa>=0.10.0", 
        "sounddevice>=0.4.6",
        "scipy>=1.11.0",
        "aiofiles>=23.0.0",
        "aiodns>=3.0.0"
    ]
    
    print("\n📦 Installing optional dependencies in background...")
    for dep in optional_deps:
        # Install in background to not block startup
        subprocess.Popen(f"pip install {dep}", shell=True)
    
    print("\n✅ Voice System dependencies installation initiated")
    print("💡 Optional dependencies will install in background")
    print("🚀 Voice System can now start with core functionality")

if __name__ == "__main__":
    main() 