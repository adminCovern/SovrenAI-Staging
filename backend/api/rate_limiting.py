#!/usr/bin/env python3
"""
SOVREN Billing System - Rate Limiting
Production-grade rate limiting for API endpoints
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
import logging

logger = logging.getLogger('RateLimiting')

class RateLimiter:
    """Production-grade rate limiter"""
    
    def __init__(self):
        self.limits: Dict[str, Dict[str, Any]] = {}
        self.windows: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    def add_limit(self, identifier: str, max_requests: int, window_seconds: int):
        """Add rate limit for identifier"""
        self.limits[identifier] = {
            'max_requests': max_requests,
            'window_seconds': window_seconds
        }
        logger.info(f"Added rate limit: {identifier} = {max_requests} requests per {window_seconds}s")
    
    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        if identifier not in self.limits:
            return True
        
        async with self.lock:
            limit_config = self.limits[identifier]
            current_time = time.time()
            window_start = current_time - limit_config['window_seconds']
            
            # Clean old requests
            self.windows[identifier] = [
                req_time for req_time in self.windows[identifier]
                if req_time > window_start
            ]
            
            # Check if under limit
            if len(self.windows[identifier]) < limit_config['max_requests']:
                self.windows[identifier].append(current_time)
                return True
            else:
                return False
    
    async def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        if identifier not in self.limits:
            return 999999  # Large number instead of float('inf')
        
        async with self.lock:
            limit_config = self.limits[identifier]
            current_time = time.time()
            window_start = current_time - limit_config['window_seconds']
            
            # Clean old requests
            self.windows[identifier] = [
                req_time for req_time in self.windows[identifier]
                if req_time > window_start
            ]
            
            return max(0, limit_config['max_requests'] - len(self.windows[identifier]))
    
    async def get_reset_time(self, identifier: str) -> Optional[float]:
        """Get reset time for identifier"""
        if identifier not in self.limits or not self.windows[identifier]:
            return None
        
        async with self.lock:
            limit_config = self.limits[identifier]
            oldest_request = min(self.windows[identifier])
            return oldest_request + limit_config['window_seconds']

class BillingRateLimiter:
    """Specialized rate limiter for billing system"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self._setup_default_limits()
    
    def _setup_default_limits(self):
        """Setup default rate limits"""
        # API endpoint limits
        self.rate_limiter.add_limit('api_customer_creation', 10, 60)  # 10 per minute
        self.rate_limiter.add_limit('api_subscription_creation', 5, 60)  # 5 per minute
        self.rate_limiter.add_limit('api_payment_processing', 20, 60)  # 20 per minute
        self.rate_limiter.add_limit('api_usage_tracking', 100, 60)  # 100 per minute
        self.rate_limiter.add_limit('api_metrics', 30, 60)  # 30 per minute
        
        # Per-customer limits
        self.rate_limiter.add_limit('customer_payment_attempts', 5, 300)  # 5 per 5 minutes
        self.rate_limiter.add_limit('customer_subscription_changes', 3, 3600)  # 3 per hour
        
        # IP-based limits
        self.rate_limiter.add_limit('ip_api_requests', 100, 60)  # 100 per minute
        self.rate_limiter.add_limit('ip_payment_attempts', 10, 300)  # 10 per 5 minutes
        
        # Kill Bill API limits
        self.rate_limiter.add_limit('killbill_api', 50, 60)  # 50 per minute
        self.rate_limiter.add_limit('stripe_api', 100, 60)  # 100 per minute
        
        logger.info("Billing rate limits configured")
    
    async def check_api_limit(self, endpoint: str, customer_id: Optional[str] = None, 
                            ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Check API rate limit"""
        identifiers = [f'api_{endpoint}']
        
        if customer_id:
            identifiers.append(f'customer_{customer_id}_{endpoint}')
        
        if ip_address:
            identifiers.append(f'ip_{ip_address}_{endpoint}')
        
        results = {}
        for identifier in identifiers:
            is_allowed = await self.rate_limiter.is_allowed(identifier)
            remaining = await self.rate_limiter.get_remaining(identifier)
            reset_time = await self.rate_limiter.get_reset_time(identifier)
            
            results[identifier] = {
                'allowed': is_allowed,
                'remaining': remaining,
                'reset_time': reset_time
            }
        
        # Overall result - all must be allowed
        overall_allowed = all(result['allowed'] for result in results.values())
        
        return {
            'allowed': overall_allowed,
            'limits': results,
            'remaining_min': min(result['remaining'] for result in results.values()),
            'reset_time': max(result['reset_time'] for result in results.values() if result['reset_time'])
        }
    
    async def check_payment_limit(self, customer_id: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Check payment rate limit"""
        identifiers = [f'customer_payment_attempts_{customer_id}']
        
        if ip_address:
            identifiers.append(f'ip_payment_attempts_{ip_address}')
        
        results = {}
        for identifier in identifiers:
            is_allowed = await self.rate_limiter.is_allowed(identifier)
            remaining = await self.rate_limiter.get_remaining(identifier)
            reset_time = await self.rate_limiter.get_reset_time(identifier)
            
            results[identifier] = {
                'allowed': is_allowed,
                'remaining': remaining,
                'reset_time': reset_time
            }
        
        overall_allowed = all(result['allowed'] for result in results.values())
        
        return {
            'allowed': overall_allowed,
            'limits': results,
            'remaining_min': min(result['remaining'] for result in results.values()),
            'reset_time': max(result['reset_time'] for result in results.values() if result['reset_time'])
        }
    
    async def check_subscription_limit(self, customer_id: str) -> Dict[str, Any]:
        """Check subscription change rate limit"""
        identifier = f'customer_subscription_changes_{customer_id}'
        
        is_allowed = await self.rate_limiter.is_allowed(identifier)
        remaining = await self.rate_limiter.get_remaining(identifier)
        reset_time = await self.rate_limiter.get_reset_time(identifier)
        
        return {
            'allowed': is_allowed,
            'remaining': remaining,
            'reset_time': reset_time
        }
    
    async def check_killbill_limit(self) -> Dict[str, Any]:
        """Check Kill Bill API rate limit"""
        identifier = 'killbill_api'
        
        is_allowed = await self.rate_limiter.is_allowed(identifier)
        remaining = await self.rate_limiter.get_remaining(identifier)
        reset_time = await self.rate_limiter.get_reset_time(identifier)
        
        return {
            'allowed': is_allowed,
            'remaining': remaining,
            'reset_time': reset_time
        }
    
    async def check_stripe_limit(self) -> Dict[str, Any]:
        """Check Stripe API rate limit"""
        identifier = 'stripe_api'
        
        is_allowed = await self.rate_limiter.is_allowed(identifier)
        remaining = await self.rate_limiter.get_remaining(identifier)
        reset_time = await self.rate_limiter.get_reset_time(identifier)
        
        return {
            'allowed': is_allowed,
            'remaining': remaining,
            'reset_time': reset_time
        }
    
    def add_custom_limit(self, identifier: str, max_requests: int, window_seconds: int):
        """Add custom rate limit"""
        self.rate_limiter.add_limit(identifier, max_requests, window_seconds)
    
    async def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get overall rate limit status"""
        status = {}
        
        for identifier in self.rate_limiter.limits:
            remaining = await self.rate_limiter.get_remaining(identifier)
            reset_time = await self.rate_limiter.get_reset_time(identifier)
            
            status[identifier] = {
                'remaining': remaining,
                'reset_time': reset_time,
                'limit': self.rate_limiter.limits[identifier]['max_requests']
            }
        
        return status

# Global rate limiter instance
billing_rate_limiter = BillingRateLimiter()

def get_billing_rate_limiter() -> BillingRateLimiter:
    """Get global rate limiter instance"""
    return billing_rate_limiter 