#!/usr/bin/env python3
"""
SOVREN Billing System - Configuration Management
Production-grade configuration management with YAML and environment variables
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger('ConfigManager')

class ConfigManager:
    """Production-grade configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or 'config/sovren_config.yaml'
        self.config: Dict[str, Any] = {}
        self.env_prefix = 'SOVREN_'
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        # Load from YAML file if exists
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load config from {self.config_path}: {e}")
                self.config = {}
        else:
            logger.warning(f"Config file not found: {self.config_path}")
            self.config = {}
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix):].lower()
                self.config[config_key] = self._parse_env_value(value)
        
        logger.info(f"Loaded {len([k for k in os.environ if k.startswith(self.env_prefix)])} environment variables")
    
    def _parse_env_value(self, value: str) -> Union[str, int, float, bool, None]:
        """Parse environment variable value"""
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.info(f"Set config: {key} = {value}")
    
    def get_billing_config(self) -> Dict[str, Any]:
        """Get billing system configuration"""
        return {
            'killbill_url': self.get('killbill.url', 'http://localhost:8080'),
            'killbill_api_key': self.get('killbill.api_key', 'sovren'),
            'killbill_api_secret': self.get('killbill.api_secret', 'sovren123'),
            'killbill_tenant_key': self.get('killbill.tenant_key', 'sovren_tenant'),
            'killbill_tenant_secret': self.get('killbill.tenant_secret', 'sovren_tenant_secret'),
            'stripe_live_secret': self.get('stripe.live_secret_key'),
            'stripe_live_publishable': self.get('stripe.live_publishable_key'),
            'stripe_webhook_secret': self.get('stripe.webhook_secret', ''),
            'currency': self.get('billing.currency', 'USD'),
            'payment_retry_attempts': self.get('billing.payment_retry_attempts', 3),
            'webhook_secret': self.get('billing.webhook_secret', 'sovren_webhook_secret')
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'host': self.get('database.host', 'localhost'),
            'port': self.get('database.port', 5432),
            'database': self.get('database.name', 'sovren_billing'),
            'username': self.get('database.username', 'sovren'),
            'password': self.get('database.password', ''),
            'pool_size': self.get('database.pool_size', 20),
            'max_overflow': self.get('database.max_overflow', 30)
        }
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        db_config = self.get_database_config()
        password = db_config['password']
        
        if password:
            return f"postgresql://{db_config['username']}:{password}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        else:
            return f"postgresql://{db_config['username']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.get('logging.level', 'INFO'),
            'format': self.get('logging.format', 'json'),
            'file_path': self.get('logging.file_path'),
            'max_size': self.get('logging.max_size', '100MB'),
            'backup_count': self.get('logging.backup_count', 5)
        }
    
    def get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics configuration"""
        return {
            'enabled': self.get('metrics.enabled', True),
            'port': self.get('metrics.port', 9090),
            'path': self.get('metrics.path', '/metrics'),
            'labels': self.get('metrics.labels', {})
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'master_key': self.get('security.master_key'),
            'jwt_secret': self.get('security.jwt_secret'),
            'session_timeout': self.get('security.session_timeout', 3600),
            'max_login_attempts': self.get('security.max_login_attempts', 5),
            'password_min_length': self.get('security.password_min_length', 8)
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            'enabled': self.get('rate_limit.enabled', True),
            'default_limit': self.get('rate_limit.default_limit', 100),
            'default_window': self.get('rate_limit.default_window', 60),
            'api_limits': self.get('rate_limit.api_limits', {}),
            'customer_limits': self.get('rate_limit.customer_limits', {})
        }
    
    def get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration"""
        return {
            'enabled': self.get('health_check.enabled', True),
            'interval': self.get('health_check.interval', 30),
            'timeout': self.get('health_check.timeout', 10),
            'checks': self.get('health_check.checks', ['system', 'killbill', 'stripe', 'database'])
        }
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration"""
        return {
            'environment': self.get('deployment.environment', 'production'),
            'version': self.get('deployment.version', '1.0.0'),
            'host': self.get('deployment.host', '0.0.0.0'),
            'port': self.get('deployment.port', 8000),
            'workers': self.get('deployment.workers', 4),
            'timeout': self.get('deployment.timeout', 30)
        }
    
    def save_config(self, path: Optional[str] = None):
        """Save configuration to file"""
        save_path = path or self.config_path
        
        # Create directory if it doesn't exist
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info(f"Saved configuration to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {save_path}: {e}")
    
    def export_env_template(self, path: str = 'config/env_template.txt'):
        """Export environment variable template"""
        template = []
        template.append("# SOVREN Billing System Environment Variables")
        template.append("# Copy this file to .env and fill in your values")
        template.append("")
        
        # Add all possible environment variables
        env_vars = {
            'KILLBILL_URL': 'http://localhost:8080',
            'KILLBILL_API_KEY': 'sovren',
            'KILLBILL_API_SECRET': 'sovren123',
            'KILLBILL_TENANT_KEY': 'sovren_tenant',
            'KILLBILL_TENANT_SECRET': 'sovren_tenant_secret',
            'STRIPE_LIVE_SECRET_KEY': 'sk_live_...',
            'STRIPE_LIVE_PUBLISHABLE_KEY': 'pk_live_...',
            'STRIPE_WEBHOOK_SECRET': '',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'sovren_billing',
            'DB_USERNAME': 'sovren',
            'DB_PASSWORD': '',
            'SOVREN_MASTER_KEY': '',
            'SOVREN_JWT_SECRET': '',
            'SOVREN_ENVIRONMENT': 'production',
            'SOVREN_LOG_LEVEL': 'INFO',
            'SOVREN_METRICS_PORT': '9090'
        }
        
        for key, default_value in env_vars.items():
            template.append(f"{key}={default_value}")
        
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write('\n'.join(template))
            logger.info(f"Exported environment template to {path}")
        except Exception as e:
            logger.error(f"Failed to export environment template: {e}")
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration"""
        errors = []
        warnings = []
        
        # Check required billing config
        billing_config = self.get_billing_config()
        if not billing_config['stripe_live_secret']:
            errors.append("Stripe live secret key not configured")
        if not billing_config['stripe_live_publishable']:
            errors.append("Stripe live publishable key not configured")
        
        # Check database config
        db_config = self.get_database_config()
        if not db_config['password']:
            warnings.append("Database password not configured")
        
        # Check security config
        security_config = self.get_security_config()
        if not security_config['master_key']:
            warnings.append("Master key not configured")
        if not security_config['jwt_secret']:
            warnings.append("JWT secret not configured")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        validation = self.validate_config()
        
        return {
            'config_path': self.config_path,
            'environment_variables': len([k for k in os.environ if k.startswith(self.env_prefix)]),
            'validation': validation,
            'sections': {
                'billing': bool(self.get_billing_config()),
                'database': bool(self.get_database_config()),
                'logging': bool(self.get_logging_config()),
                'metrics': bool(self.get_metrics_config()),
                'security': bool(self.get_security_config()),
                'rate_limit': bool(self.get_rate_limit_config()),
                'health_check': bool(self.get_health_check_config()),
                'deployment': bool(self.get_deployment_config())
            }
        }

# Global config manager instance
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    return config_manager 