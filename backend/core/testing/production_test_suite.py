#!/usr/bin/env python3
"""
SOVREN AI - Production Test Suite
Comprehensive testing with load testing, chaos engineering, and security validation
"""

import time
import threading
import logging
import json
import random
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import requests
import concurrent.futures
import statistics
import hashlib
import ssl
import socket

logger = logging.getLogger('ProductionTestSuite')

class TestType(Enum):
    """Test types"""
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    CHAOS_TEST = "chaos_test"
    SECURITY_TEST = "security_test"
    INTEGRATION_TEST = "integration_test"
    PERFORMANCE_TEST = "performance_test"

class TestResult(Enum):
    """Test result types"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    TIMEOUT = "timeout"

@dataclass
class TestConfig:
    """Test configuration"""
    base_url: str
    endpoints: List[str]
    load_test_duration: int = 300  # 5 minutes
    load_test_concurrent_users: int = 100
    stress_test_max_users: int = 1000
    chaos_test_probability: float = 0.1
    security_test_timeout: int = 30
    performance_threshold_ms: int = 1000

@dataclass
class TestResultData:
    """Test result data"""
    test_id: str
    test_type: TestType
    start_time: datetime
    end_time: datetime
    duration: float
    result: TestResult
    metrics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class ProductionTestSuite:
    """Production-ready comprehensive test suite"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.test_results: List[TestResultData] = []
        self.active_tests: Dict[str, threading.Thread] = {}
        
        # Performance metrics
        self.response_times = []
        self.error_rates = []
        self.throughput_metrics = []
        
        # Security test data
        self.security_vulnerabilities = []
        self.penetration_test_results = []
        
        # Chaos engineering
        self.chaos_events = []
        self.system_resilience_score = 0.0
        
        logger.info("Production test suite initialized")
    
    def run_load_test(self, duration: Optional[int] = None, 
                     concurrent_users: Optional[int] = None) -> str:
        """Run comprehensive load test"""
        
        test_id = f"load_test_{int(time.time())}"
        duration = duration or self.config.load_test_duration
        concurrent_users = concurrent_users or self.config.load_test_concurrent_users
        
        def load_test_worker():
            try:
                start_time = datetime.now()
                response_times = []
                errors = []
                requests_sent = 0
                
                end_time = start_time + timedelta(seconds=duration)
                
                while datetime.now() < end_time:
                    # Simulate concurrent users
                    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                        futures = []
                        
                        for _ in range(concurrent_users):
                            endpoint = random.choice(self.config.endpoints)
                            future = executor.submit(self._make_request, endpoint)
                            futures.append(future)
                        
                        # Collect results
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                response_time, success = future.result()
                                response_times.append(response_time)
                                requests_sent += 1
                                
                                if not success:
                                    errors.append(f"Request failed after {response_time}ms")
                                    
                            except Exception as e:
                                errors.append(str(e))
                                requests_sent += 1
                
                # Calculate metrics
                total_duration = (datetime.now() - start_time).total_seconds()
                throughput = requests_sent / total_duration
                avg_response_time = statistics.mean(response_times) if response_times else 0
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0
                error_rate = len(errors) / requests_sent if requests_sent > 0 else 0
                
                # Determine result
                if error_rate < 0.01 and avg_response_time < self.config.performance_threshold_ms:
                    result = TestResult.PASS
                elif error_rate < 0.05:
                    result = TestResult.WARNING
                else:
                    result = TestResult.FAIL
                
                # Store result
                test_result = TestResultData(
                    test_id=test_id,
                    test_type=TestType.LOAD_TEST,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=total_duration,
                    result=result,
                    metrics={
                        'requests_sent': requests_sent,
                        'throughput_rps': throughput,
                        'avg_response_time_ms': avg_response_time,
                        'p95_response_time_ms': p95_response_time,
                        'error_rate': error_rate,
                        'concurrent_users': concurrent_users,
                    },
                    errors=errors,
                    warnings=[],
                )
                
                self.test_results.append(test_result)
                logger.info(f"Load test completed: {result.value}")
                
            except Exception as e:
                logger.error(f"Load test failed: {e}")
        
        # Start test in background thread
        thread = threading.Thread(target=load_test_worker, daemon=True)
        self.active_tests[test_id] = thread
        thread.start()
        
        return test_id
    
    def run_stress_test(self, max_users: Optional[int] = None) -> str:
        """Run stress test to find system limits"""
        
        test_id = f"stress_test_{int(time.time())}"
        max_users = max_users or self.config.stress_test_max_users
        
        def stress_test_worker():
            try:
                start_time = datetime.now()
                current_users = 10
                max_sustainable_users = 0
                breaking_point = 0
                
                while current_users <= max_users:
                    logger.info(f"Stress test: testing with {current_users} users")
                    
                    # Test with current user count
                    success_rate = self._test_user_load(current_users)
                    
                    if success_rate >= 0.95:  # 95% success rate
                        max_sustainable_users = current_users
                        current_users = int(current_users * 1.5)
                    elif success_rate >= 0.8:  # 80% success rate
                        breaking_point = current_users
                        break
                    else:
                        breaking_point = current_users
                        break
                
                # Determine result
                if max_sustainable_users >= max_users * 0.8:
                    result = TestResult.PASS
                elif max_sustainable_users >= max_users * 0.5:
                    result = TestResult.WARNING
                else:
                    result = TestResult.FAIL
                
                # Store result
                test_result = TestResultData(
                    test_id=test_id,
                    test_type=TestType.STRESS_TEST,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds(),
                    result=result,
                    metrics={
                        'max_sustainable_users': max_sustainable_users,
                        'breaking_point': breaking_point,
                        'target_users': max_users,
                    },
                    errors=[],
                    warnings=[],
                )
                
                self.test_results.append(test_result)
                logger.info(f"Stress test completed: max sustainable users = {max_sustainable_users}")
                
            except Exception as e:
                logger.error(f"Stress test failed: {e}")
        
        # Start test in background thread
        thread = threading.Thread(target=stress_test_worker, daemon=True)
        self.active_tests[test_id] = thread
        thread.start()
        
        return test_id
    
    def run_chaos_test(self, duration: int = 300) -> str:
        """Run chaos engineering tests"""
        
        test_id = f"chaos_test_{int(time.time())}"
        
        def chaos_test_worker():
            try:
                start_time = datetime.now()
                chaos_events = []
                system_recovery_times = []
                
                end_time = start_time + timedelta(seconds=duration)
                
                while datetime.now() < end_time:
                    # Randomly trigger chaos events
                    if random.random() < self.config.chaos_test_probability:
                        event_type = random.choice([
                            'network_latency',
                            'service_failure',
                            'memory_pressure',
                            'cpu_spike',
                            'disk_io_slowdown'
                        ])
                        
                        event_start = datetime.now()
                        self._trigger_chaos_event(event_type)
                        
                        # Monitor system recovery
                        recovery_time = self._monitor_system_recovery()
                        system_recovery_times.append(recovery_time)
                        
                        chaos_events.append({
                            'type': event_type,
                            'timestamp': event_start.isoformat(),
                            'recovery_time_ms': recovery_time,
                        })
                        
                        logger.info(f"Chaos event triggered: {event_type}, recovery time: {recovery_time}ms")
                    
                    time.sleep(10)  # Wait between events
                
                # Calculate resilience score
                avg_recovery_time = statistics.mean(system_recovery_times) if system_recovery_times else 0
                max_recovery_time = max(system_recovery_times) if system_recovery_times else 0
                
                # Resilience score based on recovery times
                if avg_recovery_time < 5000:  # 5 seconds
                    resilience_score = 1.0
                elif avg_recovery_time < 15000:  # 15 seconds
                    resilience_score = 0.7
                elif avg_recovery_time < 30000:  # 30 seconds
                    resilience_score = 0.4
                else:
                    resilience_score = 0.1
                
                # Determine result
                if resilience_score >= 0.8:
                    result = TestResult.PASS
                elif resilience_score >= 0.5:
                    result = TestResult.WARNING
                else:
                    result = TestResult.FAIL
                
                # Store result
                test_result = TestResultData(
                    test_id=test_id,
                    test_type=TestType.CHAOS_TEST,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds(),
                    result=result,
                    metrics={
                        'resilience_score': resilience_score,
                        'avg_recovery_time_ms': avg_recovery_time,
                        'max_recovery_time_ms': max_recovery_time,
                        'chaos_events_count': len(chaos_events),
                    },
                    errors=[],
                    warnings=[],
                )
                
                self.test_results.append(test_result)
                self.chaos_events.extend(chaos_events)
                self.system_resilience_score = resilience_score
                
                logger.info(f"Chaos test completed: resilience score = {resilience_score:.2f}")
                
            except Exception as e:
                logger.error(f"Chaos test failed: {e}")
        
        # Start test in background thread
        thread = threading.Thread(target=chaos_test_worker, daemon=True)
        self.active_tests[test_id] = thread
        thread.start()
        
        return test_id
    
    def run_security_test(self) -> str:
        """Run comprehensive security tests"""
        
        test_id = f"security_test_{int(time.time())}"
        
        def security_test_worker():
            try:
                start_time = datetime.now()
                vulnerabilities = []
                penetration_results = []
                
                # SSL/TLS Security Test
                ssl_score = self._test_ssl_security()
                if ssl_score < 0.8:
                    vulnerabilities.append({
                        'type': 'ssl_security',
                        'severity': 'high',
                        'description': f'SSL security score: {ssl_score:.2f}',
                    })
                
                # Authentication Security Test
                auth_vulnerabilities = self._test_authentication_security()
                vulnerabilities.extend(auth_vulnerabilities)
                
                # Input Validation Test
                input_vulnerabilities = self._test_input_validation()
                vulnerabilities.extend(input_vulnerabilities)
                
                # SQL Injection Test
                sql_injection_results = self._test_sql_injection()
                penetration_results.extend(sql_injection_results)
                
                # XSS Test
                xss_results = self._test_xss_vulnerabilities()
                penetration_results.extend(xss_results)
                
                # Calculate security score
                total_vulnerabilities = len(vulnerabilities)
                high_severity_vulns = len([v for v in vulnerabilities if v['severity'] == 'high'])
                
                if high_severity_vulns == 0 and total_vulnerabilities <= 2:
                    security_score = 1.0
                elif high_severity_vulns == 0 and total_vulnerabilities <= 5:
                    security_score = 0.8
                elif high_severity_vulns <= 1:
                    security_score = 0.6
                else:
                    security_score = 0.3
                
                # Determine result
                if security_score >= 0.8:
                    result = TestResult.PASS
                elif security_score >= 0.6:
                    result = TestResult.WARNING
                else:
                    result = TestResult.FAIL
                
                # Store result
                test_result = TestResultData(
                    test_id=test_id,
                    test_type=TestType.SECURITY_TEST,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds(),
                    result=result,
                    metrics={
                        'security_score': security_score,
                        'total_vulnerabilities': total_vulnerabilities,
                        'high_severity_vulns': high_severity_vulns,
                        'ssl_score': ssl_score,
                    },
                    errors=[],
                    warnings=[],
                )
                
                self.test_results.append(test_result)
                self.security_vulnerabilities.extend(vulnerabilities)
                self.penetration_test_results.extend(penetration_results)
                
                logger.info(f"Security test completed: security score = {security_score:.2f}")
                
            except Exception as e:
                logger.error(f"Security test failed: {e}")
        
        # Start test in background thread
        thread = threading.Thread(target=security_test_worker, daemon=True)
        self.active_tests[test_id] = thread
        thread.start()
        
        return test_id
    
    def _make_request(self, endpoint: str) -> "tuple[float, bool]":
        """Make HTTP request and return response time and success status"""
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.config.base_url}{endpoint}",
                timeout=self.config.security_test_timeout
            )
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            success = 200 <= response.status_code < 400
            return response_time, success
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return response_time, False
    
    def _test_user_load(self, user_count: int) -> float:
        """Test system with specified user load"""
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=user_count) as executor:
                futures = []
                
                for _ in range(user_count):
                    endpoint = random.choice(self.config.endpoints)
                    future = executor.submit(self._make_request, endpoint)
                    futures.append(future)
                
                # Collect results
                successful_requests = 0
                total_requests = len(futures)
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        _, success = future.result()
                        if success:
                            successful_requests += 1
                    except Exception:
                        pass
                
                return successful_requests / total_requests if total_requests > 0 else 0
                
        except Exception as e:
            logger.error(f"User load test failed: {e}")
            return 0.0
    
    def _trigger_chaos_event(self, event_type: str):
        """Trigger chaos engineering event"""
        
        try:
            if event_type == 'network_latency':
                # Simulate network latency
                time.sleep(random.uniform(0.1, 0.5))
                
            elif event_type == 'service_failure':
                # Simulate service failure
                if random.random() < 0.3:
                    raise Exception("Simulated service failure")
                    
            elif event_type == 'memory_pressure':
                # Simulate memory pressure
                large_data = [random.random() for _ in range(1000000)]
                time.sleep(0.1)
                del large_data
                
            elif event_type == 'cpu_spike':
                # Simulate CPU spike
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    _ = hashlib.sha256(str(random.random()).encode()).hexdigest()
                    
            elif event_type == 'disk_io_slowdown':
                # Simulate disk I/O slowdown
                time.sleep(random.uniform(0.2, 1.0))
                
        except Exception as e:
            logger.warning(f"Chaos event {event_type} triggered: {e}")
    
    def _monitor_system_recovery(self) -> float:
        """Monitor system recovery time"""
        
        start_time = time.time()
        max_wait_time = 30.0  # 30 seconds max
        
        while time.time() - start_time < max_wait_time:
            try:
                # Test basic functionality
                response = requests.get(f"{self.config.base_url}/health", timeout=5)
                if response.status_code == 200:
                    return (time.time() - start_time) * 1000  # Return recovery time in ms
            except Exception:
                time.sleep(0.1)
        
        return max_wait_time * 1000  # Return max wait time if no recovery
    
    def _test_ssl_security(self) -> float:
        """Test SSL/TLS security"""
        
        try:
            # Parse URL to get hostname
            from urllib.parse import urlparse
            parsed_url = urlparse(self.config.base_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Test SSL connection
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    if not cert:
                        return 0.0
                    
                    # Check certificate expiration
                    not_after_str = cert['notAfter']
                    if isinstance(not_after_str, str):
                        not_after = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (not_after - datetime.now()).days
                    else:
                        return 0.0
                    
                    if days_until_expiry < 30:
                        return 0.5
                    elif days_until_expiry < 90:
                        return 0.8
                    else:
                        return 1.0
                        
        except Exception as e:
            logger.error(f"SSL security test failed: {e}")
            return 0.0
    
    def _test_authentication_security(self) -> List[Dict[str, Any]]:
        """Test authentication security"""
        
        vulnerabilities = []
        
        try:
            # Test weak password endpoints
            weak_passwords = ['admin', 'password', '123456', 'test']
            
            for password in weak_passwords:
                try:
                    response = requests.post(
                        f"{self.config.base_url}/auth/login",
                        json={'username': 'admin', 'password': password},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            'type': 'weak_password',
                            'severity': 'high',
                            'description': f'Weak password accepted: {password}',
                        })
                        
                except Exception:
                    pass
            
            # Test brute force protection
            for _ in range(10):
                try:
                    response = requests.post(
                        f"{self.config.base_url}/auth/login",
                        json={'username': 'admin', 'password': 'wrong_password'},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            'type': 'no_brute_force_protection',
                            'severity': 'high',
                            'description': 'No brute force protection detected',
                        })
                        break
                        
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Authentication security test failed: {e}")
        
        return vulnerabilities
    
    def _test_input_validation(self) -> List[Dict[str, Any]]:
        """Test input validation security"""
        
        vulnerabilities = []
        
        try:
            # Test SQL injection payloads
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
            ]
            
            for payload in sql_payloads:
                try:
                    response = requests.get(
                        f"{self.config.base_url}/api/users",
                        params={'id': payload},
                        timeout=5
                    )
                    
                    # Check for SQL error messages
                    if any(error in response.text.lower() for error in ['sql', 'mysql', 'postgresql', 'oracle']):
                        vulnerabilities.append({
                            'type': 'sql_injection',
                            'severity': 'critical',
                            'description': f'SQL injection vulnerability detected with payload: {payload}',
                        })
                        
                except Exception:
                    pass
            
            # Test XSS payloads
            xss_payloads = [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "javascript:alert('xss')",
            ]
            
            for payload in xss_payloads:
                try:
                    response = requests.post(
                        f"{self.config.base_url}/api/comments",
                        json={'content': payload},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        # Check if payload is reflected in response
                        if payload in response.text:
                            vulnerabilities.append({
                                'type': 'xss',
                                'severity': 'high',
                                'description': f'XSS vulnerability detected with payload: {payload}',
                            })
                            
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Input validation test failed: {e}")
        
        return vulnerabilities
    
    def _test_sql_injection(self) -> List[Dict[str, Any]]:
        """Test for SQL injection vulnerabilities"""
        
        results = []
        
        try:
            # Test various SQL injection techniques
            injection_payloads = [
                "' OR 1=1 --",
                "' UNION SELECT NULL --",
                "'; WAITFOR DELAY '00:00:05' --",
                "' AND (SELECT COUNT(*) FROM users) > 0 --",
            ]
            
            for payload in injection_payloads:
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.config.base_url}/api/users",
                        params={'id': payload},
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    # Check for time-based injection
                    if response_time > 5:
                        results.append({
                            'type': 'time_based_sql_injection',
                            'severity': 'critical',
                            'payload': payload,
                            'response_time': response_time,
                        })
                    
                    # Check for error-based injection
                    if any(error in response.text.lower() for error in ['sql', 'mysql', 'postgresql']):
                        results.append({
                            'type': 'error_based_sql_injection',
                            'severity': 'critical',
                            'payload': payload,
                            'response_text': response.text[:200],
                        })
                        
                except Exception as e:
                    results.append({
                        'type': 'sql_injection_test_error',
                        'severity': 'medium',
                        'payload': payload,
                        'error': str(e),
                    })
                    
        except Exception as e:
            logger.error(f"SQL injection test failed: {e}")
        
        return results
    
    def _test_xss_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Test for XSS vulnerabilities"""
        
        results = []
        
        try:
            # Test various XSS payloads
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "<iframe src=javascript:alert('XSS')>",
            ]
            
            for payload in xss_payloads:
                try:
                    response = requests.post(
                        f"{self.config.base_url}/api/comments",
                        json={'content': payload},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        # Check if payload is reflected
                        if payload in response.text:
                            results.append({
                                'type': 'reflected_xss',
                                'severity': 'high',
                                'payload': payload,
                            })
                        
                        # Check for stored XSS
                        stored_response = requests.get(
                            f"{self.config.base_url}/api/comments",
                            timeout=5
                        )
                        
                        if payload in stored_response.text:
                            results.append({
                                'type': 'stored_xss',
                                'severity': 'critical',
                                'payload': payload,
                            })
                            
                except Exception as e:
                    results.append({
                        'type': 'xss_test_error',
                        'severity': 'medium',
                        'payload': payload,
                        'error': str(e),
                    })
                    
        except Exception as e:
            logger.error(f"XSS test failed: {e}")
        
        return results
    
    def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get test status"""
        
        # Check if test is active
        if test_id in self.active_tests:
            thread = self.active_tests[test_id]
            return {
                'test_id': test_id,
                'status': 'running',
                'thread_alive': thread.is_alive(),
            }
        
        # Check completed tests
        for result in self.test_results:
            if result.test_id == test_id:
                return {
                    'test_id': test_id,
                    'status': 'completed',
                    'result': result.result.value,
                    'duration': result.duration,
                    'metrics': result.metrics,
                    'errors': result.errors,
                    'warnings': result.warnings,
                }
        
        return None
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        try:
            # Calculate overall metrics
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r.result == TestResult.PASS])
            failed_tests = len([r for r in self.test_results if r.result == TestResult.FAIL])
            warning_tests = len([r for r in self.test_results if r.result == TestResult.WARNING])
            
            # Calculate average metrics
            avg_response_time = 0
            avg_throughput = 0
            avg_error_rate = 0
            
            load_tests = [r for r in self.test_results if r.test_type == TestType.LOAD_TEST]
            if load_tests:
                response_times = [r.metrics.get('avg_response_time_ms', 0) for r in load_tests]
                throughputs = [r.metrics.get('throughput_rps', 0) for r in load_tests]
                error_rates = [r.metrics.get('error_rate', 0) for r in load_tests]
                
                avg_response_time = statistics.mean(response_times)
                avg_throughput = statistics.mean(throughputs)
                avg_error_rate = statistics.mean(error_rates)
            
            # Security summary
            security_tests = [r for r in self.test_results if r.test_type == TestType.SECURITY_TEST]
            security_score = 0
            if security_tests:
                security_score = statistics.mean([r.metrics.get('security_score', 0) for r in security_tests])
            
            return {
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'warning_tests': warning_tests,
                    'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                },
                'performance': {
                    'avg_response_time_ms': avg_response_time,
                    'avg_throughput_rps': avg_throughput,
                    'avg_error_rate': avg_error_rate,
                },
                'security': {
                    'security_score': security_score,
                    'vulnerabilities_count': len(self.security_vulnerabilities),
                    'penetration_tests_count': len(self.penetration_test_results),
                },
                'resilience': {
                    'system_resilience_score': self.system_resilience_score,
                    'chaos_events_count': len(self.chaos_events),
                },
                'recommendations': self._generate_recommendations(),
            }
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return {}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Performance recommendations
        load_tests = [r for r in self.test_results if r.test_type == TestType.LOAD_TEST]
        if load_tests:
            latest_load_test = max(load_tests, key=lambda x: x.start_time)
            
            if latest_load_test.metrics.get('avg_response_time_ms', 0) > self.config.performance_threshold_ms:
                recommendations.append("Consider optimizing response times - current average exceeds threshold")
            
            if latest_load_test.metrics.get('error_rate', 0) > 0.01:
                recommendations.append("High error rate detected - investigate system stability")
        
        # Security recommendations
        if self.security_vulnerabilities:
            high_severity_vulns = [v for v in self.security_vulnerabilities if v['severity'] == 'high']
            if high_severity_vulns:
                recommendations.append(f"Critical security vulnerabilities detected: {len(high_severity_vulns)} high-severity issues")
        
        # Resilience recommendations
        if self.system_resilience_score < 0.8:
            recommendations.append("System resilience below target - implement additional fault tolerance")
        
        return recommendations 