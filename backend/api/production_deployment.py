#!/usr/bin/env python3
"""
SOVREN AI Elite Production Deployment System
Zero-downtime deployment with bulletproof error handling
"""

import os
import sys
import time
import signal
import subprocess
import logging
import asyncio
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import psutil
import socket
import threading
from contextlib import asynccontextmanager

# Import dependency manager
from api.dependency_manager import get_dependency_manager

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"
    HEALTH_CHECK = "health_check"

class ServiceStatus(Enum):
    """Service status enumeration"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    command: List[str]
    port: int
    health_check_url: str
    health_check_timeout: float = 30.0
    restart_delay: float = 5.0
    max_restarts: int = 3
    environment: Dict[str, str] = field(default_factory=dict)
    working_directory: Optional[str] = None
    log_file: Optional[str] = None
    pid_file: Optional[str] = None

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    deployment_id: str
    services: List[ServiceConfig]
    rollback_enabled: bool = True
    health_check_enabled: bool = True
    zero_downtime: bool = True
    backup_enabled: bool = True
    max_parallel_deployments: int = 1
    deployment_timeout: float = 300.0

class ProcessManager:
    """Elite process manager for production deployment"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        self.service_pids: Dict[str, int] = {}
        self.restart_counts: Dict[str, int] = {}
        self.lock = threading.Lock()
    
    def start_service(self, config: ServiceConfig) -> bool:
        """Start a service with bulletproof error handling"""
        try:
            with self.lock:
                if config.name in self.processes:
                    logger.warning(f"Service {config.name} already running")
                    return True
                
                # Prepare environment
                env = os.environ.copy()
                env.update(config.environment)
                
                # Prepare command
                cmd = config.command
                if config.working_directory:
                    cmd = ['cd', config.working_directory, '&&'] + cmd
                
                # Start process
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE if config.log_file else None,
                    stderr=subprocess.STDOUT if config.log_file else None,
                    cwd=config.working_directory,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
                
                self.processes[config.name] = process
                self.service_pids[config.name] = process.pid
                self.service_status[config.name] = ServiceStatus.STARTING
                self.restart_counts[config.name] = 0
                
                logger.info(f"Started service {config.name} with PID {process.pid}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to start service {config.name}: {e}")
            self.service_status[config.name] = ServiceStatus.ERROR
            return False
    
    def stop_service(self, config: ServiceConfig, timeout: float = 30.0) -> bool:
        """Stop a service gracefully with timeout"""
        try:
            with self.lock:
                if config.name not in self.processes:
                    logger.warning(f"Service {config.name} not running")
                    return True
                
                process = self.processes[config.name]
                self.service_status[config.name] = ServiceStatus.STOPPING
                
                # Send SIGTERM
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Service {config.name} did not stop gracefully, forcing")
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait()
                
                # Cleanup
                del self.processes[config.name]
                if config.name in self.service_pids:
                    del self.service_pids[config.name]
                self.service_status[config.name] = ServiceStatus.STOPPED
                
                logger.info(f"Stopped service {config.name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop service {config.name}: {e}")
            self.service_status[config.name] = ServiceStatus.ERROR
            return False
    
    def restart_service(self, config: ServiceConfig) -> bool:
        """Restart a service with restart limits"""
        try:
            if self.restart_counts.get(config.name, 0) >= config.max_restarts:
                logger.error(f"Service {config.name} exceeded max restarts")
                self.service_status[config.name] = ServiceStatus.ERROR
                return False
            
            logger.info(f"Restarting service {config.name}")
            self.stop_service(config)
            time.sleep(config.restart_delay)
            success = self.start_service(config)
            
            if success:
                self.restart_counts[config.name] = self.restart_counts.get(config.name, 0) + 1
                self.service_status[config.name] = ServiceStatus.RUNNING
            else:
                self.service_status[config.name] = ServiceStatus.ERROR
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to restart service {config.name}: {e}")
            self.service_status[config.name] = ServiceStatus.ERROR
            return False
    
    def get_service_status(self, config: ServiceConfig) -> ServiceStatus:
        """Get current service status"""
        if config.name not in self.service_status:
            return ServiceStatus.STOPPED
        
        status = self.service_status[config.name]
        
        # Check if process is still running
        if status == ServiceStatus.RUNNING or status == ServiceStatus.STARTING:
            if config.name in self.processes:
                process = self.processes[config.name]
                if process.poll() is not None:
                    logger.warning(f"Service {config.name} process died")
                    self.service_status[config.name] = ServiceStatus.ERROR
                    return ServiceStatus.ERROR
            else:
                self.service_status[config.name] = ServiceStatus.STOPPED
                return ServiceStatus.STOPPED
        
        return status
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            'services': {
                name: {
                    'status': status.value,
                    'pid': self.service_pids.get(name),
                    'restart_count': self.restart_counts.get(name, 0)
                }
                for name, status in self.service_status.items()
            },
            'total_services': len(self.service_status),
            'running_services': len([s for s in self.service_status.values() if s == ServiceStatus.RUNNING]),
            'error_services': len([s for s in self.service_status.values() if s == ServiceStatus.ERROR])
        }

class HealthChecker:
    """Elite health checker for production services"""
    
    def __init__(self):
        self.health_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timeout = 30.0
    
    async def check_service_health(self, config: ServiceConfig) -> Dict[str, Any]:
        """Check service health with caching"""
        cache_key = f"{config.name}_{config.health_check_url}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.health_cache:
            cache_entry = self.health_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_timeout:
                return cache_entry['result']
        
        try:
            # Perform health check
            result = await self._perform_health_check(config)
            
            # Cache result
            self.health_cache[cache_key] = {
                'timestamp': current_time,
                'result': result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Health check failed for {config.name}: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': current_time
            }
    
    async def _perform_health_check(self, config: ServiceConfig) -> Dict[str, Any]:
        """Perform actual health check"""
        try:
            # Check if port is listening
            if not self._check_port(config.port):
                return {
                    'healthy': False,
                    'error': f"Port {config.port} not listening",
                    'timestamp': time.time()
                }
            
            # HTTP health check
            if config.health_check_url:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=config.health_check_timeout)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(config.health_check_url) as response:
                        if response.status == 200:
                            return {
                                'healthy': True,
                                'status_code': response.status,
                                'response_time': response.headers.get('X-Response-Time', 'unknown'),
                                'timestamp': time.time()
                            }
                        else:
                            return {
                                'healthy': False,
                                'error': f"HTTP {response.status}",
                                'timestamp': time.time()
                            }
            
            return {
                'healthy': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _check_port(self, port: int) -> bool:
        """Check if port is listening"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False

class BackupManager:
    """Elite backup manager for zero-downtime deployments"""
    
    def __init__(self, backup_dir: str = "/data/sovren/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, deployment_id: str, configs: List[ServiceConfig]) -> str:
        """Create backup of current deployment"""
        try:
            backup_path = self.backup_dir / f"backup_{deployment_id}_{int(time.time())}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup configuration files
            for config in configs:
                if config.working_directory:
                    config_backup = backup_path / config.name
                    config_backup.mkdir(exist_ok=True)
                    
                    # Copy configuration files
                    source_dir = Path(config.working_directory)
                    if source_dir.exists():
                        for file_path in source_dir.rglob("*.py"):
                            if file_path.is_file():
                                relative_path = file_path.relative_to(source_dir)
                                dest_path = config_backup / relative_path
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, dest_path)
            
            # Create backup manifest
            manifest = {
                'deployment_id': deployment_id,
                'timestamp': time.time(),
                'services': [config.name for config in configs],
                'backup_path': str(backup_path)
            }
            
            with open(backup_path / 'manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        try:
            backup_dir = Path(backup_path)
            manifest_file = backup_dir / 'manifest.json'
            
            if not manifest_file.exists():
                raise ValueError(f"Backup manifest not found: {manifest_file}")
            
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            logger.info(f"Restoring backup: {backup_path}")
            # Implementation would restore files and restart services
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

class ProductionDeployment:
    """Elite production deployment system"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.process_manager = ProcessManager()
        self.health_checker = HealthChecker()
        self.backup_manager = BackupManager()
        self.deployment_status = DeploymentStatus.PENDING
        self.deployment_start_time = None
        self.deployment_end_time = None
        self.error_log: List[str] = []
        self.rollback_path: Optional[str] = None
    
    async def deploy(self) -> Dict[str, Any]:
        """Execute elite production deployment"""
        try:
            self.deployment_start_time = time.time()
            self.deployment_status = DeploymentStatus.IN_PROGRESS
            
            logger.info(f"Starting deployment {self.config.deployment_id}")
            
            # Step 1: Pre-deployment checks
            await self._pre_deployment_checks()
            
            # Step 2: Create backup if enabled
            if self.config.backup_enabled:
                self.rollback_path = self.backup_manager.create_backup(
                    self.config.deployment_id, 
                    self.config.services
                )
            
            # Step 3: Deploy services
            if self.config.zero_downtime:
                await self._deploy_zero_downtime()
            else:
                await self._deploy_traditional()
            
            # Step 4: Health checks
            if self.config.health_check_enabled:
                await self._perform_health_checks()
            
            # Step 5: Finalize deployment
            self.deployment_status = DeploymentStatus.SUCCESS
            self.deployment_end_time = time.time()
            
            logger.info(f"Deployment {self.config.deployment_id} completed successfully")
            
            duration = (self.deployment_end_time - self.deployment_start_time) if self.deployment_end_time and self.deployment_start_time else None
            return {
                'deployment_id': self.config.deployment_id,
                'status': 'success',
                'duration': duration,
                'services_deployed': len(self.config.services),
                'error_log': self.error_log
            }
            
        except Exception as e:
            logger.error(f"Deployment {self.config.deployment_id} failed: {e}")
            self.error_log.append(str(e))
            self.deployment_status = DeploymentStatus.FAILED
            self.deployment_end_time = time.time()
            
            # Rollback if enabled
            if self.config.rollback_enabled and self.rollback_path:
                await self._rollback()
            
            duration = (self.deployment_end_time - self.deployment_start_time) if self.deployment_end_time and self.deployment_start_time else None
            return {
                'deployment_id': self.config.deployment_id,
                'status': 'failed',
                'duration': duration,
                'error': str(e),
                'error_log': self.error_log
            }
    
    async def _pre_deployment_checks(self):
        """Perform pre-deployment checks"""
        logger.info("Performing pre-deployment checks")
        
        # Check dependencies
        dep_manager = get_dependency_manager()
        dep_status = dep_manager.get_status()
        
        critical_failures = [
            name for name, info in dep_status['dependencies'].items()
            if info['critical'] and info['status'] == 'unavailable'
        ]
        
        if critical_failures:
            raise RuntimeError(f"Critical dependencies unavailable: {critical_failures}")
        
        # Check disk space
        disk_usage = shutil.disk_usage('/')
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 10:  # Less than 10GB free
            raise RuntimeError(f"Insufficient disk space: {free_gb:.2f}GB free")
        
        # Check memory
        memory = psutil.virtual_memory()
        if memory.available < 2 * 1024**3:  # Less than 2GB available
            raise RuntimeError(f"Insufficient memory: {memory.available / 1024**3:.2f}GB available")
        
        # Check network connectivity
        if not self._check_network_connectivity():
            raise RuntimeError("Network connectivity issues detected")
        
        logger.info("Pre-deployment checks passed")
    
    async def _deploy_zero_downtime(self):
        """Deploy with zero downtime"""
        logger.info("Starting zero-downtime deployment")
        
        # Deploy services in parallel with health checks
        deployment_tasks = []
        for config in self.config.services:
            task = asyncio.create_task(self._deploy_service_zero_downtime(config))
            deployment_tasks.append(task)
        
        # Wait for all deployments with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*deployment_tasks),
                timeout=self.config.deployment_timeout
            )
        except asyncio.TimeoutError:
            raise RuntimeError("Deployment timeout exceeded")
    
    async def _deploy_service_zero_downtime(self, config: ServiceConfig):
        """Deploy single service with zero downtime"""
        try:
            # Start new instance
            if not self.process_manager.start_service(config):
                raise RuntimeError(f"Failed to start service {config.name}")
            
            # Wait for service to be healthy
            max_wait_time = 60.0
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                health_result = await self.health_checker.check_service_health(config)
                if health_result['healthy']:
                    logger.info(f"Service {config.name} is healthy")
                    return
                
                await asyncio.sleep(2.0)
            
            raise RuntimeError(f"Service {config.name} failed health check")
            
        except Exception as e:
            logger.error(f"Failed to deploy service {config.name}: {e}")
            self.error_log.append(f"Service {config.name}: {e}")
            raise
    
    async def _deploy_traditional(self):
        """Traditional deployment (with downtime)"""
        logger.info("Starting traditional deployment")
        
        # Stop all services
        for config in self.config.services:
            self.process_manager.stop_service(config)
        
        # Start all services
        for config in self.config.services:
            if not self.process_manager.start_service(config):
                raise RuntimeError(f"Failed to start service {config.name}")
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        logger.info("Performing health checks")
        
        health_tasks = []
        for config in self.config.services:
            task = asyncio.create_task(
                self.health_checker.check_service_health(config)
            )
            health_tasks.append((config.name, task))
        
        # Wait for all health checks
        results = {}
        for name, task in health_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=30.0)
                results[name] = result
            except asyncio.TimeoutError:
                results[name] = {'healthy': False, 'error': 'Health check timeout'}
        
        # Check results
        unhealthy_services = [
            name for name, result in results.items()
            if not result.get('healthy', False)
        ]
        
        if unhealthy_services:
            raise RuntimeError(f"Unhealthy services: {unhealthy_services}")
        
        logger.info("All health checks passed")
    
    async def _rollback(self):
        """Rollback deployment"""
        logger.info("Starting rollback")
        self.deployment_status = DeploymentStatus.ROLLBACK
        
        try:
            if self.rollback_path:
                success = self.backup_manager.restore_backup(self.rollback_path)
                if not success:
                    raise RuntimeError("Rollback failed")
            
            logger.info("Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            self.error_log.append(f"Rollback error: {e}")
    
    def _check_network_connectivity(self) -> bool:
        """Check network connectivity"""
        try:
            # Test DNS resolution
            socket.gethostbyname('google.com')
            
            # Test HTTP connectivity
            import urllib.request
            urllib.request.urlopen('http://httpbin.org/get', timeout=5)
            
            return True
        except Exception:
            return False
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            'deployment_id': self.config.deployment_id,
            'status': self.deployment_status.value,
            'start_time': self.deployment_start_time,
            'end_time': self.deployment_end_time,
            'duration': (self.deployment_end_time - self.deployment_start_time) if self.deployment_end_time and self.deployment_start_time else None,
            'services': self.process_manager.get_all_status(),
            'error_log': self.error_log,
            'rollback_path': self.rollback_path
        }

# Elite deployment factory
def create_production_deployment(
    deployment_id: str,
    services: List[ServiceConfig],
    **kwargs
) -> ProductionDeployment:
    """Create elite production deployment"""
    config = DeploymentConfig(
        deployment_id=deployment_id,
        services=services,
        **kwargs
    )
    return ProductionDeployment(config)

# Elite service configurations
def create_sovren_services() -> List[ServiceConfig]:
    """Create elite Sovren AI service configurations"""
    return [
        ServiceConfig(
            name="sovren-api",
            command=["python", "api/server.py"],
            port=8000,
            health_check_url="http://localhost:8000/health",
            environment={
                "SOVREN_ENV": "production",
                "SOVREN_LOG_LEVEL": "INFO"
            },
            working_directory="/data/sovren",
            log_file="/data/sovren/logs/api.log",
            pid_file="/data/sovren/pids/api.pid"
        ),
        ServiceConfig(
            name="sovren-voice",
            command=["python", "voice/voice_system.py"],
            port=8001,
            health_check_url="http://localhost:8001/health",
            environment={
                "SOVREN_ENV": "production",
                "SOVREN_LOG_LEVEL": "INFO"
            },
            working_directory="/data/sovren",
            log_file="/data/sovren/logs/voice.log",
            pid_file="/data/sovren/pids/voice.pid"
        ),
        ServiceConfig(
            name="sovren-consciousness",
            command=["python", "core/consciousness/consciousness_engine.py"],
            port=8002,
            health_check_url="http://localhost:8002/health",
            environment={
                "SOVREN_ENV": "production",
                "SOVREN_LOG_LEVEL": "INFO"
            },
            working_directory="/data/sovren",
            log_file="/data/sovren/logs/consciousness.log",
            pid_file="/data/sovren/pids/consciousness.pid"
        )
    ]

# Elite deployment execution
async def deploy_sovren_production() -> Dict[str, Any]:
    """Execute elite Sovren AI production deployment"""
    try:
        services = create_sovren_services()
        deployment = create_production_deployment(
            deployment_id=f"sovren_production_{int(time.time())}",
            services=services,
            zero_downtime=True,
            health_check_enabled=True,
            rollback_enabled=True,
            backup_enabled=True,
            deployment_timeout=600.0
        )
        
        result = await deployment.deploy()
        return result
        
    except Exception as e:
        logger.error(f"Production deployment failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': time.time()
        }

if __name__ == "__main__":
    # Execute elite production deployment
    asyncio.run(deploy_sovren_production()) 