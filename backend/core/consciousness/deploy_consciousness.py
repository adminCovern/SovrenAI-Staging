#!/usr/bin/env python3
"""
SOVREN AI Consciousness Engine - Production Deployment Script
Deploys the consciousness engine with full production configuration
"""

import os
import sys
import time
import json
import signal
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sovren/deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConsciousnessDeployer:
    """Production deployment manager for consciousness engine"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.process = None
        self.monitoring_active = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _setup_environment(self) -> bool:
        """Setup production environment"""
        try:
            # Create necessary directories
            directories = [
                '/data/sovren/models/consciousness',
                '/var/log/sovren',
                '/dev/shm/sovren_consciousness'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Set proper permissions
            os.chmod('/var/log/sovren', 0o755)
            os.chmod('/data/sovren/models/consciousness', 0o755)
            
            # Verify GPU availability
            if not self._verify_gpu_setup():
                logger.error("GPU setup verification failed")
                return False
            
            logger.info("Environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            return False
    
    def _verify_gpu_setup(self) -> bool:
        """Verify GPU setup and availability"""
        try:
            import torch
            
            if not torch.cuda.is_available():
                logger.error("CUDA not available")
                return False
            
            gpu_count = torch.cuda.device_count()
            if gpu_count < 8:
                logger.error(f"Insufficient GPUs: {gpu_count}/8 required")
                return False
            
            # Check GPU memory
            for i in range(gpu_count):
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / (1024**3)
                logger.info(f"GPU {i}: {props.name} - {memory_gb:.1f}GB")
                
                if memory_gb < 100:  # Minimum 100GB per GPU
                    logger.warning(f"GPU {i} has limited memory: {memory_gb:.1f}GB")
            
            return True
            
        except Exception as e:
            logger.error(f"GPU verification failed: {e}")
            return False
    
    def _start_consciousness_engine(self) -> bool:
        """Start the consciousness engine process"""
        try:
            # Build command
            cmd = [
                sys.executable,
                'consciousness_engine.py',
                '--config', self.config_path,
                '--daemon'
            ]
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            
            # Wait for startup
            time.sleep(5)
            
            if self.process.poll() is None:
                logger.info(f"Consciousness engine started with PID: {self.process.pid}")
                return True
            else:
                stdout, stderr = self.process.communicate()
                logger.error(f"Process failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start consciousness engine: {e}")
            return False
    
    def _start_monitoring(self):
        """Start monitoring thread"""
        import threading
        
        def monitor_process():
            while self.monitoring_active:
                if self.process and self.process.poll() is not None:
                    logger.error("Consciousness engine process died unexpectedly")
                    self._restart_engine()
                
                # Monitor system resources
                self._log_system_status()
                time.sleep(self.config.get('monitoring_interval', 1))
        
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=monitor_process, daemon=True)
        monitor_thread.start()
        logger.info("Monitoring started")
    
    def _log_system_status(self):
        """Log system resource status"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            logger.info(f"System Status - CPU: {cpu_percent}%, Memory: {memory.percent}%")
            
            # GPU monitoring
            if self.process:
                try:
                    import torch
                    for i in range(torch.cuda.device_count()):
                        with torch.cuda.device(i):
                            util = torch.cuda.utilization(i)
                            allocated = torch.cuda.memory_allocated(i) / 1024**3
                            logger.info(f"GPU {i} - Utilization: {util}%, Memory: {allocated:.1f}GB")
                except Exception as e:
                    logger.warning(f"GPU monitoring failed: {e}")
                    
        except Exception as e:
            logger.warning(f"System monitoring failed: {e}")
    
    def _restart_engine(self) -> bool:
        """Restart the consciousness engine"""
        logger.info("Restarting consciousness engine...")
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        return self._start_consciousness_engine()
    
    def _stop_engine(self):
        """Stop the consciousness engine gracefully"""
        if self.process:
            logger.info("Stopping consciousness engine...")
            try:
                self.process.terminate()
                self.process.wait(timeout=30)
                logger.info("Consciousness engine stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("Force killing consciousness engine")
                self.process.kill()
                self.process.wait()
    
    def deploy(self) -> bool:
        """Deploy the consciousness engine"""
        logger.info("Starting consciousness engine deployment...")
        
        # Setup environment
        if not self._setup_environment():
            return False
        
        # Start engine
        if not self._start_consciousness_engine():
            return False
        
        # Start monitoring
        self._start_monitoring()
        
        logger.info("Consciousness engine deployment completed successfully")
        return True
    
    def run(self):
        """Run the deployment with signal handling"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.monitoring_active = False
            self._stop_engine()
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Deploy
        if not self.deploy():
            logger.error("Deployment failed")
            sys.exit(1)
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

def main():
    """Main deployment entry point"""
    parser = argparse.ArgumentParser(description='Deploy SOVREN Consciousness Engine')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Validate config file
    if not Path(args.config).exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Create deployer
    deployer = ConsciousnessDeployer(args.config)
    
    # Run deployment
    deployer.run()

if __name__ == '__main__':
    main() 