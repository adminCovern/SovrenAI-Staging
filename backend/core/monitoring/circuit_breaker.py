#!/usr/bin/env python3
"""
SOVREN AI - Circuit Breaker Pattern Implementation
Production-ready fault tolerance with automatic recovery and monitoring
"""

import time
import threading
import logging
import random
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger('CircuitBreaker')

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds
    half_open_max_calls: int = 3
    monitoring_window: float = 300.0  # seconds
    success_threshold: int = 2
    timeout_threshold: float = 30.0  # seconds

@dataclass
class CircuitMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None

class CircuitBreaker:
    """Production-ready circuit breaker implementation"""
    
    def __init__(self, name: str, config: Optional[CircuitConfig] = None):
        self.name = name
        self.config = config or CircuitConfig()
        
        # Circuit state
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        self.failure_count = 0
        self.success_count = 0
        
        # Metrics and monitoring
        self.metrics = CircuitMetrics()
        self.request_history = deque(maxlen=1000)
        self.failure_history = deque(maxlen=100)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Callbacks
        self.on_open_callbacks: List[Callable] = []
        self.on_close_callbacks: List[Callable] = []
        self.on_half_open_callbacks: List[Callable] = []
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    def call(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with circuit breaker protection"""
        
        # Check circuit state
        if not self._can_execute():
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        start_time = time.time()
        success = False
        
        try:
            # Execute operation with timeout
            result = self._execute_with_timeout(operation, *args, **kwargs)
            success = True
            return result
            
        except Exception as e:
            self._record_failure(e, time.time() - start_time)
            raise
            
        finally:
            if success:
                self._record_success(time.time() - start_time)
    
    async def call_async(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute async operation with circuit breaker protection"""
        
        # Check circuit state
        if not self._can_execute():
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        start_time = time.time()
        success = False
        
        try:
            # Execute async operation
            result = await operation(*args, **kwargs)
            success = True
            return result
            
        except Exception as e:
            self._record_failure(e, time.time() - start_time)
            raise
            
        finally:
            if success:
                self._record_success(time.time() - start_time)
    
    def _can_execute(self) -> bool:
        """Check if operation can be executed based on circuit state"""
        
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            elif self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self.last_state_change >= self.config.recovery_timeout:
                    self._transition_to_half_open()
                    return True
                return False
            
            elif self.state == CircuitState.HALF_OPEN:
                # Allow limited number of test calls
                return self.success_count < self.config.half_open_max_calls
            
            return False
    
    def _execute_with_timeout(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with timeout protection"""
        
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(operation, *args, **kwargs)
            
            try:
                result = future.result(timeout=self.config.timeout_threshold)
                return result
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise CircuitBreakerTimeoutError(f"Operation timed out after {self.config.timeout_threshold}s")
    
    def _record_failure(self, error: Exception, duration: float):
        """Record operation failure"""
        
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_failure_time = time.time()
            
            # Record failure details
            failure_info = {
                'timestamp': time.time(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'duration': duration,
            }
            self.failure_history.append(failure_info)
            
            # Update failure count
            self.failure_count += 1
            
            # Check if circuit should open
            if self._should_open_circuit():
                self._transition_to_open()
            
            logger.warning(f"Circuit breaker '{self.name}' failure: {error}")
    
    def _record_success(self, duration: float):
        """Record operation success"""
        
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.last_success_time = time.time()
            
            # Record success details
            success_info = {
                'timestamp': time.time(),
                'duration': duration,
            }
            self.request_history.append(success_info)
            
            # Update success count
            self.success_count += 1
            
            # Check if circuit should close
            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.config.success_threshold:
                    self._transition_to_closed()
            
            logger.debug(f"Circuit breaker '{self.name}' success")
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should open based on failure threshold"""
        
        # Check recent failures within monitoring window
        cutoff_time = time.time() - self.config.monitoring_window
        recent_failures = [
            failure for failure in self.failure_history
            if failure['timestamp'] > cutoff_time
        ]
        
        return len(recent_failures) >= self.config.failure_threshold
    
    def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            self.metrics.circuit_opens += 1
            
            # Reset counters
            self.failure_count = 0
            self.success_count = 0
            
            # Notify callbacks
            for callback in self.on_open_callbacks:
                try:
                    callback(self.name)
                except Exception as e:
                    logger.error(f"Circuit breaker open callback error: {e}")
            
            logger.warning(f"Circuit breaker '{self.name}' opened")
    
    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.last_state_change = time.time()
            
            # Reset counters for half-open testing
            self.failure_count = 0
            self.success_count = 0
            
            # Notify callbacks
            for callback in self.on_half_open_callbacks:
                try:
                    callback(self.name)
                except Exception as e:
                    logger.error(f"Circuit breaker half-open callback error: {e}")
            
            logger.info(f"Circuit breaker '{self.name}' half-opened")
    
    def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()
            self.metrics.circuit_closes += 1
            
            # Reset counters
            self.failure_count = 0
            self.success_count = 0
            
            # Notify callbacks
            for callback in self.on_close_callbacks:
                try:
                    callback(self.name)
                except Exception as e:
                    logger.error(f"Circuit breaker close callback error: {e}")
            
            logger.info(f"Circuit breaker '{self.name}' closed")
    
    def force_open(self):
        """Force circuit to OPEN state"""
        with self._lock:
            self._transition_to_open()
    
    def force_close(self):
        """Force circuit to CLOSED state"""
        with self._lock:
            self._transition_to_closed()
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()
            self.failure_count = 0
            self.success_count = 0
            self.metrics = CircuitMetrics()
            self.request_history.clear()
            self.failure_history.clear()
            
            logger.info(f"Circuit breaker '{self.name}' reset")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'last_state_change': self.last_state_change,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'metrics': {
                    'total_requests': self.metrics.total_requests,
                    'successful_requests': self.metrics.successful_requests,
                    'failed_requests': self.metrics.failed_requests,
                    'timeout_requests': self.metrics.timeout_requests,
                    'circuit_opens': self.metrics.circuit_opens,
                    'circuit_closes': self.metrics.circuit_closes,
                    'last_failure_time': self.metrics.last_failure_time,
                    'last_success_time': self.metrics.last_success_time,
                },
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'half_open_max_calls': self.config.half_open_max_calls,
                    'monitoring_window': self.config.monitoring_window,
                    'success_threshold': self.config.success_threshold,
                    'timeout_threshold': self.config.timeout_threshold,
                },
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get circuit breaker health status"""
        
        with self._lock:
            # Calculate success rate
            total_requests = self.metrics.total_requests
            success_rate = 0.0
            if total_requests > 0:
                success_rate = (self.metrics.successful_requests / total_requests) * 100
            
            # Determine health status
            if self.state == CircuitState.OPEN:
                health_status = "unhealthy"
            elif self.state == CircuitState.HALF_OPEN:
                health_status = "degraded"
            elif success_rate < 95.0:
                health_status = "warning"
            else:
                health_status = "healthy"
            
            return {
                'name': self.name,
                'status': health_status,
                'state': self.state.value,
                'success_rate': success_rate,
                'total_requests': total_requests,
                'recent_failures': len(self.failure_history),
                'uptime_percent': self._calculate_uptime(),
            }
    
    def _calculate_uptime(self) -> float:
        """Calculate circuit breaker uptime percentage"""
        
        if not self.request_history:
            return 100.0
        
        # Calculate uptime based on successful vs failed requests
        total_requests = len(self.request_history) + len(self.failure_history)
        if total_requests == 0:
            return 100.0
        
        successful_requests = len(self.request_history)
        return (successful_requests / total_requests) * 100
    
    def add_on_open_callback(self, callback: Callable):
        """Add callback for circuit open events"""
        self.on_open_callbacks.append(callback)
    
    def add_on_close_callback(self, callback: Callable):
        """Add callback for circuit close events"""
        self.on_close_callbacks.append(callback)
    
    def add_on_half_open_callback(self, callback: Callable):
        """Add callback for circuit half-open events"""
        self.on_half_open_callbacks.append(callback)


class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
        
        # Global metrics
        self.global_metrics = {
            'total_circuits': 0,
            'open_circuits': 0,
            'half_open_circuits': 0,
            'closed_circuits': 0,
        }
    
    def create_circuit_breaker(self, name: str, config: Optional[CircuitConfig] = None) -> CircuitBreaker:
        """Create a new circuit breaker"""
        
        with self._lock:
            if name in self.circuit_breakers:
                raise ValueError(f"Circuit breaker '{name}' already exists")
            
            circuit_breaker = CircuitBreaker(name, config)
            self.circuit_breakers[name] = circuit_breaker
            self.global_metrics['total_circuits'] += 1
            
            # Add state change callbacks
            circuit_breaker.add_on_open_callback(self._on_circuit_state_change)
            circuit_breaker.add_on_close_callback(self._on_circuit_state_change)
            circuit_breaker.add_on_half_open_callback(self._on_circuit_state_change)
            
            logger.info(f"Created circuit breaker '{name}'")
            return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker"""
        
        with self._lock:
            if name in self.circuit_breakers:
                del self.circuit_breakers[name]
                self.global_metrics['total_circuits'] -= 1
                logger.info(f"Removed circuit breaker '{name}'")
                return True
            return False
    
    def _on_circuit_state_change(self, circuit_name: str):
        """Handle circuit state changes"""
        
        with self._lock:
            # Update global metrics
            open_count = 0
            half_open_count = 0
            closed_count = 0
            
            for circuit in self.circuit_breakers.values():
                if circuit.state == CircuitState.OPEN:
                    open_count += 1
                elif circuit.state == CircuitState.HALF_OPEN:
                    half_open_count += 1
                elif circuit.state == CircuitState.CLOSED:
                    closed_count += 1
            
            self.global_metrics['open_circuits'] = open_count
            self.global_metrics['half_open_circuits'] = half_open_count
            self.global_metrics['closed_circuits'] = closed_count
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers"""
        
        with self._lock:
            return {
                name: circuit.get_state()
                for name, circuit in self.circuit_breakers.items()
            }
    
    def get_global_health(self) -> Dict[str, Any]:
        """Get global health status"""
        
        with self._lock:
            total_circuits = len(self.circuit_breakers)
            if total_circuits == 0:
                return {
                    'status': 'healthy',
                    'total_circuits': 0,
                    'unhealthy_circuits': 0,
                    'health_percentage': 100.0,
                }
            
            # Calculate health metrics
            unhealthy_circuits = 0
            for circuit in self.circuit_breakers.values():
                health = circuit.get_health_status()
                if health['status'] in ['unhealthy', 'degraded']:
                    unhealthy_circuits += 1
            
            health_percentage = ((total_circuits - unhealthy_circuits) / total_circuits) * 100
            
            # Determine overall status
            if health_percentage >= 95.0:
                status = 'healthy'
            elif health_percentage >= 80.0:
                status = 'warning'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'total_circuits': total_circuits,
                'unhealthy_circuits': unhealthy_circuits,
                'health_percentage': health_percentage,
                'metrics': self.global_metrics,
            }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerTimeoutError(Exception):
    """Exception raised when operation times out"""
    pass


# Decorator for easy circuit breaker usage
def circuit_breaker(name: str, config: Optional[CircuitConfig] = None):
    """Decorator to add circuit breaker protection to functions"""
    
    def decorator(func):
        # Create circuit breaker instance
        cb = CircuitBreaker(name, config)
        
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        # Store circuit breaker reference
        wrapper.circuit_breaker = cb
        return wrapper
    
    return decorator


# Example usage:
# @circuit_breaker("database_connection", CircuitConfig(failure_threshold=3))
# def database_query(query: str):
#     # Database operation here
#     pass 