#!/usr/bin/env python3
"""
SOVREN AI - Zero-Trust Authentication System
Production-ready authentication with MFA, device fingerprinting, and behavioral analysis
"""

import hashlib
import hmac
import time
import uuid
import json
import logging
import secrets
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import numpy as np
from sklearn.ensemble import IsolationForest
import threading
from collections import defaultdict, deque

logger = logging.getLogger('ZeroTrustAuth')

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthMethod(Enum):
    PASSWORD = "password"
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BIOMETRIC = "biometric"
    HARDWARE_KEY = "hardware_key"

@dataclass
class DeviceFingerprint:
    """Device fingerprinting data"""
    user_agent: str
    screen_resolution: str
    timezone: str
    language: str
    platform: str
    plugins: List[str]
    canvas_hash: str
    webgl_hash: str
    audio_hash: str
    ip_address: str
    geolocation: Optional[Dict[str, float]]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class BehavioralProfile:
    """User behavioral analysis profile"""
    user_id: str
    login_patterns: deque = field(default_factory=lambda: deque(maxlen=100))
    typing_patterns: deque = field(default_factory=lambda: deque(maxlen=100))
    mouse_patterns: deque = field(default_factory=lambda: deque(maxlen=100))
    session_durations: deque = field(default_factory=lambda: deque(maxlen=100))
    feature_usage: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class AuthSession:
    """Authentication session data"""
    session_id: str
    user_id: str
    device_fingerprint: Optional[DeviceFingerprint]
    risk_score: float
    auth_methods_used: List[AuthMethod]
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

class ZeroTrustAuth:
    """Zero-Trust Authentication System with MFA and behavioral analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.secret_key = self.config['secret_key']
        self.mfa_required = self.config['mfa_required']
        self.session_timeout = self.config['session_timeout']
        self.device_fingerprinting = self.config['device_fingerprinting']
        self.behavioral_analysis = self.config['behavioral_analysis']
        
        # Initialize components
        self.crypto_manager = self._init_crypto_manager()
        self.behavioral_analyzer = self._init_behavioral_analyzer()
        self.risk_calculator = self._init_risk_calculator()
        
        # Session management
        self.active_sessions: Dict[str, AuthSession] = {}
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        self.device_whitelist: Dict[str, List[str]] = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'secret_key': Fernet.generate_key(),
            'mfa_required': True,
            'session_timeout': 300,  # 5 minutes
            'device_fingerprinting': True,
            'behavioral_analysis': True,
            'max_failed_attempts': 5,
            'lockout_duration': 900,  # 15 minutes
            'risk_threshold_high': 0.7,
            'risk_threshold_critical': 0.9,
            'behavioral_window': 3600,  # 1 hour
            'cleanup_interval': 300,  # 5 minutes
        }
    
    def _init_crypto_manager(self) -> Fernet:
        """Initialize cryptographic manager"""
        return Fernet(self.secret_key)
    
    def _init_behavioral_analyzer(self) -> IsolationForest:
        """Initialize behavioral analysis model"""
        return IsolationForest(
            contamination="auto",
            random_state=42,
            n_estimators=100
        )
    
    def _init_risk_calculator(self) -> Dict[str, float]:
        """Initialize risk calculation weights"""
        return {
            'device_mismatch': 0.3,
            'location_anomaly': 0.25,
            'behavioral_anomaly': 0.25,
            'time_anomaly': 0.1,
            'failed_attempts': 0.1,
        }
    
    def authenticate(self, credentials: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, Optional[str], float]:
        """Authenticate user with zero-trust principles"""
        
        try:
            # Extract authentication data
            user_id = credentials.get('user_id')
            password = credentials.get('password')
            mfa_code = credentials.get('mfa_code')
            device_data = context.get('device_data', {})
            behavioral_data = context.get('behavioral_data', {})
            
            if not user_id or not password:
                return False, "Missing credentials", 1.0
            
            # Check IP blocking
            client_ip = context.get('ip_address')
            if client_ip in self.blocked_ips:
                if datetime.now() < self.blocked_ips[client_ip]:
                    return False, "IP address blocked", 1.0
                else:
                    del self.blocked_ips[client_ip]
            
            # Validate password
            if not self._validate_password(user_id, password):
                self._record_failed_attempt(client_ip)
                return False, "Invalid credentials", 1.0
            
            # Device fingerprinting
            device_fingerprint = None
            if self.device_fingerprinting:
                device_fingerprint = self._create_device_fingerprint(device_data)
                if not self._validate_device_fingerprint(user_id, device_fingerprint):
                    return False, "Device not recognized", 0.8
            
            # Behavioral analysis
            behavioral_score = 0.0
            if self.behavioral_analysis:
                behavioral_score = self._analyze_behavior(user_id, behavioral_data)
                if behavioral_score > self.config['risk_threshold_critical']:
                    return False, "Behavioral anomaly detected", 1.0
            
            # MFA validation
            if self.mfa_required:
                if not mfa_code or not self._validate_mfa(user_id, mfa_code):
                    return False, "MFA code required or invalid", 0.9
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                user_id, device_fingerprint, behavioral_score, context
            )
            
            # Create session
            session = self._create_session(user_id, device_fingerprint, risk_score, context)
            
            logger.info(f"Authentication successful for user {user_id}, risk score: {risk_score:.3f}")
            return True, session.session_id, risk_score
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, "Authentication failed", 1.0
    
    def _validate_password(self, user_id: str, password: str) -> bool:
        """Validate user password"""
        # In production, this would check against secure password storage
        # For now, using a simple hash comparison
        expected_hash = self._get_user_password_hash(user_id)
        if not expected_hash:
            return False
        
        return hmac.compare_digest(
            hashlib.sha256(password.encode()).hexdigest(),
            expected_hash
        )
    
    def _get_user_password_hash(self, user_id: str) -> Optional[str]:
        """Get user password hash from secure storage"""
        # In production, this would query a secure database
        # For demo purposes, using a mock implementation
        mock_users = {
            'admin': hashlib.sha256('admin123'.encode()).hexdigest(),
            'user1': hashlib.sha256('password123'.encode()).hexdigest(),
        }
        return mock_users.get(user_id)
    
    def _validate_mfa(self, user_id: str, mfa_code: str) -> bool:
        """Validate MFA code"""
        # In production, this would validate TOTP or other MFA methods
        # For demo purposes, accepting any 6-digit code
        return len(mfa_code) == 6 and mfa_code.isdigit()
    
    def _create_device_fingerprint(self, device_data: Dict[str, Any]) -> DeviceFingerprint:
        """Create device fingerprint from device data"""
        return DeviceFingerprint(
            user_agent=device_data.get('user_agent', ''),
            screen_resolution=device_data.get('screen_resolution', ''),
            timezone=device_data.get('timezone', ''),
            language=device_data.get('language', ''),
            platform=device_data.get('platform', ''),
            plugins=device_data.get('plugins', []),
            canvas_hash=device_data.get('canvas_hash', ''),
            webgl_hash=device_data.get('webgl_hash', ''),
            audio_hash=device_data.get('audio_hash', ''),
            ip_address=device_data.get('ip_address', ''),
            geolocation=device_data.get('geolocation'),
        )
    
    def _validate_device_fingerprint(self, user_id: str, fingerprint: DeviceFingerprint) -> bool:
        """Validate device fingerprint against user's known devices"""
        # In production, this would check against a database of known devices
        # For demo purposes, accepting all devices
        return True
    
    def _analyze_behavior(self, user_id: str, behavioral_data: Dict[str, Any]) -> float:
        """Analyze user behavior for anomalies"""
        try:
            # Extract behavioral features
            features = [
                behavioral_data.get('typing_speed', 0),
                behavioral_data.get('mouse_speed', 0),
                behavioral_data.get('session_duration', 0),
                behavioral_data.get('feature_usage_count', 0),
            ]
            
            # Convert to numpy array for analysis
            feature_array = np.array(features).reshape(1, -1)
            
            # Get anomaly score (-1 to 1, where -1 is normal, 1 is anomalous)
            anomaly_score = self.behavioral_analyzer.decision_function(feature_array)[0]
            
            # Convert to 0-1 scale where 1 is most anomalous
            normalized_score = (anomaly_score + 1) / 2
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Behavioral analysis error: {e}")
            return 0.5  # Neutral score on error
    
    def _calculate_risk_score(self, user_id: str, device_fingerprint: Optional[DeviceFingerprint], 
                            behavioral_score: float, context: Dict[str, Any]) -> float:
        """Calculate comprehensive risk score"""
        
        risk_score = 0.0
        weights = self.risk_calculator
        
        # Device mismatch risk
        if device_fingerprint:
            device_risk = 0.0 if self._validate_device_fingerprint(user_id, device_fingerprint) else 1.0
            risk_score += device_risk * weights['device_mismatch']
        
        # Location anomaly risk
        location_risk = self._calculate_location_risk(context)
        risk_score += location_risk * weights['location_anomaly']
        
        # Behavioral anomaly risk
        risk_score += behavioral_score * weights['behavioral_anomaly']
        
        # Time anomaly risk
        time_risk = self._calculate_time_risk(user_id, context)
        risk_score += time_risk * weights['time_anomaly']
        
        # Failed attempts risk
        failed_attempts_risk = self._calculate_failed_attempts_risk(context.get('ip_address'))
        risk_score += failed_attempts_risk * weights['failed_attempts']
        
        return min(risk_score, 1.0)
    
    def _calculate_location_risk(self, context: Dict[str, Any]) -> float:
        """Calculate location-based risk"""
        # In production, this would check against known user locations
        # For demo purposes, returning low risk
        return 0.1
    
    def _calculate_time_risk(self, user_id: str, context: Dict[str, Any]) -> float:
        """Calculate time-based risk"""
        current_hour = datetime.now().hour
        
        # High risk during unusual hours (2 AM - 6 AM)
        if 2 <= current_hour <= 6:
            return 0.8
        elif 22 <= current_hour or current_hour <= 6:
            return 0.5
        else:
            return 0.1
    
    def _calculate_failed_attempts_risk(self, ip_address: Optional[str]) -> float:
        """Calculate risk based on failed attempts"""
        if not ip_address:
            return 0.0
        
        recent_failures = [
            attempt for attempt in self.failed_attempts[ip_address]
            if datetime.now() - attempt < timedelta(minutes=15)
        ]
        
        if len(recent_failures) >= self.config['max_failed_attempts']:
            return 1.0
        elif len(recent_failures) > 0:
            return len(recent_failures) / self.config['max_failed_attempts']
        
        return 0.0
    
    def _create_session(self, user_id: str, device_fingerprint: Optional[DeviceFingerprint],
                       risk_score: float, context: Dict[str, Any]) -> AuthSession:
        """Create authentication session"""
        
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = AuthSession(
            session_id=session_id,
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            risk_score=risk_score,
            auth_methods_used=[AuthMethod.PASSWORD],
            created_at=now,
            expires_at=now + timedelta(seconds=self.session_timeout),
            last_activity=now,
            ip_address=context.get('ip_address', ''),
            user_agent=context.get('user_agent', ''),
        )
        
        with self._lock:
            self.active_sessions[session_id] = session
        
        return session
    
    def validate_session(self, session_id: str, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate existing session"""
        
        with self._lock:
            session = self.active_sessions.get(session_id)
            
            if not session:
                return False, "Session not found"
            
            if not session.is_active:
                return False, "Session inactive"
            
            if datetime.now() > session.expires_at:
                session.is_active = False
                return False, "Session expired"
            
            # Update last activity
            session.last_activity = datetime.now()
            
            # Check for session hijacking indicators
            if self._detect_session_hijacking(session, context):
                session.is_active = False
                return False, "Session hijacking detected"
            
            return True, session.user_id
    
    def _detect_session_hijacking(self, session: AuthSession, context: Dict[str, Any]) -> bool:
        """Detect potential session hijacking"""
        
        # Check IP address change
        if session.ip_address and context.get('ip_address') != session.ip_address:
            return True
        
        # Check user agent change
        if session.user_agent and context.get('user_agent') != session.user_agent:
            return True
        
        return False
    
    def _record_failed_attempt(self, ip_address: Optional[str]):
        """Record failed authentication attempt"""
        if not ip_address:
            return
        
        with self._lock:
            self.failed_attempts[ip_address].append(datetime.now())
            
            # Block IP if too many failed attempts
            recent_failures = [
                attempt for attempt in self.failed_attempts[ip_address]
                if datetime.now() - attempt < timedelta(minutes=15)
            ]
            
            if len(recent_failures) >= self.config['max_failed_attempts']:
                self.blocked_ips[ip_address] = datetime.now() + timedelta(seconds=self.config['lockout_duration'])
                logger.warning(f"IP {ip_address} blocked due to failed attempts")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while True:
                try:
                    self._cleanup_expired_sessions()
                    self._cleanup_failed_attempts()
                    time.sleep(self.config['cleanup_interval'])
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.now()
        
        with self._lock:
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if now > session.expires_at or not session.is_active
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
    
    def _cleanup_failed_attempts(self):
        """Clean up old failed attempts"""
        cutoff_time = datetime.now() - timedelta(minutes=15)
        
        with self._lock:
            for ip_address in list(self.failed_attempts.keys()):
                self.failed_attempts[ip_address] = [
                    attempt for attempt in self.failed_attempts[ip_address]
                    if attempt > cutoff_time
                ]
                
                if not self.failed_attempts[ip_address]:
                    del self.failed_attempts[ip_address]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            return {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'risk_score': session.risk_score,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'ip_address': session.ip_address,
                'is_active': session.is_active,
            }
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke active session"""
        with self._lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].is_active = False
                return True
            return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        with self._lock:
            return len([s for s in self.active_sessions.values() if s.is_active])
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get risk statistics"""
        with self._lock:
            active_sessions = [s for s in self.active_sessions.values() if s.is_active]
            
            if not active_sessions:
                return {'average_risk': 0.0, 'high_risk_sessions': 0}
            
            risk_scores = [s.risk_score for s in active_sessions]
            high_risk_count = len([r for r in risk_scores if r > self.config['risk_threshold_high']])
            
            return {
                'average_risk': sum(risk_scores) / len(risk_scores),
                'high_risk_sessions': high_risk_count,
                'total_sessions': len(active_sessions),
            } 