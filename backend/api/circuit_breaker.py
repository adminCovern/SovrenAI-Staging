#!/usr/bin/env python3
"""
SOVREN Billing System - Circuit Breaker
Production-grade circuit breaker for external API resilience
"""

import asyncio
import time
import logging
from typing import Callable, Any, Optional, Type
from enum import Enum
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger('CircuitBreaker')

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5      # Failures before opening circuit
    recovery_timeout: float = 60.0  # Seconds to wait before half-open
    expected_exception: Type[Exception] = Exception  # Exception type to catch
    monitor_interval: float = 10.0  # Seconds between health checks

class CircuitBreaker:
    """Production circuit breaker implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = time.time()
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    await self._set_half_open()
                else:
                    raise Exception(f"Circuit breaker '{self.name}' is OPEN")
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                await self._on_success()
                return result
                
            except self.config.expected_exception as e:
                await self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    async def _set_half_open(self):
        """Set circuit to half-open state"""
        self.state = CircuitState.HALF_OPEN
        logger.info(f"Circuit breaker '{self.name}' is HALF_OPEN")
    
    async def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit breaker '{self.name}' is CLOSED")
    
    async def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' is OPEN after {self.failure_count} failures")
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout
            }
        }

def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator for circuit breaker pattern"""
    def decorator(func: Callable) -> Callable:
        cb = CircuitBreaker(name, config or CircuitBreakerConfig())
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(cb.call(func, *args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, config or CircuitBreakerConfig())
        return self.circuit_breakers[name]
    
    def get_all_stats(self) -> dict:
        """Get statistics for all circuit breakers"""
        return {
            name: cb.get_stats() 
            for name, cb in self.circuit_breakers.items()
        }
    
    async def health_check(self) -> dict:
        """Perform health check on all circuit breakers"""
        stats = self.get_all_stats()
        open_circuits = [
            name for name, stat in stats.items() 
            if stat['state'] == CircuitState.OPEN.value
        ]
        
        return {
            'total_circuits': len(stats),
            'open_circuits': len(open_circuits),
            'open_circuit_names': open_circuits,
            'circuits': stats
        } 