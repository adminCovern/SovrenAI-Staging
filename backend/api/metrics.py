#!/usr/bin/env python3
"""
SOVREN Billing System - Prometheus Metrics
Comprehensive metrics for billing operations and system health
"""

import time
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict, Any
import logging

logger = logging.getLogger('BillingMetrics')

class BillingMetrics:
    """Comprehensive metrics for billing operations"""
    
    def __init__(self):
        # Payment metrics
        self.payment_attempts = Counter(
            'billing_payment_attempts_total',
            'Total payment attempts',
            ['payment_method', 'tier']
        )
        self.payment_success = Counter(
            'billing_payment_success_total',
            'Total successful payments',
            ['payment_method', 'tier']
        )
        self.payment_failures = Counter(
            'billing_payment_failures_total',
            'Total payment failures',
            ['payment_method', 'tier', 'error_type']
        )
        self.payment_amount = Counter(
            'billing_payment_amount_total',
            'Total payment amount processed',
            ['currency', 'tier']
        )
        
        # Subscription metrics
        self.subscription_creations = Counter(
            'billing_subscription_creations_total',
            'Total subscriptions created',
            ['tier', 'billing_period']
        )
        self.subscription_cancellations = Counter(
            'billing_subscription_cancellations_total',
            'Total subscriptions cancelled',
            ['tier', 'reason']
        )
        self.active_subscriptions = Gauge(
            'billing_active_subscriptions',
            'Number of active subscriptions',
            ['tier']
        )
        
        # Customer metrics
        self.customer_registrations = Counter(
            'billing_customer_registrations_total',
            'Total customer registrations'
        )
        self.active_customers = Gauge(
            'billing_active_customers',
            'Number of active customers'
        )
        
        # Revenue metrics
        self.mrr_gauge = Gauge(
            'billing_monthly_recurring_revenue',
            'Monthly recurring revenue',
            ['currency']
        )
        self.arr_gauge = Gauge(
            'billing_annual_recurring_revenue',
            'Annual recurring revenue',
            ['currency']
        )
        self.ltv_counter = Counter(
            'billing_lifetime_value_total',
            'Total lifetime value',
            ['currency']
        )
        
        # Performance metrics
        self.payment_duration = Histogram(
            'billing_payment_duration_seconds',
            'Payment processing time',
            ['payment_method', 'tier'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
        )
        self.api_request_duration = Histogram(
            'billing_api_request_duration_seconds',
            'API request processing time',
            ['endpoint', 'method'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Error metrics
        self.api_errors = Counter(
            'billing_api_errors_total',
            'Total API errors',
            ['service', 'endpoint', 'error_type']
        )
        self.circuit_breaker_trips = Counter(
            'billing_circuit_breaker_trips_total',
            'Circuit breaker trips',
            ['service']
        )
        
        # System metrics
        self.database_connections = Gauge(
            'billing_database_connections',
            'Number of active database connections'
        )
        self.cache_hits = Counter(
            'billing_cache_hits_total',
            'Cache hits',
            ['cache_type']
        )
        self.cache_misses = Counter(
            'billing_cache_misses_total',
            'Cache misses',
            ['cache_type']
        )
        
        # Usage metrics
        self.api_calls = Counter(
            'billing_api_calls_total',
            'Total API calls',
            ['endpoint', 'method']
        )
        self.gpu_hours_used = Counter(
            'billing_gpu_hours_total',
            'Total GPU hours used',
            ['tier']
        )
        self.storage_used = Gauge(
            'billing_storage_gb',
            'Storage used in GB',
            ['tier']
        )
    
    def record_payment_attempt(self, payment_method: str, tier: str):
        """Record payment attempt"""
        self.payment_attempts.labels(payment_method=payment_method, tier=tier).inc()
    
    def record_payment_success(self, payment_method: str, tier: str, amount: float, currency: str):
        """Record successful payment"""
        self.payment_success.labels(payment_method=payment_method, tier=tier).inc()
        self.payment_amount.labels(currency=currency, tier=tier).inc(amount)
    
    def record_payment_failure(self, payment_method: str, tier: str, error_type: str):
        """Record payment failure"""
        self.payment_failures.labels(payment_method=payment_method, tier=tier, error_type=error_type).inc()
    
    def record_subscription_creation(self, tier: str, billing_period: str):
        """Record subscription creation"""
        self.subscription_creations.labels(tier=tier, billing_period=billing_period).inc()
    
    def record_subscription_cancellation(self, tier: str, reason: str):
        """Record subscription cancellation"""
        self.subscription_cancellations.labels(tier=tier, reason=reason).inc()
    
    def set_active_subscriptions(self, tier: str, count: int):
        """Set active subscription count"""
        self.active_subscriptions.labels(tier=tier).set(count)
    
    def record_customer_registration(self):
        """Record customer registration"""
        self.customer_registrations.inc()
    
    def set_active_customers(self, count: int):
        """Set active customer count"""
        self.active_customers.set(count)
    
    def set_mrr(self, amount: float, currency: str):
        """Set monthly recurring revenue"""
        self.mrr_gauge.labels(currency=currency).set(amount)
    
    def set_arr(self, amount: float, currency: str):
        """Set annual recurring revenue"""
        self.arr_gauge.labels(currency=currency).set(amount)
    
    def record_ltv(self, amount: float, currency: str):
        """Record lifetime value"""
        self.ltv_counter.labels(currency=currency).inc(amount)
    
    def record_payment_duration(self, payment_method: str, tier: str, duration: float):
        """Record payment processing duration"""
        self.payment_duration.labels(payment_method=payment_method, tier=tier).observe(duration)
    
    def record_api_request_duration(self, endpoint: str, method: str, duration: float):
        """Record API request duration"""
        self.api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
    
    def record_api_error(self, service: str, endpoint: str, error_type: str):
        """Record API error"""
        self.api_errors.labels(service=service, endpoint=endpoint, error_type=error_type).inc()
    
    def record_circuit_breaker_trip(self, service: str):
        """Record circuit breaker trip"""
        self.circuit_breaker_trips.labels(service=service).inc()
    
    def set_database_connections(self, count: int):
        """Set database connection count"""
        self.database_connections.set(count)
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        self.cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        self.cache_misses.labels(cache_type=cache_type).inc()
    
    def record_api_call(self, endpoint: str, method: str):
        """Record API call"""
        self.api_calls.labels(endpoint=endpoint, method=method).inc()
    
    def record_gpu_hours(self, tier: str, hours: float):
        """Record GPU hours used"""
        self.gpu_hours_used.labels(tier=tier).inc(hours)
    
    def set_storage_used(self, tier: str, gb: float):
        """Set storage used"""
        self.storage_used.labels(tier=tier).set(gb)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for monitoring"""
        # Get current metric values using proper Prometheus client methods
        try:
            # For counters, we need to get the current value
            # For gauges, we can get the current value directly
            # For histograms, we need to get statistics
            
            # Get payment metrics
            payment_attempts_total = sum(
                metric._value.get() for metric in self.payment_attempts._metrics.values()
            ) if hasattr(self.payment_attempts, '_metrics') else 0
            
            payment_success_total = sum(
                metric._value.get() for metric in self.payment_success._metrics.values()
            ) if hasattr(self.payment_success, '_metrics') else 0
            
            payment_failures_total = sum(
                metric._value.get() for metric in self.payment_failures._metrics.values()
            ) if hasattr(self.payment_failures, '_metrics') else 0
            
            payment_amount_total = sum(
                metric._value.get() for metric in self.payment_amount._metrics.values()
            ) if hasattr(self.payment_amount, '_metrics') else 0
            
            # Get subscription metrics
            subscription_creations_total = sum(
                metric._value.get() for metric in self.subscription_creations._metrics.values()
            ) if hasattr(self.subscription_creations, '_metrics') else 0
            
            subscription_cancellations_total = sum(
                metric._value.get() for metric in self.subscription_cancellations._metrics.values()
            ) if hasattr(self.subscription_cancellations, '_metrics') else 0
            
            active_subscriptions_total = sum(
                metric._value.get() for metric in self.active_subscriptions._metrics.values()
            ) if hasattr(self.active_subscriptions, '_metrics') else 0
            
            # Get customer metrics
            customer_registrations_total = self.customer_registrations._value.get() if hasattr(self.customer_registrations, '_value') else 0
            active_customers_total = self.active_customers._value.get() if hasattr(self.active_customers, '_value') else 0
            
            # Get revenue metrics
            mrr_total = sum(
                metric._value.get() for metric in self.mrr_gauge._metrics.values()
            ) if hasattr(self.mrr_gauge, '_metrics') else 0
            
            arr_total = sum(
                metric._value.get() for metric in self.arr_gauge._metrics.values()
            ) if hasattr(self.arr_gauge, '_metrics') else 0
            
            ltv_total = sum(
                metric._value.get() for metric in self.ltv_counter._metrics.values()
            ) if hasattr(self.ltv_counter, '_metrics') else 0
            
            # Get error metrics
            api_errors_total = sum(
                metric._value.get() for metric in self.api_errors._metrics.values()
            ) if hasattr(self.api_errors, '_metrics') else 0
            
            circuit_trips_total = sum(
                metric._value.get() for metric in self.circuit_breaker_trips._metrics.values()
            ) if hasattr(self.circuit_breaker_trips, '_metrics') else 0
            
            return {
                'payment_metrics': {
                    'total_attempts': payment_attempts_total,
                    'total_success': payment_success_total,
                    'total_failures': payment_failures_total,
                    'total_amount': payment_amount_total
                },
                'subscription_metrics': {
                    'total_creations': subscription_creations_total,
                    'total_cancellations': subscription_cancellations_total,
                    'active_subscriptions': active_subscriptions_total
                },
                'customer_metrics': {
                    'total_registrations': customer_registrations_total,
                    'active_customers': active_customers_total
                },
                'revenue_metrics': {
                    'mrr': mrr_total,
                    'arr': arr_total,
                    'ltv': ltv_total
                },
                'performance_metrics': {
                    'avg_payment_duration': 0.0,  # Would need histogram statistics
                    'avg_api_duration': 0.0   # Would need histogram statistics
                },
                'error_metrics': {
                    'total_api_errors': api_errors_total,
                    'total_circuit_trips': circuit_trips_total
                }
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {
                'payment_metrics': {'total_attempts': 0, 'total_success': 0, 'total_failures': 0, 'total_amount': 0},
                'subscription_metrics': {'total_creations': 0, 'total_cancellations': 0, 'active_subscriptions': 0},
                'customer_metrics': {'total_registrations': 0, 'active_customers': 0},
                'revenue_metrics': {'mrr': 0, 'arr': 0, 'ltv': 0},
                'performance_metrics': {'avg_payment_duration': 0.0, 'avg_api_duration': 0.0},
                'error_metrics': {'total_api_errors': 0, 'total_circuit_trips': 0}
            }

# Global metrics instance
billing_metrics = BillingMetrics() 