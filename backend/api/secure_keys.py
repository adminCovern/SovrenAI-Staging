#!/usr/bin/env python3
"""
SOVREN Billing System - Secure Key Management
Production-grade encryption for sensitive credentials
"""

import os
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('SecureKeys')

class SecureKeyManager:
    """Production-grade secure key management"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize key manager with optional master key"""
        if master_key:
            self.master_key = master_key.encode()
        else:
            # Generate from environment or create new
            env_key = os.getenv('SOVREN_MASTER_KEY')
            if env_key:
                self.master_key = env_key.encode()
            else:
                # Generate new master key
                self.master_key = Fernet.generate_key()
                logger.warning("No master key found. Generated new key. Store this securely!")
                logger.warning(f"Master key: {self.master_key.decode()}")
        
        self.cipher = Fernet(self.master_key)
        self._encrypted_keys: Dict[str, str] = {}
    
    def encrypt_key(self, key_name: str, api_key: str) -> str:
        """Encrypt API key"""
        if not api_key:
            raise ValueError(f"API key for {key_name} cannot be empty")
        
        encrypted = self.cipher.encrypt(api_key.encode())
        encrypted_b64 = base64.b64encode(encrypted).decode()
        
        # Store encrypted key
        self._encrypted_keys[key_name] = encrypted_b64
        
        logger.info(f"Encrypted key: {key_name}")
        return encrypted_b64
    
    def decrypt_key(self, key_name: str, encrypted_key: str) -> str:
        """Decrypt API key"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt key {key_name}: {e}")
            raise ValueError(f"Invalid encrypted key for {key_name}")
    
    def store_key(self, key_name: str, api_key: str) -> str:
        """Store encrypted key"""
        return self.encrypt_key(key_name, api_key)
    
    def get_key(self, key_name: str) -> str:
        """Get decrypted key"""
        if key_name not in self._encrypted_keys:
            raise KeyError(f"Key {key_name} not found")
        
        return self.decrypt_key(key_name, self._encrypted_keys[key_name])
    
    def rotate_key(self, key_name: str, new_key: str) -> str:
        """Rotate (re-encrypt) a key"""
        encrypted = self.store_key(key_name, new_key)
        logger.info(f"Rotated key: {key_name}")
        return encrypted
    
    def list_keys(self) -> list:
        """List all stored key names"""
        return list(self._encrypted_keys.keys())
    
    def remove_key(self, key_name: str) -> bool:
        """Remove a stored key"""
        if key_name in self._encrypted_keys:
            del self._encrypted_keys[key_name]
            logger.info(f"Removed key: {key_name}")
            return True
        return False
    
    def export_keys(self) -> Dict[str, str]:
        """Export all encrypted keys (for backup)"""
        return self._encrypted_keys.copy()
    
    def import_keys(self, keys: Dict[str, str]) -> None:
        """Import encrypted keys (from backup)"""
        for key_name, encrypted_key in keys.items():
            # Validate by attempting to decrypt
            try:
                self.decrypt_key(key_name, encrypted_key)
                self._encrypted_keys[key_name] = encrypted_key
                logger.info(f"Imported key: {key_name}")
            except Exception as e:
                logger.error(f"Failed to import key {key_name}: {e}")
                raise ValueError(f"Invalid encrypted key for {key_name}")

class BillingKeyManager:
    """Specialized key manager for billing system"""
    
    def __init__(self):
        self.key_manager = SecureKeyManager()
        self._initialize_default_keys()
    
    def _initialize_default_keys(self):
        """Initialize with default keys if not already stored"""
        default_keys = {
            'stripe_live_secret': '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',
            'stripe_live_publishable': 'pk_live_51RYa1A2UNNWAe8rDFjFdM50I5jsAruUs8uzb9T7DigMqN0sfvwdmUu9XZo7T7LQ4ilBQtzJwMrgSw50R9Fl2grM300BCpn1ecA',
            'killbill_api_key': 'sovren',
            'killbill_api_secret': 'sovren123',
            'killbill_tenant_key': 'sovren_tenant',
            'killbill_tenant_secret': 'sovren_tenant_secret',
            'database_password': os.getenv('DB_PASSWORD', ''),
            'webhook_secret': os.getenv('WEBHOOK_SECRET', 'sovren_webhook_secret')
        }
        
        for key_name, key_value in default_keys.items():
            if key_value and key_name not in self.key_manager.list_keys():
                self.key_manager.store_key(key_name, key_value)
    
    def get_stripe_secret_key(self) -> str:
        """Get Stripe live secret key"""
        return self.key_manager.get_key('stripe_live_secret')
    
    def get_stripe_publishable_key(self) -> str:
        """Get Stripe live publishable key"""
        return self.key_manager.get_key('stripe_live_publishable')
    
    def get_killbill_api_key(self) -> str:
        """Get Kill Bill API key"""
        return self.key_manager.get_key('killbill_api_key')
    
    def get_killbill_api_secret(self) -> str:
        """Get Kill Bill API secret"""
        return self.key_manager.get_key('killbill_api_secret')
    
    def get_killbill_tenant_key(self) -> str:
        """Get Kill Bill tenant API key"""
        return self.key_manager.get_key('killbill_tenant_key')
    
    def get_killbill_tenant_secret(self) -> str:
        """Get Kill Bill tenant API secret"""
        return self.key_manager.get_key('killbill_tenant_secret')
    
    def get_database_password(self) -> str:
        """Get database password"""
        return self.key_manager.get_key('database_password')
    
    def get_webhook_secret(self) -> str:
        """Get webhook secret"""
        return self.key_manager.get_key('webhook_secret')
    
    def update_stripe_keys(self, secret_key: str, publishable_key: str) -> None:
        """Update Stripe keys"""
        self.key_manager.store_key('stripe_live_secret', secret_key)
        self.key_manager.store_key('stripe_live_publishable', publishable_key)
        logger.info("Updated Stripe keys")
    
    def update_killbill_credentials(self, api_key: str, api_secret: str, 
                                 tenant_key: str, tenant_secret: str) -> None:
        """Update Kill Bill credentials"""
        self.key_manager.store_key('killbill_api_key', api_key)
        self.key_manager.store_key('killbill_api_secret', api_secret)
        self.key_manager.store_key('killbill_tenant_key', tenant_key)
        self.key_manager.store_key('killbill_tenant_secret', tenant_secret)
        logger.info("Updated Kill Bill credentials")
    
    def update_database_password(self, password: str) -> None:
        """Update database password"""
        self.key_manager.store_key('database_password', password)
        logger.info("Updated database password")
    
    def get_all_keys_summary(self) -> Dict[str, Any]:
        """Get summary of all stored keys (names only)"""
        return {
            'stored_keys': self.key_manager.list_keys(),
            'total_keys': len(self.key_manager.list_keys())
        }

# Global key manager instance
billing_key_manager = BillingKeyManager() 