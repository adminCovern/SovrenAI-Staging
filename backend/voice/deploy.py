#!/usr/bin/env python3
"""
Production deployment script for SOVREN AI Voice System
Direct system deployment without containerization
"""

import os
import sys
import subprocess
import platform
import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceSystemDeployment:
    """Production deployment manager for Voice System"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("voice/config/production.json")
        self.system = platform.system().lower()
        self.architecture = platform.machine()
        self.python_version = sys.version_info
        
        # Deployment paths
        self.install_base = Path("/opt/sovren/voice")
        self.config_dir = Path("/etc/sovren/voice")
        self.log_dir = Path("/var/log/sovren/voice")
        self.data_dir = Path("/var/lib/sovren/voice")
        self.model_dir = Path("/var/lib/sovren/models")
        
        # Service configuration
        self.service_name = "sovren-voice"
        self.service_user = "sovren"
        self.service_group = "sovren"
        
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        logger.info("Checking prerequisites...")
        
        # Check Python version
        if self.python_version < (3, 10):
            logger.error(f"Python 3.10+ required, found {self.python_version}")
            return False
            
        # Check OS
        if self.system not in ['linux', 'darwin']:
            logger.warning(f"Untested OS: {self.system}")
            
        # Check required system packages
        required_packages = {
            'linux': ['ffmpeg', 'portaudio19-dev', 'libsndfile1'],
            'darwin': ['ffmpeg', 'portaudio'],
        }
        
        if self.system in required_packages:
            missing = []
            for pkg in required_packages[self.system]:
                if not self._check_system_package(pkg):
                    missing.append(pkg)
                    
            if missing:
                logger.error(f"Missing system packages: {missing}")
                logger.info(f"Install with: {self._get_install_command(missing)}")
                return False
                
        # Check for required directories
        if not os.access("/opt", os.W_OK):
            logger.error("No write access to /opt directory")
            return False
            
        return True
        
    def _check_system_package(self, package: str) -> bool:
        """Check if system package is installed"""
        check_commands = {
            'linux': ['dpkg', '-l', package],
            'darwin': ['brew', 'list', package],
        }
        
        if self.system in check_commands:
            try:
                result = subprocess.run(
                    check_commands[self.system],
                    capture_output=True,
                    check=False
                )
                return result.returncode == 0
            except FileNotFoundError:
                return False
                
        return False
        
    def _get_install_command(self, packages: List[str]) -> str:
        """Get system package install command"""
        commands = {
            'linux': f"sudo apt-get install -y {' '.join(packages)}",
            'darwin': f"brew install {' '.join(packages)}",
        }
        return commands.get(self.system, "Unknown package manager")
        
    def create_directories(self):
        """Create required directories with proper permissions"""
        logger.info("Creating directories...")
        
        directories = [
            self.install_base,
            self.config_dir,
            self.log_dir,
            self.data_dir,
            self.model_dir,
            self.data_dir / "sessions",
            self.data_dir / "recordings",
            self.model_dir / "whisper",
            self.model_dir / "tts",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created {directory}")
            
            # Set permissions
            if self.system == 'linux':
                os.chown(directory, self._get_uid(), self._get_gid())
                
    def _get_uid(self) -> int:
        """Get user ID for service user"""
        try:
            import pwd
            return pwd.getpwnam(self.service_user).pw_uid
        except:
            return os.getuid()
            
    def _get_gid(self) -> int:
        """Get group ID for service group"""
        try:
            import grp
            return grp.getgrnam(self.service_group).gr_gid
        except:
            return os.getgid()
            
    def install_python_packages(self):
        """Install Python packages from requirements.txt"""
        logger.info("Installing Python packages...")
        
        requirements_file = Path("voice/requirements.txt")
        if not requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
            
        # Install packages system-wide
        cmd = [
            sys.executable, "-m", "pip", "install",
            "--upgrade", "-r", str(requirements_file)
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            logger.error("Failed to install Python packages")
            return False
            
        return True
        
    def install_application(self):
        """Install application files"""
        logger.info("Installing application...")
        
        # Copy application files
        source_dir = Path("voice")
        if not source_dir.exists():
            logger.error("Source directory 'voice' not found")
            return False
            
        # Clear existing installation
        if self.install_base.exists():
            shutil.rmtree(self.install_base)
            
        # Copy files
        shutil.copytree(source_dir, self.install_base)
        logger.info(f"Copied application to {self.install_base}")
        
        # Set permissions
        if self.system == 'linux':
            for root, dirs, files in os.walk(self.install_base):
                for d in dirs:
                    os.chown(os.path.join(root, d), self._get_uid(), self._get_gid())
                for f in files:
                    os.chown(os.path.join(root, f), self._get_uid(), self._get_gid())
                    
        return True
        
    def create_configuration(self):
        """Create production configuration"""
        logger.info("Creating configuration...")
        
        config = {
            "voice_system": {
                "sample_rate": 16000,
                "chunk_size": 1024,
                "channels": 1,
                "whisper_model_path": str(self.model_dir / "whisper" / "ggml-large-v3.bin"),
                "styletts2_model_path": str(self.model_dir / "tts"),
                "database_url": f"sqlite:///{self.data_dir}/voice.db",
                "redis_url": "redis://localhost:6379/0",
                "log_level": "INFO",
                "metrics_port": 9090,
                "websocket_port": 8765,
                "max_concurrent_sessions": 100,
                "max_concurrent_calls": 50,
            },
            "skyetel": {
                "base_url": "https://api.skyetel.com",
                "webhook_base_url": "https://your-domain.com/api/voice/webhook",
            },
            "security": {
                "enable_auth": True,
                "api_key_header": "X-API-Key",
                "allowed_origins": ["https://your-domain.com"],
            },
            "monitoring": {
                "enable_metrics": True,
                "enable_health_check": True,
                "health_check_interval": 30,
            }
        }
        
        # Write configuration
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Configuration written to {config_file}")
        
        # Create environment file
        env_file = self.config_dir / "environment"
        with open(env_file, 'w') as f:
            f.write(f"""# SOVREN Voice System Environment
LOG_DIR={self.log_dir}
DATA_DIR={self.data_dir}
MODEL_DIR={self.model_dir}
CONFIG_FILE={config_file}
PYTHONPATH={self.install_base}
LOG_LEVEL=INFO
ENV=production
""")
        
        logger.info(f"Environment file written to {env_file}")
        return True
        
    def create_systemd_service(self):
        """Create systemd service for Linux"""
        if self.system != 'linux':
            logger.info("Skipping systemd service (not Linux)")
            return True
            
        logger.info("Creating systemd service...")
        
        service_content = f"""[Unit]
Description=SOVREN AI Voice System
Documentation=https://sovrenai.com/docs/voice
After=network.target redis.service postgresql.service
Wants=redis.service

[Service]
Type=notify
ExecStart={sys.executable} -m voice.voice_system
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
Restart=on-failure
RestartSec=30
TimeoutStartSec=300
TimeoutStopSec=30

# User and permissions
User={self.service_user}
Group={self.service_group}
UMask=0027

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={self.log_dir} {self.data_dir}
ReadOnlyPaths={self.install_base} {self.config_dir} {self.model_dir}

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096
MemoryLimit=4G
CPUQuota=200%

# Environment
EnvironmentFile={self.config_dir}/environment
WorkingDirectory={self.install_base}

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sovren-voice

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path(f"/etc/systemd/system/{self.service_name}.service")
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
                
            # Reload systemd
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            logger.info(f"Systemd service created: {service_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create systemd service: {e}")
            return False
            
    def create_startup_script(self):
        """Create startup script for non-systemd systems"""
        logger.info("Creating startup script...")
        
        script_content = f"""#!/bin/bash
# SOVREN Voice System Startup Script

# Load environment
source {self.config_dir}/environment

# Change to application directory
cd {self.install_base}

# Start the voice system
exec {sys.executable} -m voice.voice_system
"""
        
        script_file = self.install_base / "start.sh"
        with open(script_file, 'w') as f:
            f.write(script_content)
            
        # Make executable
        os.chmod(script_file, 0o755)
        logger.info(f"Startup script created: {script_file}")
        
        return True
        
    def download_models(self):
        """Download required models"""
        logger.info("Downloading models...")
        
        # Download models from configured sources
        
        whisper_model = self.model_dir / "whisper" / "ggml-large-v3.bin"
        if not whisper_model.exists():
            logger.warning("Whisper model not found - please download manually")
            logger.info(f"Download to: {whisper_model}")
            
        tts_model = self.model_dir / "tts" / "model.pt"
        if not tts_model.exists():
            logger.warning("TTS model not found - please download manually")
            logger.info(f"Download to: {tts_model}")
            
        return True
        
    def setup_monitoring(self):
        """Setup monitoring and alerting"""
        logger.info("Setting up monitoring...")
        
        # Create Prometheus configuration
        prometheus_config = f"""
# SOVREN Voice System Prometheus Alerts
groups:
  - name: voice_system
    interval: 30s
    rules:
      - alert: VoiceSystemDown
        expr: up{{job="sovren-voice"}} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Voice System is down"
          
      - alert: HighErrorRate
        expr: rate(voice_system_errors_total[5m]) > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes{{job="sovren-voice"}} > 3e9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
"""
        
        alerts_file = self.config_dir / "prometheus_alerts.yml"
        with open(alerts_file, 'w') as f:
            f.write(prometheus_config)
            
        logger.info(f"Prometheus alerts configured: {alerts_file}")
        return True
        
    def post_install_check(self):
        """Verify installation"""
        logger.info("Running post-installation checks...")
        
        checks = [
            (self.install_base.exists(), "Installation directory exists"),
            (self.config_dir.exists(), "Configuration directory exists"),
            (self.log_dir.exists(), "Log directory exists"),
            (self.data_dir.exists(), "Data directory exists"),
            ((self.config_dir / "config.json").exists(), "Configuration file exists"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                logger.info(f"✓ {description}")
            else:
                logger.error(f"✗ {description}")
                all_passed = False
                
        return all_passed
        
    def deploy(self):
        """Run full deployment"""
        logger.info("Starting SOVREN Voice System deployment...")
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Creating directories", self.create_directories),
            ("Installing Python packages", self.install_python_packages),
            ("Installing application", self.install_application),
            ("Creating configuration", self.create_configuration),
            ("Creating service", self.create_systemd_service),
            ("Creating startup script", self.create_startup_script),
            ("Setting up monitoring", self.setup_monitoring),
            ("Downloading models", self.download_models),
            ("Running post-install checks", self.post_install_check),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n=== {step_name} ===")
            try:
                result = step_func()
                if result is False:
                    logger.error(f"Step failed: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"Step failed with exception: {e}")
                return False
                
        logger.info("\n=== Deployment completed successfully! ===")
        logger.info(f"\nTo start the service:")
        if self.system == 'linux':
            logger.info(f"  sudo systemctl start {self.service_name}")
            logger.info(f"  sudo systemctl enable {self.service_name}")
        else:
            logger.info(f"  {self.install_base}/start.sh")
            
        logger.info(f"\nTo view logs:")
        logger.info(f"  tail -f {self.log_dir}/voice.log")
        
        return True


def main():
    """Main deployment entry point"""
    parser = argparse.ArgumentParser(
        description="Deploy SOVREN Voice System to production"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to deployment configuration file"
    )
    parser.add_argument(
        "--skip-packages",
        action="store_true",
        help="Skip Python package installation"
    )
    parser.add_argument(
        "--user",
        default="sovren",
        help="System user for the service"
    )
    parser.add_argument(
        "--group",
        default="sovren",
        help="System group for the service"
    )
    
    args = parser.parse_args()
    
    # Check if running as root (recommended for system installation)
    if os.geteuid() != 0 and platform.system() == 'Linux':
        logger.warning("Not running as root - some operations may fail")
        logger.info("Consider running with sudo for system-wide installation")
        
    # Create deployment instance
    deployment = VoiceSystemDeployment(args.config)
    
    if args.user:
        deployment.service_user = args.user
    if args.group:
        deployment.service_group = args.group
        
    # Run deployment
    success = deployment.deploy()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 