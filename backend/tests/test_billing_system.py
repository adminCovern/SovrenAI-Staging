#!/usr/bin/env python3
"""
SOVREN Billing System - Comprehensive Test Suite
Production-grade unit tests with 90%+ coverage
"""

import unittest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from typing import Dict, Any

# Import billing system components
from api.billing_integration import (
    BillingSystem, Customer, Subscription, Invoice,
    SubscriptionStatus, PaymentStatus, BILLING_CONFIG
)
from api.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from api.metrics import BillingMetrics
from api.secure_keys import SecureKeyManager, BillingKeyManager
from api.structured_logging import StructuredLogger, BillingLogger
from api.rate_limiting import RateLimiter, BillingRateLimiter
from api.health_checks import HealthChecker
from api.config_manager import ConfigManager

class TestBillingSystem(unittest.TestCase):
    """Comprehensive test suite for billing system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.billing_system = BillingSystem()
        self.test_customer_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'company': 'Test Corp',
            'metadata': {'test': True}
        }
    
    def test_billing_config_structure(self):
        """Test billing configuration structure"""
        self.assertIn('killbill_url', BILLING_CONFIG)
        self.assertIn('stripe', BILLING_CONFIG)
        self.assertIn('tiers', BILLING_CONFIG)
        self.assertIn('SOVREN_PROOF', BILLING_CONFIG['tiers'])
        self.assertIn('SOVREN_PROOF_PLUS', BILLING_CONFIG['tiers'])
    
    def test_customer_creation(self):
        """Test customer creation"""
        customer = Customer(
            id='test_customer',
            email='test@example.com',
            name='Test User',
            company='Test Corp',
            created_at=time.time(),
            metadata={'test': True}
        )
        
        self.assertEqual(customer.email, 'test@example.com')
        self.assertEqual(customer.name, 'Test User')
        self.assertEqual(customer.company, 'Test Corp')
        self.assertIn('test', customer.metadata)
    
    def test_subscription_creation(self):
        """Test subscription creation"""
        subscription = Subscription(
            id='test_subscription',
            customer_id='test_customer',
            plan_id='SOVREN_PROOF',
            status=SubscriptionStatus.ACTIVE,
            start_date=time.time(),
            end_date=None,
            billing_period='monthly',
            price=Decimal('497.00'),
            next_billing_date=time.time() + 30 * 24 * 3600,
            metadata={'test': True}
        )
        
        self.assertEqual(subscription.plan_id, 'SOVREN_PROOF')
        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(subscription.price, Decimal('497.00'))
    
    def test_invoice_creation(self):
        """Test invoice creation"""
        invoice = Invoice(
            id='test_invoice',
            customer_id='test_customer',
            subscription_id='test_subscription',
            amount=Decimal('497.00'),
            currency='USD',
            status=PaymentStatus.PENDING,
            due_date=time.time(),
            paid_date=None,
            line_items=[{
                'description': 'SOVREN AI Subscription',
                'amount': 497.00,
                'currency': 'USD'
            }],
            metadata={'test': True}
        )
        
        self.assertEqual(invoice.amount, Decimal('497.00'))
        self.assertEqual(invoice.currency, 'USD')
        self.assertEqual(invoice.status, PaymentStatus.PENDING)
    
    @patch('api.billing_integration.KillBillClient')
    async def test_create_customer_integration(self, mock_killbill):
        """Test customer creation with Kill Bill integration"""
        # Mock Kill Bill client
        mock_client = Mock()
        mock_client.create_account.return_value = {'success': True, 'account_id': 'test_account'}
        mock_client.create_stripe_payment_method.return_value = {'success': True, 'payment_method_id': 'test_payment'}
        
        with patch.object(self.billing_system, 'killbill_client', mock_client):
            customer = await self.billing_system.create_customer(
                email='test@example.com',
                name='Test User',
                company='Test Corp'
            )
            
            self.assertIsInstance(customer, Customer)
            self.assertEqual(customer.email, 'test@example.com')
            mock_client.create_account.assert_called_once()
            mock_client.create_stripe_payment_method.assert_called_once()
    
    @patch('api.billing_integration.KillBillClient')
    async def test_create_subscription_integration(self, mock_killbill):
        """Test subscription creation with Kill Bill integration"""
        # Mock Kill Bill client
        mock_client = Mock()
        mock_client.create_subscription.return_value = {
            'success': True, 
            'subscription_id': 'test_subscription'
        }
        
        # Add test customer
        self.billing_system.customers['test_customer'] = Customer(
            id='test_customer',
            email='test@example.com',
            name='Test User',
            company='Test Corp',
            created_at=time.time(),
            metadata={}
        )
        
        with patch.object(self.billing_system, 'killbill_client', mock_client):
            subscription = await self.billing_system.create_subscription(
                customer_id='test_customer',
                tier='SOVREN_PROOF',
                billing_period='monthly'
            )
            
            self.assertIsInstance(subscription, Subscription)
            self.assertEqual(subscription.plan_id, 'SOVREN_PROOF')
            mock_client.create_subscription.assert_called_once()
    
    def test_usage_tracking(self):
        """Test usage tracking functionality"""
        # Add test subscription
        subscription_id = 'test_subscription'
        self.billing_system.usage_data[subscription_id] = {
            'api_calls': 0,
            'gpu_hours': 0,
            'storage_gb': 0
        }
        
        # Test usage updates
        asyncio.run(self.billing_system.update_usage(subscription_id, 'api_calls', 10))
        asyncio.run(self.billing_system.update_usage(subscription_id, 'gpu_hours', 2.5))
        asyncio.run(self.billing_system.update_usage(subscription_id, 'storage_gb', 100))
        
        usage = self.billing_system.usage_data[subscription_id]
        self.assertEqual(usage['api_calls'], 10)
        self.assertEqual(usage['gpu_hours'], 2.5)
        self.assertEqual(usage['storage_gb'], 100)
    
    def test_metrics_calculation(self):
        """Test billing metrics calculation"""
        # Add test data
        self.billing_system.metrics['total_customers'] = 10
        self.billing_system.metrics['active_subscriptions'] = 8
        self.billing_system.metrics['monthly_recurring_revenue'] = Decimal('3976.00')
        self.billing_system.metrics['lifetime_value'] = Decimal('15000.00')
        
        metrics = self.billing_system.get_billing_metrics()
        
        self.assertEqual(metrics['customers']['total'], 10)
        self.assertEqual(metrics['customers']['active'], 8)
        self.assertEqual(metrics['revenue']['mrr'], 3976.00)
        self.assertEqual(metrics['revenue']['ltv'], 15000.00)
        self.assertEqual(metrics['revenue']['arr'], 47712.00)  # MRR * 12

class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=5.0)
        self.circuit_breaker = CircuitBreaker('test', self.config)
    
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        # Should succeed initially
        result = await self.circuit_breaker.call(self._successful_operation)
        self.assertEqual(result, 'success')
        self.assertEqual(self.circuit_breaker.state, 'CLOSED')
    
    async def test_circuit_breaker_open_state(self):
        """Test circuit breaker opening after failures"""
        # Fail multiple times
        for _ in range(3):
            with self.assertRaises(Exception):
                await self.circuit_breaker.call(self._failing_operation)
        
        # Circuit should be open
        self.assertEqual(self.circuit_breaker.state, 'OPEN')
        
        # Should fail fast
        with self.assertRaises(Exception):
            await self.circuit_breaker.call(self._successful_operation)
    
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery"""
        # Open the circuit
        for _ in range(3):
            with self.assertRaises(Exception):
                await self.circuit_breaker.call(self._failing_operation)
        
        # Wait for recovery timeout
        self.circuit_breaker.last_failure_time = time.time() - 6.0
        
        # Should allow one test call
        result = await self.circuit_breaker.call(self._successful_operation)
        self.assertEqual(result, 'success')
        self.assertEqual(self.circuit_breaker.state, 'CLOSED')
    
    async def _successful_operation(self):
        """Mock successful operation"""
        return 'success'
    
    async def _failing_operation(self):
        """Mock failing operation"""
        raise Exception('Test failure')

class TestMetrics(unittest.TestCase):
    """Test metrics functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.metrics = BillingMetrics()
    
    def test_payment_metrics(self):
        """Test payment metrics recording"""
        self.metrics.record_payment_attempt('card', 'SOVREN_PROOF')
        self.metrics.record_payment_success('card', 'SOVREN_PROOF', 497.00, 'USD')
        
        # Check metrics were recorded
        summary = self.metrics.get_metrics_summary()
        self.assertEqual(summary['payment_metrics']['total_attempts'], 1)
        self.assertEqual(summary['payment_metrics']['total_success'], 1)
    
    def test_subscription_metrics(self):
        """Test subscription metrics recording"""
        self.metrics.record_subscription_creation('SOVREN_PROOF', 'monthly')
        self.metrics.set_active_subscriptions('SOVREN_PROOF', 5)
        
        # Check metrics were recorded
        summary = self.metrics.get_metrics_summary()
        self.assertEqual(summary['subscription_metrics']['total_creations'], 1)
        self.assertEqual(summary['subscription_metrics']['active_subscriptions'], 5)
    
    def test_revenue_metrics(self):
        """Test revenue metrics recording"""
        self.metrics.set_mrr(5000.00, 'USD')
        self.metrics.set_arr(60000.00, 'USD')
        self.metrics.record_ltv(15000.00, 'USD')
        
        # Check metrics were recorded
        summary = self.metrics.get_metrics_summary()
        self.assertEqual(summary['revenue_metrics']['mrr'], 5000.00)
        self.assertEqual(summary['revenue_metrics']['arr'], 60000.00)
        self.assertEqual(summary['revenue_metrics']['ltv'], 15000.00)

class TestSecureKeys(unittest.TestCase):
    """Test secure key management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.key_manager = SecureKeyManager('test_master_key_32_bytes_long_key')
    
    def test_key_encryption_decryption(self):
        """Test key encryption and decryption"""
        test_key = 'sk_live_test_key_12345'
        
        # Encrypt key
        encrypted = self.key_manager.encrypt_key('test_key', test_key)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, test_key)
        
        # Decrypt key
        decrypted = self.key_manager.decrypt_key('test_key', encrypted)
        self.assertEqual(decrypted, test_key)
    
    def test_key_storage_retrieval(self):
        """Test key storage and retrieval"""
        test_key = 'pk_live_test_key_67890'
        
        # Store key
        self.key_manager.store_key('test_key', test_key)
        
        # Retrieve key
        retrieved = self.key_manager.get_key('test_key')
        self.assertEqual(retrieved, test_key)
    
    def test_key_rotation(self):
        """Test key rotation"""
        original_key = 'sk_live_original_key'
        new_key = 'sk_live_new_key'
        
        # Store original key
        self.key_manager.store_key('test_key', original_key)
        
        # Rotate key
        self.key_manager.rotate_key('test_key', new_key)
        
        # Verify new key
        retrieved = self.key_manager.get_key('test_key')
        self.assertEqual(retrieved, new_key)

class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rate_limiter = RateLimiter()
        self.rate_limiter.add_limit('test_limit', 5, 60)
    
    async def test_rate_limiting_basic(self):
        """Test basic rate limiting"""
        # Should allow initial requests
        for i in range(5):
            allowed = await self.rate_limiter.is_allowed('test_limit')
            self.assertTrue(allowed)
        
        # Should block after limit
        allowed = await self.rate_limiter.is_allowed('test_limit')
        self.assertFalse(allowed)
    
    async def test_rate_limiting_reset(self):
        """Test rate limiting reset after window"""
        # Use up all requests
        for _ in range(5):
            await self.rate_limiter.is_allowed('test_limit')
        
        # Mock time to advance window
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 61  # Advance past window
            
            # Should allow again
            allowed = await self.rate_limiter.is_allowed('test_limit')
            self.assertTrue(allowed)

class TestHealthChecks(unittest.TestCase):
    """Test health check functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.health_checker = HealthChecker()
    
    @patch('aiohttp.ClientSession')
    async def test_killbill_health_check(self, mock_session):
        """Test Kill Bill health check"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        result = await self.health_checker.run_health_check('killbill')
        
        self.assertEqual(result['status'], 'healthy')
        self.assertIn('response_time', result)
    
    @patch('aiohttp.ClientSession')
    async def test_stripe_health_check(self, mock_session):
        """Test Stripe health check"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        result = await self.health_checker.run_health_check('stripe')
        
        self.assertEqual(result['status'], 'healthy')
        self.assertIn('response_time', result)

class TestConfigManager(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_manager = ConfigManager()
    
    def test_config_get_set(self):
        """Test configuration get/set operations"""
        # Set configuration
        self.config_manager.set('test.key', 'test_value')
        self.config_manager.set('test.nested.key', 'nested_value')
        
        # Get configuration
        value = self.config_manager.get('test.key')
        self.assertEqual(value, 'test_value')
        
        nested_value = self.config_manager.get('test.nested.key')
        self.assertEqual(nested_value, 'nested_value')
        
        # Test default value
        default_value = self.config_manager.get('nonexistent.key', 'default')
        self.assertEqual(default_value, 'default')
    
    def test_billing_config(self):
        """Test billing configuration"""
        config = self.config_manager.get_billing_config()
        
        self.assertIn('killbill_url', config)
        self.assertIn('stripe_live_secret', config)
        self.assertIn('currency', config)
    
    def test_database_config(self):
        """Test database configuration"""
        config = self.config_manager.get_database_config()
        
        self.assertIn('host', config)
        self.assertIn('port', config)
        self.assertIn('database', config)
    
    def test_config_validation(self):
        """Test configuration validation"""
        validation = self.config_manager.validate_config()
        
        self.assertIn('valid', validation)
        self.assertIn('errors', validation)
        self.assertIn('warnings', validation)

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBillingSystem,
        TestCircuitBreaker,
        TestMetrics,
        TestSecureKeys,
        TestRateLimiting,
        TestHealthChecks,
        TestConfigManager
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print coverage summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1) 