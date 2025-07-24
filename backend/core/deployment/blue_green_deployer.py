#!/usr/bin/env python3
"""
SOVREN AI - Blue-Green Deployment System
Zero-downtime deployment with automatic rollback and health validation
"""

import os
import sys
import time
import threading
import logging
import json
import subprocess
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import hashlib
from collections import defaultdict, deque

logger = logging.getLogger('BlueGreenDeployer')

class DeploymentState(Enum):
    """Deployment states"""
    IDLE = "idle"
    DEPLOYING = "deploying"
    VALIDATING = "validating"
    SWITCHING = "switching"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"

class Environment(Enum):
    """Deployment environments"""
    BLUE = "blue"
    GREEN = "green"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    service_name: str
    blue_port: int
    green_port: int
    health_check_endpoint: str
    health_check_timeout: float = 30.0
    validation_timeout: float = 300.0  # 5 minutes
    max_validation_attempts: int = 10
    rollback_threshold: float = 0.8  # 80% success rate
    traffic_switch_delay: float = 10.0  # seconds
    backup_enabled: bool = True
    auto_rollback_enabled: bool = True

@dataclass
class DeploymentInfo:
    """Deployment information"""
    deployment_id: str
    version: str
    timestamp: datetime
    environment: Environment
    state: DeploymentState
    health_score: float = 0.0
    validation_attempts: int = 0
    rollback_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BlueGreenDeployer:
    """Production-ready blue-green deployment system"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.current_environment = Environment.BLUE
        self.active_deployment: Optional[DeploymentInfo] = None
        self.deployment_history: List[DeploymentInfo] = []
        
        # Health monitoring
        self.health_scores = defaultdict(lambda: deque(maxlen=100))
        self.error_counts = defaultdict(int)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Deployment state
        self.deployment_state = DeploymentState.IDLE
        self.deployment_thread: Optional[threading.Thread] = None
        
        # Initialize environments
        self._init_environments()
        
        logger.info(f"Blue-green deployer initialized for {config.service_name}")
    
    def _init_environments(self):
        """Initialize blue and green environments"""
        try:
            # Create environment directories
            base_path = Path(f"/opt/sovren/{self.config.service_name}")
            
            for env in Environment:
                env_path = base_path / env.value
                env_path.mkdir(parents=True, exist_ok=True)
                
                # Create environment configuration
                config_file = env_path / "config.json"
                if not config_file.exists():
                    env_config = {
                        'environment': env.value,
                        'port': self.config.blue_port if env == Environment.BLUE else self.config.green_port,
                        'health_check_endpoint': self.config.health_check_endpoint,
                        'created_at': datetime.now().isoformat(),
                    }
                    with open(config_file, 'w') as f:
                        json.dump(env_config, f, indent=2)
            
            logger.info("Environment directories initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize environments: {e}")
    
    def deploy(self, version: str, deployment_package: str, 
              metadata: Optional[Dict[str, Any]] = None) -> str:
        """Deploy new version using blue-green strategy"""
        
        try:
            with self._lock:
                if self.deployment_state != DeploymentState.IDLE:
                    raise RuntimeError("Deployment already in progress")
                
                # Generate deployment ID
                deployment_id = f"deploy_{int(time.time())}_{hashlib.md5(version.encode()).hexdigest()[:8]}"
                
                # Create deployment info
                deployment = DeploymentInfo(
                    deployment_id=deployment_id,
                    version=version,
                    timestamp=datetime.now(),
                    environment=self._get_next_environment(),
                    state=DeploymentState.DEPLOYING,
                    metadata=metadata or {},
                )
                
                self.active_deployment = deployment
                self.deployment_state = DeploymentState.DEPLOYING
                
                # Start deployment in background thread
                self.deployment_thread = threading.Thread(
                    target=self._execute_deployment,
                    args=(deployment, deployment_package),
                    daemon=True
                )
                self.deployment_thread.start()
                
                logger.info(f"Started deployment {deployment_id} for version {version}")
                return deployment_id
                
        except Exception as e:
            logger.error(f"Failed to start deployment: {e}")
            raise
    
    def _execute_deployment(self, deployment: DeploymentInfo, deployment_package: str):
        """Execute deployment in background thread"""
        
        try:
            # Step 1: Deploy to inactive environment
            logger.info(f"Deploying version {deployment.version} to {deployment.environment.value}")
            
            if not self._deploy_to_environment(deployment.environment, deployment_package):
                self._fail_deployment(deployment, "Deployment to environment failed")
                return
            
            # Step 2: Validate deployment
            logger.info("Validating deployment health")
            deployment.state = DeploymentState.VALIDATING
            
            if not self._validate_deployment(deployment):
                self._fail_deployment(deployment, "Health validation failed")
                return
            
            # Step 3: Switch traffic
            logger.info("Switching traffic to new environment")
            deployment.state = DeploymentState.SWITCHING
            
            if not self._switch_traffic(deployment.environment):
                self._fail_deployment(deployment, "Traffic switch failed")
                return
            
            # Step 4: Final validation
            logger.info("Performing final validation")
            if not self._final_validation(deployment):
                logger.warning("Final validation failed, initiating rollback")
                self._rollback_deployment(deployment, "Final validation failed")
                return
            
            # Step 5: Complete deployment
            self._complete_deployment(deployment)
            
        except Exception as e:
            logger.error(f"Deployment execution failed: {e}")
            self._fail_deployment(deployment, str(e))
    
    def _deploy_to_environment(self, environment: Environment, deployment_package: str) -> bool:
        """Deploy package to specified environment"""
        
        try:
            env_path = Path(f"/opt/sovren/{self.config.service_name}/{environment.value}")
            
            # Create backup if enabled
            if self.config.backup_enabled:
                self._create_backup(environment)
            
            # Extract deployment package
            if deployment_package.endswith('.tar.gz'):
                subprocess.run([
                    'tar', '-xzf', deployment_package, '-C', str(env_path)
                ], check=True)
            elif deployment_package.endswith('.zip'):
                subprocess.run([
                    'unzip', '-o', deployment_package, '-d', str(env_path)
                ], check=True)
            else:
                # Copy files directly
                shutil.copytree(deployment_package, env_path, dirs_exist_ok=True)
            
            # Update environment configuration
            config_file = env_path / "config.json"
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config['version'] = deployment_package
            config['deployed_at'] = datetime.now().isoformat()
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Start service
            if not self._start_service(environment):
                return False
            
            logger.info(f"Successfully deployed to {environment.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy to {environment.value}: {e}")
            return False
    
    def _create_backup(self, environment: Environment):
        """Create backup of current environment"""
        
        try:
            env_path = Path(f"/opt/sovren/{self.config.service_name}/{environment.value}")
            backup_path = Path(f"/opt/sovren/{self.config.service_name}/backups/{environment.value}_{int(time.time())}")
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(env_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    def _start_service(self, environment: Environment) -> bool:
        """Start service in specified environment"""
        
        try:
            env_path = Path(f"/opt/sovren/{self.config.service_name}/{environment.value}")
            port = self.config.blue_port if environment == Environment.BLUE else self.config.green_port
            
            # Start service process
            service_script = env_path / "start.sh"
            if service_script.exists():
                subprocess.run([
                    'bash', str(service_script), '--port', str(port)
                ], check=True, cwd=str(env_path))
            else:
                # Default service start
                subprocess.run([
                    'python', '-m', 'uvicorn', 'main:app',
                    '--host', '0.0.0.0', '--port', str(port)
                ], check=True, cwd=str(env_path))
            
            # Wait for service to start
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service in {environment.value}: {e}")
            return False
    
    def _validate_deployment(self, deployment: DeploymentInfo) -> bool:
        """Validate deployment health"""
        
        environment = deployment.environment
        port = self.config.blue_port if environment == Environment.BLUE else self.config.green_port
        
        for attempt in range(self.config.max_validation_attempts):
            try:
                # Perform health check
                health_score = self._perform_health_check(port)
                deployment.health_score = health_score
                deployment.validation_attempts = attempt + 1
                
                if health_score >= self.config.rollback_threshold:
                    logger.info(f"Health validation passed: {health_score:.2f}")
                    return True
                else:
                    logger.warning(f"Health validation attempt {attempt + 1}: {health_score:.2f}")
                    time.sleep(self.config.validation_timeout / self.config.max_validation_attempts)
                    
            except Exception as e:
                logger.error(f"Health validation attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.validation_timeout / self.config.max_validation_attempts)
        
        return False
    
    def _perform_health_check(self, port: int) -> float:
        """Perform health check on service"""
        
        try:
            url = f"http://localhost:{port}{self.config.health_check_endpoint}"
            response = requests.get(url, timeout=self.config.health_check_timeout)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Calculate health score based on multiple factors
                score = 0.0
                
                # Basic health status
                if health_data.get('status') == 'healthy':
                    score += 0.4
                
                # Performance metrics
                if 'response_time_ms' in health_data:
                    response_time = health_data['response_time_ms']
                    if response_time < 100:
                        score += 0.3
                    elif response_time < 500:
                        score += 0.2
                    elif response_time < 1000:
                        score += 0.1
                
                # Error rate
                if 'error_rate' in health_data:
                    error_rate = health_data['error_rate']
                    if error_rate < 0.01:  # 1%
                        score += 0.3
                    elif error_rate < 0.05:  # 5%
                        score += 0.2
                    elif error_rate < 0.1:  # 10%
                        score += 0.1
                
                return min(score, 1.0)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return 0.0
    
    def _switch_traffic(self, target_environment: Environment) -> bool:
        """Switch traffic to target environment"""
        
        try:
            # Update load balancer configuration
            if not self._update_load_balancer(target_environment):
                return False
            
            # Wait for traffic switch to propagate
            time.sleep(self.config.traffic_switch_delay)
            
            # Verify traffic is flowing to new environment
            if not self._verify_traffic_switch(target_environment):
                return False
            
            # Update current environment
            self.current_environment = target_environment
            
            logger.info(f"Successfully switched traffic to {target_environment.value}")
            return True
            
        except Exception as e:
            logger.error(f"Traffic switch failed: {e}")
            return False
    
    def _update_load_balancer(self, target_environment: Environment) -> bool:
        """Update load balancer configuration"""
        
        try:
            # This would update nginx, haproxy, or cloud load balancer
            # For now, using a simple file-based approach
            
            lb_config_path = Path("/etc/nginx/sites-available/sovren")
            if lb_config_path.exists():
                # Update nginx configuration
                port = self.config.blue_port if target_environment == Environment.BLUE else self.config.green_port
                
                config_content = f"""
server {{
    listen 80;
    server_name sovren.example.com;
    
    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""
                with open(lb_config_path, 'w') as f:
                    f.write(config_content)
                
                # Reload nginx
                subprocess.run(['nginx', '-s', 'reload'], check=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update load balancer: {e}")
            return False
    
    def _verify_traffic_switch(self, target_environment: Environment) -> bool:
        """Verify traffic is flowing to target environment"""
        
        try:
            # Check if requests are reaching the target environment
            port = self.config.blue_port if target_environment == Environment.BLUE else self.config.green_port
            
            # Send test request
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            
            if response.status_code == 200:
                # Check if response indicates correct environment
                health_data = response.json()
                if health_data.get('environment') == target_environment.value:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Traffic switch verification failed: {e}")
            return False
    
    def _final_validation(self, deployment: DeploymentInfo) -> bool:
        """Perform final validation after traffic switch"""
        
        try:
            # Perform comprehensive health check
            health_score = self._perform_health_check(
                self.config.blue_port if self.current_environment == Environment.BLUE else self.config.green_port
            )
            
            deployment.health_score = health_score
            
            if health_score >= self.config.rollback_threshold:
                logger.info(f"Final validation passed: {health_score:.2f}")
                return True
            else:
                logger.warning(f"Final validation failed: {health_score:.2f}")
                return False
                
        except Exception as e:
            logger.error(f"Final validation failed: {e}")
            return False
    
    def _complete_deployment(self, deployment: DeploymentInfo):
        """Complete successful deployment"""
        
        try:
            deployment.state = DeploymentState.COMPLETED
            
            # Add to deployment history
            with self._lock:
                self.deployment_history.append(deployment)
                self.active_deployment = None
                self.deployment_state = DeploymentState.IDLE
            
            # Clean up old deployments
            self._cleanup_old_deployments()
            
            logger.info(f"Deployment {deployment.deployment_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to complete deployment: {e}")
    
    def _fail_deployment(self, deployment: DeploymentInfo, reason: str):
        """Handle deployment failure"""
        
        try:
            deployment.state = DeploymentState.FAILED
            deployment.rollback_reason = reason
            
            # Add to deployment history
            with self._lock:
                self.deployment_history.append(deployment)
                self.active_deployment = None
                self.deployment_state = DeploymentState.IDLE
            
            logger.error(f"Deployment {deployment.deployment_id} failed: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to handle deployment failure: {e}")
    
    def _rollback_deployment(self, deployment: DeploymentInfo, reason: str):
        """Rollback deployment to previous version"""
        
        try:
            deployment.state = DeploymentState.ROLLING_BACK
            
            logger.info(f"Rolling back deployment {deployment.deployment_id}: {reason}")
            
            # Switch traffic back to previous environment
            previous_environment = Environment.GREEN if deployment.environment == Environment.BLUE else Environment.BLUE
            
            if self._switch_traffic(previous_environment):
                deployment.state = DeploymentState.FAILED
                deployment.rollback_reason = f"Rolled back: {reason}"
                
                with self._lock:
                    self.deployment_history.append(deployment)
                    self.active_deployment = None
                    self.deployment_state = DeploymentState.IDLE
                
                logger.info(f"Rollback completed for deployment {deployment.deployment_id}")
            else:
                logger.error(f"Rollback failed for deployment {deployment.deployment_id}")
                
        except Exception as e:
            logger.error(f"Failed to rollback deployment: {e}")
    
    def _get_next_environment(self) -> Environment:
        """Get next environment for deployment"""
        return Environment.GREEN if self.current_environment == Environment.BLUE else Environment.BLUE
    
    def _cleanup_old_deployments(self):
        """Clean up old deployment artifacts"""
        
        try:
            # Keep only last 5 deployments
            if len(self.deployment_history) > 5:
                old_deployments = self.deployment_history[:-5]
                
                for deployment in old_deployments:
                    env_path = Path(f"/opt/sovren/{self.config.service_name}/{deployment.environment.value}")
                    
                    # Remove old deployment files
                    if env_path.exists():
                        shutil.rmtree(env_path)
                        env_path.mkdir()
                
                logger.info(f"Cleaned up {len(old_deployments)} old deployments")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old deployments: {e}")
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        
        with self._lock:
            # Check active deployment
            if self.active_deployment and self.active_deployment.deployment_id == deployment_id:
                deployment = self.active_deployment
            else:
                # Check deployment history
                deployment = next(
                    (d for d in self.deployment_history if d.deployment_id == deployment_id),
                    None
                )
            
            if not deployment:
                return None
            
            return {
                'deployment_id': deployment.deployment_id,
                'version': deployment.version,
                'environment': deployment.environment.value,
                'state': deployment.state.value,
                'timestamp': deployment.timestamp.isoformat(),
                'health_score': deployment.health_score,
                'validation_attempts': deployment.validation_attempts,
                'rollback_reason': deployment.rollback_reason,
                'metadata': deployment.metadata,
            }
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        
        with self._lock:
            return {
                'current_environment': self.current_environment.value,
                'deployment_state': self.deployment_state.value,
                'active_deployment': self.active_deployment.deployment_id if self.active_deployment else None,
                'total_deployments': len(self.deployment_history),
                'successful_deployments': len([d for d in self.deployment_history if d.state == DeploymentState.COMPLETED]),
                'failed_deployments': len([d for d in self.deployment_history if d.state == DeploymentState.FAILED]),
            }
    
    def force_rollback(self, reason: str = "Manual rollback"):
        """Force rollback of current deployment"""
        
        with self._lock:
            if self.active_deployment:
                self._rollback_deployment(self.active_deployment, reason)
            else:
                logger.warning("No active deployment to rollback")
    
    def get_deployment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get deployment history"""
        
        with self._lock:
            recent_deployments = self.deployment_history[-limit:] if self.deployment_history else []
            
            return [
                {
                    'deployment_id': d.deployment_id,
                    'version': d.version,
                    'environment': d.environment.value,
                    'state': d.state.value,
                    'timestamp': d.timestamp.isoformat(),
                    'health_score': d.health_score,
                    'rollback_reason': d.rollback_reason,
                }
                for d in recent_deployments
            ] 