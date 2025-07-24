#!/usr/bin/env python3
"""
SOVREN Billing System - Test Suite
Comprehensive testing for production deployment
"""

import pytest
import asyncio
import json
import time
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import the billing system
from billing_integration import (
    BillingSystem, KillBillClient, Customer, Subscription, Invoice,
    SubscriptionStatus, PaymentStatus, BILLING_CONFIG, initialize_billing
)

class TestKillBillClient:
    """Test Kill Bill API client"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return KillBillClient(BILLING_CONFIG)
    
    @pytest.mark.asyncio
    async def test_create_auth_headers(self, client):
        """Test authentication header creation"""
        headers = client._create_auth_headers()
        
        assert 'Authorization' in headers
        assert 'X-Killbill-ApiKey' in headers
        assert 'X-Killbill-ApiSecret' in headers
        assert 'Content-Type' in headers
        assert headers['Content-Type'] == 'application/json'
    
    @pytest.mark.asyncio
    async def test_create_account_success(self, client):
        """Test successful account creation"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 201
            mock_response.headers = {'Location': '/1.0/kb/accounts/12345'}
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            customer = Customer(
                id='test_cust_123',
                email='test@example.com',
                name='Test User',
                company='Test Corp',
                created_at=time.time()
            )
            
            result = await client.create_account(customer)
            
            assert result['success'] is True
            assert result['account_id'] == '12345'
    
    @pytest.mark.asyncio
    async def test_create_account_failure(self, client):
        """Test failed account creation"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 400
            mock_response.text = AsyncMock(return_value='Bad Request')
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            customer = Customer(
                id='test_cust_123',
                email='test@example.com',
                name='Test User',
                company='Test Corp',
                created_at=time.time()
            )
            
            result = await client.create_account(customer)
            
            assert result['success'] is False
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_create_subscription_success(self, client):
        """Test successful subscription creation"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 201
            mock_response.headers = {'Location': '/1.0/kb/subscriptions/67890'}
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.create_subscription('12345', 'SOVREN_PROOF', 'monthly')
            
            assert result['success'] is True
            assert result['subscription_id'] == '67890'
    
    @pytest.mark.asyncio
    async def test_process_payment_success(self, client):
        """Test successful payment processing"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 201
            mock_response.headers = {'Location': '/1.0/kb/payments/11111'}
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.process_payment('12345', Decimal('497.00'), 'payment_method_123')
            
            assert result['success'] is True
            assert result['status'] == PaymentStatus.SUCCESS.value
            assert result['payment_id'] == '11111'
    
    @pytest.mark.asyncio
    async def test_process_payment_failure(self, client):
        """Test failed payment processing"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 400
            mock_response.text = AsyncMock(return_value='Payment failed')
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await client.process_payment('12345', Decimal('497.00'), 'payment_method_123')
            
            assert result['success'] is False
            assert result['status'] == PaymentStatus.FAILED.value
            assert 'error' in result

class TestBillingSystem:
    """Test billing system functionality"""
    
    @pytest.fixture
    async def billing_system(self):
        """Create test billing system"""
        system = BillingSystem()
        yield system
        await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_create_customer_success(self, billing_system):
        """Test successful customer creation"""
        with patch.object(billing_system.kb_client, 'create_account') as mock_create:
            mock_create.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User',
                company='Test Corp'
            )
            
            assert customer.id.startswith('cust_')
            assert customer.email == 'test@example.com'
            assert customer.name == 'Test User'
            assert customer.company == 'Test Corp'
            assert customer.metadata['kb_account_id'] == 'kb_account_123'
            assert billing_system.metrics['total_customers'] == 1
    
    @pytest.mark.asyncio
    async def test_create_customer_failure(self, billing_system):
        """Test failed customer creation"""
        with patch.object(billing_system.kb_client, 'create_account') as mock_create:
            mock_create.return_value = {
                'success': False,
                'error': 'Account creation failed'
            }
            
            with pytest.raises(Exception, match='Failed to create customer'):
                await billing_system.create_customer(
                    email='test@example.com',
                    name='Test User'
                )
    
    @pytest.mark.asyncio
    async def test_create_subscription_success(self, billing_system):
        """Test successful subscription creation"""
        # First create a customer
        with patch.object(billing_system.kb_client, 'create_account') as mock_create_account:
            mock_create_account.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User'
            )
            
            # Then create subscription
            with patch.object(billing_system.kb_client, 'create_subscription') as mock_create_sub:
                mock_create_sub.return_value = {
                    'success': True,
                    'subscription_id': 'kb_sub_456'
                }
                
                subscription = await billing_system.create_subscription(
                    customer.id,
                    'SOVREN_PROOF',
                    'monthly'
                )
                
                assert subscription.id.startswith('sub_')
                assert subscription.customer_id == customer.id
                assert subscription.plan_id == 'SOVREN_PROOF'
                assert subscription.status == SubscriptionStatus.ACTIVE
                assert subscription.price == Decimal('497.00')
                assert subscription.billing_period == 'monthly'
                assert subscription.metadata['kb_subscription_id'] == 'kb_sub_456'
                assert billing_system.metrics['active_subscriptions'] == 1
    
    @pytest.mark.asyncio
    async def test_create_subscription_invalid_customer(self, billing_system):
        """Test subscription creation with invalid customer"""
        with pytest.raises(ValueError, match='Customer.*not found'):
            await billing_system.create_subscription(
                'invalid_customer_id',
                'SOVREN_PROOF',
                'monthly'
            )
    
    @pytest.mark.asyncio
    async def test_create_subscription_invalid_tier(self, billing_system):
        """Test subscription creation with invalid tier"""
        # Create customer first
        with patch.object(billing_system.kb_client, 'create_account') as mock_create:
            mock_create.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User'
            )
            
            # Try to create subscription with invalid tier
            with pytest.raises(ValueError, match='Invalid tier'):
                await billing_system.create_subscription(
                    customer.id,
                    'INVALID_TIER',
                    'monthly'
                )
    
    @pytest.mark.asyncio
    async def test_process_payment_success(self, billing_system):
        """Test successful payment processing"""
        # Create customer first
        with patch.object(billing_system.kb_client, 'create_account') as mock_create:
            mock_create.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User'
            )
            
            # Process payment
            with patch.object(billing_system.kb_client, 'process_payment') as mock_payment:
                mock_payment.return_value = {
                    'success': True,
                    'payment_id': 'kb_payment_789',
                    'status': PaymentStatus.SUCCESS.value
                }
                
                payment_method = {'id': 'payment_method_123'}
                invoice = await billing_system.process_payment(
                    customer.id,
                    Decimal('497.00'),
                    payment_method
                )
                
                assert invoice.id.startswith('inv_')
                assert invoice.customer_id == customer.id
                assert invoice.amount == Decimal('497.00')
                assert invoice.status == PaymentStatus.SUCCESS
                assert invoice.paid_date is not None
                assert billing_system.metrics['lifetime_value'] == Decimal('497.00')
    
    @pytest.mark.asyncio
    async def test_process_payment_failure(self, billing_system):
        """Test failed payment processing"""
        # Create customer first
        with patch.object(billing_system.kb_client, 'create_account') as mock_create:
            mock_create.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User'
            )
            
            # Process payment with failure
            with patch.object(billing_system.kb_client, 'process_payment') as mock_payment:
                mock_payment.return_value = {
                    'success': False,
                    'status': PaymentStatus.FAILED.value,
                    'error': 'Payment failed'
                }
                
                payment_method = {'id': 'payment_method_123'}
                
                with pytest.raises(Exception, match='Payment failed'):
                    await billing_system.process_payment(
                        customer.id,
                        Decimal('497.00'),
                        payment_method
                    )
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self, billing_system):
        """Test successful subscription cancellation"""
        # Create customer and subscription first
        with patch.object(billing_system.kb_client, 'create_account') as mock_create_account:
            mock_create_account.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User'
            )
            
            with patch.object(billing_system.kb_client, 'create_subscription') as mock_create_sub:
                mock_create_sub.return_value = {
                    'success': True,
                    'subscription_id': 'kb_sub_456'
                }
                
                subscription = await billing_system.create_subscription(
                    customer.id,
                    'SOVREN_PROOF',
                    'monthly'
                )
                
                # Cancel subscription
                with patch.object(billing_system.kb_client, 'cancel_subscription') as mock_cancel:
                    mock_cancel.return_value = {'success': True}
                    
                    result = await billing_system.cancel_subscription(subscription.id)
                    
                    assert result['success'] is True
                    assert subscription.status == SubscriptionStatus.CANCELLED
                    assert subscription.end_date is not None
                    assert billing_system.metrics['active_subscriptions'] == 0
    
    @pytest.mark.asyncio
    async def test_update_usage(self, billing_system):
        """Test usage tracking"""
        # Create customer and subscription first
        with patch.object(billing_system.kb_client, 'create_account') as mock_create_account:
            mock_create_account.return_value = {
                'success': True,
                'account_id': 'kb_account_123'
            }
            
            customer = await billing_system.create_customer(
                email='test@example.com',
                name='Test User'
            )
            
            with patch.object(billing_system.kb_client, 'create_subscription') as mock_create_sub:
                mock_create_sub.return_value = {
                    'success': True,
                    'subscription_id': 'kb_sub_456'
                }
                
                subscription = await billing_system.create_subscription(
                    customer.id,
                    'SOVREN_PROOF',
                    'monthly'
                )
                
                # Update usage
                await billing_system.update_usage(subscription.id, 'api_calls', 100)
                await billing_system.update_usage(subscription.id, 'gpu_hours', 2.5)
                await billing_system.update_usage(subscription.id, 'storage_gb', 50)
                
                usage = billing_system.usage_data[subscription.id]
                assert usage['api_calls'] == 100
                assert usage['gpu_hours'] == 2.5
                assert usage['storage_gb'] == 50
    
    @pytest.mark.asyncio
    async def test_webhook_handling(self, billing_system):
        """Test webhook handling"""
        # Test payment success webhook
        payload = {
            'payment_id': 'test_payment_123',
            'amount': '497.00',
            'signature': 'valid_signature'
        }
        
        with patch.object(billing_system, '_verify_webhook_signature', return_value=True):
            result = await billing_system.handle_webhook('PAYMENT_SUCCESS', payload)
            assert result['status'] == 'success'
    
    def test_get_billing_metrics(self, billing_system):
        """Test billing metrics calculation"""
        metrics = billing_system.get_billing_metrics()
        
        assert 'customers' in metrics
        assert 'revenue' in metrics
        assert 'subscriptions' in metrics
        assert 'churn_rate' in metrics
        assert 'usage' in metrics
        
        assert metrics['customers']['total'] == 0
        assert metrics['customers']['active'] == 0
        assert metrics['revenue']['mrr'] == 0.0
        assert metrics['revenue']['ltv'] == 0.0
        assert metrics['revenue']['arr'] == 0.0
    
    def test_id_generation(self, billing_system):
        """Test ID generation methods"""
        customer_id = billing_system._generate_customer_id()
        subscription_id = billing_system._generate_subscription_id()
        invoice_id = billing_system._generate_invoice_id()
        
        assert customer_id.startswith('cust_')
        assert subscription_id.startswith('sub_')
        assert invoice_id.startswith('inv_')
        assert len(customer_id) == 16  # cust_ + 12 hex chars
        assert len(subscription_id) == 16  # sub_ + 12 hex chars
        assert len(invoice_id) == 16  # inv_ + 12 hex chars

class TestBillingSystemIntegration:
    """Integration tests for billing system"""
    
    @pytest.mark.asyncio
    async def test_full_customer_lifecycle(self):
        """Test complete customer lifecycle"""
        system = BillingSystem()
        
        try:
            # Mock all external API calls
            with patch.object(system.kb_client, 'create_account') as mock_create_account, \
                 patch.object(system.kb_client, 'create_subscription') as mock_create_sub, \
                 patch.object(system.kb_client, 'process_payment') as mock_payment, \
                 patch.object(system.kb_client, 'cancel_subscription') as mock_cancel:
                
                # Setup mocks
                mock_create_account.return_value = {
                    'success': True,
                    'account_id': 'kb_account_123'
                }
                mock_create_sub.return_value = {
                    'success': True,
                    'subscription_id': 'kb_sub_456'
                }
                mock_payment.return_value = {
                    'success': True,
                    'payment_id': 'kb_payment_789',
                    'status': PaymentStatus.SUCCESS.value
                }
                mock_cancel.return_value = {'success': True}
                
                # 1. Create customer
                customer = await system.create_customer(
                    email='integration@example.com',
                    name='Integration User',
                    company='Integration Corp'
                )
                
                # 2. Create subscription
                subscription = await system.create_subscription(
                    customer.id,
                    'SOVREN_PROOF_PLUS',
                    'yearly'
                )
                
                # 3. Process payment
                payment_method = {'id': 'payment_method_123'}
                invoice = await system.process_payment(
                    customer.id,
                    Decimal('8607.00'),
                    payment_method
                )
                
                # 4. Update usage
                await system.update_usage(subscription.id, 'api_calls', 5000)
                await system.update_usage(subscription.id, 'gpu_hours', 25)
                
                # 5. Get metrics
                metrics = system.get_billing_metrics()
                
                # 6. Cancel subscription
                result = await system.cancel_subscription(subscription.id)
                
                # Verify results
                assert customer.id in system.customers
                assert subscription.id in system.subscriptions
                assert invoice.id in system.invoices
                assert subscription.status == SubscriptionStatus.CANCELLED
                assert result['success'] is True
                assert metrics['customers']['total'] == 1
                assert metrics['revenue']['ltv'] == 8607.0
                
        finally:
            await system.shutdown()

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        system = BillingSystem()
        
        try:
            with patch.object(system.kb_client, 'create_account') as mock_create:
                mock_create.side_effect = asyncio.TimeoutError("Network timeout")
                
                with pytest.raises(asyncio.TimeoutError):
                    await system.create_customer(
                        email='timeout@example.com',
                        name='Timeout User'
                    )
        finally:
            await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_invalid_webhook_signature(self):
        """Test invalid webhook signature handling"""
        system = BillingSystem()
        
        try:
            payload = {
                'payment_id': 'test_payment',
                'amount': '100.00',
                'signature': 'invalid_signature'
            }
            
            with patch.object(system, '_verify_webhook_signature', return_value=False):
                result = await system.handle_webhook('PAYMENT_SUCCESS', payload)
                assert result['status'] == 'error'
                assert 'Invalid signature' in result['message']
        finally:
            await system.shutdown()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 