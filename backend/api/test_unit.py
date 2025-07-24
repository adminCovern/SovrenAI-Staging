#!/usr/bin/env python3
"""
SOVREN Billing System - Unit Tests
Core functionality tests without external dependencies
"""

import unittest
import asyncio
import time
import json
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import core billing components
from billing_integration import (
    BillingSystem, KillBillClient, Customer, Subscription, Invoice,
    SubscriptionStatus, PaymentStatus, BILLING_CONFIG
)

class TestBillingSystemCore(unittest.TestCase):
    """Test core billing system functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.billing_system = BillingSystem()
    
    def tearDown(self):
        """Clean up after tests"""
        asyncio.run(self.billing_system.shutdown())
    
    def test_billing_config_structure(self):
        """Test billing configuration structure"""
        self.assertIn('tiers', BILLING_CONFIG)
        self.assertIn('SOVREN_PROOF', BILLING_CONFIG['tiers'])
        self.assertIn('SOVREN_PROOF_PLUS', BILLING_CONFIG['tiers'])
        
        # Test tier configuration
        proof_tier = BILLING_CONFIG['tiers']['SOVREN_PROOF']
        self.assertIn('monthly_price', proof_tier)
        self.assertIn('yearly_price', proof_tier)
        self.assertIn('features', proof_tier)
        self.assertIn('limits', proof_tier)
    
    def test_id_generation(self):
        """Test ID generation methods"""
        customer_id = self.billing_system._generate_customer_id()
        subscription_id = self.billing_system._generate_subscription_id()
        invoice_id = self.billing_system._generate_invoice_id()
        
        self.assertTrue(customer_id.startswith('cust_'))
        self.assertTrue(subscription_id.startswith('sub_'))
        self.assertTrue(invoice_id.startswith('inv_'))
        
        # Test ID length
        self.assertEqual(len(customer_id), 16)  # cust_ + 12 hex chars
        self.assertEqual(len(subscription_id), 16)  # sub_ + 12 hex chars
        self.assertEqual(len(invoice_id), 16)  # inv_ + 12 hex chars
    
    def test_mrr_calculation(self):
        """Test MRR calculation"""
        # Test monthly billing
        self.billing_system._update_mrr(Decimal('497.00'), 'monthly')
        self.assertEqual(self.billing_system.metrics['monthly_recurring_revenue'], Decimal('497.00'))
        
        # Test yearly billing (should divide by 12)
        self.billing_system._update_mrr(Decimal('5367.00'), 'yearly')
        expected_mrr = Decimal('497.00') + (Decimal('5367.00') / 12)
        self.assertEqual(self.billing_system.metrics['monthly_recurring_revenue'], expected_mrr)
    
    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        payload = {
            'payment_id': 'test_payment',
            'amount': '100.00',
            'timestamp': '1234567890'
        }
        
        # Test valid signature
        webhook_secret = BILLING_CONFIG['webhook_secret']
        payload_str = json.dumps(payload, sort_keys=True)
        import hashlib
        expected_signature = hashlib.sha256(
            f"{webhook_secret}{payload_str}".encode()
        ).hexdigest()
        
        payload['signature'] = expected_signature
        self.assertTrue(self.billing_system._verify_webhook_signature(payload))
        
        # Test invalid signature
        payload['signature'] = 'invalid_signature'
        self.assertFalse(self.billing_system._verify_webhook_signature(payload))
    
    def test_usage_limit_checking(self):
        """Test usage limit checking"""
        # Create mock subscription
        subscription = Subscription(
            id='test_sub_123',
            customer_id='test_cust_123',
            plan_id='SOVREN_PROOF',
            status=SubscriptionStatus.ACTIVE,
            start_date=time.time(),
            end_date=None,
            billing_period='monthly',
            price=Decimal('497.00'),
            next_billing_date=time.time() + (30 * 24 * 3600)
        )
        
        self.billing_system.subscriptions[subscription.id] = subscription
        
        # Initialize usage data
        self.billing_system.usage_data[subscription.id] = {
            'api_calls': 0,
            'gpu_hours': 0,
            'storage_gb': 0
        }
        
        # Test within limits
        asyncio.run(self.billing_system.update_usage(subscription.id, 'api_calls', 500))
        
        # Test exceeding limits
        asyncio.run(self.billing_system.update_usage(subscription.id, 'api_calls', 600))
        # Should log warning but not fail
    
    def test_billing_metrics_structure(self):
        """Test billing metrics structure"""
        metrics = self.billing_system.get_billing_metrics()
        
        # Test required keys
        required_keys = ['customers', 'revenue', 'subscriptions', 'churn_rate', 'usage']
        for key in required_keys:
            self.assertIn(key, metrics)
        
        # Test initial values
        self.assertEqual(metrics['customers']['total'], 0)
        self.assertEqual(metrics['customers']['active'], 0)
        self.assertEqual(metrics['revenue']['mrr'], 0.0)
        self.assertEqual(metrics['revenue']['ltv'], 0.0)
        self.assertEqual(metrics['revenue']['arr'], 0.0)
    
    def test_subscription_status_enum(self):
        """Test subscription status enum"""
        self.assertEqual(SubscriptionStatus.ACTIVE.value, "ACTIVE")
        self.assertEqual(SubscriptionStatus.PENDING.value, "PENDING")
        self.assertEqual(SubscriptionStatus.BLOCKED.value, "BLOCKED")
        self.assertEqual(SubscriptionStatus.CANCELLED.value, "CANCELLED")
        self.assertEqual(SubscriptionStatus.EXPIRED.value, "EXPIRED")
    
    def test_payment_status_enum(self):
        """Test payment status enum"""
        self.assertEqual(PaymentStatus.SUCCESS.value, "SUCCESS")
        self.assertEqual(PaymentStatus.PENDING.value, "PENDING")
        self.assertEqual(PaymentStatus.FAILED.value, "FAILED")
        self.assertEqual(PaymentStatus.RETRY.value, "RETRY")
        self.assertEqual(PaymentStatus.REFUNDED.value, "REFUNDED")

class TestKillBillClientCore(unittest.TestCase):
    """Test Kill Bill client core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = KillBillClient(BILLING_CONFIG)
    
    def test_auth_headers_creation(self):
        """Test authentication header creation"""
        headers = self.client._create_auth_headers()
        
        # Test required headers
        required_headers = ['Authorization', 'X-Killbill-ApiKey', 'X-Killbill-ApiSecret', 'Content-Type']
        for header in required_headers:
            self.assertIn(header, headers)
        
        # Test content type
        self.assertEqual(headers['Content-Type'], 'application/json')
        
        # Test authorization format
        self.assertTrue(headers['Authorization'].startswith('Basic '))
    
    def test_config_structure(self):
        """Test configuration structure"""
        self.assertIn('killbill_url', BILLING_CONFIG)
        self.assertIn('api_key', BILLING_CONFIG)
        self.assertIn('api_secret', BILLING_CONFIG)
        self.assertIn('tenant_api_key', BILLING_CONFIG)
        self.assertIn('tenant_api_secret', BILLING_CONFIG)
        self.assertIn('currency', BILLING_CONFIG)
        self.assertIn('payment_retry_attempts', BILLING_CONFIG)
        self.assertIn('webhook_secret', BILLING_CONFIG)

class TestCustomerDataStructures(unittest.TestCase):
    """Test customer data structures"""
    
    def test_customer_creation(self):
        """Test customer data structure creation"""
        customer = Customer(
            id='test_cust_123',
            email='test@example.com',
            name='Test User',
            company='Test Corp',
            created_at=time.time(),
            metadata={'source': 'test'}
        )
        
        self.assertEqual(customer.id, 'test_cust_123')
        self.assertEqual(customer.email, 'test@example.com')
        self.assertEqual(customer.name, 'Test User')
        self.assertEqual(customer.company, 'Test Corp')
        self.assertIn('source', customer.metadata)
    
    def test_subscription_creation(self):
        """Test subscription data structure creation"""
        subscription = Subscription(
            id='test_sub_123',
            customer_id='test_cust_123',
            plan_id='SOVREN_PROOF',
            status=SubscriptionStatus.ACTIVE,
            start_date=time.time(),
            end_date=None,
            billing_period='monthly',
            price=Decimal('497.00'),
            next_billing_date=time.time() + (30 * 24 * 3600),
            metadata={'kb_subscription_id': 'kb_sub_123'}
        )
        
        self.assertEqual(subscription.id, 'test_sub_123')
        self.assertEqual(subscription.customer_id, 'test_cust_123')
        self.assertEqual(subscription.plan_id, 'SOVREN_PROOF')
        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(subscription.price, Decimal('497.00'))
        self.assertEqual(subscription.billing_period, 'monthly')
    
    def test_invoice_creation(self):
        """Test invoice data structure creation"""
        invoice = Invoice(
            id='test_inv_123',
            customer_id='test_cust_123',
            subscription_id='test_sub_123',
            amount=Decimal('497.00'),
            currency='USD',
            status=PaymentStatus.SUCCESS,
            due_date=time.time(),
            paid_date=time.time(),
            line_items=[{'description': 'Monthly subscription', 'amount': 497.00}],
            metadata={'kb_payment_id': 'kb_payment_123'}
        )
        
        self.assertEqual(invoice.id, 'test_inv_123')
        self.assertEqual(invoice.customer_id, 'test_cust_123')
        self.assertEqual(invoice.amount, Decimal('497.00'))
        self.assertEqual(invoice.currency, 'USD')
        self.assertEqual(invoice.status, PaymentStatus.SUCCESS)

def run_tests():
    """Run all unit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBillingSystemCore))
    suite.addTests(loader.loadTestsFromTestCase(TestKillBillClientCore))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomerDataStructures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 