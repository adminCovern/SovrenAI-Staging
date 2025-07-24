#!/usr/bin/env python3
"""
SOVREN AI Security System Deployment Script
Production-ready deployment with health checks and monitoring
"""

import os
import sys
import time
import signal
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import json
import tempfile
import shutil

# Import security system directly
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.security.security_system import SecuritySystem, SecurityError, AuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SecurityDeployment')

class SecurityDeployment:
    """Production deployment manager for security system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.security_system: Optional[SecuritySystem] = None
        self.db_path: Optional[str] = None
        self.running = False
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        
        default_config = {
            'database_path': 'security.db',
            'log_level': 'INFO',
            'max_connections': 100,
            'cleanup_interval': 300,
            'backup_interval': 3600,
            'health_check_interval': 60
        }
        
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
                
        return default_config
        
    def setup_environment(self) -> bool:
        """Setup deployment environment"""
        
        try:
            # Create necessary directories
            os.makedirs('logs', exist_ok=True)
            os.makedirs('backups', exist_ok=True)
            os.makedirs('data', exist_ok=True)
            
            # Setup database path
            self.db_path = os.path.join('data', self.config['database_path'])
            
            # Verify dependencies
            self._check_dependencies()
            
            # Initialize security system
            self.security_system = SecuritySystem(self.db_path)
            
            logger.info("Environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            return False
            
    def _check_dependencies(self):
        """Check if all required dependencies are available"""
        
        required_packages = [
            'cryptography',
            'torch',
            'numpy',
            'scikit-learn',
            'sqlite3'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            raise SecurityError(f"Missing required packages: {missing_packages}")
            
        logger.info("All dependencies verified")
        
    def start(self) -> bool:
        """Start the security system"""
        
        try:
            if not self.setup_environment():
                return False
                
            # Perform health check
            if not self.health_check():
                logger.error("Health check failed")
                return False
                
            self.running = True
            logger.info("Security system started successfully")
            
            # Start monitoring
            self._start_monitoring()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start security system: {e}")
            return False
            
    def stop(self):
        """Stop the security system gracefully"""
        
        try:
            self.running = False
            
            if self.security_system:
                self.security_system.close()
                
            logger.info("Security system stopped gracefully")
            
        except Exception as e:
            logger.error(f"Error stopping security system: {e}")
            
    def health_check(self) -> bool:
        """Perform comprehensive health check"""
        
        try:
            if not self.security_system:
                return False
                
            # Test cryptographic operations
            test_data = b"health_check_test"
            encrypted, key_version = self.security_system.crypto_manager.encrypt_data(test_data)
            decrypted = self.security_system.crypto_manager.decrypt_data(encrypted, key_version)
            
            if decrypted != test_data:
                logger.error("Cryptographic health check failed")
                return False
                
            # Test token creation
            test_token = self.security_system.create_access_token(
                "health_check_user",
                {"read_own_data"}
            )
            
            if not test_token:
                logger.error("Token creation health check failed")
                return False
                
            # Test token validation
            validated_token = self.security_system.validate_token(test_token.token_id)
            
            if not validated_token:
                logger.error("Token validation health check failed")
                return False
                
            # Test access control
            permissions = self.security_system.access_control.get_user_permissions('user')
            if not permissions:
                logger.error("Access control health check failed")
                return False
                
            logger.info("Health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
            
    def _start_monitoring(self):
        """Start background monitoring"""
        
        import threading
        
        def monitor_worker():
            while self.running:
                try:
                    time.sleep(self.config['health_check_interval'])
                    
                    if not self.health_check():
                        logger.error("Health check failed during monitoring")
                        # In production, this might trigger alerts or restart
                        
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()
        
    def backup_database(self) -> bool:
        """Create database backup"""
        
        try:
            if not self.db_path or not os.path.exists(self.db_path):
                return False
                
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'security_backup_{timestamp}.db')
            
            # Ensure db_path is not None before copying
            if self.db_path is not None:
                shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
            
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
                
            # Stop the system
            self.stop()
            
            # Restore database
            if self.db_path and os.path.exists(self.db_path):
                os.remove(self.db_path)
                
            if self.db_path is not None:
                shutil.copy2(backup_path, self.db_path)
            else:
                logger.error("db_path is None, cannot restore database.")
                return False
            
            # Restart the system
            self.start()
            
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    if deployment:
        deployment.stop()
    sys.exit(0)

def main():
    """Main deployment function"""
    
    parser = argparse.ArgumentParser(description='SOVREN AI Security System Deployment')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--backup', action='store_true', help='Create database backup')
    parser.add_argument('--restore', help='Restore database from backup file')
    parser.add_argument('--health-check', action='store_true', help='Run health check only')
    
    args = parser.parse_args()
    
    global deployment
    deployment = SecurityDeployment(args.config)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.backup:
            if deployment.backup_database():
                logger.info("Backup completed successfully")
                return 0
            else:
                logger.error("Backup failed")
                return 1
                
        elif args.restore:
            if deployment.restore_database(args.restore):
                logger.info("Restore completed successfully")
                return 0
            else:
                logger.error("Restore failed")
                return 1
                
        elif args.health_check:
            if deployment.setup_environment() and deployment.health_check():
                logger.info("Health check passed")
                return 0
            else:
                logger.error("Health check failed")
                return 1
                
        else:
            # Normal deployment
            if deployment.start():
                logger.info("Security system deployed successfully")
                
                # Keep running
                try:
                    while deployment.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Received interrupt, shutting down...")
                    
                deployment.stop()
                return 0
            else:
                logger.error("Deployment failed")
                return 1
                
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return 1

if __name__ == '__main__':
    deployment = None
    sys.exit(main()) 