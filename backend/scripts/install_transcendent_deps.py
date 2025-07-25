#!/usr/bin/env python3
"""
Transcendent MCP Server Dependency Installer
Installs dependencies for the Absolute Market Domination Protocol: Omnicide Edition
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name: str, description: str = "") -> bool:
    """Install a single package"""
    try:
        print(f"📦 Installing {package_name}...")
        if description:
            print(f"   {description}")
        
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def main():
    """Install Transcendent MCP Server dependencies"""
    print("🚀 TRANSCENDENT MCP SERVER DEPENDENCY INSTALLER")
    print("⚡ ABSOLUTE MARKET DOMINATION PROTOCOL: OMNICIDE EDITION")
    print("=" * 60)
    
    # Core dependencies (required)
    core_deps = [
        ("numpy>=1.21.0", "Numerical computing"),
        ("psutil>=5.8.0", "System monitoring"),
        ("torch>=1.9.0", "PyTorch for AI"),
        ("cryptography>=3.4.0", "Encryption and security")
    ]
    
    # Optional dependencies (recommended)
    optional_deps = [
        ("GPUtil>=1.4.0", "GPU monitoring"),
        ("qiskit>=0.34.0", "Quantum computing"),
        ("quantumrandom>=1.9.0", "Quantum random numbers"),
        ("scipy>=1.7.0", "Scientific computing"),
        ("scikit-learn>=1.0.0", "Machine learning"),
        ("networkx>=2.6.0", "Graph algorithms"),
        ("matplotlib>=3.4.0", "Data visualization"),
        ("opencv-python>=4.5.0", "Computer vision"),
        ("librosa>=0.8.0", "Audio processing"),
        ("soundfile>=0.10.0", "Audio file handling"),
        ("Pillow>=8.3.0", "Image processing"),
        ("requests>=2.25.0", "HTTP requests"),
        ("aiohttp>=3.8.0", "Async HTTP"),
        ("websockets>=10.0", "WebSocket support"),
        ("redis>=4.0.0", "Caching and storage"),
        ("PyYAML>=5.4.0", "YAML parsing"),
        ("toml>=0.10.0", "TOML parsing"),
        ("jsonlines>=2.0.0", "JSON Lines support")
    ]
    
    # Development dependencies (optional)
    dev_deps = [
        ("pylint>=2.10.0", "Code linting"),
        ("flake8>=3.9.0", "Style checking"),
        ("black>=21.7.0", "Code formatting"),
        ("isort>=5.9.0", "Import sorting"),
        ("mypy>=0.910", "Type checking"),
        ("pytest>=6.2.0", "Testing framework"),
        ("coverage>=5.5.0", "Code coverage"),
        ("safety>=1.10.0", "Security scanning"),
        ("bandit>=1.6.0", "Security linting"),
        ("pipdeptree>=2.0.0", "Dependency tree"),
        ("virtualenv>=20.7.0", "Virtual environments"),
        ("memory_profiler>=0.58.0", "Memory profiling"),
        ("line_profiler>=3.3.0", "Line profiling")
    ]
    
    print("📦 Installing core dependencies...")
    core_success = 0
    for package, description in core_deps:
        if install_package(package, description):
            core_success += 1
    
    print(f"\n✅ Core dependencies: {core_success}/{len(core_deps)} installed")
    
    if core_success < len(core_deps):
        print("⚠️  Some core dependencies failed to install")
        print("The Transcendent MCP Server may not function properly")
    
    print("\n📦 Installing optional dependencies...")
    optional_success = 0
    for package, description in optional_deps:
        if install_package(package, description):
            optional_success += 1
    
    print(f"\n✅ Optional dependencies: {optional_success}/{len(optional_deps)} installed")
    
    # Ask about development dependencies
    print("\n🔧 Development dependencies (optional)")
    print("These are tools for development, testing, and code quality")
    response = input("Install development dependencies? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\n📦 Installing development dependencies...")
        dev_success = 0
        for package, description in dev_deps:
            if install_package(package, description):
                dev_success += 1
        
        print(f"\n✅ Development dependencies: {dev_success}/{len(dev_deps)} installed")
    
    print("\n🎉 TRANSCENDENT MCP SERVER DEPENDENCY INSTALLATION COMPLETE")
    print("=" * 60)
    print("🌌 Reality Distortion Index: Ready")
    print("🎯 Singularity Coefficient: Ready")
    print("🧠 Consciousness Integration: Ready")
    print("🔥 Metamorphic Phoenix Biology: Ready")
    print("🔄 Entropy Reversal Engine: Ready")
    print("🎯 Competitive Omnicide: Ready")
    print("=" * 60)
    print("🚀 You can now run the Transcendent MCP Server!")
    print("   python backend/mcp_server.py")

if __name__ == "__main__":
    main() 