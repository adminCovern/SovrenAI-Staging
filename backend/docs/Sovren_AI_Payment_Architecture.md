# BILLING.md - SOVREN AI Payment Architecture

## 🎯 Overview

This document details the complete billing and payment architecture for SOVREN AI using Kill Bill as the orchestration layer with Stripe (primary) and Zoho Payments (fallback) as payment gateways. This is one of only THREE allowed external API integrations in the entire SOVREN system.

### Document Version Control
- **Version**: 1.0.0
- **Last Updated**: [Current Date]
- **Review Cycle**: Monthly
- **Approval Required**: Technical Lead + CFO + Security Officer

---

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Kill Bill Configuration](#kill-bill-configuration)
3. [Payment Gateway Integration](#payment-gateway-integration)
4. [Subscription Management](#subscription-management)
5. [Payment Flow](#payment-flow)
6. [Security Requirements](#security-requirements)
7. [Webhook Handling](#webhook-handling)
8. [Retry Logic & Failover](#retry-logic)
9. [PCI Compliance](#pci-compliance)
10. [Testing Strategy](#testing-strategy)
11. [Monitoring & Alerts](#monitoring-alerts)
12. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

### High-Level Payment Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   SOVREN    │────▶│   Kill Bill  │────▶│   Stripe    │────▶│   Customer   │
│   Backend   │     │ Orchestrator │     │  (Primary)  │     │    Bank      │
└─────────────┘     └──────┬───────┘     └─────────────┘     └──────────────┘
                           │                      
                           │ Failover             
                           ▼                      
                    ┌─────────────┐               
                    │    Zoho     │               
                    │  Payments   │               
                    │ (Fallback)  │               
                    └─────────────┘               
```

### Key Principles

1. **Kill Bill as Single Source of Truth** - All billing logic centralized
2. **No Direct Gateway Access** - SOVREN never calls Stripe/Zoho directly
3. **Plugin Architecture** - Payment gateways integrated via Kill Bill plugins
4. **Automatic Failover** - Seamless switch from Stripe to Zoho if needed
5. **Idempotency** - All operations must be idempotent

---

## 🔧 Kill Bill Configuration

### Installation & Setup

```bash
# Kill Bill runs locally on the SOVREN infrastructure
cd /data/sovren/billing

# Download Kill Bill
wget https://github.com/killbill/killbill/releases/download/killbill-0.24.0/killbill-0.24.0.tar.gz
tar -xzf killbill-0.24.0.tar.gz

# Install with custom configuration
./setup-killbill.sh --data-dir=/data/sovren/billing/data \
                   --config=/data/sovren/billing/config/killbill.properties
```

### Kill Bill Configuration File

```properties
# /data/sovren/billing/config/killbill.properties

# Database (local PostgreSQL)
org.killbill.dao.url=jdbc:postgresql://localhost:5432/killbill
org.killbill.dao.user=killbill
org.killbill.dao.password=${KB_DB_PASSWORD}

# Security
org.killbill.security.apiKey=${KB_API_KEY}
org.killbill.security.apiSecret=${KB_API_SECRET}

# Notifications (local only)
org.killbill.notificationq.main.class=org.killbill.billing.notification.plugin.api.NotificationPluginApi
org.killbill.notificationq.main.queue.capacity=30000
org.killbill.notificationq.main.queue.size=100

# Payment retry configuration
org.killbill.payment.retry.days=1,3,7,14
org.killbill.payment.failure.retry.max=4

# Plugin directory
org.killbill.osgi.bundle.install.dir=/data/sovren/billing/plugins
```

### Database Schema

```sql
-- Kill Bill requires its own database
CREATE DATABASE killbill;
CREATE USER killbill WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE killbill TO killbill;

-- Run Kill Bill DDL
\i /data/sovren/billing/ddl/killbill-0.24.0.sql
```

---

## 💳 Payment Gateway Integration

### Stripe Plugin Configuration

```xml
<!-- /data/sovren/billing/plugins/stripe-plugin/stripe.xml -->
<stripe>
    <apiKey>${STRIPE_API_KEY}</apiKey>
    <webhookSecret>${STRIPE_WEBHOOK_SECRET}</webhookSecret>
    <captureDelayHours>24</captureDelayHours>
    <connectionTimeout>30000</connectionTimeout>
    <requestTimeout>60000</requestTimeout>
    
    <!-- Retry configuration -->
    <retryConfiguration>
        <maxAttempts>3</maxAttempts>
        <initialInterval>1000</initialInterval>
        <maxInterval>10000</maxInterval>
        <multiplier>2.0</multiplier>
    </retryConfiguration>
    
    <!-- Supported payment methods -->
    <paymentMethods>
        <method>card</method>
        <method>ach_debit</method>
        <method>wire_transfer</method>
    </paymentMethods>
</stripe>
```

### Zoho Payments Plugin Configuration

```xml
<!-- /data/sovren/billing/plugins/zoho-plugin/zoho.xml -->
<zoho>
    <organizationId>${ZOHO_ORG_ID}</organizationId>
    <authToken>${ZOHO_AUTH_TOKEN}</authToken>
    <merchantId>${ZOHO_MERCHANT_ID}</merchantId>
    
    <!-- Failover triggers -->
    <failoverRules>
        <rule>
            <condition>stripe_connection_error</condition>
            <action>activate</action>
        </rule>
        <rule>
            <condition>stripe_rate_limit</condition>
            <action>activate</action>
        </rule>
        <rule>
            <condition>stripe_service_unavailable</condition>
            <action>activate</action>
        </rule>
    </failoverRules>
    
    <!-- API endpoints -->
    <endpoints>
        <production>https://payments.zoho.com/api/v1</production>
        <sandbox>https://sandbox.zoho.com/api/v1</sandbox>
    </endpoints>
</zoho>
```

### Plugin Priority Configuration

```python
# /data/sovren/billing/config/payment_routing.py

class PaymentRouter:
    """Determines which payment gateway to use"""
    
    def __init__(self):
        self.primary = "killbill-stripe"
        self.fallback = "killbill-zoho"
        self.failure_threshold = 3
        self.failure_window = 300  # 5 minutes
        
    def get_active_gateway(self, account_id: str) -> str:
        """Determine which gateway to use for account"""
        
        # Check recent failures for Stripe
        recent_failures = self.get_recent_failures(
            self.primary, 
            self.failure_window
        )
        
        if len(recent_failures) >= self.failure_threshold:
            # Failover to Zoho
            self.log_failover(account_id, self.primary, self.fallback)
            return self.fallback
            
        return self.primary
        
    def should_retry_primary(self) -> bool:
        """Check if we should retry primary gateway"""
        last_failure = self.get_last_failure_time(self.primary)
        if not last_failure:
            return True
            
        # Retry after 30 minutes
        return (time.time() - last_failure) > 1800
```

---

## 📊 Subscription Management

### SOVREN Pricing Plans in Kill Bill

```python
# /data/sovren/billing/plans/sovren_catalog.py

from killbill import Catalog, Plan, Product, PriceList

class SOVRENCatalog:
    """SOVREN subscription catalog"""
    
    def create_catalog(self):
        catalog = Catalog(
            name="SOVREN AI",
            effective_date="2024-01-01T00:00:00Z",
            currencies=["USD"]
        )
        
        # Products
        products = {
            "sovren-proof": Product(
                name="SOVREN Proof",
                category="BASE",
                available=["Monthly", "Annual"]
            ),
            "sovren-proof-plus": Product(
                name="SOVREN Proof+",
                category="PREMIUM",
                available=["Monthly", "Annual"],
                limit=7  # Only 7 seats
            ),
            "sovren-enterprise": Product(
                name="SOVREN Enterprise",
                category="ENTERPRISE",
                available=["Custom"]
            )
        }
        
        # Price lists with SOVREN pricing
        price_lists = {
            "DEFAULT": PriceList(
                name="DEFAULT",
                plans=[
                    Plan(
                        name="sovren-proof-monthly",
                        product="sovren-proof",
                        price=497.00,
                        billing_period="MONTHLY",
                        trial_length=0
                    ),
                    Plan(
                        name="sovren-proof-annual",
                        product="sovren-proof",
                        price=5367.00,
                        billing_period="ANNUAL",
                        trial_length=0
                    ),
                    Plan(
                        name="sovren-proof-plus-monthly",
                        product="sovren-proof-plus",
                        price=797.00,
                        billing_period="MONTHLY",
                        trial_length=0
                    ),
                    Plan(
                        name="sovren-proof-plus-annual",
                        product="sovren-proof-plus",
                        price=8607.00,
                        billing_period="ANNUAL",
                        trial_length=0
                    )
                ]
            )
        }
        
        return catalog
```

### Subscription Lifecycle Management

```python
# /data/sovren/billing/subscription_manager.py

class SubscriptionManager:
    """Manages SOVREN subscriptions through Kill Bill"""
    
    def __init__(self, kb_client):
        self.kb = kb_client
        self.seat_tracker = SeatTracker()
        
    async def create_subscription(
        self, 
        user_data: dict, 
        plan_name: str,
        payment_method: dict
    ) -> dict:
        """Create new SOVREN subscription"""
        
        # 1. Validate plan availability (for limited seats)
        if 'proof-plus' in plan_name:
            if not self.seat_tracker.check_availability(plan_name):
                raise PlanFullError(f"{plan_name} is at capacity (7 seats)")
        
        # 2. Create Kill Bill account
        kb_account = await self.kb.create_account({
            'externalKey': user_data['user_id'],
            'email': user_data['email'],
            'name': user_data['name'],
            'currency': 'USD',
            'timeZone': user_data.get('timezone', 'UTC')
        })
        
        # 3. Add payment method via appropriate plugin
        payment_method_id = await self._add_payment_method(
            kb_account['accountId'],
            payment_method
        )
        
        # 4. Create subscription
        subscription = await self.kb.create_subscription({
            'accountId': kb_account['accountId'],
            'externalKey': f"sovren-{user_data['user_id']}",
            'planName': plan_name,
            'paymentMethodId': payment_method_id
        })
        
        # 5. Allocate seat if limited plan
        if 'proof-plus' in plan_name:
            self.seat_tracker.allocate_seat(
                plan_name, 
                kb_account['accountId']
            )
        
        # 6. Initialize SOVREN features
        await self._initialize_sovren_features(
            user_data,
            plan_name
        )
        
        return {
            'subscription_id': subscription['subscriptionId'],
            'account_id': kb_account['accountId'],
            'status': 'ACTIVE'
        }
        
    async def _add_payment_method(
        self, 
        account_id: str, 
        payment_data: dict
    ) -> str:
        """Add payment method through Kill Bill"""
        
        # Determine which plugin to use
        plugin_name = self._get_payment_plugin()
        
        # Create payment method
        payment_method = await self.kb.create_payment_method({
            'accountId': account_id,
            'pluginName': plugin_name,
            'pluginInfo': {
                'type': payment_data['type'],  # card, ach_debit, wire
                'token': payment_data.get('token'),  # From Stripe.js
                'account_number': payment_data.get('account_number')
            }
        })
        
        return payment_method['paymentMethodId']
```

---

## 💰 Payment Flow

### Payment Processing Sequence

```python
# /data/sovren/billing/payment_processor.py

class PaymentProcessor:
    """Processes payments through Kill Bill"""
    
    async def process_payment(
        self,
        invoice_id: str,
        amount: Decimal,
        currency: str = 'USD'
    ) -> dict:
        """Process payment for invoice"""
        
        # 1. Get invoice details
        invoice = await self.kb.get_invoice(invoice_id)
        account_id = invoice['accountId']
        
        # 2. Create payment transaction
        transaction = await self.kb.create_payment({
            'accountId': account_id,
            'paymentMethodId': invoice['paymentMethodId'],
            'amount': amount,
            'currency': currency,
            'paymentExternalKey': f"sovren-pay-{uuid.uuid4()}",
            'transactionType': 'PURCHASE',
            'properties': {
                'invoiceId': invoice_id,
                'processingTime': datetime.utcnow().isoformat()
            }
        })
        
        # 3. Handle payment result
        if transaction['status'] == 'SUCCESS':
            await self._handle_successful_payment(transaction)
        elif transaction['status'] == 'PENDING':
            await self._handle_pending_payment(transaction)
        else:
            await self._handle_failed_payment(transaction)
            
        return transaction
        
    async def _handle_failed_payment(self, transaction: dict):
        """Handle failed payment with intelligent retry"""
        
        # Check if we should failover to Zoho
        if self._should_failover(transaction):
            await self._retry_with_fallback(transaction)
        else:
            # Schedule retry with primary
            await self._schedule_retry(transaction)
```

### Automatic Retry Logic

```python
# /data/sovren/billing/retry_manager.py

class RetryManager:
    """Manages payment retry logic"""
    
    RETRY_SCHEDULE = [
        timedelta(days=1),   # Day 1
        timedelta(days=3),   # Day 3
        timedelta(days=7),   # Day 7
        timedelta(days=14)  # Day 14
    ]
    
    async def schedule_retry(
        self, 
        payment_id: str, 
        attempt_number: int
    ):
        """Schedule payment retry"""
        
        if attempt_number >= len(self.RETRY_SCHEDULE):
            # Max retries reached
            await self._handle_max_retries_reached(payment_id)
            return
            
        # Calculate next retry time
        next_retry = datetime.utcnow() + self.RETRY_SCHEDULE[attempt_number]
        
        # Schedule with Kill Bill
        await self.kb.create_payment_retry({
            'paymentId': payment_id,
            'retryDate': next_retry.isoformat(),
            'attemptNumber': attempt_number + 1,
            'properties': {
                'retryReason': 'scheduled_retry',
                'originalFailure': await self._get_failure_reason(payment_id)
            }
        })
        
    async def _handle_max_retries_reached(self, payment_id: str):
        """Handle max retries reached"""
        
        # Get account details
        payment = await self.kb.get_payment(payment_id)
        account = await self.kb.get_account(payment['accountId'])
        
        # Determine action based on account value
        if await self._is_high_value_account(account['accountId']):
            # Trigger Shadow Board CFO intervention
            await self._trigger_executive_intervention(
                account,
                'payment_failure_high_value'
            )
        else:
            # Standard suspension process
            await self._initiate_suspension_process(account)
```

---

## 🔒 Security Requirements

### API Authentication

```python
# /data/sovren/billing/security/auth.py

class BillingAuth:
    """Secure authentication for billing operations"""
    
    def __init__(self):
        self.kb_api_key = self._load_secure_config('KB_API_KEY')
        self.kb_api_secret = self._load_secure_config('KB_API_SECRET')
        self.encryption_key = self._load_secure_config('BILLING_ENCRYPTION_KEY')
        
    def create_kb_auth_headers(self) -> dict:
        """Create authenticated headers for Kill Bill"""
        
        # Basic auth for Kill Bill
        auth_string = f"{self.kb_api_key}:{self.kb_api_secret}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded}',
            'X-Killbill-ApiKey': self.kb_api_key,
            'X-Killbill-ApiSecret': self.kb_api_secret,
            'X-Killbill-CreatedBy': 'SOVREN',
            'Content-Type': 'application/json'
        }
        
    def encrypt_sensitive_data(self, data: dict) -> str:
        """Encrypt sensitive payment data"""
        
        # Use Fernet for symmetric encryption
        f = Fernet(self.encryption_key)
        
        # Serialize and encrypt
        json_data = json.dumps(data).encode()
        encrypted = f.encrypt(json_data)
        
        return encrypted.decode()
```

### PCI Compliance Requirements

```python
# /data/sovren/billing/security/pci_compliance.py

class PCICompliance:
    """Ensures PCI DSS compliance"""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
        
    def validate_card_data_handling(self, request: dict) -> bool:
        """Ensure we never store card details"""
        
        # Check for prohibited fields
        prohibited_fields = [
            'card_number', 
            'cvv', 
            'cvc',
            'full_pan'
        ]
        
        for field in prohibited_fields:
            if field in request:
                self.audit_logger.log_security_violation(
                    'Attempted to process prohibited card data',
                    {'field': field}
                )
                raise SecurityViolation(
                    f"Cannot process {field} - use tokenization"
                )
                
        return True
        
    def tokenize_payment_method(self, payment_data: dict) -> str:
        """Convert payment data to token"""
        
        # This should use Stripe.js or Zoho's tokenization
        # NEVER handle raw card data server-side
        
        if payment_data.get('token'):
            # Already tokenized
            return payment_data['token']
        else:
            raise SecurityViolation(
                "Payment data must be tokenized client-side"
            )
```

---

## 🔔 Webhook Handling

### Webhook Security

```python
# /data/sovren/billing/webhooks/webhook_handler.py

class WebhookHandler:
    """Handles webhooks from payment gateways via Kill Bill"""
    
    def __init__(self):
        self.stripe_webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        self.zoho_webhook_secret = os.environ.get('ZOHO_WEBHOOK_SECRET')
        
    async def handle_webhook(
        self, 
        headers: dict, 
        body: bytes,
        source: str
    ) -> dict:
        """Process webhook from payment gateway"""
        
        # 1. Verify webhook signature
        if source == 'stripe':
            event = self._verify_stripe_webhook(headers, body)
        elif source == 'zoho':
            event = self._verify_zoho_webhook(headers, body)
        else:
            raise ValueError(f"Unknown webhook source: {source}")
            
        # 2. Process event
        return await self._process_payment_event(event, source)
        
    def _verify_stripe_webhook(
        self, 
        headers: dict, 
        body: bytes
    ) -> dict:
        """Verify Stripe webhook signature"""
        
        sig_header = headers.get('Stripe-Signature')
        
        if not sig_header:
            raise SecurityViolation("Missing Stripe signature")
            
        # Verify using Stripe's method
        timestamp = self._extract_timestamp(sig_header)
        signatures = self._extract_signatures(sig_header)
        
        # Create expected signature
        signed_payload = f"{timestamp}.{body.decode()}"
        expected_sig = hmac.new(
            self.stripe_webhook_secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify at least one signature matches
        if not any(
            hmac.compare_digest(expected_sig, sig) 
            for sig in signatures
        ):
            raise SecurityViolation("Invalid Stripe webhook signature")
            
        return json.loads(body)
```

### Event Processing

```python
# /data/sovren/billing/webhooks/event_processor.py

class EventProcessor:
    """Processes payment events"""
    
    EVENT_HANDLERS = {
        'payment_intent.succeeded': 'handle_payment_success',
        'payment_intent.payment_failed': 'handle_payment_failure',
        'customer.subscription.updated': 'handle_subscription_update',
        'customer.subscription.deleted': 'handle_subscription_cancellation',
        'invoice.payment_failed': 'handle_invoice_failure'
    }
    
    async def process_event(self, event: dict, source: str) -> dict:
        """Process payment event"""
        
        event_type = event.get('type')
        handler_name = self.EVENT_HANDLERS.get(event_type)
        
        if not handler_name:
            # Unknown event type
            self.logger.warning(f"Unknown event type: {event_type}")
            return {'status': 'ignored'}
            
        # Get handler method
        handler = getattr(self, handler_name)
        
        # Process with idempotency check
        idempotency_key = f"{source}:{event.get('id')}"
        
        if await self._is_duplicate_event(idempotency_key):
            return {'status': 'duplicate', 'key': idempotency_key}
            
        # Process event
        result = await handler(event, source)
        
        # Mark as processed
        await self._mark_event_processed(idempotency_key)
        
        return result
```

---

## 🔄 Retry Logic & Failover

### Intelligent Failover System

```python
# /data/sovren/billing/failover/failover_manager.py

class FailoverManager:
    """Manages failover between Stripe and Zoho"""
    
    def __init__(self):
        self.health_checker = GatewayHealthChecker()
        self.metrics = MetricsCollector()
        
    async def should_failover(self, gateway: str) -> bool:
        """Determine if failover is needed"""
        
        # Check multiple factors
        factors = {
            'health_check': await self.health_checker.is_healthy(gateway),
            'error_rate': self.metrics.get_error_rate(gateway, minutes=5),
            'response_time': self.metrics.get_avg_response_time(gateway),
            'consecutive_failures': self.metrics.get_consecutive_failures(gateway)
        }
        
        # Failover if any critical condition met
        if not factors['health_check']:
            self.logger.error(f"{gateway} health check failed")
            return True
            
        if factors['error_rate'] > 0.1:  # 10% error rate
            self.logger.error(f"{gateway} error rate: {factors['error_rate']}")
            return True
            
        if factors['response_time'] > 5000:  # 5 seconds
            self.logger.error(f"{gateway} slow response: {factors['response_time']}ms")
            return True
            
        if factors['consecutive_failures'] >= 3:
            self.logger.error(f"{gateway} consecutive failures: {factors['consecutive_failures']}")
            return True
            
        return False
        
    async def execute_failover(self, from_gateway: str, to_gateway: str):
        """Execute failover to backup gateway"""
        
        self.logger.info(f"Executing failover: {from_gateway} -> {to_gateway}")
        
        # 1. Update Kill Bill configuration
        await self.kb.update_plugin_config({
            'active_gateway': to_gateway,
            'failover_reason': await self._get_failover_reason(from_gateway),
            'failover_time': datetime.utcnow().isoformat()
        })
        
        # 2. Notify monitoring systems
        await self.metrics.record_failover(from_gateway, to_gateway)
        
        # 3. Schedule health checks for recovery
        await self._schedule_recovery_checks(from_gateway)

class GatewayHealthChecker:
    """Health checks for payment gateways"""
    
    async def is_healthy(self, gateway: str) -> bool:
        """Check if gateway is healthy"""
        
        if gateway == 'stripe':
            return await self._check_stripe_health()
        elif gateway == 'zoho':
            return await self._check_zoho_health()
            
    async def _check_stripe_health(self) -> bool:
        """Stripe-specific health check"""
        try:
            # Use Stripe's status endpoint
            response = await self.http_client.get(
                'https://api.stripe.com/v1/health',
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Stripe health check failed: {e}")
            return False