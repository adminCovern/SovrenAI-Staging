#!/usr/bin/env python3
"""
SOVREN Billing System - Structured Logging
Production-grade logging with correlation IDs and structured output
"""

import logging
import json
import time
import uuid
import threading
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from datetime import datetime
import traceback
import sys

class CorrelationContext:
    """Thread-local correlation context"""
    
    def __init__(self):
        self._local = threading.local()
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return getattr(self._local, 'correlation_id', None)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for current thread"""
        self._local.correlation_id = correlation_id
    
    def clear_correlation_id(self) -> None:
        """Clear correlation ID for current thread"""
        if hasattr(self._local, 'correlation_id'):
            delattr(self._local, 'correlation_id')

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for production logging"""
    
    def __init__(self):
        super().__init__()
        self.correlation_context = CorrelationContext()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add correlation ID if available
        correlation_id = self.correlation_context.get_correlation_id()
        if correlation_id:
            log_entry['correlation_id'] = correlation_id
        
        # Add thread information
        log_entry['thread_id'] = record.thread
        log_entry['thread_name'] = record.threadName
        
        # Add process information
        log_entry['process_id'] = record.process
        
        # Add exception information if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'correlation_id']:
                if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                    log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)

class StructuredLogger:
    """Production-grade structured logger"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.correlation_context = CorrelationContext()
        
        # Add structured formatter if no handlers exist
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = StructuredFormatter()
            formatter.correlation_context = self.correlation_context
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with correlation context and extra fields"""
        extra = kwargs.copy()
        
        # Add correlation ID if available
        correlation_id = self.correlation_context.get_correlation_id()
        if correlation_id:
            extra['correlation_id'] = correlation_id
        
        # Add timestamp
        extra['timestamp'] = time.time()
        
        self.logger.log(level, message, extra=extra)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current thread"""
        self.correlation_context.set_correlation_id(correlation_id)
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return self.correlation_context.get_correlation_id()
    
    def clear_correlation_id(self):
        """Clear correlation ID for current thread"""
        self.correlation_context.clear_correlation_id()

class OperationLogger:
    """Context manager for logging operations with correlation IDs"""
    
    def __init__(self, logger: StructuredLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.correlation_id = str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        """Enter operation context"""
        self.start_time = time.time()
        self.logger.set_correlation_id(self.correlation_id)
        
        self.logger.info(
            f"Starting operation: {self.operation}",
            operation=self.operation,
            correlation_id=self.correlation_id,
            **self.context
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit operation context"""
        duration = time.time() - (self.start_time or 0)
        
        if exc_type is None:
            # Operation completed successfully
            self.logger.info(
                f"Completed operation: {self.operation}",
                operation=self.operation,
                correlation_id=self.correlation_id,
                duration=duration,
                status="success",
                **self.context
            )
        else:
            # Operation failed
            self.logger.error(
                f"Failed operation: {self.operation}",
                operation=self.operation,
                correlation_id=self.correlation_id,
                duration=duration,
                status="failed",
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                **self.context
            )
        
        self.logger.clear_correlation_id()

class BillingLogger:
    """Specialized logger for billing operations"""
    
    def __init__(self):
        self.logger = StructuredLogger('BillingSystem')
    
    def log_customer_creation(self, customer_id: str, email: str, **kwargs):
        """Log customer creation"""
        with OperationLogger(self.logger, "customer_creation", customer_id=customer_id, email=email, **kwargs):
            self.logger.info(f"Creating customer: {email}", customer_id=customer_id, email=email, **kwargs)
    
    def log_subscription_creation(self, subscription_id: str, customer_id: str, tier: str, **kwargs):
        """Log subscription creation"""
        with OperationLogger(self.logger, "subscription_creation", 
                           subscription_id=subscription_id, customer_id=customer_id, tier=tier, **kwargs):
            self.logger.info(f"Creating subscription: {tier}", 
                           subscription_id=subscription_id, customer_id=customer_id, tier=tier, **kwargs)
    
    def log_payment_processing(self, payment_id: str, customer_id: str, amount: float, **kwargs):
        """Log payment processing"""
        with OperationLogger(self.logger, "payment_processing", 
                           payment_id=payment_id, customer_id=customer_id, amount=amount, **kwargs):
            self.logger.info(f"Processing payment: ${amount}", 
                           payment_id=payment_id, customer_id=customer_id, amount=amount, **kwargs)
    
    def log_payment_success(self, payment_id: str, amount: float, **kwargs):
        """Log successful payment"""
        self.logger.info(f"Payment successful: {payment_id}", 
                        payment_id=payment_id, amount=amount, status="success", **kwargs)
    
    def log_payment_failure(self, payment_id: str, error: str, **kwargs):
        """Log failed payment"""
        self.logger.error(f"Payment failed: {payment_id}", 
                         payment_id=payment_id, error=error, status="failed", **kwargs)
    
    def log_subscription_cancellation(self, subscription_id: str, customer_id: str, reason: str, **kwargs):
        """Log subscription cancellation"""
        with OperationLogger(self.logger, "subscription_cancellation", 
                           subscription_id=subscription_id, customer_id=customer_id, reason=reason, **kwargs):
            self.logger.info(f"Cancelling subscription: {subscription_id}", 
                           subscription_id=subscription_id, customer_id=customer_id, reason=reason, **kwargs)
    
    def log_usage_tracking(self, subscription_id: str, usage_type: str, amount: float, **kwargs):
        """Log usage tracking"""
        self.logger.info(f"Recording usage: {usage_type}", 
                        subscription_id=subscription_id, usage_type=usage_type, amount=amount, **kwargs)
    
    def log_api_request(self, endpoint: str, method: str, duration: float, status_code: int, **kwargs):
        """Log API request"""
        self.logger.info(f"API request: {method} {endpoint}", 
                        endpoint=endpoint, method=method, duration=duration, 
                        status_code=status_code, **kwargs)
    
    def log_api_error(self, endpoint: str, method: str, error: str, status_code: int, **kwargs):
        """Log API error"""
        self.logger.error(f"API error: {method} {endpoint}", 
                         endpoint=endpoint, method=method, error=error, 
                         status_code=status_code, **kwargs)
    
    def log_circuit_breaker_trip(self, service: str, **kwargs):
        """Log circuit breaker trip"""
        self.logger.warning(f"Circuit breaker tripped: {service}", 
                           service=service, circuit_breaker_state="open", **kwargs)
    
    def log_database_operation(self, operation: str, table: str, duration: float, **kwargs):
        """Log database operation"""
        self.logger.info(f"Database operation: {operation}", 
                        operation=operation, table=table, duration=duration, **kwargs)
    
    def log_security_event(self, event_type: str, user_id: str, ip_address: str, **kwargs):
        """Log security event"""
        self.logger.warning(f"Security event: {event_type}", 
                           event_type=event_type, user_id=user_id, ip_address=ip_address, **kwargs)
    
    def log_system_health(self, component: str, status: str, details: Dict[str, Any], **kwargs):
        """Log system health check"""
        self.logger.info(f"Health check: {component}", 
                        component=component, status=status, details=details, **kwargs)

# Global billing logger instance
billing_logger = BillingLogger()

def get_billing_logger() -> BillingLogger:
    """Get global billing logger instance"""
    return billing_logger 