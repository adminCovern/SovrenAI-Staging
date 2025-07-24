#!/usr/bin/env python3
"""
SOVREN AI - Secure Configuration Management System
Production-ready config management with encryption, access controls, and audit logging
"""

import os
import sys
import json
import time
import threading
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3

logger = logging.getLogger('SecureConfigManager')

class ConfigAccessLevel(Enum):
    """Configuration access levels"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SYSTEM = "system"

class ConfigCategory(Enum):
    """Configuration categories"""
    DATABASE = "database"
    API_KEYS = "api_keys"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MONITORING = "monitoring"
    BUSINESS = "business"
    SYSTEM = "system"

@dataclass
class ConfigItem:
    """Configuration item"""
    key: str
    value: Any
    category: ConfigCategory
    encrypted: bool = False
    access_level: ConfigAccessLevel = ConfigAccessLevel.READ_WRITE
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1

@dataclass
class ConfigAccess:
    """Configuration access control"""
    user_id: str
    access_level: ConfigAccessLevel
    categories: List[ConfigCategory]
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

class SecureConfigManager:
    """Production-ready secure configuration management system"""
    
    def __init__(self, config_path: str = "/etc/sovren/config", 
                 encryption_key: Optional[bytes] = None):
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.crypto_manager = self._init_crypto_manager(encryption_key)
        
        # Initialize database
        self.db_path = self.config_path / "config.db"
        self.db_connection = self._init_database()
        
        # Configuration cache
        self.config_cache: Dict[str, ConfigItem] = {}
        self.cache_lock = threading.RLock()
        
        # Access control
        self.access_controls: Dict[str, ConfigAccess] = {}
        self.access_lock = threading.RLock()
        
        # Audit logging
        self.audit_log = []
        self.audit_lock = threading.RLock()
        
        # Load initial configuration
        self._load_initial_config()
        
        logger.info("Secure configuration manager initialized")
    
    def _init_crypto_manager(self, encryption_key: Optional[bytes]) -> Fernet:
        """Initialize cryptographic manager"""
        
        if encryption_key:
            return Fernet(encryption_key)
        else:
            # Generate new key or load from file
            key_file = self.config_path / "encryption.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
            
            return Fernet(key)
    
    def _init_database(self) -> sqlite3.Connection:
        """Initialize configuration database"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Create configuration table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS config_items (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                encrypted INTEGER DEFAULT 0,
                access_level TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                hash_signature TEXT
            )
        ''')
        
        # Create access control table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS config_access (
                user_id TEXT,
                access_level TEXT NOT NULL,
                categories TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                expires_at TEXT,
                PRIMARY KEY (user_id, access_level)
            )
        ''')
        
        # Create audit log table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS config_audit (
                audit_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                action TEXT NOT NULL,
                config_key TEXT,
                old_value TEXT,
                new_value TEXT,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        # Create indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_config_category ON config_items(category)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_config_access_level ON config_items(access_level)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON config_audit(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON config_audit(user_id)')
        
        conn.commit()
        return conn
    
    def _load_initial_config(self):
        """Load initial configuration"""
        
        try:
            # Load from database
            cursor = self.db_connection.execute('SELECT * FROM config_items')
            rows = cursor.fetchall()
            
            for row in rows:
                config_item = ConfigItem(
                    key=row[0],
                    value=self._decrypt_value(row[1]) if row[3] else json.loads(row[1]),
                    category=ConfigCategory(row[2]),
                    encrypted=bool(row[3]),
                    access_level=ConfigAccessLevel(row[4]),
                    description=row[5] or "",
                    created_at=datetime.fromisoformat(row[6]),
                    updated_at=datetime.fromisoformat(row[7]),
                    version=row[8],
                )
                
                with self.cache_lock:
                    self.config_cache[config_item.key] = config_item
            
            logger.info(f"Loaded {len(rows)} configuration items")
            
        except Exception as e:
            logger.error(f"Failed to load initial configuration: {e}")
    
    def set_config(self, key: str, value: Any, category: ConfigCategory,
                  user_id: str, encrypted: bool = False, 
                  access_level: ConfigAccessLevel = ConfigAccessLevel.READ_WRITE,
                  description: str = "") -> bool:
        """Set configuration value with access control"""
        
        try:
            # Check access permissions
            if not self._check_access(user_id, access_level, category):
                self._log_audit_event(user_id, "access_denied", key, None, None)
                logger.warning(f"Access denied for user {user_id} to config {key}")
                return False
            
            # Get current value for audit
            old_value = None
            if key in self.config_cache:
                old_value = self.config_cache[key].value
            
            # Create or update configuration item
            if key in self.config_cache:
                config_item = self.config_cache[key]
                config_item.value = value
                config_item.updated_at = datetime.now()
                config_item.version += 1
                config_item.encrypted = encrypted
                config_item.access_level = access_level
                config_item.description = description
            else:
                config_item = ConfigItem(
                    key=key,
                    value=value,
                    category=category,
                    encrypted=encrypted,
                    access_level=access_level,
                    description=description,
                )
            
            # Encrypt value if needed
            if encrypted:
                value_to_store = self._encrypt_value(value)
                stored_value = base64.b64encode(value_to_store).decode()
            else:
                stored_value = json.dumps(value)
            
            # Generate hash signature
            hash_data = f"{key}{stored_value}{config_item.updated_at.isoformat()}"
            hash_signature = hashlib.sha256(hash_data.encode()).hexdigest()
            
            # Store in database
            self.db_connection.execute('''
                INSERT OR REPLACE INTO config_items (
                    key, value, category, encrypted, access_level, description,
                    created_at, updated_at, version, hash_signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                key,
                stored_value,
                category.value,
                1 if encrypted else 0,
                access_level.value,
                description,
                config_item.created_at.isoformat(),
                config_item.updated_at.isoformat(),
                config_item.version,
                hash_signature,
            ))
            
            self.db_connection.commit()
            
            # Update cache
            with self.cache_lock:
                self.config_cache[key] = config_item
            
            # Log audit event
            self._log_audit_event(user_id, "set_config", key, old_value, value)
            
            logger.info(f"Configuration set: {key} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set configuration {key}: {e}")
            return False
    
    def get_config(self, key: str, user_id: str, default: Any = None) -> Any:
        """Get configuration value with access control"""
        
        try:
            # Check if key exists
            if key not in self.config_cache:
                return default
            
            config_item = self.config_cache[key]
            
            # Check access permissions
            if not self._check_access(user_id, ConfigAccessLevel.READ_ONLY, config_item.category):
                self._log_audit_event(user_id, "access_denied", key, None, None)
                logger.warning(f"Access denied for user {user_id} to config {key}")
                return default
            
            # Log audit event
            self._log_audit_event(user_id, "get_config", key, None, None)
            
            return config_item.value
            
        except Exception as e:
            logger.error(f"Failed to get configuration {key}: {e}")
            return default
    
    def delete_config(self, key: str, user_id: str) -> bool:
        """Delete configuration value with access control"""
        
        try:
            # Check if key exists
            if key not in self.config_cache:
                return False
            
            config_item = self.config_cache[key]
            
            # Check access permissions
            if not self._check_access(user_id, ConfigAccessLevel.ADMIN, config_item.category):
                self._log_audit_event(user_id, "access_denied", key, None, None)
                logger.warning(f"Access denied for user {user_id} to delete config {key}")
                return False
            
            # Get current value for audit
            old_value = config_item.value
            
            # Remove from database
            self.db_connection.execute('DELETE FROM config_items WHERE key = ?', (key,))
            self.db_connection.commit()
            
            # Remove from cache
            with self.cache_lock:
                del self.config_cache[key]
            
            # Log audit event
            self._log_audit_event(user_id, "delete_config", key, old_value, None)
            
            logger.info(f"Configuration deleted: {key} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete configuration {key}: {e}")
            return False
    
    def list_configs(self, user_id: str, category: Optional[ConfigCategory] = None) -> List[Dict[str, Any]]:
        """List configuration items with access control"""
        
        try:
            configs = []
            
            with self.cache_lock:
                for key, config_item in self.config_cache.items():
                    # Filter by category if specified
                    if category and config_item.category != category:
                        continue
                    
                    # Check access permissions
                    if not self._check_access(user_id, ConfigAccessLevel.READ_ONLY, config_item.category):
                        continue
                    
                    configs.append({
                        'key': key,
                        'category': config_item.category.value,
                        'access_level': config_item.access_level.value,
                        'description': config_item.description,
                        'encrypted': config_item.encrypted,
                        'created_at': config_item.created_at.isoformat(),
                        'updated_at': config_item.updated_at.isoformat(),
                        'version': config_item.version,
                    })
            
            # Log audit event
            self._log_audit_event(user_id, "list_configs", None, None, None)
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to list configurations: {e}")
            return []
    
    def grant_access(self, user_id: str, access_level: ConfigAccessLevel,
                    categories: List[ConfigCategory], expires_at: Optional[datetime] = None):
        """Grant configuration access to user"""
        
        try:
            access = ConfigAccess(
                user_id=user_id,
                access_level=access_level,
                categories=categories,
                expires_at=expires_at,
            )
            
            # Store in database
            self.db_connection.execute('''
                INSERT OR REPLACE INTO config_access (
                    user_id, access_level, categories, granted_at, expires_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                access_level.value,
                json.dumps([cat.value for cat in categories]),
                access.granted_at.isoformat(),
                expires_at.isoformat() if expires_at else None,
            ))
            
            self.db_connection.commit()
            
            # Update cache
            with self.access_lock:
                self.access_controls[user_id] = access
            
            # Log audit event
            self._log_audit_event(user_id, "grant_access", None, None, {
                'access_level': access_level.value,
                'categories': [cat.value for cat in categories],
                'expires_at': expires_at.isoformat() if expires_at else None,
            })
            
            logger.info(f"Access granted to user {user_id}: {access_level.value}")
            
        except Exception as e:
            logger.error(f"Failed to grant access to user {user_id}: {e}")
    
    def revoke_access(self, user_id: str):
        """Revoke configuration access from user"""
        
        try:
            # Remove from database
            self.db_connection.execute('DELETE FROM config_access WHERE user_id = ?', (user_id,))
            self.db_connection.commit()
            
            # Remove from cache
            with self.access_lock:
                if user_id in self.access_controls:
                    del self.access_controls[user_id]
            
            # Log audit event
            self._log_audit_event(user_id, "revoke_access", None, None, None)
            
            logger.info(f"Access revoked from user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to revoke access from user {user_id}: {e}")
    
    def _check_access(self, user_id: str, required_level: ConfigAccessLevel, 
                     category: ConfigCategory) -> bool:
        """Check if user has required access level for category"""
        
        try:
            with self.access_lock:
                if user_id not in self.access_controls:
                    return False
                
                access = self.access_controls[user_id]
                
                # Check if access has expired
                if access.expires_at and datetime.now() > access.expires_at:
                    return False
                
                # Check access level hierarchy
                level_hierarchy = {
                    ConfigAccessLevel.READ_ONLY: 1,
                    ConfigAccessLevel.READ_WRITE: 2,
                    ConfigAccessLevel.ADMIN: 3,
                    ConfigAccessLevel.SYSTEM: 4,
                }
                
                user_level = level_hierarchy.get(access.access_level, 0)
                required_level_value = level_hierarchy.get(required_level, 0)
                
                if user_level < required_level_value:
                    return False
                
                # Check category access
                return category in access.categories
                
        except Exception as e:
            logger.error(f"Failed to check access for user {user_id}: {e}")
            return False
    
    def _encrypt_value(self, value: Any) -> bytes:
        """Encrypt configuration value"""
        
        value_json = json.dumps(value)
        return self.crypto_manager.encrypt(value_json.encode())
    
    def _decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt configuration value"""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted_bytes = self.crypto_manager.decrypt(encrypted_bytes)
            return json.loads(decrypted_bytes.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt value: {e}")
            return None
    
    def _log_audit_event(self, user_id: str, action: str, config_key: Optional[str],
                         old_value: Any, new_value: Any):
        """Log audit event"""
        
        try:
            audit_id = f"audit_{int(time.time() * 1000000)}"
            
            # Sanitize values for logging
            old_value_str = json.dumps(old_value) if old_value is not None else None
            new_value_str = json.dumps(new_value) if new_value is not None else None
            
            # Truncate long values
            if old_value_str and len(old_value_str) > 1000:
                old_value_str = old_value_str[:1000] + "..."
            if new_value_str and len(new_value_str) > 1000:
                new_value_str = new_value_str[:1000] + "..."
            
            # Store in database
            self.db_connection.execute('''
                INSERT INTO config_audit (
                    audit_id, timestamp, user_id, action, config_key,
                    old_value, new_value, ip_address, user_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                datetime.now().isoformat(),
                user_id,
                action,
                config_key,
                old_value_str,
                new_value_str,
                None,  # IP address would be passed from request context
                None,  # User agent would be passed from request context
            ))
            
            self.db_connection.commit()
            
            # Add to memory log
            with self.audit_lock:
                self.audit_log.append({
                    'audit_id': audit_id,
                    'timestamp': datetime.now(),
                    'user_id': user_id,
                    'action': action,
                    'config_key': config_key,
                })
                
                # Keep only last 1000 audit events in memory
                if len(self.audit_log) > 1000:
                    self.audit_log = self.audit_log[-1000:]
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def get_audit_log(self, user_id: Optional[str] = None, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log with filtering"""
        
        try:
            query = 'SELECT * FROM config_audit WHERE 1=1'
            params = []
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date.isoformat())
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date.isoformat())
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor = self.db_connection.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {
                    'audit_id': row[0],
                    'timestamp': row[1],
                    'user_id': row[2],
                    'action': row[3],
                    'config_key': row[4],
                    'old_value': row[5],
                    'new_value': row[6],
                    'ip_address': row[7],
                    'user_agent': row[8],
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            return []
    
    def export_config(self, user_id: str, category: Optional[ConfigCategory] = None) -> Dict[str, Any]:
        """Export configuration with access control"""
        
        try:
            # Check admin access
            if not self._check_access(user_id, ConfigAccessLevel.ADMIN, ConfigCategory.SYSTEM):
                logger.warning(f"Access denied for user {user_id} to export config")
                return {}
            
            configs = {}
            
            with self.cache_lock:
                for key, config_item in self.config_cache.items():
                    # Filter by category if specified
                    if category and config_item.category != category:
                        continue
                    
                    # Check access permissions
                    if not self._check_access(user_id, ConfigAccessLevel.READ_ONLY, config_item.category):
                        continue
                    
                    configs[key] = {
                        'value': config_item.value,
                        'category': config_item.category.value,
                        'access_level': config_item.access_level.value,
                        'description': config_item.description,
                        'encrypted': config_item.encrypted,
                        'created_at': config_item.created_at.isoformat(),
                        'updated_at': config_item.updated_at.isoformat(),
                        'version': config_item.version,
                    }
            
            # Log audit event
            self._log_audit_event(user_id, "export_config", None, None, {
                'category': category.value if category else 'all',
                'config_count': len(configs),
            })
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return {}
    
    def import_config(self, user_id: str, config_data: Dict[str, Any]) -> bool:
        """Import configuration with access control"""
        
        try:
            # Check admin access
            if not self._check_access(user_id, ConfigAccessLevel.ADMIN, ConfigCategory.SYSTEM):
                logger.warning(f"Access denied for user {user_id} to import config")
                return False
            
            imported_count = 0
            
            for key, config_info in config_data.items():
                try:
                    category = ConfigCategory(config_info['category'])
                    access_level = ConfigAccessLevel(config_info['access_level'])
                    
                    # Check access permissions for this category
                    if not self._check_access(user_id, ConfigAccessLevel.ADMIN, category):
                        continue
                    
                    # Set configuration
                    success = self.set_config(
                        key=key,
                        value=config_info['value'],
                        category=category,
                        user_id=user_id,
                        encrypted=config_info.get('encrypted', False),
                        access_level=access_level,
                        description=config_info.get('description', ''),
                    )
                    
                    if success:
                        imported_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to import config {key}: {e}")
            
            # Log audit event
            self._log_audit_event(user_id, "import_config", None, None, {
                'imported_count': imported_count,
                'total_count': len(config_data),
            })
            
            logger.info(f"Imported {imported_count} configuration items")
            return imported_count > 0
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get configuration system health status"""
        
        try:
            # Check database health
            cursor = self.db_connection.execute('SELECT COUNT(*) FROM config_items')
            total_configs = cursor.fetchone()[0]
            
            cursor = self.db_connection.execute('SELECT COUNT(*) FROM config_access')
            total_access_controls = cursor.fetchone()[0]
            
            cursor = self.db_connection.execute('SELECT COUNT(*) FROM config_audit')
            total_audit_events = cursor.fetchone()[0]
            
            # Check cache health
            cache_size = len(self.config_cache)
            cache_hit_rate = cache_size / total_configs if total_configs > 0 else 1.0
            
            # Check for encrypted configs
            encrypted_count = len([c for c in self.config_cache.values() if c.encrypted])
            
            return {
                'status': 'healthy',
                'total_configs': total_configs,
                'cache_size': cache_size,
                'cache_hit_rate': cache_hit_rate,
                'encrypted_configs': encrypted_count,
                'access_controls': total_access_controls,
                'audit_events': total_audit_events,
                'database_size_mb': self._get_database_size(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_database_size(self) -> float:
        """Get database size in MB"""
        try:
            size_bytes = self.db_path.stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0 