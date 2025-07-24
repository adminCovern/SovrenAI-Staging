#!/usr/bin/env python3
"""
SOVREN AI Launcher - Type Checking Script
Verifies type annotations and helps resolve type checking issues
"""

import subprocess
import sys
from pathlib import Path

def run_type_check():
    """Run type checking with Pyright"""
    print("🔍 Running type checks...")
    
    try:
        # Run Pyright
        result = subprocess.run([
            sys.executable, "-m", "pyright", 
            "--project", "scripts/pyrightconfig.json",
            "scripts/launch_sovren.py",
            "scripts/test_launch_sovren.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Type checking passed!")
            return True
        else:
            print("❌ Type checking failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Type checking error: {e}")
        return False
    except FileNotFoundError:
        print("❌ Pyright not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyright"], check=True)
            return run_type_check()
        except subprocess.CalledProcessError:
            print("❌ Failed to install Pyright")
            return False

def check_imports():
    """Check if all required imports are available"""
    print("🔍 Checking imports...")
    
    imports = [
        ('psutil', 'psutil'),
        ('yaml', 'PyYAML'),
        ('requests', 'requests'),
        ('cryptography', 'cryptography'),
    ]
    
    all_good = True
    for module, package in imports:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError:
            print(f"❌ {module} not available")
            print(f"   Install with: pip install {package}")
            all_good = False
    
    return all_good

def create_type_stubs():
    """Create type stub files if they don't exist"""
    print("🔧 Creating type stubs...")
    
    typings_dir = Path("scripts/typings")
    typings_dir.mkdir(exist_ok=True)
    
    # Create __init__.py for typings directory
    init_file = typings_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print("✅ Created typings/__init__.py")
    
    return True

def main():
    """Main type checking function"""
    print("🔍 SOVREN AI Launcher - Type Checking")
    print("=" * 50)
    
    # Create type stubs
    if not create_type_stubs():
        print("❌ Failed to create type stubs")
        sys.exit(1)
    
    # Check imports
    if not check_imports():
        print("\n❌ Some imports are missing.")
        print("Please run: python scripts/install_dependencies.py")
        sys.exit(1)
    
    # Run type checking
    if not run_type_check():
        print("\n❌ Type checking failed.")
        print("Please fix the issues above or run: python scripts/fix_imports.py")
        sys.exit(1)
    
    print("\n✅ All type checks passed!")
    print("The launcher is ready for production use.")

if __name__ == "__main__":
    main() 