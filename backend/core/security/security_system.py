#!/usr/bin/env python3
"""
SOVREN AI Security System
Zero-Trust Architecture with Adversarial Hardening
"""

import asyncio
import json
import time
import uuid
import logging
import hashlib
import secrets
import hmac
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import torch
import torch.nn as nn
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import sqlite3
import redis
import jwt
from collections import defaultdict, deque
import re
import ipaddress
import geoip2.database
import aiohttp
from sklearn.ensemble import IsolationForest
import joblib
import threading
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SecuritySystem')

# Security configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 3600  # 1 hour
SESSION_TIMEOUT = 3600  # 1 hour
API_RATE_LIMIT = 1000  # requests per hour
ANOMALY_THRESHOLD = 0.8
THREAT_DETECTION_WINDOW = 300  # 5 minutes
MAX_CONCURRENT_SESSIONS = 10
TOKEN_CLEANUP_INTERVAL = 300  # 5 minutes

class SecurityError(Exception):
    """Base exception for security system errors"""
    pass

class AuthenticationError(SecurityError):
    """Authentication-related errors"""
    pass

class AuthorizationError(SecurityError):
    """Authorization-related errors"""
    pass

class CryptoError(SecurityError):
    """Cryptographic operation errors"""
    pass

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEvent(Enum):
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    API_ACCESS = "api_access"
    DATA_ACCESS = "data_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALY_DETECTED = "anomaly_detected"
    THREAT_BLOCKED = "threat_blocked"
    ENCRYPTION_EVENT = "encryption_event"
    AUDIT_EVENT = "audit_event"

@dataclass
class SecurityIncident:
    """Represents a security incident"""
    id: str
    timestamp: float
    event_type: SecurityEvent
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    details: Dict[str, Any]
    blocked: bool = False
    resolved: bool = False
    
@dataclass
class AccessToken:
    """Secure access token"""
    token_id: str
    user_id: str
    permissions: Set[str]
    created_at: float
    expires_at: float
    refresh_token: Optional[str] = None
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None

class AdversarialDetector(nn.Module):
    """Neural network for adversarial attack detection"""
    
    def __init__(self, input_dim: int = 128):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Linear(128, 64)
        )
        
        self.threat_classifier = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 4)  # 4 threat levels
        )
        
        self.anomaly_detector = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        threat_probs = torch.softmax(self.threat_classifier(encoded), dim=1)
        anomaly_score = self.anomaly_detector(encoded)
        return encoded, threat_probs, anomaly_score

class CryptoManager:
    """Manages encryption and cryptographic operations"""
    
    def __init__(self):
        self.master_key = self._generate_master_key()
        self.key_rotation_interval = 86400 * 30  # 30 days
        self.last_rotation = time.time()
        self.key_versions = {}
        self._lock = threading.RLock()
        
    def _generate_master_key(self) -> bytes:
        """Generate secure master key"""
        return secrets.token_bytes(32)
        
    def encrypt_data(self, data: bytes, context: str = "general") -> Tuple[bytes, str]:
        """Encrypt data with context-aware encryption"""
        
        if not isinstance(data, bytes):
            raise CryptoError("Data must be bytes")
            
        if not context:
            raise CryptoError("Context cannot be empty")
            
        with self._lock:
            try:
                # Derive key from master key and context
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=context.encode(),
                    iterations=100000,
                )
                key = kdf.derive(self.master_key)
                
                # Generate nonce
                nonce = secrets.token_bytes(12)
                
                # Encrypt with AES-GCM
                aesgcm = AESGCM(key)
                ciphertext = aesgcm.encrypt(nonce, data, context.encode())
                
                # Create encrypted package
                package = nonce + ciphertext
                
                # Generate key version ID
                key_version = hashlib.sha256(key).hexdigest()[:8]
                self.key_versions[key_version] = {
                    'context': context,
                    'created': time.time()
                }
                
                return package, key_version
                
            except Exception as e:
                logger.error(f"Encryption failed: {e}")
                raise CryptoError(f"Encryption failed: {e}")
        
    def decrypt_data(self, encrypted_package: bytes, key_version: str,
                    context: str = "general") -> bytes:
        """Decrypt data"""
        
        if not isinstance(encrypted_package, bytes):
            raise CryptoError("Encrypted package must be bytes")
            
        if len(encrypted_package) < 12:
            raise CryptoError("Invalid encrypted package")
            
        with self._lock:
            try:
                # Extract nonce and ciphertext
                nonce = encrypted_package[:12]
                ciphertext = encrypted_package[12:]
                
                # Derive key
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=context.encode(),
                    iterations=100000,
                )
                key = kdf.derive(self.master_key)
                
                # Verify key version
                expected_version = hashlib.sha256(key).hexdigest()[:8]
                if expected_version != key_version:
                    raise CryptoError("Key version mismatch")
                    
                # Decrypt
                aesgcm = AESGCM(key)
                plaintext = aesgcm.decrypt(nonce, ciphertext, context.encode())
                
                return plaintext
                
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                raise CryptoError(f"Decryption failed: {e}")
        
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        
        if length < 16:
            raise CryptoError("Token length must be at least 16 bytes")
            
        return secrets.token_urlsafe(length)
        
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """Hash password with salt"""
        
        if not password:
            raise CryptoError("Password cannot be empty")
            
        if salt is None:
            salt = secrets.token_bytes(32)
            
        # Use PBKDF2 for password hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        
        return (
            key.hex(),
            salt.hex()
        )
        
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        
        if not password or not password_hash or not salt:
            return False
            
        try:
            salt_bytes = bytes.fromhex(salt)
            computed_hash, _ = self.hash_password(password, salt_bytes)
            
            return hmac.compare_digest(computed_hash, password_hash)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
        
    def rotate_keys(self):
        """Rotate encryption keys"""
        
        with self._lock:
            if time.time() - self.last_rotation > self.key_rotation_interval:
                try:
                    # Generate new master key
                    old_key = self.master_key
                    self.master_key = self._generate_master_key()
                    
                    # Re-encrypt critical data with new key
                    # In practice, this would be a gradual migration
                    
                    self.last_rotation = time.time()
                    logger.info("Encryption keys rotated")
                except Exception as e:
                    logger.error(f"Key rotation failed: {e}")
                    raise CryptoError(f"Key rotation failed: {e}")

class AccessControl:
    """Manages access control and permissions"""
    
    def __init__(self):
        self.permissions = {
            'user': {
                'read_own_data',
                'create_tasks',
                'view_dashboard',
                'use_voice',
                'basic_api'
            },
            'power_user': {
                'read_own_data',
                'create_tasks',
                'view_dashboard',
                'use_voice',
                'basic_api',
                'advanced_features',
                'shadow_board_access',
                'time_machine_access'
            },
            'admin': {
                'all_permissions',
                'user_management',
                'system_configuration',
                'security_management',
                'billing_management'
            }
        }
        
        self.resource_permissions = defaultdict(set)
        self.role_hierarchy = {
            'admin': ['power_user', 'user'],
            'power_user': ['user'],
            'user': []
        }
        
    def check_permission(self, user_role: str, permission: str) -> bool:
        """Check if user has permission"""
        
        if not user_role or not permission:
            return False
            
        # Check direct role permissions
        if permission in self.permissions.get(user_role, set()):
            return True
            
        # Check inherited permissions
        for inherited_role in self.role_hierarchy.get(user_role, []):
            if permission in self.permissions.get(inherited_role, set()):
                return True
                
        return False
        
    def get_user_permissions(self, user_role: str) -> Set[str]:
        """Get all permissions for a user role"""
        
        if not user_role:
            return set()
            
        permissions = set()
        
        # Add direct permissions
        permissions.update(self.permissions.get(user_role, set()))
        
        # Add inherited permissions
        for inherited_role in self.role_hierarchy.get(user_role, []):
            permissions.update(self.permissions.get(inherited_role, set()))
            
        return permissions

class SecuritySystem:
    """Main security system orchestrator"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.crypto_manager = CryptoManager()
        self.access_control = AccessControl()
        self.adversarial_detector = AdversarialDetector()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)  # type: ignore
        
        # Security state
        self.active_sessions = {}
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.security_incidents = []
        self._lock = threading.RLock()
        
        # Initialize components
        self._init_database(db_path)
        self._init_geoip()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
    def _init_database(self, db_path: Optional[str] = None):
        """Initialize security database"""
        
        try:
            if db_path:
                self.db = sqlite3.connect(db_path)
            else:
                self.db = sqlite3.connect(':memory:')  # Use file in production
                
            cursor = self.db.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    event_type TEXT,
                    threat_level TEXT,
                    source_ip TEXT,
                    user_id TEXT,
                    description TEXT,
                    details TEXT,
                    blocked INTEGER,
                    resolved INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_tokens (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    permissions TEXT,
                    created_at REAL,
                    expires_at REAL,
                    refresh_token TEXT,
                    ip_address TEXT,
                    device_fingerprint TEXT
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_events_source_ip ON security_events(source_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_tokens_expires_at ON access_tokens(expires_at)')
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise SecurityError(f"Database initialization failed: {e}")
        
    def _init_geoip(self):
        """Initialize GeoIP database"""
        
        try:
            # In production, download and use MaxMind GeoIP2 database
            self.geoip_reader = None
            logger.info("GeoIP database not available - using fallback")
        except Exception as e:
            logger.warning(f"Failed to initialize GeoIP: {e}")
            self.geoip_reader = None
            
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        
        def cleanup_worker():
            while True:
                try:
                    time.sleep(TOKEN_CLEANUP_INTERVAL)
                    self.cleanup_expired_tokens()
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
                    
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
            
    def create_access_token(self, user_id: str, permissions: Set[str],
                          ip_address: Optional[str] = None,
                          device_fingerprint: Optional[str] = None) -> AccessToken:
        """Create secure access token"""
        
        if not user_id or not permissions:
            raise AuthenticationError("User ID and permissions are required")
            
        with self._lock:
            # Check concurrent sessions limit
            user_sessions = sum(1 for token in self.active_sessions.values() 
                              if token.user_id == user_id)
            if user_sessions >= MAX_CONCURRENT_SESSIONS:
                raise AuthenticationError("Maximum concurrent sessions exceeded")
                
            token_id = self.crypto_manager.generate_secure_token()
            created_at = time.time()
            expires_at = created_at + SESSION_TIMEOUT
            
            token = AccessToken(
                token_id=token_id,
                user_id=user_id,
                permissions=permissions,
                created_at=created_at,
                expires_at=expires_at,
                ip_address=ip_address,
                device_fingerprint=device_fingerprint
            )
            
            # Store token
            self._store_token(token)
            
            # Add to active sessions
            self.active_sessions[token_id] = token
            
            return token
        
    def _store_token(self, token: AccessToken):
        """Store access token in database"""
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO access_tokens
                (token_id, user_id, permissions, created_at, expires_at, 
                 refresh_token, ip_address, device_fingerprint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                token.token_id,
                token.user_id,
                json.dumps(list(token.permissions)),
                token.created_at,
                token.expires_at,
                token.refresh_token,
                token.ip_address,
                token.device_fingerprint
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store token: {e}")
            raise SecurityError(f"Failed to store token: {e}")
        
    def validate_token(self, token_id: str, ip_address: Optional[str] = None) -> Optional[AccessToken]:
        """Validate access token"""
        
        if not token_id:
            return None
            
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT * FROM access_tokens WHERE token_id = ?
            ''', (token_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            # Check expiration
            if time.time() > row[4]:  # expires_at
                return None
                
            # Check IP if provided
            if ip_address and row[6] and ip_address != row[6]:
                self._log_security_event(
                    SecurityEvent.LOGIN_ATTEMPT,
                    ThreatLevel.MEDIUM,
                    ip_address,
                    row[1],  # user_id
                    "Token used from different IP"
                )
                return None
                
            # Reconstruct token
            token = AccessToken(
                token_id=row[0],
                user_id=row[1],
                permissions=set(json.loads(row[2])),
                created_at=row[3],
                expires_at=row[4],
                refresh_token=row[5],
                ip_address=row[6],
                device_fingerprint=row[7]
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
        
    def _log_security_event(self, event_type: SecurityEvent, threat_level: ThreatLevel,
                           source_ip: str, user_id: Optional[str], description: str,
                           details: Optional[Dict[str, Any]] = None):
        """Log security event"""
        
        try:
            incident = SecurityIncident(
                id=str(uuid.uuid4()),
                timestamp=time.time(),
                event_type=event_type,
                threat_level=threat_level,
                source_ip=source_ip,
                user_id=user_id,
                description=description,
                details=details or {}
            )
            
            # Store in database
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO security_events
                (id, timestamp, event_type, threat_level, source_ip, user_id, 
                 description, details, blocked, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.id,
                incident.timestamp,
                incident.event_type.value,
                incident.threat_level.value,
                incident.source_ip,
                incident.user_id,
                incident.description,
                json.dumps(incident.details),
                incident.blocked,
                incident.resolved
            ))
            
            self.db.commit()
            
            # Add to memory list
            with self._lock:
                self.security_incidents.append(incident)
            
            logger.warning(f"Security event: {event_type.value} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
        
    def check_threat_level(self, source_ip: str, user_id: Optional[str] = None) -> ThreatLevel:
        """Check threat level for IP/user combination"""
        
        if not source_ip:
            return ThreatLevel.LOW
            
        with self._lock:
            # Check if IP is blocked
            if source_ip in self.blocked_ips:
                return ThreatLevel.CRITICAL
                
            # Check failed attempts
            recent_failures = [
                attempt for attempt in self.failed_attempts.get(source_ip, [])
                if time.time() - attempt < THREAT_DETECTION_WINDOW
            ]
            
            if len(recent_failures) >= MAX_LOGIN_ATTEMPTS:
                return ThreatLevel.HIGH
                
            # Check for anomalies
            # This would use the adversarial detector in practice
            
            return ThreatLevel.LOW
        
    def block_ip(self, ip_address: str, reason: str = "Security violation"):
        """Block IP address"""
        
        if not ip_address:
            return
            
        with self._lock:
            self.blocked_ips.add(ip_address)
            self._log_security_event(
                SecurityEvent.THREAT_BLOCKED,
                ThreatLevel.CRITICAL,
                ip_address,
                None,
                f"IP blocked: {reason}"
            )
            
            logger.warning(f"Blocked IP: {ip_address} - {reason}")
        
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        
        if not ip_address:
            return
            
        with self._lock:
            self.blocked_ips.discard(ip_address)
            logger.info(f"Unblocked IP: {ip_address}")
        
    def cleanup_expired_tokens(self):
        """Remove expired access tokens"""
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                DELETE FROM access_tokens WHERE expires_at < ?
            ''', (time.time(),))
            
            self.db.commit()
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired tokens")
                
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            
    def close(self):
        """Cleanup resources"""
        
        try:
            if hasattr(self, 'db'):
                self.db.close()
        except Exception as e:
            logger.error(f"Failed to close database: {e}")

# Global security system instance
security_system = SecuritySystem()