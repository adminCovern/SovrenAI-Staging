#!/usr/bin/env python3
"""
SOVREN AI Launcher - Import Fix Script
Quickly resolves import issues and verifies the installation
"""

import sys
import subprocess
from pathlib import Path

def check_import(module_name, install_name=None):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} is available")
        return True
    except ImportError:
        print(f"❌ {module_name} is missing")
        if install_name:
            print(f"   Installing {install_name}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", install_name], check=True)
                print(f"✅ {install_name} installed successfully")
                return True
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {install_name}")
                return False
        return False

def main():
    """Main function to fix import issues"""
    print("🔧 SOVREN AI Launcher - Import Fix")
    print("=" * 50)
    
    # Check and fix critical imports
    critical_imports = [
        ('psutil', 'psutil>=5.9.0'),
        ('yaml', 'PyYAML>=6.0'),
        ('requests', 'requests>=2.28.0'),
        ('cryptography', 'cryptography>=3.4.0'),
    ]
    
    all_good = True
    for module, package in critical_imports:
        if not check_import(module, package):
            all_good = False
    
    if all_good:
        print("\n✅ All critical imports are available!")
        print("You can now run: python scripts/launch_sovren.py")
    else:
        print("\n❌ Some imports are still missing.")
        print("Please run: python scripts/install_dependencies.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 