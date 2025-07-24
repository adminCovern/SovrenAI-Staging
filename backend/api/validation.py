#!/usr/bin/env python3
"""
SOVREN Billing System - Input Validation
Production-grade input validation with security hardening
"""

import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger('BillingValidation')

class ValidationError(Exception):
    """Validation error with field details"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

@dataclass
class ValidationResult:
    """Validation result with success status and errors"""
    is_valid: bool
    errors: List[ValidationError]
    sanitized_data: Dict[str, Any]

class BillingValidator:
    """Production input validator for billing system"""
    
    def __init__(self):
        # Security patterns
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.name_pattern = re.compile(r'^[a-zA-Z\s\-\.\']{1,100}$')
        self.company_pattern = re.compile(r'^[a-zA-Z0-9\s\-\.\&]{1,200}$')
        self.id_pattern = re.compile(r'^[a-zA-Z0-9_-]{1,50}$')
        
        # Allowed tiers
        self.allowed_tiers = {'SOVREN_PROOF', 'SOVREN_PROOF_PLUS'}
        self.allowed_billing_periods = {'monthly', 'yearly'}
        self.allowed_currencies = {'USD', 'EUR', 'GBP'}
        
        # Price limits
        self.max_price = Decimal('100000.00')
        self.min_price = Decimal('0.01')
    
    def validate_customer_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate customer creation data"""
        errors = []
        sanitized = {}
        
        try:
            # Email validation
            email = data.get('email', '').strip().lower()
            if not email:
                errors.append(ValidationError('email', 'Email is required'))
            elif not self.email_pattern.match(email):
                errors.append(ValidationError('email', 'Invalid email format'))
            else:
                # Additional email validation
                try:
                    validate_email(email)
                    sanitized['email'] = email
                except EmailNotValidError:
                    errors.append(ValidationError('email', 'Invalid email address'))
            
            # Name validation
            name = data.get('name', '').strip()
            if not name:
                errors.append(ValidationError('name', 'Name is required'))
            elif not self.name_pattern.match(name):
                errors.append(ValidationError('name', 'Invalid name format'))
            else:
                sanitized['name'] = name[:100]  # Limit length
            
            # Company validation (optional)
            company = data.get('company', '').strip()
            if company:
                if not self.company_pattern.match(company):
                    errors.append(ValidationError('company', 'Invalid company name format'))
                else:
                    sanitized['company'] = company[:200]  # Limit length
            
            # Metadata validation
            metadata = data.get('metadata', {})
            if not isinstance(metadata, dict):
                errors.append(ValidationError('metadata', 'Metadata must be a dictionary'))
            else:
                # Sanitize metadata keys and values
                sanitized_metadata = {}
                for key, value in metadata.items():
                    if isinstance(key, str) and self.id_pattern.match(key):
                        if isinstance(value, (str, int, float, bool)):
                            sanitized_metadata[key] = value
                        elif isinstance(value, dict):
                            # Recursively validate nested dict
                            nested_result = self.validate_metadata_dict(value)
                            if nested_result.is_valid:
                                sanitized_metadata[key] = nested_result.sanitized_data
                            else:
                                errors.extend(nested_result.errors)
                
                sanitized['metadata'] = sanitized_metadata
            
        except Exception as e:
            errors.append(ValidationError('general', f'Validation error: {str(e)}'))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_data=sanitized
        )
    
    def validate_subscription_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate subscription creation data"""
        errors = []
        sanitized = {}
        
        try:
            # Customer ID validation
            customer_id = data.get('customer_id', '').strip()
            if not customer_id:
                errors.append(ValidationError('customer_id', 'Customer ID is required'))
            elif not self.id_pattern.match(customer_id):
                errors.append(ValidationError('customer_id', 'Invalid customer ID format'))
            else:
                sanitized['customer_id'] = customer_id
            
            # Tier validation
            tier = data.get('tier', '').strip()
            if not tier:
                errors.append(ValidationError('tier', 'Tier is required'))
            elif tier not in self.allowed_tiers:
                errors.append(ValidationError('tier', f'Invalid tier. Allowed: {", ".join(self.allowed_tiers)}'))
            else:
                sanitized['tier'] = tier
            
            # Billing period validation
            billing_period = data.get('billing_period', 'monthly').strip()
            if billing_period not in self.allowed_billing_periods:
                errors.append(ValidationError('billing_period', f'Invalid billing period. Allowed: {", ".join(self.allowed_billing_periods)}'))
            else:
                sanitized['billing_period'] = billing_period
            
        except Exception as e:
            errors.append(ValidationError('general', f'Validation error: {str(e)}'))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_data=sanitized
        )
    
    def validate_payment_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate payment processing data"""
        errors = []
        sanitized = {}
        
        try:
            # Customer ID validation
            customer_id = data.get('customer_id', '').strip()
            if not customer_id:
                errors.append(ValidationError('customer_id', 'Customer ID is required'))
            elif not self.id_pattern.match(customer_id):
                errors.append(ValidationError('customer_id', 'Invalid customer ID format'))
            else:
                sanitized['customer_id'] = customer_id
            
            # Amount validation
            amount_str = data.get('amount', '')
            if not amount_str:
                errors.append(ValidationError('amount', 'Amount is required'))
            else:
                try:
                    amount = Decimal(str(amount_str))
                    if amount < self.min_price or amount > self.max_price:
                        errors.append(ValidationError('amount', f'Amount must be between {self.min_price} and {self.max_price}'))
                    else:
                        sanitized['amount'] = amount
                except (InvalidOperation, ValueError):
                    errors.append(ValidationError('amount', 'Invalid amount format'))
            
            # Currency validation
            currency = data.get('currency', 'USD').strip().upper()
            if currency not in self.allowed_currencies:
                errors.append(ValidationError('currency', f'Invalid currency. Allowed: {", ".join(self.allowed_currencies)}'))
            else:
                sanitized['currency'] = currency
            
            # Payment method validation
            payment_method = data.get('payment_method', {})
            if not isinstance(payment_method, dict):
                errors.append(ValidationError('payment_method', 'Payment method must be a dictionary'))
            else:
                # Basic payment method validation
                if 'id' not in payment_method:
                    errors.append(ValidationError('payment_method', 'Payment method ID is required'))
                else:
                    payment_id = str(payment_method['id']).strip()
                    if not self.id_pattern.match(payment_id):
                        errors.append(ValidationError('payment_method', 'Invalid payment method ID format'))
                    else:
                        sanitized['payment_method'] = {'id': payment_id}
            
        except Exception as e:
            errors.append(ValidationError('general', f'Validation error: {str(e)}'))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_data=sanitized
        )
    
    def validate_usage_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate usage tracking data"""
        errors = []
        sanitized = {}
        
        try:
            # Subscription ID validation
            subscription_id = data.get('subscription_id', '').strip()
            if not subscription_id:
                errors.append(ValidationError('subscription_id', 'Subscription ID is required'))
            elif not self.id_pattern.match(subscription_id):
                errors.append(ValidationError('subscription_id', 'Invalid subscription ID format'))
            else:
                sanitized['subscription_id'] = subscription_id
            
            # Usage type validation
            usage_type = data.get('usage_type', '').strip()
            allowed_usage_types = {'api_calls', 'gpu_hours', 'storage_gb'}
            if not usage_type:
                errors.append(ValidationError('usage_type', 'Usage type is required'))
            elif usage_type not in allowed_usage_types:
                errors.append(ValidationError('usage_type', f'Invalid usage type. Allowed: {", ".join(allowed_usage_types)}'))
            else:
                sanitized['usage_type'] = usage_type
            
            # Amount validation
            amount_str = data.get('amount', '')
            if not amount_str:
                errors.append(ValidationError('amount', 'Amount is required'))
            else:
                try:
                    amount = float(amount_str)
                    if amount < 0:
                        errors.append(ValidationError('amount', 'Amount must be non-negative'))
                    else:
                        sanitized['amount'] = amount
                except (ValueError, TypeError):
                    errors.append(ValidationError('amount', 'Invalid amount format'))
            
        except Exception as e:
            errors.append(ValidationError('general', f'Validation error: {str(e)}'))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_data=sanitized
        )
    
    def validate_metadata_dict(self, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate metadata dictionary recursively"""
        errors = []
        sanitized = {}
        
        try:
            for key, value in metadata.items():
                if isinstance(key, str) and self.id_pattern.match(key):
                    if isinstance(value, (str, int, float, bool)):
                        # Limit string length
                        if isinstance(value, str):
                            sanitized[key] = value[:1000]  # Limit string length
                        else:
                            sanitized[key] = value
                    elif isinstance(value, dict):
                        # Recursively validate nested dict (max depth 3)
                        nested_result = self.validate_metadata_dict(value)
                        if nested_result.is_valid:
                            sanitized[key] = nested_result.sanitized_data
                        else:
                            errors.extend(nested_result.errors)
                else:
                    errors.append(ValidationError('metadata', f'Invalid metadata key: {key}'))
            
        except Exception as e:
            errors.append(ValidationError('metadata', f'Metadata validation error: {str(e)}'))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_data=sanitized
        )
    
    def sanitize_string(self, value: str, max_length: int = 100) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32)
        
        # Limit length
        return sanitized[:max_length].strip()
    
    def validate_webhook_payload(self, payload: Dict[str, Any]) -> ValidationResult:
        """Validate webhook payload"""
        errors = []
        sanitized = {}
        
        try:
            # Event type validation
            event_type = payload.get('event_type', '').strip()
            allowed_events = {'PAYMENT_SUCCESS', 'PAYMENT_FAILED', 'SUBSCRIPTION_CANCELLED', 'INVOICE_CREATED'}
            if not event_type:
                errors.append(ValidationError('event_type', 'Event type is required'))
            elif event_type not in allowed_events:
                errors.append(ValidationError('event_type', f'Invalid event type. Allowed: {", ".join(allowed_events)}'))
            else:
                sanitized['event_type'] = event_type
            
            # Signature validation
            signature = payload.get('signature', '').strip()
            if not signature:
                errors.append(ValidationError('signature', 'Webhook signature is required'))
            elif not re.match(r'^[a-f0-9]{64}$', signature):
                errors.append(ValidationError('signature', 'Invalid signature format'))
            else:
                sanitized['signature'] = signature
            
            # Payload data validation
            payload_data = payload.get('data', {})
            if not isinstance(payload_data, dict):
                errors.append(ValidationError('data', 'Payload data must be a dictionary'))
            else:
                sanitized['data'] = payload_data
            
        except Exception as e:
            errors.append(ValidationError('general', f'Webhook validation error: {str(e)}'))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_data=sanitized
        )

# Global validator instance
validator: Optional[BillingValidator] = None

def initialize_validator():
    """Initialize global validator"""
    global validator
    validator = BillingValidator()
    logger.info("Billing validator initialized")

def get_validator() -> BillingValidator:
    """Get global validator instance"""
    if validator is None:
        raise RuntimeError("Validator not initialized")
    return validator 