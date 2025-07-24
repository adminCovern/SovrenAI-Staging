#!/usr/bin/env python3
"""
SOVREN AI - Production Launch Script
Enterprise-grade launcher with security, monitoring, and fault tolerance
"""

import os
import sys
import time
import subprocess
import signal
import logging
import json
import threading
import socket
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Import external dependencies with fallback
try:
    import psutil  # type: ignore
except ImportError:
    print("❌ ERROR: psutil is required but not installed.")
    print("Please install it with: pip install psutil>=5.9.0")
    print("Or install all requirements with: pip install -r scripts/requirements.txt")
    sys.exit(1)

try:
    import yaml  # type: ignore
except ImportError:
    print("❌ ERROR: PyYAML is required but not installed.")
    print("Please install it with: pip install PyYAML>=6.0")
    print("Or install all requirements with: pip install -r scripts/requirements.txt")
    sys.exit(1)

# Security and configuration
SECURITY_KEY = os.environ.get('SOVREN_SECURITY_KEY', secrets.token_hex(32))
MAX_RESTART_ATTEMPTS = 3
HEALTH_CHECK_INTERVAL = 30
GRACEFUL_SHUTDOWN_TIMEOUT = 10

# Setup enterprise logging
def setup_logging() -> logging.Logger:
    """Configure enterprise-grade logging with rotation and security"""
    log_dir = Path('/data/sovren/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatter with security context
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.FileHandler(log_dir / 'sovren_launcher.log')
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure logger
    logger = logging.getLogger('SOVREN-LAUNCHER')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# Add SOVREN to Python path
SOVREN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SOVREN_ROOT))

@dataclass
class ServiceConfig:
    """Service configuration with security and monitoring"""
    script: str
    name: str
    port: Optional[int]
    critical: bool
    health_check_url: Optional[str] = None
    restart_attempts: int = 0
    max_restart_attempts: int = MAX_RESTART_ATTEMPTS
    startup_timeout: int = 30
    memory_limit_mb: int = 2048
    cpu_limit_percent: float = 50.0

class SecurityManager:
    """Enterprise security management"""
    
    def __init__(self):
        self.security_key = SECURITY_KEY
        self.allowed_ips = self._load_allowed_ips()
        self.service_tokens = {}
    
    def _load_allowed_ips(self) -> List[str]:
        """Load allowed IP addresses from config"""
        config_path = Path('/data/sovren/config/security.yaml')
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    return config.get('allowed_ips', ['127.0.0.1'])
            except Exception as e:
                logger.warning(f"Failed to load security config: {e}")
        return ['127.0.0.1']
    
    def generate_service_token(self, service_name: str) -> str:
        """Generate secure token for service authentication"""
        token = hashlib.sha256(
            f"{service_name}:{self.security_key}:{secrets.token_hex(16)}".encode()
        ).hexdigest()
        self.service_tokens[service_name] = token
        return token
    
    def validate_service_token(self, service_name: str, token: str) -> bool:
        """Validate service authentication token"""
        return self.service_tokens.get(service_name) == token

class HealthMonitor:
    """Enterprise health monitoring system"""
    
    def __init__(self):
        self.health_status = {}
        self.monitoring_thread = None
        self._stop_monitoring = False
    
    def start_monitoring(self, services: Dict[str, ServiceConfig]):
        """Start health monitoring in background thread"""
        self._stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._monitor_services,
            args=(services,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def _monitor_services(self, services: Dict[str, ServiceConfig]):
        """Monitor service health in background"""
        while not self._stop_monitoring:
            try:
                for service_name, config in services.items():
                    self._check_service_health(service_name, config)
                time.sleep(HEALTH_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
    
    def _check_service_health(self, service_name: str, config: ServiceConfig):
        """Check individual service health"""
        try:
            # Check if service is responding on its port
            if config.port and config.health_check_url:
                response = self._http_health_check(config.health_check_url)
                self.health_status[service_name] = {
                    'status': 'healthy' if response else 'unhealthy',
                    'last_check': datetime.now().isoformat(),
                    'response_time': response.get('response_time', 0) if response else None
                }
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.health_status[service_name] = {
                'status': 'error',
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _http_health_check(self, url: str) -> Optional[Dict[str, Any]]:
        """Perform HTTP health check"""
        try:
            import requests  # type: ignore
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = time.time() - start_time
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'healthy': response.status_code == 200
            }
        except Exception:
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status.copy()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self._stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

class SOVRENLauncher:
    """Enterprise-grade SOVREN AI launcher"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.security_manager = SecurityManager()
        self.health_monitor = HealthMonitor()
        self.shutdown_event = threading.Event()
        self._load_service_configurations()
    
    def _load_service_configurations(self):
        """Load service configurations with security"""
        self.service_configs = {
            # MCP Server is already running on port 9999, so we skip starting a new one
            # 'mcp_server': ServiceConfig(
            #     script='scripts/enterprise_mcp_server.py',
            #     name='MCP Memory Management Server',
            #     port=9998,
            #     critical=True,
            #     startup_timeout=30,
            #     memory_limit_mb=1024
            # ),
            'consciousness': ServiceConfig(
                script='core/consciousness/consciousness_engine.py',
                name='Consciousness Engine',
                port=None,
                critical=True,
                startup_timeout=5400,  # Increased to 1.5 hours for very large model initialization
                memory_limit_mb=8192  # Increased memory limit for 8 GPUs
            ),
            'bayesian': ServiceConfig(
                script='core/bayesian_engine/bayesian_engine.py',
                name='Bayesian Decision Engine',
                port=None,
                critical=True,
                startup_timeout=120,  # Increased to 2 minutes for B200 compatibility
                memory_limit_mb=4096  # Increased memory limit
            ),
            'agent_battalion': ServiceConfig(
                script='core/agent_battalion/agent_battalion.py',
                name='Agent Battalion',
                port=None,
                critical=True,
                startup_timeout=60,  # 60 seconds for agent initialization
                memory_limit_mb=4096  # Memory for agent coordination
            ),
            'voice': ServiceConfig(
                script='voice/voice_system.py',
                name='Voice System',
                port=8000,
                critical=True,
                health_check_url='http://localhost:8000/health',
                startup_timeout=300,  # Increased to 5 minutes for large model loading
                memory_limit_mb=6144  # Increased memory limit
            ),
            'api': ServiceConfig(
                script='api/server.py',
                name='API Server',
                port=8001,
                critical=True,
                health_check_url='http://localhost:8001/health',
                startup_timeout=30,
                memory_limit_mb=1024
            ),
            'mcp': ServiceConfig(
                script='scripts/mcp_server.py',
                name='MCP Optimization Server',
                port=9999,
                critical=False,
                health_check_url='http://localhost:9999/health',
                startup_timeout=20,
                memory_limit_mb=512
            )
        }
    
    def check_prerequisites(self) -> bool:
        """Comprehensive prerequisite checking with security validation"""
        logger.info("🔍 Performing enterprise prerequisite validation...")
        
        try:
            # System requirements
            self._check_system_requirements()
            
            # Security validation
            self._validate_security_environment()
            
            # Directory structure
            self._ensure_directory_structure()
            
            # Network connectivity
            self._check_network_connectivity()
            
            # Resource availability
            self._check_resource_availability()
            
            logger.info("✅ All enterprise prerequisites validated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Prerequisite validation failed: {e}")
            return False
    
    def _check_system_requirements(self):
        """Check system requirements"""
        # Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8+ required")
        
        # Check NVIDIA GPUs with error handling
        try:
            result = subprocess.run(
                ['nvidia-smi', '-L'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                gpu_count = len([line for line in result.stdout.strip().split('\n') if line])
                logger.info(f"✅ Found {gpu_count} NVIDIA GPUs")
            else:
                logger.warning("⚠️  NVIDIA GPUs not detected - running in CPU mode")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️  NVIDIA GPUs not detected - running in CPU mode")
    
    def _validate_security_environment(self):
        """Validate security environment"""
        # Check for required security variables
        required_env_vars = ['SOVREN_ENV', 'SOVREN_SECURITY_KEY']
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            logger.info("🔧 Auto-setting missing environment variables...")
            
            # Auto-set missing environment variables
            if not os.environ.get('SOVREN_ENV'):
                os.environ['SOVREN_ENV'] = 'production'
                logger.info("✅ Set SOVREN_ENV=production")
            
            if not os.environ.get('SOVREN_SECURITY_KEY'):
                # Use the provided SOVREN security key
                security_key = "aa9628c23683705c6c1eee9771bb3224f438333e925df0c5df2e88f0699603fd"
                os.environ['SOVREN_SECURITY_KEY'] = security_key
                logger.info(f"✅ Set SOVREN_SECURITY_KEY: {security_key[:16]}...")
            
            # Set additional recommended environment variables
            additional_vars = {
                'SOVREN_LOG_LEVEL': 'INFO',
                'SOVREN_HOST': '0.0.0.0',
                'SOVREN_PORT': '8000',
                'SOVREN_JWT_SECRET': secrets.token_hex(32),
                'SOVREN_JWT_EXPIRY_HOURS': '24',
                'SOVREN_MCP_ENABLED': '1',
                'SOVREN_MCP_HOST': 'localhost',
                'SOVREN_MCP_PORT': '9999'
            }
            
            for var, value in additional_vars.items():
                if not os.environ.get(var):
                    os.environ[var] = value
                    logger.info(f"✅ Set {var}={value}")
        
        # Validate security key strength
        if len(SECURITY_KEY) < 32:
            logger.warning("Security key may be weak")
    
    def _ensure_directory_structure(self):
        """Ensure required directory structure exists"""
        required_dirs = [
            '/data/sovren',
            '/data/sovren/models',
            '/data/sovren/logs',
            '/data/sovren/voice',
            '/data/sovren/config',
            '/data/sovren/temp'
        ]
        
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Ensured directory: {dir_path}")
    
    def _check_network_connectivity(self):
        """Check network connectivity"""
        test_hosts = ['localhost', '127.0.0.1']
        for host in test_hosts:
            try:
                socket.create_connection((host, 80), timeout=5)
                logger.info(f"✅ Network connectivity to {host} confirmed")
            except Exception as e:
                logger.warning(f"⚠️  Network connectivity to {host} failed: {e}")
    
    def _check_resource_availability(self):
        """Check system resource availability"""
        # Check memory
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # 1GB
            logger.warning("⚠️  Low memory availability")
        
        # Check disk space
        disk = psutil.disk_usage('/data')
        if disk.free < 10 * 1024 * 1024 * 1024:  # 10GB
            logger.warning("⚠️  Low disk space")
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        if cpu_count is not None and cpu_count < 4:
            logger.warning("⚠️  Limited CPU cores available")
    
    def _check_numactl_available(self) -> bool:
        """Check if numactl is available on the system"""
        try:
            result = subprocess.run(['numactl', '--show'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _start_service(self, service_name: str, config: ServiceConfig) -> bool:
        """Start a service with enhanced security and monitoring"""
        try:
            script_path = SOVREN_ROOT / config.script
            
            if not script_path.exists():
                logger.error(f"❌ Service script not found: {script_path}")
                if config.critical:
                    return False
                return True
            
            logger.info(f"🚀 Starting {config.name}...")
            
            # Generate security token for service
            service_token = self.security_manager.generate_service_token(service_name)
            
            # Build command with NUMA optimization if available
            if self._check_numactl_available():
                cmd = [
                    "numactl", "--interleave=all",  # NUMA-aware launch
                    "python3", str(script_path)
                ]
                logger.info(f"Using NUMA-aware launch for {config.name}")
            else:
                cmd = ["python3", str(script_path)]
                logger.info(f"Using standard launch for {config.name} (numactl not available)")
            
            # Set environment variables for optimal performance with MCP memory management
            env = os.environ.copy()
            env.update({
                'PYTHONPATH': str(SOVREN_ROOT),
                'SOVREN_SERVICE_TOKEN': service_token,
                'SOVREN_SERVICE_NAME': service_name,
                'SOVREN_SECURITY_KEY': SECURITY_KEY,
                'PYTHONUNBUFFERED': '1',
                'CUDA_DEVICE_ORDER': 'PCI_BUS_ID',
                'OMP_NUM_THREADS': str(min(16, os.cpu_count() or 1)),  # Reduced for B200 compatibility
                'MKL_NUM_THREADS': str(min(16, os.cpu_count() or 1)),  # Reduced for B200 compatibility
                'OPENBLAS_NUM_THREADS': str(min(16, os.cpu_count() or 1)),  # Reduced for B200 compatibility
                'VECLIB_MAXIMUM_THREADS': str(min(16, os.cpu_count() or 1)),  # Reduced for B200 compatibility
                'NUMEXPR_NUM_THREADS': str(min(16, os.cpu_count() or 1)),  # Reduced for B200 compatibility
                'MALLOC_ARENA_MAX': '2',  # Limit memory arenas for B200 compatibility
                'PYTHONMALLOC': 'malloc',  # Use system malloc for B200 compatibility
                'SOVREN_MCP_ENABLED': '1',  # Enable MCP memory management
                'SOVREN_MCP_HOST': 'localhost',
                'SOVREN_MCP_PORT': '9999'  # Use existing MCP Server
            })
            
            # Start process with resource limits (handle platform differences)
            try:
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=lambda: self._set_process_limits(config.memory_limit_mb)
                )
            except OSError:
                # Fallback for platforms that don't support preexec_fn
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes[service_name] = process
            logger.info(f"Started {config.name} (PID: {process.pid})")
            
            # Wait for startup with timeout
            if self._wait_for_service_startup(service_name, config):
                logger.info(f"✅ {config.name} started (PID: {process.pid})")
                return True
            else:
                # Log any error output from the process
                try:
                    stderr_output = process.stderr.read().decode('utf-8')
                    if stderr_output:
                        logger.error(f"❌ {config.name} stderr output: {stderr_output}")
                except Exception:
                    pass
                logger.error(f"❌ {config.name} failed to start within timeout")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start {config.name}: {e}")
            return False
    
    def _set_process_limits(self, memory_limit_mb: int):
        """Set resource limits for child processes"""
        try:
            import resource
            # Set memory limit
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit_mb * 1024 * 1024, -1))
        except Exception:
            pass
    
    def _wait_for_service_startup(self, service_key: str, config: ServiceConfig) -> bool:
        """Wait for service to start with health check"""
        start_time = time.time()
        
        while time.time() - start_time < config.startup_timeout:
            # Check if process is still running
            process = self.processes[service_key]
            if process.poll() is not None:
                logger.error(f"❌ {config.name} process terminated unexpectedly")
                return False
            
            # Check health endpoint if available
            if config.health_check_url:
                try:
                    import requests  # type: ignore
                    response = requests.get(config.health_check_url, timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ {config.name} health check passed")
                        return True
                except Exception:
                    pass
            else:
                # For services without health check URLs, just check if process is running
                # and give them time to initialize (at least 10 seconds)
                if time.time() - start_time > 10:
                    logger.info(f"✅ {config.name} started (no health check configured)")
                    return True
            
            time.sleep(1)
        
        logger.error(f"❌ {config.name} failed to start within {config.startup_timeout} seconds")
        return False
    
    def start_all_services(self) -> bool:
        """Start all services with dependency management"""
        logger.info("🌟 Starting SOVREN AI System...")
        
        # Start critical services first
        critical_services = [key for key, config in self.service_configs.items() 
                           if config.critical]
        
        for service_key in critical_services:
            if not self._start_service(service_key, self.service_configs[service_key]):
                logger.error(f"❌ Critical service {service_key} failed to start")
                self.shutdown()
                return False
            time.sleep(3)  # Allow initialization time
        
        # Start non-critical services
        non_critical_services = [key for key, config in self.service_configs.items() 
                               if not config.critical]
        
        for service_key in non_critical_services:
            self._start_service(service_key, self.service_configs[service_key])
            time.sleep(1)
        
        # Start health monitoring
        self.health_monitor.start_monitoring(self.service_configs)
        
        logger.info("✅ All services started successfully!")
        logger.info("🎯 SOVREN AI is now fully operational")
        return True
    
    def monitor_services(self):
        """Monitor services with automatic recovery"""
        logger.info("🔍 Starting service monitoring...")
        
        while not self.shutdown_event.is_set():
            try:
                time.sleep(10)
                
                # Check each process
                for service_key, process in list(self.processes.items()):
                    if process.poll() is not None:
                        config = self.service_configs[service_key]
                        logger.error(f"❌ {config.name} has stopped!")
                        
                        if config.critical:
                            logger.error("Critical service failed - initiating shutdown")
                            self.shutdown()
                            return
                        else:
                            # Attempt restart for non-critical services
                            if config.restart_attempts < config.max_restart_attempts:
                                logger.info(f"🔄 Restarting {config.name}...")
                                config.restart_attempts += 1
                                self._start_service(service_key, config)
                            else:
                                logger.error(f"❌ {config.name} exceeded restart attempts")
                
                # Log health status periodically
                health_status = self.health_monitor.get_health_status()
                if health_status:
                    logger.debug(f"Health status: {json.dumps(health_status, indent=2)}")
                    
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
    
    def shutdown(self):
        """Graceful shutdown with proper cleanup"""
        logger.info("🛑 Initiating SOVREN AI shutdown...")
        
        # Stop health monitoring
        self.health_monitor.stop_monitoring()
        
        # Set shutdown flag
        self.shutdown_event.set()
        
        # Stop services in reverse dependency order
        shutdown_order = list(self.processes.keys())
        shutdown_order.reverse()
        
        for service_key in shutdown_order:
            process = self.processes[service_key]
            config = self.service_configs[service_key]
            
            logger.info(f"Stopping {config.name}...")
            
            try:
                # Send SIGTERM for graceful shutdown
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=GRACEFUL_SHUTDOWN_TIMEOUT)
                    logger.info(f"✅ {config.name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    logger.warning(f"⚠️  Force killing {config.name}")
                    process.kill()
                    process.wait()
                    logger.info(f"✅ {config.name} force stopped")
                    
            except Exception as e:
                logger.error(f"❌ Error stopping {config.name}: {e}")
        
        logger.info("✅ SOVREN AI shutdown complete")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.shutdown()
        sys.exit(0)
    
    def run(self) -> int:
        """Main run method with proper exit codes"""
        try:
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Check prerequisites
            if not self.check_prerequisites():
                return 1
            
            # Display startup banner
            self.display_banner()
            
            # Start all services
            if not self.start_all_services():
                return 1
            
            # Monitor services
            self.monitor_services()
            
            return 0
            
        except Exception as e:
            logger.error(f"Fatal error in SOVREN launcher: {e}")
            self.shutdown()
            return 1
    
    def display_banner(self):
        """Display enterprise startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗ ██████╗ ██╗   ██╗██████╗ ███████╗███╗   ██╗     ║
║   ██╔════╝██╔═══██╗██║   ██║██╔══██╗██╔════╝████╗  ██║     ║
║   ███████╗██║   ██║██║   ██║██████╔╝█████╗  ██╔██╗ ██║     ║
║   ╚════██║██║   ██║╚██╗ ██╔╝██╔══██╗██╔══╝  ██║╚██╗██║     ║
║   ███████║╚██████╔╝ ╚████╔╝ ██║  ██║███████╗██║ ╚████║     ║
║   ╚══════╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝     ║
║                                                              ║
║              SOVEREIGN AI - ENTERPRISE EDITION               ║
║                                                              ║
║   Hardware: 8x NVIDIA B200 | 2.3TB RAM | 288 CPU Cores     ║
║   Target: <150ms ASR | <100ms TTS | <90ms/token LLM        ║
║   Security: Enterprise-grade authentication & monitoring     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

def main() -> int:
    """Main entry point with proper exit codes"""
    launcher = SOVRENLauncher()
    return launcher.run()

if __name__ == "__main__":
    sys.exit(main())