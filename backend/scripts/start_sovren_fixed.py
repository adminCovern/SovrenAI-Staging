#!/usr/bin/env python3
"""
SOVREN AI Production Startup Script
Fixed version with proper environment variables and B200 GPU optimization
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for production deployment"""
    logger.info("Setting up production environment variables...")
    
    # Single-node distributed processing environment
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    os.environ['WORLD_SIZE'] = '1'
    os.environ['RANK'] = '0'
    os.environ['LOCAL_RANK'] = '0'
    
    # CUDA environment for B200 compatibility
    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3,4,5,6,7'
    
    # PyTorch optimizations for B200
    os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'
    os.environ['TORCH_CUDNN_V8_API_DISABLED'] = '0'
    
    # Memory optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
    
    # Suppress B200 warnings
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    
    logger.info("Environment variables configured successfully")

def verify_dependencies():
    """Verify all required dependencies are available"""
    logger.info("Verifying dependencies...")
    
    required_packages = [
        'torch',
        'numpy',
        'fastapi',
        'uvicorn',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} available")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} not available")
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.error("Please install missing packages: pip install " + " ".join(missing_packages))
        return False
    
    return True

def start_server():
    """Start the SOVREN AI server"""
    logger.info("Starting SOVREN AI server...")
    
    # Get project root
    project_root = Path(__file__).parent.parent
    server_path = project_root / "api" / "server.py"
    
    if not server_path.exists():
        logger.error(f"Server file not found: {server_path}")
        return False
    
    try:
        # Change to project directory
        os.chdir(project_root)
        
        # Start server with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "api.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        logger.info(f"Starting server with command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return True
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 SOVREN AI Production Startup")
    print("=" * 50)
    
    try:
        # Step 1: Setup environment
        setup_environment()
        
        # Step 2: Verify dependencies
        if not verify_dependencies():
            print("\n❌ Dependency verification failed")
            sys.exit(1)
        
        # Step 3: Start server
        print("\n✅ Environment configured successfully")
        print("✅ Dependencies verified")
        print("\nStarting SOVREN AI server...")
        print("Server will be available at: http://0.0.0.0:8000")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        if not start_server():
            print("\n❌ Server startup failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        print(f"\n❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 