#!/usr/bin/env python3
"""
Logging configuration for SOVREN AI Voice System
Production-grade logging with structured JSON output
"""

import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import os

class SecurityFilter(logging.Filter):
    """Filter out sensitive information from logs"""
    
    SENSITIVE_FIELDS = {
        'password', 'token', 'key', 'secret', 'api_key', 
        'authorization', 'cookie', 'session'
    }
    
    def filter(self, record):
        """Filter sensitive data from log records"""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for field in self.SENSITIVE_FIELDS:
                if field.lower() in record.msg.lower():
                    record.msg = f"[REDACTED] {field}"
        return True

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields from record attributes
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno',
                          'module', 'msecs', 'message', 'pathname', 'process',
                          'processName', 'relativeCreated', 'thread', 'threadName',
                          'exc_info', 'exc_text', 'stack_info') and not key.startswith('_'):
                log_entry[key] = value
            
        return json.dumps(log_entry)

def setup_logging(name: str, level: str = "INFO", 
                 log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup production logging for the voice system
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
            'console': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'filters': {
            'security': {
                '()': SecurityFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'console',
                'filters': ['security'],
                'stream': sys.stdout
            }
        },
        'loggers': {
            name: {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    }
    
    # Add file handler if specified
    if log_file:
        config['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'level': level,
            'formatter': 'json',
            'filters': ['security'],
            'filename': log_file,
            'mode': 'a'
        }
        config['loggers'][name]['handlers'].append('file')
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Log startup message
    logger.info("Logging system initialized", extra={
        'extra_fields': {
            'system': 'voice',
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
    })
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)

# Performance monitoring
class PerformanceLogger:
    """Performance monitoring for voice operations"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_time = None
        
    def start_operation(self, operation: str, **kwargs):
        """Start timing an operation"""
        self.start_time = datetime.utcnow()
        self.logger.info(f"Starting {operation}", extra={
            'extra_fields': {
                'operation': operation,
                'start_time': self.start_time.isoformat(),
                **kwargs
            }
        })
        
    def end_operation(self, operation: str, success: bool = True, **kwargs):
        """End timing an operation"""
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.logger.info(f"Completed {operation}", extra={
                'extra_fields': {
                    'operation': operation,
                    'duration_seconds': duration,
                    'success': success,
                    'end_time': datetime.utcnow().isoformat(),
                    **kwargs
                }
            })
            self.start_time = None

# Error tracking
def log_error(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an error with context"""
    logger.error(f"Error occurred: {str(error)}", extra={
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or {}
    }, exc_info=True)

# Usage example
if __name__ == "__main__":
    # Setup logging
    logger = setup_logging("voice_system", level="DEBUG")
    
    # Test logging
    logger.info("Voice system logging test")
    logger.warning("This is a warning")
    
    # Test performance logging
    perf_logger = PerformanceLogger(logger)
    perf_logger.start_operation("test_operation", user_id="test_user")
    perf_logger.end_operation("test_operation", success=True, result="success")
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error(logger, e, {"test": True}) 