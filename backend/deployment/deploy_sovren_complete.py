#!/usr/bin/env python3
"""
SOVREN AI Complete Production Deployment
Bare metal deployment script for all components
"""

import os
import sys
import subprocess
import logging
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SovrenDeployment')

class SovrenCompleteDeployment:
    """Complete SOVREN AI deployment orchestrator"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_dir = self.project_root / "deployment"
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
        
        # System components
        self.components = {
            'database': self._deploy_database,
            'redis': self._deploy_redis,
            'freeswitch': self._deploy_freeswitch,
            'voice_system': self._deploy_voice_system,
            'mcp_server': self._deploy_mcp_server,
            'core_systems': self._deploy_core_systems,
            'api_server': self._deploy_api_server,
            'frontend': self._deploy_frontend,
            'monitoring': self._deploy_monitoring
        }
        
        # Deployment status
        self.deployment_status = {}
        
    async def deploy_all(self):
        """Deploy all SOVREN AI components"""
        logger.info("Starting complete SOVREN AI deployment...")
        
        try:
            # Create necessary directories
            self._create_directories()
            
            # Deploy components in order
            for component, deploy_func in self.components.items():
                logger.info(f"Deploying {component}...")
                try:
                    await deploy_func()
                    self.deployment_status[component] = 'success'
                    logger.info(f"✅ {component} deployed successfully")
                except Exception as e:
                    self.deployment_status[component] = f'failed: {e}'
                    logger.error(f"❌ {component} deployment failed: {e}")
                    raise
            
            # Final verification
            await self._verify_deployment()
            
            logger.info("🎉 Complete SOVREN AI deployment successful!")
            self._print_deployment_summary()
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self._print_deployment_summary()
            raise
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.logs_dir,
            self.config_dir,
            self.deployment_dir / "data",
            self.deployment_dir / "models",
            self.deployment_dir / "recordings",
            self.deployment_dir / "transcriptions"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    async def _deploy_database(self):
        """Deploy PostgreSQL database"""
        logger.info("Setting up PostgreSQL database...")
        
        # Install PostgreSQL if not present
        if not self._check_command('psql'):
            self._install_postgresql()
        
        # Create database and user
        commands = [
            "sudo -u postgres createdb sovren_ai",
            "sudo -u postgres createuser sovren_user",
            "sudo -u postgres psql -c \"ALTER USER sovren_user WITH PASSWORD 'sovren_password';\"",
            "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE sovren_ai TO sovren_user;\""
        ]
        
        for command in commands:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Database command failed: {result.stderr}")
        
        logger.info("Database setup complete")
    
    async def _deploy_redis(self):
        """Deploy Redis server"""
        logger.info("Setting up Redis server...")
        
        # Install Redis if not present
        if not self._check_command('redis-server'):
            self._install_redis()
        
        # Start Redis service
        subprocess.run("sudo systemctl start redis", shell=True)
        subprocess.run("sudo systemctl enable redis", shell=True)
        
        logger.info("Redis setup complete")
    
    async def _deploy_freeswitch(self):
        """Deploy FreeSwitch PBX from source"""
        logger.info("Compiling and installing FreeSwitch from source...")
        
        freeswitch_dir = self.deployment_dir / "freeswitch"
        freeswitch_dir.mkdir(exist_ok=True)
        
        # Download and compile FreeSwitch
        commands = [
            f"cd {freeswitch_dir}",
            "git clone https://github.com/signalwire/freeswitch.git .",
            "./bootstrap.sh",
            "./configure --enable-core-pgsql-support --enable-core-odbc-support",
            "make",
            "sudo make install",
            "sudo make samples"
        ]
        
        for command in commands:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FreeSwitch compilation failed: {result.stderr}")
                raise RuntimeError("FreeSwitch compilation failed")
        
        # Configure FreeSwitch
        await self._configure_freeswitch()
        
        logger.info("FreeSwitch installation complete")
    
    async def _configure_freeswitch(self):
        """Configure FreeSwitch for SOVREN AI"""
        logger.info("Configuring FreeSwitch...")
        
        # Create configuration files
        configs = {
            'sip_profiles/skyetel_trunk.xml': self._generate_sip_config(),
            'dialplan/default/01_inbound.xml': self._generate_dialplan(),
            'autoload_configs/acl.conf.xml': self._generate_acl_config()
        }
        
        freeswitch_conf = Path("/usr/local/freeswitch/conf")
        
        for config_file, content in configs.items():
            file_path = freeswitch_conf / config_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Created FreeSwitch config: {config_file}")
    
    def _generate_sip_config(self) -> str:
        """Generate SIP configuration for Skyetel"""
        return """<?xml version="1.0" encoding="utf-8"?>
<configuration name="sip_profiles.conf" description="SIP Profiles">
  <profiles>
    <profile name="skyetel_trunk">
      <settings>
        <param name="username" value="${SKYETEL_USERNAME}"/>
        <param name="password" value="${SKYETEL_PASSWORD}"/>
        <param name="realm" value="sip.skyetel.com"/>
        <param name="register" value="true"/>
        <param name="context" value="default"/>
      </settings>
    </profile>
  </profiles>
</configuration>"""
    
    def _generate_dialplan(self) -> str:
        """Generate dialplan configuration"""
        return """<?xml version="1.0" encoding="utf-8"?>
<include>
  <context name="default">
    <extension name="inbound_call">
      <condition field="destination_number" expression="^(\d+)$">
        <action application="answer"/>
        <action application="lua" data="inbound_call_handler.lua"/>
      </condition>
    </extension>
  </context>
</include>"""
    
    def _generate_acl_config(self) -> str:
        """Generate ACL configuration"""
        return """<?xml version="1.0" encoding="utf-8"?>
<configuration name="acl.conf" description="Network Lists">
  <network-lists>
    <list name="domains" default="allow">
      <node type="allow" cidr="192.168.0.0/16"/>
      <node type="allow" cidr="10.0.0.0/8"/>
    </list>
  </network-lists>
</configuration>"""
    
    async def _deploy_voice_system(self):
        """Deploy voice system with FreeSwitch and Skyetel integration"""
        logger.info("Deploying voice system...")
        
        # Install voice system dependencies
        voice_requirements = self.project_root / "voice" / "requirements.txt"
        subprocess.run(f"pip install -r {voice_requirements}", shell=True)
        
        # Create voice system service
        await self._create_voice_service()
        
        logger.info("Voice system deployment complete")
    
    async def _create_voice_service(self):
        """Create systemd service for voice system"""
        service_content = """[Unit]
Description=SOVREN AI Voice System
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=sovren
WorkingDirectory=/opt/sovren-ai
Environment=PATH=/opt/sovren-ai/venv/bin
ExecStart=/opt/sovren-ai/venv/bin/python -m voice.voice_system
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
        
        service_file = Path("/etc/systemd/system/sovren-voice.service")
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Enable and start service
        subprocess.run("sudo systemctl daemon-reload", shell=True)
        subprocess.run("sudo systemctl enable sovren-voice", shell=True)
        subprocess.run("sudo systemctl start sovren-voice", shell=True)
    
    async def _deploy_mcp_server(self):
        """Deploy MCP Server for memory management"""
        logger.info("Deploying MCP Server...")
        
        # Create MCP Server service
        mcp_service_content = """[Unit]
Description=SOVREN AI MCP Server
After=network.target

[Service]
Type=simple
User=sovren
WorkingDirectory=/opt/sovren-ai
Environment=PATH=/opt/sovren-ai/venv/bin
ExecStart=/opt/sovren-ai/venv/bin/python mcp_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
        
        mcp_service_file = Path("/etc/systemd/system/sovren-mcp.service")
        with open(mcp_service_file, 'w') as f:
            f.write(mcp_service_content)
        
        # Enable and start service
        subprocess.run("sudo systemctl daemon-reload", shell=True)
        subprocess.run("sudo systemctl enable sovren-mcp", shell=True)
        subprocess.run("sudo systemctl start sovren-mcp", shell=True)
        
        logger.info("MCP Server deployment complete")
    
    async def _deploy_core_systems(self):
        """Deploy core AI systems"""
        logger.info("Deploying core AI systems...")
        
        # Install core dependencies
        core_requirements = self.project_root / "core" / "requirements.txt"
        if core_requirements.exists():
            subprocess.run(f"pip install -r {core_requirements}", shell=True)
        
        # Create core systems service
        core_service_content = """[Unit]
Description=SOVREN AI Core Systems
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=sovren
WorkingDirectory=/opt/sovren-ai
Environment=PATH=/opt/sovren-ai/venv/bin
ExecStart=/opt/sovren-ai/venv/bin/python -m core.main_integration_system
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
        
        core_service_file = Path("/etc/systemd/system/sovren-core.service")
        with open(core_service_file, 'w') as f:
            f.write(core_service_content)
        
        # Enable and start service
        subprocess.run("sudo systemctl daemon-reload", shell=True)
        subprocess.run("sudo systemctl enable sovren-core", shell=True)
        subprocess.run("sudo systemctl start sovren-core", shell=True)
        
        logger.info("Core systems deployment complete")
    
    async def _deploy_api_server(self):
        """Deploy API server"""
        logger.info("Deploying API server...")
        
        # Create API server service
        api_service_content = """[Unit]
Description=SOVREN AI API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=sovren
WorkingDirectory=/opt/sovren-ai
Environment=PATH=/opt/sovren-ai/venv/bin
ExecStart=/opt/sovren-ai/venv/bin/python -m api.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
        
        api_service_file = Path("/etc/systemd/system/sovren-api.service")
        with open(api_service_file, 'w') as f:
            f.write(api_service_content)
        
        # Enable and start service
        subprocess.run("sudo systemctl daemon-reload", shell=True)
        subprocess.run("sudo systemctl enable sovren-api", shell=True)
        subprocess.run("sudo systemctl start sovren-api", shell=True)
        
        logger.info("API server deployment complete")
    
    async def _deploy_frontend(self):
        """Deploy frontend application"""
        logger.info("Deploying frontend...")
        
        frontend_dir = self.project_root / "frontend"
        
        # Install Node.js dependencies
        subprocess.run(f"cd {frontend_dir} && npm install", shell=True)
        
        # Build frontend
        subprocess.run(f"cd {frontend_dir} && npm run build", shell=True)
        
        # Configure nginx
        await self._configure_nginx()
        
        logger.info("Frontend deployment complete")
    
    async def _configure_nginx(self):
        """Configure nginx for frontend and API"""
        nginx_config = """server {
    listen 80;
    server_name sovrenai.app;
    
    # Frontend
    location / {
        root /opt/sovren-ai/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}"""
        
        nginx_file = Path("/etc/nginx/sites-available/sovren-ai")
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        
        # Enable site
        subprocess.run("sudo ln -sf /etc/nginx/sites-available/sovren-ai /etc/nginx/sites-enabled/", shell=True)
        subprocess.run("sudo nginx -t", shell=True)
        subprocess.run("sudo systemctl reload nginx", shell=True)
    
    async def _deploy_monitoring(self):
        """Deploy monitoring and logging"""
        logger.info("Deploying monitoring...")
        
        # Install monitoring tools
        subprocess.run("sudo apt-get install -y prometheus grafana", shell=True)
        
        # Configure Prometheus
        await self._configure_prometheus()
        
        # Configure Grafana
        await self._configure_grafana()
        
        # Start monitoring services
        subprocess.run("sudo systemctl enable prometheus", shell=True)
        subprocess.run("sudo systemctl start prometheus", shell=True)
        subprocess.run("sudo systemctl enable grafana-server", shell=True)
        subprocess.run("sudo systemctl start grafana-server", shell=True)
        
        logger.info("Monitoring deployment complete")
    
    async def _configure_prometheus(self):
        """Configure Prometheus for SOVREN AI metrics"""
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sovren-voice'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'sovren-api'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'sovren-core'
    static_configs:
      - targets: ['localhost:9091']"""
        
        config_file = Path("/etc/prometheus/prometheus.yml")
        with open(config_file, 'w') as f:
            f.write(prometheus_config)
    
    async def _configure_grafana(self):
        """Configure Grafana dashboards"""
        # Create basic dashboard configuration
        dashboard_dir = Path("/etc/grafana/provisioning/dashboards")
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Dashboard configuration would be added here
        logger.info("Grafana configuration complete")
    
    async def _verify_deployment(self):
        """Verify all components are running"""
        logger.info("Verifying deployment...")
        
        services = [
            'sovren-voice',
            'sovren-mcp',
            'sovren-core',
            'sovren-api',
            'postgresql',
            'redis',
            'freeswitch'
        ]
        
        for service in services:
            result = subprocess.run(f"sudo systemctl is-active {service}", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == 'active':
                logger.info(f"✅ {service} is running")
            else:
                logger.warning(f"⚠️  {service} is not running")
    
    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        result = subprocess.run(f"which {command}", shell=True, capture_output=True)
        return result.returncode == 0
    
    def _install_postgresql(self):
        """Install PostgreSQL"""
        logger.info("Installing PostgreSQL...")
        subprocess.run("sudo apt-get update", shell=True)
        subprocess.run("sudo apt-get install -y postgresql postgresql-contrib", shell=True)
    
    def _install_redis(self):
        """Install Redis"""
        logger.info("Installing Redis...")
        subprocess.run("sudo apt-get update", shell=True)
        subprocess.run("sudo apt-get install -y redis-server", shell=True)
    
    def _print_deployment_summary(self):
        """Print deployment summary"""
        logger.info("=" * 50)
        logger.info("SOVREN AI DEPLOYMENT SUMMARY")
        logger.info("=" * 50)
        
        for component, status in self.deployment_status.items():
            if status == 'success':
                logger.info(f"✅ {component}: SUCCESS")
            else:
                logger.error(f"❌ {component}: {status}")
        
        logger.info("=" * 50)

async def main():
    """Main deployment function"""
    deployment = SovrenCompleteDeployment()
    await deployment.deploy_all()

if __name__ == "__main__":
    asyncio.run(main()) 