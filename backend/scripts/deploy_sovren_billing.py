#!/usr/bin/env python3
"""
SOVREN Billing System - Automated Deployment
Production deployment without Docker, containers, or virtual environments
"""

import os
import sys
import subprocess
import shutil
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Deployment')

class SOVRENDeployment:
    """Production deployment manager for SOVREN billing system"""
    
    def __init__(self, environment: str = 'production'):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.deploy_path = Path('/opt/sovren-billing')
        self.service_name = 'sovren-billing'
        self.user = 'sovren'
        self.group = 'sovren'
        
        # Deployment configuration
        self.config = {
            'production': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 4,
                'log_level': 'INFO',
                'database_url': 'postgresql://sovren:password@localhost:5432/sovren_billing',
                'killbill_url': 'http://localhost:8080'
            },
            'staging': {
                'host': '0.0.0.0',
                'port': 8001,
                'workers': 2,
                'log_level': 'DEBUG',
                'database_url': 'postgresql://sovren:password@localhost:5432/sovren_billing_staging',
                'killbill_url': 'http://localhost:8080'
            }
        }
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run shell command with error handling"""
        try:
            logger.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Command completed successfully")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    def check_system_requirements(self) -> bool:
        """Check system requirements"""
        logger.info("Checking system requirements...")
        
        requirements = [
            ('python3', '--version'),
            ('pip3', '--version'),
            ('systemctl', '--version'),
            ('psql', '--version'),
            ('java', '-version')
        ]
        
        for cmd, arg in requirements:
            try:
                self.run_command([cmd, arg])
                logger.info(f"✓ {cmd} is available")
            except subprocess.CalledProcessError:
                logger.error(f"✗ {cmd} is not available")
                return False
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        try:
            # Install required packages
            packages = [
                'aiohttp',
                'asyncpg',
                'cryptography',
                'prometheus_client',
                'psutil',
                'pyyaml',
                'redis'
            ]
            
            for package in packages:
                logger.info(f"Installing {package}...")
                self.run_command(['pip3', 'install', package])
            
            logger.info("✓ All dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def setup_database(self) -> bool:
        """Setup PostgreSQL database"""
        logger.info("Setting up database...")
        
        try:
            # Create database and user
            db_config = self.config[self.environment]
            
            # Create user if not exists
            self.run_command([
                'sudo', '-u', 'postgres', 'psql', '-c',
                f"CREATE USER {self.user} WITH PASSWORD 'password';"
            ])
            
            # Create database
            db_name = 'sovren_billing' if self.environment == 'production' else 'sovren_billing_staging'
            self.run_command([
                'sudo', '-u', 'postgres', 'psql', '-c',
                f"CREATE DATABASE {db_name} OWNER {self.user};"
            ])
            
            logger.info("✓ Database setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup database: {e}")
            return False
    
    def create_deployment_directory(self) -> bool:
        """Create deployment directory structure"""
        logger.info("Creating deployment directory...")
        
        try:
            # Create deployment directory
            self.deploy_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.deploy_path / 'logs').mkdir(exist_ok=True)
            (self.deploy_path / 'config').mkdir(exist_ok=True)
            (self.deploy_path / 'data').mkdir(exist_ok=True)
            
            # Set permissions
            self.run_command(['sudo', 'chown', '-R', f'{self.user}:{self.group}', str(self.deploy_path)])
            self.run_command(['sudo', 'chmod', '-R', '755', str(self.deploy_path)])
            
            logger.info("✓ Deployment directory created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create deployment directory: {e}")
            return False
    
    def copy_application_files(self) -> bool:
        """Copy application files to deployment directory"""
        logger.info("Copying application files...")
        
        try:
            # Copy API files
            api_source = self.project_root / 'api'
            api_dest = self.deploy_path / 'api'
            
            if api_dest.exists():
                shutil.rmtree(api_dest)
            shutil.copytree(api_source, api_dest)
            
            # Copy configuration files
            config_source = self.project_root / 'config'
            config_dest = self.deploy_path / 'config'
            
            if config_dest.exists():
                shutil.rmtree(config_dest)
            shutil.copytree(config_source, config_dest)
            
            # Copy scripts
            scripts_source = self.project_root / 'scripts'
            scripts_dest = self.deploy_path / 'scripts'
            
            if scripts_dest.exists():
                shutil.rmtree(scripts_dest)
            shutil.copytree(scripts_source, scripts_dest)
            
            # Set permissions
            self.run_command(['sudo', 'chown', '-R', f'{self.user}:{self.group}', str(self.deploy_path)])
            
            logger.info("✓ Application files copied")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy application files: {e}")
            return False
    
    def create_systemd_service(self) -> bool:
        """Create systemd service file"""
        logger.info("Creating systemd service...")
        
        try:
            service_content = f"""[Unit]
Description=SOVREN Billing System
After=network.target postgresql.service

[Service]
Type=simple
User={self.user}
Group={self.group}
WorkingDirectory={self.deploy_path}
Environment=PYTHONPATH={self.deploy_path}
Environment=SOVREN_ENVIRONMENT={self.environment}
ExecStart=/usr/bin/python3 {self.deploy_path}/api/server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
            
            service_file = Path(f'/etc/systemd/system/{self.service_name}.service')
            service_file.write_text(service_content)
            
            # Reload systemd
            self.run_command(['sudo', 'systemctl', 'daemon-reload'])
            
            logger.info("✓ Systemd service created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create systemd service: {e}")
            return False
    
    def create_nginx_config(self) -> bool:
        """Create nginx configuration"""
        logger.info("Creating nginx configuration...")
        
        try:
            nginx_config = f"""server {{
    listen 80;
    server_name billing.sovren.ai;

    location / {{
        proxy_pass http://127.0.0.1:{self.config[self.environment]['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /metrics {{
        proxy_pass http://127.0.0.1:{self.config[self.environment]['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /health {{
        proxy_pass http://127.0.0.1:{self.config[self.environment]['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
            
            nginx_file = Path(f'/etc/nginx/sites-available/{self.service_name}')
            nginx_file.write_text(nginx_config)
            
            # Enable site
            self.run_command(['sudo', 'ln', '-sf', f'/etc/nginx/sites-available/{self.service_name}', 
                           f'/etc/nginx/sites-enabled/{self.service_name}'])
            
            # Test nginx config
            self.run_command(['sudo', 'nginx', '-t'])
            
            logger.info("✓ Nginx configuration created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create nginx configuration: {e}")
            return False
    
    def setup_logging(self) -> bool:
        """Setup logging configuration"""
        logger.info("Setting up logging...")
        
        try:
            # Create logrotate configuration
            logrotate_config = f"""{self.deploy_path}/logs/*.log {{
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 {self.user} {self.group}
    postrotate
        systemctl reload {self.service_name}
    endscript
}}
"""
            
            logrotate_file = Path(f'/etc/logrotate.d/{self.service_name}')
            logrotate_file.write_text(logrotate_config)
            
            logger.info("✓ Logging configuration created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup logging: {e}")
            return False
    
    def setup_monitoring(self) -> bool:
        """Setup monitoring and metrics"""
        logger.info("Setting up monitoring...")
        
        try:
            # Create prometheus configuration
            prometheus_config = f"""global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sovren-billing'
    static_configs:
      - targets: ['localhost:{self.config[self.environment]["port"]}']
    metrics_path: /metrics
    scrape_interval: 5s
"""
            
            prometheus_file = Path('/etc/prometheus/prometheus.yml')
            if prometheus_file.parent.exists():
                prometheus_file.write_text(prometheus_config)
            
            logger.info("✓ Monitoring configuration created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")
            return False
    
    def start_services(self) -> bool:
        """Start all services"""
        logger.info("Starting services...")
        
        try:
            # Start billing service
            self.run_command(['sudo', 'systemctl', 'enable', self.service_name])
            self.run_command(['sudo', 'systemctl', 'start', self.service_name])
            
            # Restart nginx
            self.run_command(['sudo', 'systemctl', 'restart', 'nginx'])
            
            # Check service status
            result = self.run_command(['sudo', 'systemctl', 'is-active', self.service_name])
            if result.stdout.strip() == 'active':
                logger.info("✓ Services started successfully")
                return True
            else:
                logger.error("Service failed to start")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start services: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """Run health check after deployment"""
        logger.info("Running health check...")
        
        try:
            import requests
            import time
            
            # Wait for service to start
            time.sleep(10)
            
            # Check health endpoint
            response = requests.get(f"http://localhost:{self.config[self.environment]['port']}/health")
            
            if response.status_code == 200:
                logger.info("✓ Health check passed")
                return True
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def deploy(self) -> bool:
        """Run complete deployment"""
        logger.info(f"Starting SOVREN Billing deployment for {self.environment} environment")
        
        steps = [
            ("Check system requirements", self.check_system_requirements),
            ("Install dependencies", self.install_dependencies),
            ("Setup database", self.setup_database),
            ("Create deployment directory", self.create_deployment_directory),
            ("Copy application files", self.copy_application_files),
            ("Create systemd service", self.create_systemd_service),
            ("Create nginx config", self.create_nginx_config),
            ("Setup logging", self.setup_logging),
            ("Setup monitoring", self.setup_monitoring),
            ("Start services", self.start_services),
            ("Run health check", self.run_health_check)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            if not step_func():
                logger.error(f"Deployment failed at step: {step_name}")
                return False
        
        logger.info("✓ SOVREN Billing deployment completed successfully!")
        return True
    
    def rollback(self) -> bool:
        """Rollback deployment"""
        logger.info("Rolling back deployment...")
        
        try:
            # Stop service
            self.run_command(['sudo', 'systemctl', 'stop', self.service_name])
            self.run_command(['sudo', 'systemctl', 'disable', self.service_name])
            
            # Remove service file
            service_file = Path(f'/etc/systemd/system/{self.service_name}.service')
            if service_file.exists():
                service_file.unlink()
            
            # Remove nginx config
            nginx_file = Path(f'/etc/nginx/sites-available/{self.service_name}')
            if nginx_file.exists():
                nginx_file.unlink()
            
            # Remove deployment directory
            if self.deploy_path.exists():
                shutil.rmtree(self.deploy_path)
            
            # Reload systemd
            self.run_command(['sudo', 'systemctl', 'daemon-reload'])
            
            logger.info("✓ Rollback completed")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy SOVREN Billing System')
    parser.add_argument('--environment', choices=['production', 'staging'], 
                       default='production', help='Deployment environment')
    parser.add_argument('--rollback', action='store_true', help='Rollback deployment')
    
    args = parser.parse_args()
    
    deployment = SOVRENDeployment(args.environment)
    
    if args.rollback:
        success = deployment.rollback()
    else:
        success = deployment.deploy()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 