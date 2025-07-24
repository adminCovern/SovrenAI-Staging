#!/usr/bin/env python3
"""
SOVREN AI - Comprehensive Audit Logging System
Production-ready audit trail with immutable logging and compliance reporting
"""

import os
import sys
import time
import threading
import logging
import json
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import uuid
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger('ComprehensiveAudit')

class AuditLevel(Enum):
    """Audit log levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditCategory(Enum):
    """Audit event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_EVENT = "security_event"
    BUSINESS_OPERATION = "business_operation"
    COMPLIANCE = "compliance"

@dataclass
class AuditEvent:
    """Audit event data"""
    event_id: str
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    category: AuditCategory
    level: AuditLevel
    action: str
    resource: str
    details: Dict[str, Any]
    outcome: str  # "success", "failure", "denied"
    risk_score: float = 0.0
    compliance_tags: List[str] = field(default_factory=list)
    encrypted: bool = False

@dataclass
class AuditConfig:
    """Audit system configuration"""
    database_path: str = "/var/log/sovren/audit/audit.db"
    log_file_path: str = "/var/log/sovren/audit/audit.log"
    encryption_key: Optional[bytes] = None
    retention_days: int = 2555  # 7 years
    max_log_size_mb: int = 100
    compression_enabled: bool = True
    real_time_monitoring: bool = True
    compliance_mode: bool = True
    data_classification_enabled: bool = True

class ComprehensiveAudit:
    """Production-ready comprehensive audit logging system"""
    
    def __init__(self, config: Optional[AuditConfig] = None):
        self.config = config or AuditConfig()
        
        # Initialize encryption
        self.crypto_manager = self._init_crypto_manager()
        
        # Initialize database
        self.db_connection = self._init_database()
        
        # Initialize file logging
        self._init_file_logging()
        
        # Event processing
        self.event_queue = []
        self.event_lock = threading.RLock()
        
        # Compliance tracking
        self.compliance_rules = self._load_compliance_rules()
        self.data_classification = self._load_data_classification()
        
        # Real-time monitoring
        self.monitoring_callbacks = []
        self.alert_thresholds = {
            'high_risk_events': 5,
            'failed_authentications': 3,
            'data_access_violations': 2,
        }
        
        # Start background processing
        self._start_background_processing()
        
        logger.info("Comprehensive audit system initialized")
    
    def _init_crypto_manager(self) -> Fernet:
        """Initialize cryptographic manager for sensitive data"""
        
        if self.config.encryption_key:
            return Fernet(self.config.encryption_key)
        else:
            # Generate new key
            key = Fernet.generate_key()
            self.config.encryption_key = key
            return Fernet(key)
    
    def _init_database(self) -> sqlite3.Connection:
        """Initialize audit database"""
        
        try:
            # Create database directory
            db_path = Path(self.config.database_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database connection
            conn = sqlite3.connect(self.config.database_path)
            
            # Create audit events table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    category TEXT NOT NULL,
                    level TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    details TEXT,
                    outcome TEXT NOT NULL,
                    risk_score REAL DEFAULT 0.0,
                    compliance_tags TEXT,
                    encrypted INTEGER DEFAULT 0,
                    hash_signature TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_events(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_events(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_level ON audit_events(level)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_events(action)')
            
            # Create compliance tracking table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_violations (
                    violation_id TEXT PRIMARY KEY,
                    event_id TEXT,
                    rule_id TEXT,
                    violation_type TEXT,
                    severity TEXT,
                    description TEXT,
                    timestamp TEXT,
                    resolved INTEGER DEFAULT 0,
                    resolution_notes TEXT,
                    FOREIGN KEY (event_id) REFERENCES audit_events (event_id)
                )
            ''')
            
            conn.commit()
            return conn
            
        except Exception as e:
            logger.error(f"Failed to initialize audit database: {e}")
            raise
    
    def _init_file_logging(self):
        """Initialize file-based logging"""
        
        try:
            log_path = Path(self.config.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configure file handler
            file_handler = logging.FileHandler(self.config.log_file_path)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.error(f"Failed to initialize file logging: {e}")
    
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance rules"""
        
        return {
            'gdpr': {
                'name': 'GDPR Compliance',
                'rules': [
                    {
                        'id': 'gdpr_data_access',
                        'description': 'Track all data access events',
                        'category': AuditCategory.DATA_ACCESS,
                        'required_fields': ['user_id', 'resource', 'purpose'],
                    },
                    {
                        'id': 'gdpr_data_deletion',
                        'description': 'Track data deletion requests',
                        'category': AuditCategory.DATA_MODIFICATION,
                        'required_fields': ['user_id', 'resource', 'deletion_reason'],
                    },
                ],
            },
            'sox': {
                'name': 'SOX Compliance',
                'rules': [
                    {
                        'id': 'sox_financial_access',
                        'description': 'Track financial data access',
                        'category': AuditCategory.DATA_ACCESS,
                        'required_fields': ['user_id', 'resource', 'business_justification'],
                    },
                ],
            },
            'hipaa': {
                'name': 'HIPAA Compliance',
                'rules': [
                    {
                        'id': 'hipaa_phi_access',
                        'description': 'Track PHI data access',
                        'category': AuditCategory.DATA_ACCESS,
                        'required_fields': ['user_id', 'resource', 'patient_id', 'purpose'],
                    },
                ],
            },
        }
    
    def _load_data_classification(self) -> Dict[str, Dict[str, Any]]:
        """Load data classification rules"""
        
        return {
            'public': {
                'level': 1,
                'encryption_required': False,
                'audit_level': AuditLevel.INFO,
            },
            'internal': {
                'level': 2,
                'encryption_required': False,
                'audit_level': AuditLevel.INFO,
            },
            'confidential': {
                'level': 3,
                'encryption_required': True,
                'audit_level': AuditLevel.WARNING,
            },
            'restricted': {
                'level': 4,
                'encryption_required': True,
                'audit_level': AuditLevel.SECURITY,
            },
        }
    
    def log_event(self, user_id: Optional[str], session_id: Optional[str],
                  ip_address: Optional[str], user_agent: Optional[str],
                  category: AuditCategory, level: AuditLevel, action: str,
                  resource: str, details: Dict[str, Any], outcome: str,
                  risk_score: float = 0.0, compliance_tags: Optional[List[str]] = None):
        """Log audit event"""
        
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Classify data sensitivity
            data_classification = self._classify_data_sensitivity(resource, details)
            
            # Determine if encryption is needed
            should_encrypt = data_classification.get('encryption_required', False)
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                category=category,
                level=level,
                action=action,
                resource=resource,
                details=details,
                outcome=outcome,
                risk_score=risk_score,
                compliance_tags=compliance_tags or [],
                encrypted=should_encrypt,
            )
            
            # Process event
            self._process_audit_event(event)
            
            # Real-time monitoring
            if self.config.real_time_monitoring:
                self._check_real_time_alerts(event)
            
            logger.info(f"Audit event logged: {event_id}")
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def _classify_data_sensitivity(self, resource: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Classify data sensitivity level"""
        
        # Simple classification based on resource patterns
        resource_lower = resource.lower()
        
        if any(keyword in resource_lower for keyword in ['password', 'secret', 'key', 'token']):
            return self.data_classification['restricted']
        elif any(keyword in resource_lower for keyword in ['financial', 'payment', 'credit']):
            return self.data_classification['confidential']
        elif any(keyword in resource_lower for keyword in ['user', 'profile', 'personal']):
            return self.data_classification['internal']
        else:
            return self.data_classification['public']
    
    def _process_audit_event(self, event: AuditEvent):
        """Process audit event"""
        
        try:
            # Encrypt sensitive details if needed
            details_json = json.dumps(event.details)
            if event.encrypted:
                encrypted_details = self.crypto_manager.encrypt(details_json.encode())
                details_json = base64.b64encode(encrypted_details).decode()
            
            # Generate hash signature for integrity
            event_data = f"{event.event_id}{event.timestamp.isoformat()}{event.action}{event.resource}"
            hash_signature = hashlib.sha256(event_data.encode()).hexdigest()
            
            # Store in database
            self.db_connection.execute('''
                INSERT INTO audit_events (
                    event_id, timestamp, user_id, session_id, ip_address, user_agent,
                    category, level, action, resource, details, outcome, risk_score,
                    compliance_tags, encrypted, hash_signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.timestamp.isoformat(),
                event.user_id,
                event.session_id,
                event.ip_address,
                event.user_agent,
                event.category.value,
                event.level.value,
                event.action,
                event.resource,
                details_json,
                event.outcome,
                event.risk_score,
                json.dumps(event.compliance_tags),
                1 if event.encrypted else 0,
                hash_signature,
            ))
            
            self.db_connection.commit()
            
            # Check compliance rules
            if self.config.compliance_mode:
                self._check_compliance_rules(event)
            
        except Exception as e:
            logger.error(f"Failed to process audit event: {e}")
    
    def _check_compliance_rules(self, event: AuditEvent):
        """Check event against compliance rules"""
        
        try:
            for compliance_standard, rules in self.compliance_rules.items():
                for rule in rules['rules']:
                    if rule['category'] == event.category:
                        # Check if required fields are present
                        missing_fields = []
                        for field in rule['required_fields']:
                            if field not in event.details:
                                missing_fields.append(field)
                        
                        if missing_fields:
                            # Log compliance violation
                            violation_id = str(uuid.uuid4())
                            
                            self.db_connection.execute('''
                                INSERT INTO compliance_violations (
                                    violation_id, event_id, rule_id, violation_type,
                                    severity, description, timestamp
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                violation_id,
                                event.event_id,
                                rule['id'],
                                'missing_required_fields',
                                'medium',
                                f"Missing required fields: {', '.join(missing_fields)}",
                                datetime.now().isoformat(),
                            ))
                            
                            self.db_connection.commit()
                            
                            logger.warning(f"Compliance violation: {rule['id']} - missing fields: {missing_fields}")
            
        except Exception as e:
            logger.error(f"Failed to check compliance rules: {e}")
    
    def _check_real_time_alerts(self, event: AuditEvent):
        """Check for real-time alert conditions"""
        
        try:
            # Check for high-risk events
            if event.risk_score > 0.8:
                self._trigger_alert('high_risk_event', event)
            
            # Check for failed authentications
            if (event.category == AuditCategory.AUTHENTICATION and 
                event.outcome == 'failure'):
                self._trigger_alert('failed_authentication', event)
            
            # Check for data access violations
            if (event.category == AuditCategory.DATA_ACCESS and 
                event.level == AuditLevel.SECURITY):
                self._trigger_alert('data_access_violation', event)
            
        except Exception as e:
            logger.error(f"Failed to check real-time alerts: {e}")
    
    def _trigger_alert(self, alert_type: str, event: AuditEvent):
        """Trigger real-time alert"""
        
        alert_data = {
            'alert_type': alert_type,
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'user_id': event.user_id,
            'ip_address': event.ip_address,
            'action': event.action,
            'resource': event.resource,
            'risk_score': event.risk_score,
        }
        
        # Notify monitoring callbacks
        for callback in self.monitoring_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(f"Real-time alert triggered: {alert_type}")
    
    def _start_background_processing(self):
        """Start background processing thread"""
        
        def background_loop():
            while True:
                try:
                    # Clean up old audit records
                    self._cleanup_old_records()
                    
                    # Compress log files if enabled
                    if self.config.compression_enabled:
                        self._compress_log_files()
                    
                    time.sleep(3600)  # Run every hour
                    
                except Exception as e:
                    logger.error(f"Background processing error: {e}")
        
        background_thread = threading.Thread(target=background_loop, daemon=True)
        background_thread.start()
    
    def _cleanup_old_records(self):
        """Clean up old audit records"""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            
            # Delete old audit events
            self.db_connection.execute('''
                DELETE FROM audit_events 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            # Delete old compliance violations
            self.db_connection.execute('''
                DELETE FROM compliance_violations 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            self.db_connection.commit()
            
            logger.info("Cleaned up old audit records")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
    
    def _compress_log_files(self):
        """Compress old log files"""
        
        try:
            log_path = Path(self.config.log_file_path)
            log_dir = log_path.parent
            
            # Find old log files
            for log_file in log_dir.glob("audit.log.*"):
                if not log_file.name.endswith('.gz'):
                    # Compress file
                    import gzip
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    # Remove original file
                    log_file.unlink()
            
        except Exception as e:
            logger.error(f"Failed to compress log files: {e}")
    
    def get_audit_report(self, start_date: datetime, end_date: datetime,
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        
        try:
            query = '''
                SELECT * FROM audit_events 
                WHERE timestamp BETWEEN ? AND ?
            '''
            params = [start_date.isoformat(), end_date.isoformat()]
            
            # Add filters
            if filters:
                if 'user_id' in filters:
                    query += ' AND user_id = ?'
                    params.append(filters['user_id'])
                
                if 'category' in filters:
                    query += ' AND category = ?'
                    params.append(filters['category'])
                
                if 'level' in filters:
                    query += ' AND level = ?'
                    params.append(filters['level'])
            
            cursor = self.db_connection.execute(query, params)
            events = cursor.fetchall()
            
            # Process events
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                },
                'summary': {
                    'total_events': len(events),
                    'events_by_category': {},
                    'events_by_level': {},
                    'events_by_outcome': {},
                    'high_risk_events': 0,
                    'compliance_violations': 0,
                },
                'top_users': {},
                'top_resources': {},
                'risk_analysis': {},
            }
            
            for event in events:
                # Count by category
                category = event[7]  # category column
                report['summary']['events_by_category'][category] = \
                    report['summary']['events_by_category'].get(category, 0) + 1
                
                # Count by level
                level = event[8]  # level column
                report['summary']['events_by_level'][level] = \
                    report['summary']['events_by_level'].get(level, 0) + 1
                
                # Count by outcome
                outcome = event[12]  # outcome column
                report['summary']['events_by_outcome'][outcome] = \
                    report['summary']['events_by_outcome'].get(outcome, 0) + 1
                
                # Count high-risk events
                risk_score = event[13]  # risk_score column
                if risk_score > 0.7:
                    report['summary']['high_risk_events'] += 1
                
                # Track top users
                user_id = event[2]  # user_id column
                if user_id:
                    report['top_users'][user_id] = report['top_users'].get(user_id, 0) + 1
                
                # Track top resources
                resource = event[11]  # resource column
                report['top_resources'][resource] = report['top_resources'].get(resource, 0) + 1
            
            # Get compliance violations
            cursor = self.db_connection.execute('''
                SELECT COUNT(*) FROM compliance_violations 
                WHERE timestamp BETWEEN ? AND ?
            ''', [start_date.isoformat(), end_date.isoformat()])
            
            report['summary']['compliance_violations'] = cursor.fetchone()[0]
            
            # Sort top users and resources
            report['top_users'] = dict(sorted(report['top_users'].items(), 
                                            key=lambda x: x[1], reverse=True)[:10])
            report['top_resources'] = dict(sorted(report['top_resources'].items(), 
                                                key=lambda x: x[1], reverse=True)[:10])
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate audit report: {e}")
            return {}
    
    def get_compliance_report(self, compliance_standard: str, 
                            start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance-specific report"""
        
        try:
            if compliance_standard not in self.compliance_rules:
                raise ValueError(f"Unknown compliance standard: {compliance_standard}")
            
            # Get compliance violations
            cursor = self.db_connection.execute('''
                SELECT * FROM compliance_violations 
                WHERE rule_id LIKE ? AND timestamp BETWEEN ? AND ?
            ''', [f"{compliance_standard}_%", start_date.isoformat(), end_date.isoformat()])
            
            violations = cursor.fetchall()
            
            report = {
                'compliance_standard': compliance_standard,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                },
                'violations': {
                    'total': len(violations),
                    'by_rule': {},
                    'by_severity': {},
                    'resolved': 0,
                    'unresolved': 0,
                },
                'rules': self.compliance_rules[compliance_standard]['rules'],
            }
            
            for violation in violations:
                rule_id = violation[2]  # rule_id column
                severity = violation[4]  # severity column
                resolved = violation[7]  # resolved column
                
                # Count by rule
                report['violations']['by_rule'][rule_id] = \
                    report['violations']['by_rule'].get(rule_id, 0) + 1
                
                # Count by severity
                report['violations']['by_severity'][severity] = \
                    report['violations']['by_severity'].get(severity, 0) + 1
                
                # Count resolved/unresolved
                if resolved:
                    report['violations']['resolved'] += 1
                else:
                    report['violations']['unresolved'] += 1
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {}
    
    def add_monitoring_callback(self, callback):
        """Add real-time monitoring callback"""
        self.monitoring_callbacks.append(callback)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get audit system health status"""
        
        try:
            # Check database health
            cursor = self.db_connection.execute('SELECT COUNT(*) FROM audit_events')
            total_events = cursor.fetchone()[0]
            
            # Check recent activity
            recent_cutoff = datetime.now() - timedelta(hours=1)
            cursor = self.db_connection.execute('''
                SELECT COUNT(*) FROM audit_events 
                WHERE timestamp > ?
            ''', [recent_cutoff.isoformat()])
            recent_events = cursor.fetchone()[0]
            
            # Check for errors
            cursor = self.db_connection.execute('''
                SELECT COUNT(*) FROM audit_events 
                WHERE level = 'error' AND timestamp > ?
            ''', [recent_cutoff.isoformat()])
            error_events = cursor.fetchone()[0]
            
            return {
                'status': 'healthy' if error_events == 0 else 'warning',
                'total_events': total_events,
                'recent_events': recent_events,
                'error_events': error_events,
                'database_size_mb': self._get_database_size(),
                'log_file_size_mb': self._get_log_file_size(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_database_size(self) -> float:
        """Get database size in MB"""
        try:
            size_bytes = Path(self.config.database_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _get_log_file_size(self) -> float:
        """Get log file size in MB"""
        try:
            size_bytes = Path(self.config.log_file_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0 