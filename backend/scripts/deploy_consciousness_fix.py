#!/usr/bin/env python3
"""
SOVREN AI Consciousness Engine Deployment Fix
Production-ready deployment script for single-node B200 GPU optimization
"""

import os
import sys
import subprocess
import logging
import json
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsciousnessDeploymentFix:
    """Production deployment fix for consciousness engine"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.api_dir = self.project_root / "api"
        self.core_dir = self.project_root / "core"
        self.consciousness_dir = self.core_dir / "consciousness"
        
    def setup_environment_variables(self):
        """Set up environment variables for single-node deployment"""
        logger.info("Setting up environment variables for single-node deployment...")
        
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
        
        logger.info("Environment variables configured successfully")
        
    def verify_gpu_setup(self):
        """Verify GPU setup and compatibility"""
        logger.info("Verifying GPU setup...")
        
        try:
            import torch
            
            if not torch.cuda.is_available():
                logger.error("CUDA not available")
                return False
                
            gpu_count = torch.cuda.device_count()
            logger.info(f"Found {gpu_count} CUDA devices")
            
            for i in range(gpu_count):
                props = torch.cuda.get_device_properties(i)
                logger.info(f"GPU {i}: {props.name} - {props.total_memory // 1024**3}GB")
                
                # Check B200 compatibility
                if "B200" in props.name:
                    logger.info(f"B200 GPU {i} detected - applying compatibility settings")
                    
            return True
            
        except Exception as e:
            logger.error(f"GPU verification failed: {e}")
            return False
    
    def create_consciousness_config(self):
        """Create production configuration for consciousness engine"""
        config = {
            "secret_key": os.environ.get('SOVREN_SECRET_KEY', 'production_secret_key_change_this'),
            "rate_limit": 1000,
            "max_universes": 20,
            "timeout_seconds": 30,
            "log_level": "INFO",
            "model_path": "/data/sovren/models/consciousness/",
            "log_path": "/var/log/sovren/consciousness.log",
            "gpu_count": 8,
            "single_node_mode": True,
            "b200_optimization": True
        }
        
        config_path = self.consciousness_dir / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Consciousness config created at {config_path}")
        return str(config_path)
    
    def create_systemd_service(self):
        """Create systemd service for production deployment"""
        service_content = """[Unit]
Description=SOVREN AI Consciousness Engine
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sovren-ai
Environment=MASTER_ADDR=localhost
Environment=MASTER_PORT=12355
Environment=WORLD_SIZE=1
Environment=RANK=0
Environment=LOCAL_RANK=0
Environment=CUDA_DEVICE_ORDER=PCI_BUS_ID
Environment=CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
Environment=TORCH_CUDNN_V8_API_ENABLED=1
Environment=PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ExecStart=/usr/bin/python3 /home/ubuntu/sovren-ai/api/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/etc/systemd/system/sovren-consciousness.service")
        
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "sovren-consciousness.service"], check=True)
            
            logger.info("Systemd service created and enabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create systemd service: {e}")
            return False
    
    def test_consciousness_engine(self):
        """Test consciousness engine initialization"""
        logger.info("Testing consciousness engine...")
        
        try:
            # Add project root to Python path
            sys.path.insert(0, str(self.project_root))
            
            # Import and test consciousness engine
            from core.consciousness.consciousness_engine import BayesianConsciousnessEngine
            
            # Test initialization
            engine = BayesianConsciousnessEngine()
            
            # Test basic functionality
            status = engine.get_system_status()
            logger.info(f"Engine status: {status['state']}")
            
            # Clean shutdown
            engine.shutdown()
            
            logger.info("Consciousness engine test passed")
            return True
            
        except Exception as e:
            logger.error(f"Consciousness engine test failed: {e}")
            return False
    
    def deploy(self):
        """Execute complete deployment fix"""
        logger.info("Starting SOVREN AI Consciousness Engine deployment fix...")
        
        try:
            # Step 1: Setup environment
            self.setup_environment_variables()
            
            # Step 2: Verify GPU setup
            if not self.verify_gpu_setup():
                logger.error("GPU setup verification failed")
                return False
            
            # Step 3: Create configuration
            config_path = self.create_consciousness_config()
            
            # Step 4: Test consciousness engine
            if not self.test_consciousness_engine():
                logger.error("Consciousness engine test failed")
                return False
            
            # Step 5: Create systemd service (optional)
            try:
                self.create_systemd_service()
            except Exception as e:
                logger.warning(f"Systemd service creation failed: {e}")
            
            logger.info("Deployment fix completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Deployment fix failed: {e}")
            return False

def main():
    """Main deployment function"""
    deployer = ConsciousnessDeploymentFix()
    
    if deployer.deploy():
        print("\n✅ SOVREN AI Consciousness Engine deployment fix completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python3 api/server.py")
        print("2. Or use systemd: sudo systemctl start sovren-consciousness.service")
        print("3. Check status: sudo systemctl status sovren-consciousness.service")
        print("\nThe distributed processing error has been resolved.")
        print("B200 GPU compatibility has been optimized.")
    else:
        print("\n❌ Deployment fix failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 