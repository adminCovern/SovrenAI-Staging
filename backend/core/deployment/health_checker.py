#!/usr/bin/env python3
"""
SOVREN AI - Comprehensive Health Checker
Production-ready health monitoring with deep diagnostics and automated remediation
"""

import os
import sys
import time
import threading
import logging
import json
import psutil
import requests
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import subprocess
import socket
import hashlib

logger = logging.getLogger('HealthChecker')

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class CheckType(Enum):
    """Health check types"""
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    check_type: CheckType
    check_function: Callable
    interval: int = 60  # seconds
    timeout: int = 30   # seconds
    critical_threshold: float = 0.0
    warning_threshold: float = 0.0
    auto_remediate: bool = False
    enabled: bool = True

@dataclass
class HealthResult:
    """Health check result"""
    check_name: str
    status: HealthStatus
    timestamp: datetime
    value: float
    message: str
    details: Dict[str, Any]
    remediation_applied: bool = False

class ComprehensiveHealthChecker:
    """Production-ready comprehensive health checking system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Health checks registry
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Results storage
        self.health_results: Dict[str, List[HealthResult]] = {}
        self.results_lock = threading.RLock()
        
        # Monitoring and alerting
        self.alert_callbacks: List[Callable] = []
        self.remediation_callbacks: List[Callable] = []
        
        # System metrics
        self.system_metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': [],
        }
        
        # Performance tracking
        self.performance_history = []
        
        # Initialize health checks
        self._register_default_checks()
        
        # Start monitoring thread
        self._start_monitoring_thread()
        
        logger.info("Comprehensive health checker initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'monitoring_interval': 30,  # seconds
            'alert_threshold': 0.8,     # 80% health score
            'auto_remediation': True,
            'max_history_size': 1000,
            'endpoints': {
                'health': '/health',
                'metrics': '/metrics',
                'ready': '/ready',
                'live': '/live',
            },
            'thresholds': {
                'cpu_warning': 80.0,
                'cpu_critical': 95.0,
                'memory_warning': 85.0,
                'memory_critical': 95.0,
                'disk_warning': 85.0,
                'disk_critical': 95.0,
                'response_time_warning': 1000,  # ms
                'response_time_critical': 5000,  # ms
            },
        }
    
    def _register_default_checks(self):
        """Register default health checks"""
        
        # System health checks
        self.register_check(HealthCheck(
            name="cpu_usage",
            check_type=CheckType.SYSTEM,
            check_function=self._check_cpu_usage,
            interval=30,
            critical_threshold=self.config['thresholds']['cpu_critical'],
            warning_threshold=self.config['thresholds']['cpu_warning'],
            auto_remediate=True,
        ))
        
        self.register_check(HealthCheck(
            name="memory_usage",
            check_type=CheckType.SYSTEM,
            check_function=self._check_memory_usage,
            interval=30,
            critical_threshold=self.config['thresholds']['memory_critical'],
            warning_threshold=self.config['thresholds']['memory_warning'],
            auto_remediate=True,
        ))
        
        self.register_check(HealthCheck(
            name="disk_usage",
            check_type=CheckType.SYSTEM,
            check_function=self._check_disk_usage,
            interval=60,
            critical_threshold=self.config['thresholds']['disk_critical'],
            warning_threshold=self.config['thresholds']['disk_warning'],
            auto_remediate=True,
        ))
        
        # Application health checks
        self.register_check(HealthCheck(
            name="application_health",
            check_type=CheckType.APPLICATION,
            check_function=self._check_application_health,
            interval=30,
            timeout=10,
        ))
        
        self.register_check(HealthCheck(
            name="response_time",
            check_type=CheckType.PERFORMANCE,
            check_function=self._check_response_time,
            interval=30,
            critical_threshold=self.config['thresholds']['response_time_critical'],
            warning_threshold=self.config['thresholds']['response_time_warning'],
        ))
        
        # Database health checks
        self.register_check(HealthCheck(
            name="database_connection",
            check_type=CheckType.DATABASE,
            check_function=self._check_database_connection,
            interval=60,
            timeout=15,
        ))
        
        # Network health checks
        self.register_check(HealthCheck(
            name="network_connectivity",
            check_type=CheckType.NETWORK,
            check_function=self._check_network_connectivity,
            interval=60,
        ))
        
        # Security health checks
        self.register_check(HealthCheck(
            name="security_scan",
            check_type=CheckType.SECURITY,
            check_function=self._check_security_health,
            interval=300,  # 5 minutes
        ))
    
    def register_check(self, health_check: HealthCheck):
        """Register a health check"""
        
        self.health_checks[health_check.name] = health_check
        
        # Initialize results storage
        if health_check.name not in self.health_results:
            self.health_results[health_check.name] = []
        
        logger.info(f"Registered health check: {health_check.name}")
    
    def unregister_check(self, check_name: str):
        """Unregister a health check"""
        
        if check_name in self.health_checks:
            del self.health_checks[check_name]
            logger.info(f"Unregistered health check: {check_name}")
    
    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        
        def monitoring_loop():
            while True:
                try:
                    # Run all enabled health checks
                    for check_name, health_check in self.health_checks.items():
                        if health_check.enabled:
                            self._run_health_check(health_check)
                    
                    # Update system metrics
                    self._update_system_metrics()
                    
                    # Check overall health
                    self._check_overall_health()
                    
                    time.sleep(self.config['monitoring_interval'])
                    
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    def _run_health_check(self, health_check: HealthCheck):
        """Run individual health check"""
        
        try:
            start_time = time.time()
            
            # Execute health check with timeout
            with threading.Timer(health_check.timeout, lambda: None) as timer:
                try:
                    value, message, details = health_check.check_function()
                    timer.cancel()
                except Exception as e:
                    value = 0.0
                    message = f"Health check failed: {e}"
                    details = {'error': str(e)}
            
            duration = time.time() - start_time
            
            # Determine health status
            status = self._determine_health_status(value, health_check)
            
            # Create result
            result = HealthResult(
                check_name=health_check.name,
                status=status,
                timestamp=datetime.now(),
                value=value,
                message=message,
                details=details,
            )
            
            # Store result
            with self.results_lock:
                self.health_results[health_check.name].append(result)
                
                # Keep only recent results
                max_history = self.config['max_history_size']
                if len(self.health_results[health_check.name]) > max_history:
                    self.health_results[health_check.name] = \
                        self.health_results[health_check.name][-max_history:]
            
            # Apply auto-remediation if needed
            if (health_check.auto_remediate and 
                status in [HealthStatus.CRITICAL, HealthStatus.WARNING]):
                self._apply_remediation(health_check, result)
            
            # Trigger alerts if needed
            if status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                self._trigger_alert(health_check, result)
            
            logger.debug(f"Health check {health_check.name}: {status.value} ({value:.2f})")
            
        except Exception as e:
            logger.error(f"Failed to run health check {health_check.name}: {e}")
    
    def _determine_health_status(self, value: float, health_check: HealthCheck) -> HealthStatus:
        """Determine health status based on thresholds"""
        
        if value >= health_check.critical_threshold:
            return HealthStatus.CRITICAL
        elif value >= health_check.warning_threshold:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def _check_cpu_usage(self) -> tuple[float, str, Dict[str, Any]]:
        """Check CPU usage"""
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get detailed CPU info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            details = {
                'cpu_count': cpu_count,
                'cpu_freq_mhz': cpu_freq.current if cpu_freq else None,
                'cpu_percent_per_core': psutil.cpu_percent(interval=1, percpu=True),
            }
            
            return cpu_percent, f"CPU usage: {cpu_percent:.1f}%", details
            
        except Exception as e:
            return 100.0, f"CPU check failed: {e}", {'error': str(e)}
    
    def _check_memory_usage(self) -> tuple[float, str, Dict[str, Any]]:
        """Check memory usage"""
        
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            details = {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'free_gb': memory.free / (1024**3),
                'swap_percent': psutil.swap_memory().percent,
            }
            
            return memory_percent, f"Memory usage: {memory_percent:.1f}%", details
            
        except Exception as e:
            return 100.0, f"Memory check failed: {e}", {'error': str(e)}
    
    def _check_disk_usage(self) -> tuple[float, str, Dict[str, Any]]:
        """Check disk usage"""
        
        try:
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Check multiple mount points
            mount_points = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    mount_points[partition.mountpoint] = {
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent': usage.percent,
                    }
                except Exception:
                    pass
            
            details = {
                'root_usage_gb': disk.used / (1024**3),
                'root_free_gb': disk.free / (1024**3),
                'mount_points': mount_points,
            }
            
            return disk_percent, f"Disk usage: {disk_percent:.1f}%", details
            
        except Exception as e:
            return 100.0, f"Disk check failed: {e}", {'error': str(e)}
    
    def _check_application_health(self) -> tuple[float, str, Dict[str, Any]]:
        """Check application health endpoints"""
        
        try:
            health_score = 0.0
            checks_passed = 0
            total_checks = 0
            details = {}
            
            # Check health endpoint
            try:
                response = requests.get(
                    f"http://localhost:8000{self.config['endpoints']['health']}",
                    timeout=5
                )
                if response.status_code == 200:
                    health_data = response.json()
                    health_score += 0.4
                    checks_passed += 1
                    details['health_endpoint'] = health_data
                else:
                    details['health_endpoint_error'] = f"Status code: {response.status_code}"
            except Exception as e:
                details['health_endpoint_error'] = str(e)
            
            total_checks += 1
            
            # Check ready endpoint
            try:
                response = requests.get(
                    f"http://localhost:8000{self.config['endpoints']['ready']}",
                    timeout=5
                )
                if response.status_code == 200:
                    health_score += 0.3
                    checks_passed += 1
                    details['ready_endpoint'] = 'OK'
                else:
                    details['ready_endpoint_error'] = f"Status code: {response.status_code}"
            except Exception as e:
                details['ready_endpoint_error'] = str(e)
            
            total_checks += 1
            
            # Check live endpoint
            try:
                response = requests.get(
                    f"http://localhost:8000{self.config['endpoints']['live']}",
                    timeout=5
                )
                if response.status_code == 200:
                    health_score += 0.3
                    checks_passed += 1
                    details['live_endpoint'] = 'OK'
                else:
                    details['live_endpoint_error'] = f"Status code: {response.status_code}"
            except Exception as e:
                details['live_endpoint_error'] = str(e)
            
            total_checks += 1
            
            # Calculate final score
            final_score = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
            
            return final_score, f"Application health: {checks_passed}/{total_checks} checks passed", details
            
        except Exception as e:
            return 0.0, f"Application health check failed: {e}", {'error': str(e)}
    
    def _check_response_time(self) -> tuple[float, str, Dict[str, Any]]:
        """Check application response time"""
        
        try:
            start_time = time.time()
            
            response = requests.get(
                f"http://localhost:8000{self.config['endpoints']['health']}",
                timeout=10
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            details = {
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'content_length': len(response.content),
            }
            
            return response_time, f"Response time: {response_time:.2f}ms", details
            
        except Exception as e:
            return 10000.0, f"Response time check failed: {e}", {'error': str(e)}
    
    def _check_database_connection(self) -> tuple[float, str, Dict[str, Any]]:
        """Check database connection health"""
        
        try:
            # Test database connectivity
            import sqlite3
            
            # Try to connect to database
            start_time = time.time()
            conn = sqlite3.connect('/var/log/sovren/audit/audit.db')
            connection_time = (time.time() - start_time) * 1000
            
            # Test simple query
            cursor = conn.execute('SELECT COUNT(*) FROM config_items')
            row_count = cursor.fetchone()[0]
            
            conn.close()
            
            details = {
                'connection_time_ms': connection_time,
                'row_count': row_count,
                'database_path': '/var/log/sovren/audit/audit.db',
            }
            
            # Score based on connection time
            if connection_time < 100:
                score = 100.0
            elif connection_time < 500:
                score = 80.0
            elif connection_time < 1000:
                score = 60.0
            else:
                score = 20.0
            
            return score, f"Database connection: {connection_time:.2f}ms", details
            
        except Exception as e:
            return 0.0, f"Database connection failed: {e}", {'error': str(e)}
    
    def _check_network_connectivity(self) -> tuple[float, str, Dict[str, Any]]:
        """Check network connectivity"""
        
        try:
            # Test DNS resolution
            import socket
            
            start_time = time.time()
            try:
                socket.gethostbyname('google.com')
                dns_time = (time.time() - start_time) * 1000
                dns_working = True
            except Exception:
                dns_time = 0
                dns_working = False
            
            # Test HTTP connectivity
            start_time = time.time()
            try:
                response = requests.get('https://httpbin.org/get', timeout=5)
                http_time = (time.time() - start_time) * 1000
                http_working = response.status_code == 200
            except Exception:
                http_time = 0
                http_working = False
            
            # Calculate score
            score = 0.0
            if dns_working:
                score += 50.0
            if http_working:
                score += 50.0
            
            details = {
                'dns_working': dns_working,
                'dns_time_ms': dns_time,
                'http_working': http_working,
                'http_time_ms': http_time,
            }
            
            return score, f"Network connectivity: DNS={dns_working}, HTTP={http_working}", details
            
        except Exception as e:
            return 0.0, f"Network connectivity check failed: {e}", {'error': str(e)}
    
    def _check_security_health(self) -> tuple[float, str, Dict[str, Any]]:
        """Check security health"""
        
        try:
            security_score = 100.0
            security_issues = []
            
            # Check for open ports
            open_ports = []
            for port in [22, 80, 443, 8000, 8080]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                except Exception:
                    pass
            
            # Check for suspicious processes
            suspicious_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if any(keyword in proc_info['name'].lower() for keyword in ['crypto', 'miner', 'backdoor']):
                        suspicious_processes.append(proc_info)
                except Exception:
                    pass
            
            # Calculate security score
            if len(open_ports) > 5:
                security_score -= 20.0
                security_issues.append(f"Too many open ports: {open_ports}")
            
            if suspicious_processes:
                security_score -= 30.0
                security_issues.append(f"Suspicious processes found: {len(suspicious_processes)}")
            
            # Check file permissions
            critical_files = ['/etc/passwd', '/etc/shadow', '/etc/sudoers']
            for file_path in critical_files:
                try:
                    if os.path.exists(file_path):
                        stat = os.stat(file_path)
                        if stat.st_mode & 0o777 > 0o600:
                            security_score -= 10.0
                            security_issues.append(f"Insecure permissions on {file_path}")
                except Exception:
                    pass
            
            details = {
                'open_ports': open_ports,
                'suspicious_processes': suspicious_processes,
                'security_issues': security_issues,
            }
            
            return max(security_score, 0.0), f"Security score: {security_score:.1f}", details
            
        except Exception as e:
            return 0.0, f"Security health check failed: {e}", {'error': str(e)}
    
    def _update_system_metrics(self):
        """Update system metrics"""
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_metrics['cpu_usage'].append(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_metrics['memory_usage'].append(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_metrics['disk_usage'].append(disk.percent)
            
            # Network I/O
            network = psutil.net_io_counters()
            self.system_metrics['network_io'].append({
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
            })
            
            # Keep only recent metrics
            max_metrics = 100
            for key in self.system_metrics:
                if len(self.system_metrics[key]) > max_metrics:
                    self.system_metrics[key] = self.system_metrics[key][-max_metrics:]
                    
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    def _check_overall_health(self):
        """Check overall system health"""
        
        try:
            # Calculate overall health score
            total_score = 0.0
            total_checks = 0
            
            with self.results_lock:
                for check_name, results in self.health_results.items():
                    if results:
                        latest_result = results[-1]
                        
                        # Convert status to score
                        if latest_result.status == HealthStatus.HEALTHY:
                            score = 100.0
                        elif latest_result.status == HealthStatus.WARNING:
                            score = 60.0
                        elif latest_result.status == HealthStatus.CRITICAL:
                            score = 20.0
                        else:
                            score = 0.0
                        
                        total_score += score
                        total_checks += 1
            
            overall_score = total_score / total_checks if total_checks > 0 else 0
            
            # Store performance history
            self.performance_history.append({
                'timestamp': datetime.now(),
                'overall_score': overall_score,
                'total_checks': total_checks,
            })
            
            # Keep only recent history
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
            
            # Check if overall health is below threshold
            if overall_score < (self.config['alert_threshold'] * 100):
                self._trigger_overall_alert(overall_score)
                
        except Exception as e:
            logger.error(f"Failed to check overall health: {e}")
    
    def _apply_remediation(self, health_check: HealthCheck, result: HealthResult):
        """Apply automated remediation"""
        
        try:
            if health_check.name == "cpu_usage" and result.status == HealthStatus.CRITICAL:
                # Kill high CPU processes
                self._remediate_high_cpu_usage()
                result.remediation_applied = True
                
            elif health_check.name == "memory_usage" and result.status == HealthStatus.CRITICAL:
                # Clear memory cache
                self._remediate_high_memory_usage()
                result.remediation_applied = True
                
            elif health_check.name == "disk_usage" and result.status == HealthStatus.CRITICAL:
                # Clean up disk space
                self._remediate_high_disk_usage()
                result.remediation_applied = True
            
            # Notify remediation callbacks
            for callback in self.remediation_callbacks:
                try:
                    callback(health_check, result)
                except Exception as e:
                    logger.error(f"Remediation callback failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to apply remediation for {health_check.name}: {e}")
    
    def _remediate_high_cpu_usage(self):
        """Remediate high CPU usage"""
        
        try:
            # Find processes with high CPU usage
            high_cpu_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 50:  # 50% CPU threshold
                        high_cpu_processes.append(proc_info)
                except Exception:
                    pass
            
            # Kill non-critical high CPU processes
            killed_count = 0
            for proc_info in high_cpu_processes[:5]:  # Limit to 5 processes
                try:
                    if proc_info['name'] not in ['systemd', 'sshd', 'bash', 'python']:
                        psutil.Process(proc_info['pid']).terminate()
                        killed_count += 1
                        logger.info(f"Terminated high CPU process: {proc_info['name']} (PID: {proc_info['pid']})")
                except Exception:
                    pass
            
            logger.info(f"CPU remediation: killed {killed_count} high CPU processes")
            
        except Exception as e:
            logger.error(f"CPU remediation failed: {e}")
    
    def _remediate_high_memory_usage(self):
        """Remediate high memory usage"""
        
        try:
            # Clear page cache
            subprocess.run(['sync'], check=True)
            subprocess.run(['echo', '3'], stdout=subprocess.PIPE, input=b'3\n', check=True)
            
            # Clear swap
            subprocess.run(['swapoff', '-a'], check=True)
            subprocess.run(['swapon', '-a'], check=True)
            
            logger.info("Memory remediation: cleared page cache and swap")
            
        except Exception as e:
            logger.error(f"Memory remediation failed: {e}")
    
    def _remediate_high_disk_usage(self):
        """Remediate high disk usage"""
        
        try:
            # Clean up log files
            log_dirs = ['/var/log', '/tmp', '/var/tmp']
            cleaned_size = 0
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    for root, dirs, files in os.walk(log_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                # Remove old log files
                                if file.endswith('.log') or file.endswith('.gz'):
                                    stat = os.stat(file_path)
                                    if time.time() - stat.st_mtime > 7 * 24 * 3600:  # 7 days
                                        file_size = stat.st_size
                                        os.remove(file_path)
                                        cleaned_size += file_size
                            except Exception:
                                pass
            
            logger.info(f"Disk remediation: cleaned {cleaned_size / (1024*1024):.2f} MB")
            
        except Exception as e:
            logger.error(f"Disk remediation failed: {e}")
    
    def _trigger_alert(self, health_check: HealthCheck, result: HealthResult):
        """Trigger health alert"""
        
        alert_data = {
            'check_name': health_check.name,
            'check_type': health_check.check_type.value,
            'status': result.status.value,
            'value': result.value,
            'message': result.message,
            'timestamp': result.timestamp.isoformat(),
        }
        
        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(f"Health alert: {health_check.name} - {result.status.value}")
    
    def _trigger_overall_alert(self, overall_score: float):
        """Trigger overall system alert"""
        
        alert_data = {
            'type': 'overall_health',
            'overall_score': overall_score,
            'timestamp': datetime.now().isoformat(),
            'message': f"Overall system health below threshold: {overall_score:.1f}%",
        }
        
        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Overall alert callback failed: {e}")
        
        logger.warning(f"Overall health alert: {overall_score:.1f}%")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        
        try:
            with self.results_lock:
                # Get latest results for each check
                latest_results = {}
                for check_name, results in self.health_results.items():
                    if results:
                        latest_results[check_name] = results[-1]
                
                # Calculate overall health
                total_score = 0.0
                total_checks = 0
                healthy_checks = 0
                warning_checks = 0
                critical_checks = 0
                
                for result in latest_results.values():
                    if result.status == HealthStatus.HEALTHY:
                        total_score += 100.0
                        healthy_checks += 1
                    elif result.status == HealthStatus.WARNING:
                        total_score += 60.0
                        warning_checks += 1
                    elif result.status == HealthStatus.CRITICAL:
                        total_score += 20.0
                        critical_checks += 1
                    
                    total_checks += 1
                
                overall_score = total_score / total_checks if total_checks > 0 else 0
                
                # Determine overall status
                if overall_score >= 90:
                    overall_status = HealthStatus.HEALTHY
                elif overall_score >= 70:
                    overall_status = HealthStatus.WARNING
                else:
                    overall_status = HealthStatus.CRITICAL
                
                return {
                    'overall_status': overall_status.value,
                    'overall_score': overall_score,
                    'total_checks': total_checks,
                    'healthy_checks': healthy_checks,
                    'warning_checks': warning_checks,
                    'critical_checks': critical_checks,
                    'latest_results': {
                        name: {
                            'status': result.status.value,
                            'value': result.value,
                            'message': result.message,
                            'timestamp': result.timestamp.isoformat(),
                        }
                        for name, result in latest_results.items()
                    },
                    'system_metrics': {
                        'cpu_usage': self.system_metrics['cpu_usage'][-1] if self.system_metrics['cpu_usage'] else 0,
                        'memory_usage': self.system_metrics['memory_usage'][-1] if self.system_metrics['memory_usage'] else 0,
                        'disk_usage': self.system_metrics['disk_usage'][-1] if self.system_metrics['disk_usage'] else 0,
                    },
                }
                
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                'overall_status': HealthStatus.UNKNOWN.value,
                'error': str(e),
            }
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback"""
        self.alert_callbacks.append(callback)
    
    def add_remediation_callback(self, callback: Callable):
        """Add remediation callback"""
        self.remediation_callbacks.append(callback)
    
    def get_performance_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance history"""
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            return [
                {
                    'timestamp': entry['timestamp'].isoformat(),
                    'overall_score': entry['overall_score'],
                    'total_checks': entry['total_checks'],
                }
                for entry in self.performance_history
                if entry['timestamp'] > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return [] 