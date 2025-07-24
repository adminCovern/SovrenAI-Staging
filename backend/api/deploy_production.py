#!/usr/bin/env python3
"""
SOVREN Billing System - Production Deployment
Direct deployment without containerization
"""

import os
import sys
import subprocess
import logging
import signal
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sovren-billing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ProductionDeployment')

class ProductionDeployment:
    """Production deployment manager without containerization"""
    
    def __init__(self):
        self.process = None
        self.running = False
        self.service_name = 'sovren-billing'
        
    def install_dependencies(self):
        """Install system dependencies"""
        logger.info("Installing system dependencies...")
        
        try:
            # Install Python dependencies
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True)
            
            # Install system packages if needed
            subprocess.run([
                'apt-get', 'update'
            ], check=True)
            
            subprocess.run([
                'apt-get', 'install', '-y', 'postgresql-client', 'redis-tools'
            ], check=True)
            
            logger.info("Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            raise
    
    def create_systemd_service(self):
        """Create systemd service file"""
        service_content = f"""[Unit]
Description=SOVREN Billing System
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=sovren
Group=sovren
WorkingDirectory={os.getcwd()}
Environment=PYTHONPATH={os.getcwd()}
Environment=PRODUCTION_MODE=true
ExecStart={sys.executable} deploy_billing.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        service_path = f"/etc/systemd/system/{self.service_name}.service"
        
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            # Reload systemd
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            logger.info(f"Systemd service created: {service_path}")
            
        except Exception as e:
            logger.error(f"Failed to create systemd service: {e}")
            raise
    
    def start_service(self):
        """Start the billing service"""
        try:
            subprocess.run([
                'systemctl', 'enable', self.service_name
            ], check=True)
            
            subprocess.run([
                'systemctl', 'start', self.service_name
            ], check=True)
            
            logger.info(f"Service {self.service_name} started successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start service: {e}")
            raise
    
    def stop_service(self):
        """Stop the billing service"""
        try:
            subprocess.run([
                'systemctl', 'stop', self.service_name
            ], check=True)
            
            logger.info(f"Service {self.service_name} stopped")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop service: {e}")
    
    def check_service_status(self):
        """Check service status"""
        try:
            result = subprocess.run([
                'systemctl', 'is-active', self.service_name
            ], capture_output=True, text=True)
            
            return result.stdout.strip() == 'active'
            
        except subprocess.CalledProcessError:
            return False
    
    def setup_logging(self):
        """Setup production logging"""
        log_dir = Path('/var/log/sovren-billing')
        log_dir.mkdir(exist_ok=True)
        
        # Create log rotation
        logrotate_content = f"""/var/log/sovren-billing/*.log {{
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 sovren sovren
    postrotate
        systemctl reload {self.service_name}
    endscript
}}
"""
        
        with open('/etc/logrotate.d/sovren-billing', 'w') as f:
            f.write(logrotate_content)
    
    def setup_monitoring(self):
        """Setup monitoring and metrics"""
        # Create monitoring directory
        monitoring_dir = Path('/opt/sovren-billing/monitoring')
        monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Create health check script
        health_check_script = monitoring_dir / 'health_check.py'
        with open(health_check_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get('http://localhost:8080/health', timeout=5)
    if response.status_code == 200:
        sys.exit(0)
    else:
        sys.exit(1)
except:
    sys.exit(1)
''')
        
        health_check_script.chmod(0o755)
    
    def deploy(self):
        """Perform full production deployment"""
        logger.info("Starting production deployment...")
        
        try:
            # Install dependencies
            self.install_dependencies()
            
            # Setup logging
            self.setup_logging()
            
            # Setup monitoring
            self.setup_monitoring()
            
            # Create systemd service
            self.create_systemd_service()
            
            # Start service
            self.start_service()
            
            # Verify deployment
            time.sleep(5)
            if self.check_service_status():
                logger.info("Production deployment completed successfully")
            else:
                raise Exception("Service failed to start")
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise

def main():
    """Main deployment function"""
    if os.geteuid() != 0:
        logger.error("This script must be run as root for production deployment")
        sys.exit(1)
    
    deployment = ProductionDeployment()
    
    try:
        deployment.deploy()
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 