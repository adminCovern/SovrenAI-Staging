#!/usr/bin/env python3
"""
SOVREN Billing System - Health Checks
Production-grade health monitoring for all system components
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, List
import logging
from api.structured_logging import get_billing_logger

logger = get_billing_logger()

class HealthChecker:
    """Production-grade health checker"""
    
    def __init__(self):
        self.logger = logger
        self.checks: Dict[str, Any] = {}
        self._setup_default_checks()
    
    def _setup_default_checks(self):
        """Setup default health checks"""
        self.checks = {
            'system': self._check_system_health,
            'killbill': self._check_killbill_health,
            'stripe': self._check_stripe_health,
            'database': self._check_database_health,
            'memory': self._check_memory_health,
            'disk': self._check_disk_health,
            'network': self._check_network_health
        }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Load average
            load_avg = psutil.getloadavg()
            
            # Process count
            process_count = len(psutil.pids())
            
            status = 'healthy'
            if cpu_percent > 90:
                status = 'warning'
            if cpu_percent > 95:
                status = 'critical'
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'load_average': load_avg,
                'process_count': process_count,
                'timestamp': time.time()
            }
            
        except ImportError:
            return {
                'status': 'unknown',
                'error': 'psutil not available',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_killbill_health(self) -> Dict[str, Any]:
        """Check Kill Bill connectivity"""
        try:
            from api.billing_integration import get_billing_system
            
            billing_system = get_billing_system()
            start_time = time.time()
            
            # Test Kill Bill connection
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{billing_system.killbill_client.base_url}/1.0/kb/healthcheck",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            'status': 'healthy',
                            'response_time': duration,
                            'status_code': response.status,
                            'timestamp': time.time()
                        }
                    else:
                        return {
                            'status': 'error',
                            'response_time': duration,
                            'status_code': response.status,
                            'error': f"HTTP {response.status}",
                            'timestamp': time.time()
                        }
                        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_stripe_health(self) -> Dict[str, Any]:
        """Check Stripe API connectivity"""
        try:
            from api.secure_keys import billing_key_manager
            
            # Test Stripe API key validity
            stripe_secret = billing_key_manager.get_stripe_secret_key()
            
            if not stripe_secret.startswith('sk_live_'):
                return {
                    'status': 'error',
                    'error': 'Invalid Stripe secret key format',
                    'timestamp': time.time()
                }
            
            # Test Stripe API connection
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {stripe_secret}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                start_time = time.time()
                async with session.get(
                    'https://api.stripe.com/v1/account',
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            'status': 'healthy',
                            'response_time': duration,
                            'status_code': response.status,
                            'timestamp': time.time()
                        }
                    else:
                        return {
                            'status': 'error',
                            'response_time': duration,
                            'status_code': response.status,
                            'error': f"HTTP {response.status}",
                            'timestamp': time.time()
                        }
                        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from api.database import get_database_manager
            
            db_manager = get_database_manager()
            start_time = time.time()
            
            # Test database connection
            async with db_manager.get_connection() as conn:
                await conn.execute("SELECT 1")
                duration = time.time() - start_time
                
                # Get connection pool stats
                pool_stats = {}
                if db_manager.pool:
                    try:
                        pool_stats = {
                            'size': getattr(db_manager.pool, 'get_size', lambda: 0)(),
                            'free_size': getattr(db_manager.pool, 'get_free_size', lambda: 0)()
                        }
                    except Exception:
                        pool_stats = {'size': 0, 'free_size': 0}
                
                return {
                    'status': 'healthy',
                    'response_time': duration,
                    'pool_stats': pool_stats,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            if memory.percent > 80:
                status = 'warning'
            if memory.percent > 95:
                status = 'critical'
            
            return {
                'status': status,
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'timestamp': time.time()
            }
            
        except ImportError:
            return {
                'status': 'unknown',
                'error': 'psutil not available',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            status = 'healthy'
            if disk.percent > 80:
                status = 'warning'
            if disk.percent > 95:
                status = 'critical'
            
            return {
                'status': status,
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
                'timestamp': time.time()
            }
            
        except ImportError:
            return {
                'status': 'unknown',
                'error': 'psutil not available',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Test external connectivity
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://httpbin.org/get',
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            'status': 'healthy',
                            'response_time': duration,
                            'status_code': response.status,
                            'timestamp': time.time()
                        }
                    else:
                        return {
                            'status': 'error',
                            'response_time': duration,
                            'status_code': response.status,
                            'timestamp': time.time()
                        }
                        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def run_health_check(self, check_name: str) -> Dict[str, Any]:
        """Run specific health check"""
        if check_name not in self.checks:
            return {
                'status': 'error',
                'error': f'Unknown health check: {check_name}',
                'timestamp': time.time()
            }
        
        try:
            result = await self.checks[check_name]()
            self.logger.log_system_health(check_name, result['status'], result)
            return result
        except Exception as e:
            result = {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
            self.logger.log_system_health(check_name, 'error', result)
            return result
    
    async def run_all_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        start_time = time.time()
        
        for check_name in self.checks:
            results[check_name] = await self.run_health_check(check_name)
        
        # Determine overall status
        statuses = [result['status'] for result in results.values()]
        
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'error' in statuses:
            overall_status = 'error'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'checks': results,
            'total_duration': time.time() - start_time,
            'timestamp': time.time()
        }
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for monitoring"""
        all_checks = await self.run_all_health_checks()
        
        # Count by status
        status_counts = {}
        for check_result in all_checks['checks'].values():
            status = check_result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'overall_status': all_checks['status'],
            'status_counts': status_counts,
            'total_checks': len(all_checks['checks']),
            'timestamp': all_checks['timestamp']
        }
    
    def add_custom_check(self, name: str, check_func: Any):
        """Add custom health check"""
        self.checks[name] = check_func
        self.logger.logger.info(f"Added custom health check: {name}")

# Global health checker instance
health_checker = HealthChecker()

def get_health_checker() -> HealthChecker:
    """Get global health checker instance"""
    return health_checker 