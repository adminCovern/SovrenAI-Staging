#!/usr/bin/env python3
"""
SOVREN AI Environment Setup Script
Sets up required environment variables for production deployment
"""

import os
import sys
import secrets
import hashlib
from pathlib import Path
from typing import Dict, Any

def generate_security_key() -> str:
    """Generate a secure security key"""
    return secrets.token_hex(32)

def setup_environment_variables():
    """Set up all required environment variables"""
    print("🔧 Setting up SOVREN AI environment variables...")
    
    # Set the specific SOVREN security key
    security_key = "aa9628c23683705c6c1eee9771bb3224f438333e925df0c5df2e88f0699603fd"
    os.environ['SOVREN_SECURITY_KEY'] = security_key
    print(f"✅ Set SOVREN_SECURITY_KEY: {security_key[:16]}...")
    
    # Set environment
    if not os.environ.get('SOVREN_ENV'):
        os.environ['SOVREN_ENV'] = 'production'
        print("✅ Set SOVREN_ENV=production")
    else:
        print(f"✅ Using existing SOVREN_ENV: {os.environ['SOVREN_ENV']}")
    
    # Set additional required variables
    env_vars = {
        'SOVREN_LOG_LEVEL': 'INFO',
        'SOVREN_HOST': '0.0.0.0',
        'SOVREN_PORT': '8000',
        'SOVREN_MAX_CONNECTIONS': '1000',
        'SOVREN_RATE_LIMIT_PER_MINUTE': '100',
        'SOVREN_ENABLE_TLS': 'false',
        'SOVREN_LOG_FORMAT': 'json',
        'SOVREN_MAX_MEMORY_MB': '2048',
        'SOVREN_METRICS_PORT': '9090',
        'SOVREN_JWT_SECRET': secrets.token_hex(32),
        'SOVREN_JWT_EXPIRY_HOURS': '24',
        'SOVREN_MCP_ENABLED': '1',
        'SOVREN_MCP_HOST': 'localhost',
        'SOVREN_MCP_PORT': '9999',
        'CUDA_DEVICE_ORDER': 'PCI_BUS_ID',
        'PYTHONUNBUFFERED': '1',
        'OMP_NUM_THREADS': str(min(16, os.cpu_count() or 1)),
        'MKL_NUM_THREADS': str(min(16, os.cpu_count() or 1)),
        'OPENBLAS_NUM_THREADS': str(min(16, os.cpu_count() or 1)),
        'VECLIB_MAXIMUM_THREADS': str(min(16, os.cpu_count() or 1)),
        'NUMEXPR_NUM_THREADS': str(min(16, os.cpu_count() or 1)),
        'MALLOC_ARENA_MAX': '2',
        'PYTHONMALLOC': 'malloc',
        'TORCH_CUDNN_V8_API_ENABLED': '1',
        'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:512',
        'CUDA_LAUNCH_BLOCKING': '0'
    }
    
    for var, value in env_vars.items():
        if not os.environ.get(var):
            os.environ[var] = value
            print(f"✅ Set {var}={value}")
        else:
            print(f"✅ Using existing {var}: {os.environ[var]}")
    
    print("\n🎯 Environment setup complete!")
    print("All required environment variables are now set.")
    
    return True

def create_env_file():
    """Create a .env file with all environment variables"""
    print("\n📝 Creating .env file...")
    
    env_content = """# SOVREN AI Environment Configuration
# Generated automatically - DO NOT EDIT MANUALLY

# Security Configuration
SOVREN_SECURITY_KEY={security_key}
SOVREN_ENV=production
SOVREN_JWT_SECRET={jwt_secret}

# Network Configuration
SOVREN_HOST=0.0.0.0
SOVREN_PORT=8000
SOVREN_MAX_CONNECTIONS=1000
SOVREN_RATE_LIMIT_PER_MINUTE=100
SOVREN_ENABLE_TLS=false

# Logging Configuration
SOVREN_LOG_LEVEL=INFO
SOVREN_LOG_FORMAT=json

# Performance Configuration
SOVREN_MAX_MEMORY_MB=2048
SOVREN_METRICS_PORT=9090
SOVREN_JWT_EXPIRY_HOURS=24

# MCP Server Configuration
SOVREN_MCP_ENABLED=1
SOVREN_MCP_HOST=localhost
SOVREN_MCP_PORT=9999

# CUDA Configuration for B200 GPUs
CUDA_DEVICE_ORDER=PCI_BUS_ID
PYTHONUNBUFFERED=1
OMP_NUM_THREADS={cpu_threads}
MKL_NUM_THREADS={cpu_threads}
OPENBLAS_NUM_THREADS={cpu_threads}
VECLIB_MAXIMUM_THREADS={cpu_threads}
NUMEXPR_NUM_THREADS={cpu_threads}
MALLOC_ARENA_MAX=2
PYTHONMALLOC=malloc
TORCH_CUDNN_V8_API_ENABLED=1
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
CUDA_LAUNCH_BLOCKING=0
""".format(
        security_key=os.environ.get('SOVREN_SECURITY_KEY', generate_security_key()),
        jwt_secret=os.environ.get('SOVREN_JWT_SECRET', secrets.token_hex(32)),
        cpu_threads=min(16, os.cpu_count() or 1)
    )
    
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file: {env_file.absolute()}")
    return True

def verify_environment():
    """Verify that all required environment variables are set"""
    print("\n🔍 Verifying environment variables...")
    
    required_vars = [
        'SOVREN_SECURITY_KEY',
        'SOVREN_ENV',
        'SOVREN_JWT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

def main():
    """Main setup function"""
    print("🚀 SOVREN AI Environment Setup")
    print("=" * 50)
    
    try:
        # Set up environment variables
        setup_environment_variables()
        
        # Create .env file
        create_env_file()
        
        # Verify setup
        if verify_environment():
            print("\n🎉 Environment setup completed successfully!")
            print("You can now run: python3 scripts/launch_sovren.py")
            return True
        else:
            print("\n❌ Environment setup failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during environment setup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 