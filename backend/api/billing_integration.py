#!/usr/bin/env python3
"""
SOVREN Billing System - Kill Bill Integration
Sovereign billing with full subscription management
"""

import os
import json
import time
import asyncio
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import aiohttp
from decimal import Decimal
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BillingSystem')

try:
    from circuit_breaker import CircuitBreaker as CircuitBreakerBase, CircuitBreakerConfig as CircuitBreakerConfigBase, CircuitBreakerManager as CircuitBreakerManagerBase
    
    # Create aliases to avoid type conflicts
    CircuitBreaker = CircuitBreakerBase  # type: ignore
    CircuitBreakerConfig = CircuitBreakerConfigBase  # type: ignore
    CircuitBreakerManager = CircuitBreakerManagerBase  # type: ignore
    
except ImportError as e:
    logger.error(f"Failed to import circuit breaker: {e}")
    # Fallback implementation
    class CircuitBreaker:
        def __init__(self, name: str, config=None):
            self.name = name
            self.config = config
        async def call(self, func, *args, **kwargs):
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
    
    class CircuitBreakerConfig:
        def __init__(self, failure_threshold=5, recovery_timeout=60.0):
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
    
    class CircuitBreakerManager:
        def __init__(self):
            self.circuit_breakers = {}
        def get_circuit_breaker(self, name: str, config=None):
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(name, config or CircuitBreakerConfig())
            return self.circuit_breakers[name]

# Logging already configured above

# Enhanced Billing Configuration with Your Stripe API Keys
BILLING_CONFIG = {
    # Kill Bill Configuration
    'killbill_url': os.getenv('KILLBILL_URL', 'http://localhost:8080'),
    'api_key': os.getenv('KILLBILL_API_KEY', 'sovren'),
    'api_secret': os.getenv('KILLBILL_API_SECRET', 'sovren123'),
    'tenant_api_key': os.getenv('KILLBILL_TENANT_API_KEY', 'sovren_tenant'),
    'tenant_api_secret': os.getenv('KILLBILL_TENANT_API_SECRET', 'sovren_tenant_secret'),
    
    # Your Stripe API Keys - Integrated into Kill Bill
    'stripe': {
        'live_secret_key': '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',
        'live_publishable_key': 'pk_live_51RYa1A2UNNWAe8rDFjFdM50I5jsAruUs8uzb9T7DigMqN0sfvwdmUu9XZo7T7LQ4ilBQtzJwMrgSw50R9Fl2grM300BCpn1ecA',
        'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET', ''),
        'api_version': '2023-10-16',
        'currency': 'usd',
        'payment_method_types': ['card', 'us_bank_account'],
        'automatic_payment_methods': True,
    },
    
    # General Configuration
    'currency': 'USD',
    'payment_retry_attempts': 3,
    'webhook_secret': os.getenv('WEBHOOK_SECRET', 'sovren_webhook_secret'),
    
    # Subscription Tiers
    'tiers': {
        'SOVREN_PROOF': {
            'name': 'SOVREN Proof',
            'monthly_price': 497.00,
            'yearly_price': 5367.00,  # 10% discount
            'features': [
                'full_platform_access',
                'shared_b200_gpu',
                'unlimited_api_calls',
                'community_support',
                'weekly_office_hours'
            ],
            'limits': {
                'api_calls_per_minute': 1000,
                'concurrent_sessions': 100,
                'storage_gb': 1000
            }
        },
        'SOVREN_PROOF_PLUS': {
            'name': 'SOVREN Proof+ (Founder\'s Circle)',
            'monthly_price': 797.00,
            'yearly_price': 8607.00,  # 10% discount
            'features': [
                'everything_in_proof',
                'priority_gpu_access',
                'dedicated_account_manager',
                'custom_onboarding',
                'direct_founder_access',
                'monthly_strategy_calls',
                'white_glove_support'
            ],
            'limits': {
                'api_calls_per_minute': 10000,
                'concurrent_sessions': 1000,
                'storage_gb': 10000,
                'dedicated_gpu_hours': 100
            }
        }
    }
}

class SubscriptionStatus(Enum):
    """Subscription status types"""
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class PaymentStatus(Enum):
    """Payment status types"""
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"
    RETRY = "RETRY"
    REFUNDED = "REFUNDED"

@dataclass
class Customer:
    """Customer information"""
    id: str
    email: str
    name: str
    company: Optional[str]
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Subscription:
    """Subscription information"""
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    start_date: float
    end_date: Optional[float]
    billing_period: str  # monthly/yearly
    price: Decimal
    next_billing_date: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Invoice:
    """Invoice information"""
    id: str
    customer_id: str
    subscription_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    due_date: float
    paid_date: Optional[float]
    line_items: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

class KillBillClient:
    """Kill Bill API client with integrated Stripe configuration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config['killbill_url']
        self.session = None
        self._auth_headers = self._create_auth_headers()
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.killbill_circuit = self.circuit_breaker_manager.get_circuit_breaker(
            'killbill-api',
            CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60.0)
        )
        
    def _create_auth_headers(self) -> Dict[str, str]:
        """Create authentication headers"""
        import base64
        
        credentials = f"{self.config['api_key']}:{self.config['api_secret']}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded}',
            'X-Killbill-ApiKey': self.config['tenant_api_key'],
            'X-Killbill-ApiSecret': self.config['tenant_api_secret'],
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self._auth_headers)
        return self.session
    
    async def configure_stripe_plugin(self) -> Dict[str, Any]:
        """Configure Kill Bill with your Stripe API keys"""
        
        async def _configure_plugin():
            session = await self._get_session()
            
            # Configure Stripe plugin with your API keys
            plugin_config = {
                "plugin_name": "killbill-stripe",
                "version": "0.1.0",
                "plugin_type": "PAYMENT",
                "plugin_info": {
                    "properties": [
                        {
                            "key": "org.killbill.billing.plugin.stripe.api_key",
                            "value": self.config['stripe']['live_secret_key']
                        },
                        {
                            "key": "org.killbill.billing.plugin.stripe.publishable_key",
                            "value": self.config['stripe']['live_publishable_key']
                        },
                        {
                            "key": "org.killbill.billing.plugin.stripe.currency",
                            "value": self.config['stripe']['currency']
                        }
                    ]
                }
            }
            
            # Add webhook secret if provided
            if self.config['stripe']['webhook_secret']:
                plugin_config["plugin_info"]["properties"].append({
                    "key": "org.killbill.billing.plugin.stripe.webhook_secret",
                    "value": self.config['stripe']['webhook_secret']
                })
            
            async with session.post(
                f"{self.base_url}/1.0/kb/plugins",
                json=plugin_config
            ) as response:
                if response.status in [200, 201, 409]:  # 409 means already configured
                    logger.info("Stripe plugin configured successfully")
                    return {'success': True}
                else:
                    error = await response.text()
                    logger.error(f"Failed to configure Stripe plugin: {error}")
                    return {'success': False, 'error': error}
        
        return await self.killbill_circuit.call(_configure_plugin)
    
    async def create_stripe_payment_method(self, account_id: str) -> Dict[str, Any]:
        """Create Stripe payment method for account"""
        
        session = await self._get_session()
        
        payment_method_data = {
            "pluginName": "killbill-stripe",
            "pluginInfo": {
                "properties": [
                    {
                        "key": "payment_method_type",
                        "value": "card"
                    }
                ]
            }
        }
        
        async with session.post(
            f"{self.base_url}/1.0/kb/accounts/{account_id}/paymentMethods",
            json=payment_method_data
        ) as response:
            if response.status in [200, 201]:
                payment_method = await response.json()
                return {
                    'payment_method_id': payment_method.get('paymentMethodId'),
                    'success': True,
                    'data': payment_method
                }
            else:
                error = await response.text()
                logger.error(f"Failed to create payment method: {error}")
                return {'success': False, 'error': error}
        
    async def create_account(self, customer: Customer) -> Dict[str, Any]:
        """Create Kill Bill account"""
        
        session = await self._get_session()
        
        account_data = {
            'name': customer.name,
            'email': customer.email,
            'currency': self.config['currency'],
            'externalKey': customer.id,
            'company': customer.company,
            'notes': json.dumps(customer.metadata)
        }
        
        async with session.post(
            f"{self.base_url}/1.0/kb/accounts",
            json=account_data
        ) as response:
            if response.status == 201:
                location = response.headers.get('Location', '')
                account_id = location.split('/')[-1]
                return {'account_id': account_id, 'success': True}
            else:
                error = await response.text()
                logger.error(f"Failed to create account: {error}")
                return {'success': False, 'error': error}
                
    async def create_subscription(self, account_id: str, 
                                plan_id: str,
                                billing_period: str) -> Dict[str, Any]:
        """Create subscription in Kill Bill"""
        
        session = await self._get_session()
        
        subscription_data = {
            'accountId': account_id,
            'planName': f"{plan_id}_{billing_period.upper()}",
            'productName': 'SOVREN_AI',
            'productCategory': 'BASE',
            'billingPeriod': billing_period.upper(),
            'priceList': 'DEFAULT'
        }
        
        async with session.post(
            f"{self.base_url}/1.0/kb/subscriptions",
            json=subscription_data
        ) as response:
            if response.status == 201:
                location = response.headers.get('Location', '')
                subscription_id = location.split('/')[-1]
                return {
                    'subscription_id': subscription_id,
                    'success': True
                }
            else:
                error = await response.text()
                logger.error(f"Failed to create subscription: {error}")
                return {'success': False, 'error': error}
                
    async def process_payment(self, account_id: str, 
                            amount: Decimal,
                            payment_method_id: str) -> Dict[str, Any]:
        """Process payment through Kill Bill using your Stripe API keys"""
        
        session = await self._get_session()
        
        payment_data = {
            'accountId': account_id,
            'paymentMethodId': payment_method_id,
            'amount': float(amount),
            'currency': self.config['currency'],
            'paymentExternalKey': str(uuid.uuid4())
        }
        
        async with session.post(
            f"{self.base_url}/1.0/kb/payments",
            json=payment_data
        ) as response:
            if response.status == 201:
                payment_id = response.headers.get('Location', '').split('/')[-1]
                return {
                    'payment_id': payment_id,
                    'status': PaymentStatus.SUCCESS.value,
                    'success': True
                }
            else:
                error = await response.text()
                logger.error(f"Payment failed: {error}")
                return {'success': False, 'error': error}
                
    async def get_invoices(self, account_id: str) -> List[Dict[str, Any]]:
        """Get invoices for account"""
        
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/1.0/kb/accounts/{account_id}/invoices"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Failed to get invoices: {response.status}")
                return []
                
    async def cancel_subscription(self, subscription_id: str,
                                requested_date: Optional[str] = None) -> Dict[str, Any]:
        """Cancel subscription in Kill Bill"""
        
        session = await self._get_session()
        
        cancel_data = {
            'requestedDate': requested_date or 'NOW',
            'entitlementPolicy': 'IMMEDIATE',
            'billingPolicy': 'IMMEDIATE'
        }
        
        async with session.delete(
            f"{self.base_url}/1.0/kb/subscriptions/{subscription_id}",
            json=cancel_data
        ) as response:
            if response.status == 200:
                return {'success': True}
            else:
                error = await response.text()
                logger.error(f"Failed to cancel subscription: {error}")
                return {'success': False, 'error': error}
                
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

class BillingSystem:
    """SOVREN Billing System with integrated Stripe configuration"""
    
    def __init__(self):
        self.killbill_client = KillBillClient(BILLING_CONFIG)
        self.customers: Dict[str, Customer] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.usage_data: Dict[str, Dict[str, float]] = {}
        self.metrics = {
            'total_customers': 0,
            'active_subscriptions': 0,
            'monthly_recurring_revenue': Decimal('0'),
            'lifetime_value': Decimal('0'),
            'churn_rate': 0.0
        }
        self._stripe_configured = False
        
    async def initialize_stripe_integration(self) -> bool:
        """Initialize Stripe integration with your API keys"""
        
        if self._stripe_configured:
            return True
            
        logger.info("Configuring Kill Bill with Stripe API keys...")
        
        # Configure Stripe plugin
        stripe_result = await self.killbill_client.configure_stripe_plugin()
        
        if not stripe_result['success']:
            logger.error("Failed to configure Stripe plugin")
            return False
            
        self._stripe_configured = True
        logger.info("Stripe integration configured successfully")
        return True
    
    async def create_customer(self, email: str, name: str,
                            company: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> Customer:
        """Create customer with automatic Stripe payment method setup"""
        
        # Ensure Stripe is configured
        if not self._stripe_configured:
            await self.initialize_stripe_integration()
        
        # Create local customer record
        customer = Customer(
            id=self._generate_customer_id(),
            email=email,
            name=name,
            company=company,
            created_at=time.time(),
            metadata=metadata or {}
        )
        
        # Create account in Kill Bill
        account_result = await self.killbill_client.create_account(customer)
        
        if not account_result['success']:
            raise Exception(f"Failed to create account: {account_result['error']}")
        
        # Create Stripe payment method for this account
        payment_result = await self.killbill_client.create_stripe_payment_method(account_result['account_id'])
        
        if not payment_result['success']:
            logger.warning(f"Failed to create payment method: {payment_result['error']}")
        
        self.customers[customer.id] = customer
        self.metrics['total_customers'] += 1
        logger.info(f"Created customer: {customer.id} ({email})")
        
        return customer
    
    async def create_subscription(self, customer_id: str, tier: str,
                                billing_period: str = 'monthly') -> Subscription:
        """Create subscription with integrated Stripe billing"""
        
        if customer_id not in self.customers:
            raise Exception(f"Customer not found: {customer_id}")
        
        if tier not in BILLING_CONFIG['tiers']:
            raise Exception(f"Invalid tier: {tier}")
        
        # Ensure Stripe is configured
        if not self._stripe_configured:
            await self.initialize_stripe_integration()
        
        # Get customer's Kill Bill account ID
        customer = self.customers[customer_id]
        
        # Create subscription in Kill Bill (will use Stripe for payments)
        subscription_result = await self.killbill_client.create_subscription(
            customer_id, tier, billing_period
        )
        
        if not subscription_result['success']:
            raise Exception(f"Failed to create subscription: {subscription_result['error']}")
        
        # Get pricing
        tier_config = BILLING_CONFIG['tiers'][tier]
        price = Decimal(str(tier_config['monthly_price'] if billing_period == 'monthly' else tier_config['yearly_price']))
        
        # Create local subscription record
        subscription = Subscription(
            id=subscription_result['subscription_id'],
            customer_id=customer_id,
            plan_id=tier,
            status=SubscriptionStatus.ACTIVE,
            start_date=time.time(),
            end_date=None,
            billing_period=billing_period,
            price=price,
            next_billing_date=time.time() + (30 * 24 * 3600 if billing_period == 'monthly' else 365 * 24 * 3600),
            metadata={'stripe_subscription_id': subscription_result['subscription_id']}
        )
        
        self.subscriptions[subscription.id] = subscription
        self.metrics['active_subscriptions'] += 1
        self._update_mrr(price, billing_period)
        
        logger.info(f"Created subscription: {subscription.id} for {tier} ({billing_period})")
        
        return subscription
    
    async def process_payment(self, customer_id: str, amount: Decimal,
                            payment_method: Dict[str, Any]) -> Invoice:
        """Process payment using integrated Stripe through Kill Bill"""
        
        if customer_id not in self.customers:
            raise Exception(f"Customer not found: {customer_id}")
        
        # Ensure Stripe is configured
        if not self._stripe_configured:
            await self.initialize_stripe_integration()
        
        # Create invoice
        invoice = Invoice(
            id=self._generate_invoice_id(),
            customer_id=customer_id,
            subscription_id=payment_method.get('subscription_id', ''),
            amount=amount,
            currency=BILLING_CONFIG['currency'],
            status=PaymentStatus.PENDING,
            due_date=time.time(),
            paid_date=None,
            line_items=[{
                'description': 'SOVREN AI Subscription',
                'amount': float(amount),
                'currency': BILLING_CONFIG['currency']
            }],
            metadata={'payment_method': payment_method}
        )
        
        # Process payment through Kill Bill (which uses your Stripe API keys)
        payment_result = await self.killbill_client.process_payment(
            customer_id, amount, payment_method.get('payment_method_id', '')
        )
        
        if payment_result['success']:
            invoice.status = PaymentStatus.SUCCESS
            invoice.paid_date = time.time()
            logger.info(f"Payment successful: {invoice.id}")
        else:
            invoice.status = PaymentStatus.FAILED
            logger.error(f"Payment failed: {payment_result['error']}")
            
            # Retry logic
            if BILLING_CONFIG['payment_retry_attempts'] > 0:
                await self._retry_payment(invoice)
        
        self.invoices[invoice.id] = invoice
        return invoice
    
    async def _retry_payment(self, invoice: Invoice):
        """Retry failed payment"""
        
        max_attempts = BILLING_CONFIG['payment_retry_attempts']
        
        for attempt in range(max_attempts):
            # Wait before retry (exponential backoff)
            await asyncio.sleep(60 * (2 ** attempt))
            
            logger.info(f"Retrying payment for invoice {invoice.id}, attempt {attempt + 1}")
            
            # Attempt payment again through Kill Bill
            payment_result = await self.killbill_client.process_payment(
                invoice.customer_id, 
                invoice.amount, 
                invoice.metadata.get('payment_method', {}).get('payment_method_id', '')
            )
            
            if payment_result['success']:
                invoice.status = PaymentStatus.SUCCESS
                invoice.paid_date = time.time()
                logger.info(f"Payment retry successful: {invoice.id}")
                break
            else:
                logger.warning(f"Payment retry failed: {payment_result['error']}")
    
    async def cancel_subscription(self, subscription_id: str,
                                immediate: bool = False) -> Dict[str, Any]:
        """Cancel subscription"""
        
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription {subscription_id} not found")
            
        subscription = self.subscriptions[subscription_id]
        
        # Cancel in Kill Bill
        requested_date = 'NOW' if immediate else None
        
        result = await self.killbill_client.cancel_subscription(
            subscription_id,
            requested_date
        )
        
        if result['success']:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.end_date = time.time()
            
            self.metrics['active_subscriptions'] -= 1
            self._update_mrr(-subscription.price, subscription.billing_period)
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return {'success': True}
        else:
            raise Exception(f"Failed to cancel subscription: {result.get('error')}")
            
    async def update_usage(self, subscription_id: str,
                         usage_type: str, amount: float):
        """Update usage metrics for subscription"""
        
        if subscription_id not in self.usage_data:
            self.usage_data[subscription_id] = {
                'api_calls': 0,
                'gpu_hours': 0,
                'storage_gb': 0
            }
            
        if usage_type in self.usage_data[subscription_id]:
            self.usage_data[subscription_id][usage_type] += amount
            
            # Check limits
            await self._check_usage_limits(subscription_id)
            
    async def _check_usage_limits(self, subscription_id: str):
        """Check if usage exceeds limits"""
        
        if subscription_id not in self.subscriptions:
            return
            
        subscription = self.subscriptions[subscription_id]
        tier_config = BILLING_CONFIG['tiers'].get(subscription.plan_id, {})
        limits = tier_config.get('limits', {})
        
        usage = self.usage_data.get(subscription_id, {})
        
        # Check each limit
        for metric, limit in limits.items():
            current_usage = usage.get(metric.replace('_per_minute', ''), 0)
            
            if current_usage > limit:
                logger.warning(
                    f"Usage limit exceeded for {subscription_id}: "
                    f"{metric} = {current_usage} (limit: {limit})"
                )
                
                # Could trigger overage billing or throttling
                
    def _update_mrr(self, amount: Decimal, billing_period: str):
        """Update monthly recurring revenue"""
        
        monthly_amount = amount
        if billing_period == 'yearly':
            monthly_amount = amount / 12
            
        self.metrics['monthly_recurring_revenue'] += monthly_amount
        
    def _generate_customer_id(self) -> str:
        """Generate unique customer ID"""
        return f"cust_{uuid.uuid4().hex[:12]}"
        
    def _generate_subscription_id(self) -> str:
        """Generate unique subscription ID"""
        return f"sub_{uuid.uuid4().hex[:12]}"
        
    def _generate_invoice_id(self) -> str:
        """Generate unique invoice ID"""
        return f"inv_{uuid.uuid4().hex[:12]}"
        
    async def handle_webhook(self, event_type: str, 
                           payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Kill Bill webhooks"""
        
        logger.info(f"Received webhook: {event_type}")
        
        # Verify webhook signature
        if not self._verify_webhook_signature(payload):
            logger.error("Invalid webhook signature")
            return {'status': 'error', 'message': 'Invalid signature'}
            
        # Handle different event types
        if event_type == 'PAYMENT_SUCCESS':
            await self._handle_payment_success(payload)
        elif event_type == 'PAYMENT_FAILED':
            await self._handle_payment_failed(payload)
        elif event_type == 'SUBSCRIPTION_CANCELLED':
            await self._handle_subscription_cancelled(payload)
        elif event_type == 'INVOICE_CREATED':
            await self._handle_invoice_created(payload)
            
        return {'status': 'success'}
        
    def _verify_webhook_signature(self, payload: Dict[str, Any]) -> bool:
        """Verify webhook signature"""
        
        # Extract signature from headers
        provided_signature = payload.get('signature', '')
        
        # Calculate expected signature
        webhook_secret = BILLING_CONFIG['webhook_secret']
        payload_str = json.dumps(payload, sort_keys=True)
        expected_signature = hashlib.sha256(
            f"{webhook_secret}{payload_str}".encode()
        ).hexdigest()
        
        return provided_signature == expected_signature
        
    async def _handle_payment_success(self, payload: Dict[str, Any]):
        """Handle successful payment webhook"""
        
        payment_id = payload.get('payment_id')
        amount = Decimal(str(payload.get('amount', 0)))
        
        logger.info(f"Payment successful: {payment_id} for ${amount}")
        
        # Update metrics
        self.metrics['lifetime_value'] += amount
        
    async def _handle_payment_failed(self, payload: Dict[str, Any]):
        """Handle failed payment webhook"""
        
        payment_id = payload.get('payment_id')
        reason = payload.get('failure_reason', 'Unknown')
        
        logger.warning(f"Payment failed: {payment_id} - {reason}")
        
        # Could trigger retry or notification
        
    async def _handle_subscription_cancelled(self, payload: Dict[str, Any]):
        """Handle subscription cancellation webhook"""
        
        subscription_id = payload.get('subscription_id')
        
        # Update local subscription status
        for sub_id, subscription in self.subscriptions.items():
            if subscription.metadata.get('kb_subscription_id') == subscription_id:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.end_date = time.time()
                
                self.metrics['active_subscriptions'] -= 1
                break
                
    async def _handle_invoice_created(self, payload: Dict[str, Any]):
        """Handle invoice creation webhook"""
        
        invoice_id = payload.get('invoice_id')
        amount = Decimal(str(payload.get('amount', 0)))
        
        logger.info(f"Invoice created: {invoice_id} for ${amount}")
        
    def get_billing_metrics(self) -> Dict[str, Any]:
        """Get billing system metrics"""
        
        # Calculate churn rate
        if self.metrics['total_customers'] > 0:
            churned = sum(
                1 for sub in self.subscriptions.values()
                if sub.status == SubscriptionStatus.CANCELLED
            )
            self.metrics['churn_rate'] = churned / self.metrics['total_customers']
            
        return {
            'customers': {
                'total': self.metrics['total_customers'],
                'active': self.metrics['active_subscriptions']
            },
            'revenue': {
                'mrr': float(self.metrics['monthly_recurring_revenue']),
                'ltv': float(self.metrics['lifetime_value']),
                'arr': float(self.metrics['monthly_recurring_revenue'] * 12)
            },
            'subscriptions': {
                'active': self.metrics['active_subscriptions'],
                'by_tier': self._get_subscriptions_by_tier()
            },
            'churn_rate': self.metrics['churn_rate'],
            'usage': self._get_usage_summary()
        }
        
    def _get_subscriptions_by_tier(self) -> Dict[str, int]:
        """Get subscription count by tier"""
        
        tier_counts = {}
        for subscription in self.subscriptions.values():
            if subscription.status == SubscriptionStatus.ACTIVE:
                tier = subscription.plan_id
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
                
        return tier_counts
        
    def _get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary across all subscriptions"""
        
        total_usage = {
            'api_calls': 0.0,
            'gpu_hours': 0.0,
            'storage_gb': 0.0
        }
        
        for usage in self.usage_data.values():
            for metric, value in usage.items():
                total_usage[metric] += value
                
        return total_usage
        
    async def shutdown(self):
        """Shutdown billing system"""
        
        logger.info("Shutting down Billing System...")
        
        # Close Kill Bill client
        await self.killbill_client.close()
        
        logger.info("Billing System shutdown complete")

# Global instance
billing_system: Optional[BillingSystem] = None

async def initialize_billing() -> BillingSystem:
    """Initialize the global billing system with your Stripe API keys"""
    global billing_system
    billing_system = BillingSystem()
    
    # Automatically configure Stripe integration
    await billing_system.initialize_stripe_integration()
    
    logger.info("Billing System initialized - Ready for subscriptions")
    return billing_system

def get_billing_system() -> BillingSystem:
    """Get the global billing system instance"""
    if billing_system is None:
        raise RuntimeError("Billing system not initialized. Call initialize_billing() first.")
    return billing_system

if __name__ == "__main__":
    # Test billing system
    async def test_billing():
        try:
            # Initialize billing system
            system = await initialize_billing()
            
            # Create test customer
            customer = await system.create_customer(
                email='test@example.com',
                name='Test User',
                company='Test Corp'
            )
            print(f"Created customer: {customer.id}")
            
            # Create subscription
            subscription = await system.create_subscription(
                customer.id,
                'SOVREN_PROOF',
                'monthly'
            )
            print(f"Created subscription: {subscription.id}")
            
            # Get metrics
            metrics = system.get_billing_metrics()
            print(f"Billing metrics: {json.dumps(metrics, indent=2)}")
            
            await system.shutdown()
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
        
    asyncio.run(test_billing())