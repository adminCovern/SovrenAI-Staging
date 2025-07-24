#!/usr/bin/env python3
"""
SOVREN Billing System - Rate Limiter
Production-grade rate limiting with Redis backend
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis

logger = logging.getLogger('RateLimiter')

class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    pass

class RateLimitType(Enum):
    """Rate limit types"""
    API_CALLS = "api_calls"
    PAYMENT_ATTEMPTS = "payment_attempts"
    WEBHOOK_EVENTS = "webhook_events"
    SUBSCRIPTION_CREATES = "subscription_creates"

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests: int
    window_seconds: int
    burst_size: int = 0
    cost_per_request: int = 1

class RateLimiter:
    """Production rate limiter with Redis backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            if self.redis_client:
                await self.redis_client.ping()
            logger.info("Rate limiter initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter: {e}")
            raise
    
    async def _get_key(self, identifier: str, limit_type: RateLimitType) -> str:
        """Generate Redis key for rate limiting"""
        return f"rate_limit:{limit_type.value}:{identifier}"
    
    async def check_rate_limit(self, identifier: str, limit_type: RateLimitType, 
                             config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        
        if not self.redis_client:
            raise RuntimeError("Rate limiter not initialized")
        
        key = await self._get_key(identifier, limit_type)
        now = int(time.time())
        window_start = now - config.window_seconds
        
        async with self._lock:
            try:
                # Get current usage
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zrange(key, 0, -1)
                pipe.expire(key, config.window_seconds * 2)
                
                results = await pipe.execute()
                current_count = results[1]
                
                # Check if limit exceeded
                if current_count >= config.max_requests:
                    return False, {
                        'current': current_count,
                        'limit': config.max_requests,
                        'window': config.window_seconds,
                        'reset_time': window_start + config.window_seconds
                    }
                
                # Add current request
                await self.redis_client.zadd(key, {str(now): now})
                
                return True, {
                    'current': current_count + 1,
                    'limit': config.max_requests,
                    'remaining': config.max_requests - (current_count + 1)
                }
                
            except Exception as e:
                logger.error(f"Rate limit check failed: {e}")
                # Fail open - allow request if Redis is down
                return True, {'error': 'rate_limiter_unavailable'}
    
    async def enforce_rate_limit(self, identifier: str, limit_type: RateLimitType,
                               config: RateLimitConfig) -> Dict[str, int]:
        """Enforce rate limit and raise exception if exceeded"""
        
        allowed, stats = await self.check_rate_limit(identifier, limit_type, config)
        
        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded for {identifier}: {stats['current']}/{stats['limit']} "
                f"requests in {config.window_seconds}s window"
            )
        
        return stats
    
    async def get_usage_stats(self, identifier: str, limit_type: RateLimitType) -> Dict[str, Any]:
        """Get current usage statistics"""
        
        if not self.redis_client:
            return {'error': 'rate_limiter_unavailable'}
        
        key = await self._get_key(identifier, limit_type)
        
        try:
            now = int(time.time())
            window_start = now - 3600  # Last hour
            
            # Clean old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Get current count
            current_count = await self.redis_client.zcard(key)
            
            return {
                'identifier': identifier,
                'limit_type': limit_type.value,
                'current_usage': current_count,
                'window_start': window_start,
                'window_end': now
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {'error': str(e)}
    
    async def reset_rate_limit(self, identifier: str, limit_type: RateLimitType):
        """Reset rate limit for identifier"""
        
        if not self.redis_client:
            return
        
        key = await self._get_key(identifier, limit_type)
        
        try:
            await self.redis_client.delete(key)
            logger.info(f"Reset rate limit for {identifier}:{limit_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Rate limiter connections closed")

class BillingRateLimiter:
    """Billing-specific rate limiter with tier-based limits"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.tier_limits = {
            'SOVREN_PROOF': {
                'api_calls': RateLimitConfig(1000, 60),  # 1000 calls per minute
                'payment_attempts': RateLimitConfig(10, 300),  # 10 attempts per 5 minutes
                'subscription_creates': RateLimitConfig(5, 3600),  # 5 creates per hour
            },
            'SOVREN_PROOF_PLUS': {
                'api_calls': RateLimitConfig(10000, 60),  # 10000 calls per minute
                'payment_attempts': RateLimitConfig(50, 300),  # 50 attempts per 5 minutes
                'subscription_creates': RateLimitConfig(20, 3600),  # 20 creates per hour
            }
        }
    
    async def check_api_rate_limit(self, customer_id: str, tier: str) -> Dict[str, int]:
        """Check API rate limit for customer"""
        
        config = self.tier_limits.get(tier, {}).get('api_calls')
        if not config:
            raise ValueError(f"Unknown tier: {tier}")
        
        return await self.rate_limiter.enforce_rate_limit(
            customer_id, RateLimitType.API_CALLS, config
        )
    
    async def check_payment_rate_limit(self, customer_id: str, tier: str) -> Dict[str, int]:
        """Check payment rate limit for customer"""
        
        config = self.tier_limits.get(tier, {}).get('payment_attempts')
        if not config:
            raise ValueError(f"Unknown tier: {tier}")
        
        return await self.rate_limiter.enforce_rate_limit(
            customer_id, RateLimitType.PAYMENT_ATTEMPTS, config
        )
    
    async def check_subscription_rate_limit(self, customer_id: str, tier: str) -> Dict[str, int]:
        """Check subscription creation rate limit"""
        
        config = self.tier_limits.get(tier, {}).get('subscription_creates')
        if not config:
            raise ValueError(f"Unknown tier: {tier}")
        
        return await self.rate_limiter.enforce_rate_limit(
            customer_id, RateLimitType.SUBSCRIPTION_CREATES, config
        )

# Global rate limiter instance
rate_limiter: Optional[RateLimiter] = None
billing_rate_limiter: Optional[BillingRateLimiter] = None

async def initialize_rate_limiter(redis_url: str = "redis://localhost:6379"):
    """Initialize global rate limiter"""
    global rate_limiter, billing_rate_limiter
    
    rate_limiter = RateLimiter(redis_url)
    await rate_limiter.initialize()
    
    billing_rate_limiter = BillingRateLimiter(rate_limiter)
    logger.info("Billing rate limiter initialized")

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    if rate_limiter is None:
        raise RuntimeError("Rate limiter not initialized")
    return rate_limiter

def get_billing_rate_limiter() -> BillingRateLimiter:
    """Get global billing rate limiter instance"""
    if billing_rate_limiter is None:
        raise RuntimeError("Billing rate limiter not initialized")
    return billing_rate_limiter 