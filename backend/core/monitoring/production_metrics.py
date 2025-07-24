#!/usr/bin/env python3
"""
SOVREN AI - Production Metrics System
Comprehensive monitoring with Prometheus, OpenTelemetry, and business KPIs
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import hashlib
import random

# Optional imports for production monitoring
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available - metrics disabled")

try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.metrics import Meter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logging.warning("OpenTelemetry not available - tracing disabled")

logger = logging.getLogger('ProductionMetrics')

class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class BusinessMetric(Enum):
    """Business metric types"""
    REVENUE = "revenue"
    USERS = "users"
    SESSIONS = "sessions"
    CONVERSIONS = "conversions"
    RETENTION = "retention"
    SATISFACTION = "satisfaction"

@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: float
    value: float
    labels: Dict[str, str]
    metric_name: str
    metric_type: MetricType

@dataclass
class BusinessKPI:
    """Business Key Performance Indicator"""
    name: str
    value: float
    target: float
    unit: str
    trend: str  # "up", "down", "stable"
    last_updated: datetime
    description: str

@dataclass
class TraceSpan:
    """Distributed tracing span"""
    span_id: str
    trace_id: str
    name: str
    start_time: float
    end_time: Optional[float]
    status: str
    attributes: Dict[str, Any]
    events: List[Dict[str, Any]]

class ProductionMetrics:
    """Production-ready metrics collection system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.service_name = self.config['service_name']
        self.environment = self.config['environment']
        
        # Metrics storage
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.business_kpis: Dict[str, BusinessKPI] = {}
        self.traces: Dict[str, TraceSpan] = {}
        
        # Performance tracking
        self.performance_metrics = defaultdict(lambda: deque(maxlen=10000))
        self.error_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.business_metrics = defaultdict(lambda: deque(maxlen=1000))
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize monitoring systems
        self._init_prometheus()
        self._init_opentelemetry()
        
        # Start monitoring threads
        self._start_metrics_collection()
        self._start_business_kpi_tracking()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'service_name': 'sovren-ai',
            'environment': 'production',
            'prometheus_enabled': True,
            'opentelemetry_enabled': True,
            'metrics_retention_hours': 24,
            'sampling_rate': 0.1,  # 10% sampling
            'business_kpi_interval': 300,  # 5 minutes
            'performance_thresholds': {
                'response_time_ms': 1000,
                'error_rate_percent': 1.0,
                'cpu_usage_percent': 80.0,
                'memory_usage_percent': 85.0,
            },
        }
    
    def _init_prometheus(self):
        """Initialize Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus not available - using internal metrics")
            return
        
        try:
            # Request metrics
            self.request_counter = Counter(
                'sovren_requests_total',
                'Total requests processed',
                ['service', 'endpoint', 'method', 'status']
            )
            
            self.request_duration = Histogram(
                'sovren_request_duration_seconds',
                'Request processing time',
                ['service', 'endpoint', 'method'],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            )
            
            # Error metrics
            self.error_counter = Counter(
                'sovren_errors_total',
                'Total errors',
                ['service', 'error_type', 'severity']
            )
            
            # Business metrics
            self.revenue_gauge = Gauge(
                'sovren_revenue_usd',
                'Current revenue in USD',
                ['service', 'tier']
            )
            
            self.active_users = Gauge(
                'sovren_active_users',
                'Number of active users',
                ['service', 'user_type']
            )
            
            # System metrics
            self.cpu_usage = Gauge(
                'sovren_cpu_usage_percent',
                'CPU usage percentage',
                ['service', 'node']
            )
            
            self.memory_usage = Gauge(
                'sovren_memory_usage_percent',
                'Memory usage percentage',
                ['service', 'node']
            )
            
            self.gpu_utilization = Gauge(
                'sovren_gpu_utilization_percent',
                'GPU utilization percentage',
                ['service', 'gpu_id']
            )
            
            # Performance metrics
            self.latency_p95 = Gauge(
                'sovren_latency_p95_seconds',
                '95th percentile latency',
                ['service', 'endpoint']
            )
            
            self.throughput = Gauge(
                'sovren_throughput_requests_per_second',
                'Requests per second',
                ['service', 'endpoint']
            )
            
            logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus: {e}")
    
    def _init_opentelemetry(self):
        """Initialize OpenTelemetry tracing"""
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available - using internal tracing")
            return
        
        try:
            # Initialize tracer
            self.tracer = trace.get_tracer(self.service_name)
            
            # Initialize meter
            self.meter = metrics.get_meter(self.service_name)
            
            # Create instruments
            self.request_counter_otel = self.meter.create_counter(
                name="sovren.requests",
                description="Total requests processed"
            )
            
            self.request_duration_otel = self.meter.create_histogram(
                name="sovren.request.duration",
                description="Request processing time",
                unit="seconds"
            )
            
            logger.info("OpenTelemetry tracing initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      duration_ms: float, labels: Optional[Dict[str, str]] = None):
        """Record HTTP request metrics"""
        
        try:
            timestamp = time.time()
            labels = labels or {}
            
            # Add standard labels
            labels.update({
                'service': self.service_name,
                'endpoint': endpoint,
                'method': method,
                'status': str(status_code),
                'environment': self.environment,
            })
            
            # Record internal metrics
            metric_point = MetricPoint(
                timestamp=timestamp,
                value=duration_ms / 1000.0,  # Convert to seconds
                labels=labels,
                metric_name='request_duration',
                metric_type=MetricType.HISTOGRAM
            )
            
            with self._lock:
                self.metrics['request_duration'].append(metric_point)
                self.performance_metrics['request_duration'].append(duration_ms)
            
            # Record Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.request_counter.labels(
                    service=self.service_name,
                    endpoint=endpoint,
                    method=method,
                    status=str(status_code)
                ).inc()
                
                self.request_duration.labels(
                    service=self.service_name,
                    endpoint=endpoint,
                    method=method
                ).observe(duration_ms / 1000.0)
            
            # Record OpenTelemetry metrics
            if OPENTELEMETRY_AVAILABLE:
                self.request_counter_otel.add(1, labels)
                self.request_duration_otel.record(duration_ms / 1000.0, labels)
            
            # Check performance thresholds
            self._check_performance_thresholds('response_time_ms', duration_ms)
            
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")
    
    def record_error(self, error_type: str, error_message: str, severity: str = "error",
                    labels: Optional[Dict[str, str]] = None):
        """Record error metrics"""
        
        try:
            timestamp = time.time()
            labels = labels or {}
            
            # Add standard labels
            labels.update({
                'service': self.service_name,
                'error_type': error_type,
                'severity': severity,
                'environment': self.environment,
            })
            
            # Record internal metrics
            metric_point = MetricPoint(
                timestamp=timestamp,
                value=1.0,
                labels=labels,
                metric_name='errors',
                metric_type=MetricType.COUNTER
            )
            
            with self._lock:
                self.metrics['errors'].append(metric_point)
                self.error_metrics[error_type].append(timestamp)
            
            # Record Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.error_counter.labels(
                    service=self.service_name,
                    error_type=error_type,
                    severity=severity
                ).inc()
            
            # Check error rate thresholds
            self._check_error_rate_thresholds()
            
        except Exception as e:
            logger.error(f"Failed to record error metrics: {e}")
    
    def record_business_metric(self, metric_name: str, value: float, 
                             labels: Optional[Dict[str, str]] = None):
        """Record business metrics"""
        
        try:
            timestamp = time.time()
            labels = labels or {}
            
            # Add standard labels
            labels.update({
                'service': self.service_name,
                'environment': self.environment,
            })
            
            # Record internal metrics
            metric_point = MetricPoint(
                timestamp=timestamp,
                value=value,
                labels=labels,
                metric_name=metric_name,
                metric_type=MetricType.GAUGE
            )
            
            with self._lock:
                self.metrics[metric_name].append(metric_point)
                self.business_metrics[metric_name].append(value)
            
            # Update specific business metrics
            if metric_name == 'revenue':
                self._update_revenue_metrics(value, labels)
            elif metric_name == 'active_users':
                self._update_user_metrics(value, labels)
            
        except Exception as e:
            logger.error(f"Failed to record business metric: {e}")
    
    def _update_revenue_metrics(self, value: float, labels: Dict[str, str]):
        """Update revenue-related metrics"""
        if PROMETHEUS_AVAILABLE:
            tier = labels.get('tier', 'unknown')
            self.revenue_gauge.labels(
                service=self.service_name,
                tier=tier
            ).set(value)
    
    def _update_user_metrics(self, value: float, labels: Dict[str, str]):
        """Update user-related metrics"""
        if PROMETHEUS_AVAILABLE:
            user_type = labels.get('user_type', 'unknown')
            self.active_users.labels(
                service=self.service_name,
                user_type=user_type
            ).set(value)
    
    def record_system_metrics(self, cpu_percent: float, memory_percent: float,
                            gpu_metrics: Optional[Dict[int, float]] = None):
        """Record system performance metrics"""
        
        try:
            timestamp = time.time()
            
            # Record CPU usage
            self._record_system_metric('cpu_usage', cpu_percent, {'node': 'primary'})
            
            # Record memory usage
            self._record_system_metric('memory_usage', memory_percent, {'node': 'primary'})
            
            # Record GPU metrics
            if gpu_metrics:
                for gpu_id, utilization in gpu_metrics.items():
                    self._record_system_metric('gpu_utilization', utilization, {'gpu_id': str(gpu_id)})
            
            # Check system thresholds
            self._check_performance_thresholds('cpu_usage_percent', cpu_percent)
            self._check_performance_thresholds('memory_usage_percent', memory_percent)
            
        except Exception as e:
            logger.error(f"Failed to record system metrics: {e}")
    
    def _record_system_metric(self, metric_name: str, value: float, labels: Dict[str, str]):
        """Record individual system metric"""
        
        # Record internal metrics
        metric_point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels,
            metric_name=metric_name,
            metric_type=MetricType.GAUGE
        )
        
        with self._lock:
            self.metrics[metric_name].append(metric_point)
        
        # Record Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            if metric_name == 'cpu_usage':
                self.cpu_usage.labels(
                    service=self.service_name,
                    node=labels.get('node', 'unknown')
                ).set(value)
            elif metric_name == 'memory_usage':
                self.memory_usage.labels(
                    service=self.service_name,
                    node=labels.get('node', 'unknown')
                ).set(value)
            elif metric_name == 'gpu_utilization':
                self.gpu_utilization.labels(
                    service=self.service_name,
                    gpu_id=labels.get('gpu_id', 'unknown')
                ).set(value)
    
    def start_trace(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None) -> str:
        """Start a distributed trace span"""
        
        try:
            span_id = str(uuid.uuid4())
            trace_id = str(uuid.uuid4())
            
            # Create internal span
            span = TraceSpan(
                span_id=span_id,
                trace_id=trace_id,
                name=operation_name,
                start_time=time.time(),
                end_time=None,
                status='running',
                attributes=attributes or {},
                events=[]
            )
            
            with self._lock:
                self.traces[span_id] = span
            
            # Create OpenTelemetry span
            if OPENTELEMETRY_AVAILABLE:
                with self.tracer.start_as_current_span(
                    operation_name,
                    attributes=attributes or {}
                ) as otel_span:
                    span.attributes['otel_span'] = otel_span
            
            return span_id
            
        except Exception as e:
            logger.error(f"Failed to start trace: {e}")
            return str(uuid.uuid4())
    
    def end_trace(self, span_id: str, status: str = "success", 
                  attributes: Optional[Dict[str, Any]] = None):
        """End a distributed trace span"""
        
        try:
            with self._lock:
                if span_id in self.traces:
                    span = self.traces[span_id]
                    span.end_time = time.time()
                    span.status = status
                    
                    if attributes:
                        span.attributes.update(attributes)
                    
                    # Update OpenTelemetry span
                    if OPENTELEMETRY_AVAILABLE and 'otel_span' in span.attributes:
                        otel_span = span.attributes['otel_span']
                        if status == "success":
                            otel_span.set_status(Status(StatusCode.OK))
                        else:
                            otel_span.set_status(Status(StatusCode.ERROR))
                        otel_span.end()
            
        except Exception as e:
            logger.error(f"Failed to end trace: {e}")
    
    def add_trace_event(self, span_id: str, event_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to trace span"""
        
        try:
            with self._lock:
                if span_id in self.traces:
                    span = self.traces[span_id]
                    event = {
                        'name': event_name,
                        'timestamp': time.time(),
                        'attributes': attributes or {}
                    }
                    span.events.append(event)
                    
                    # Add to OpenTelemetry span
                    if OPENTELEMETRY_AVAILABLE and 'otel_span' in span.attributes:
                        otel_span = span.attributes['otel_span']
                        otel_span.add_event(event_name, attributes or {})
            
        except Exception as e:
            logger.error(f"Failed to add trace event: {e}")
    
    def _check_performance_thresholds(self, metric_name: str, value: float):
        """Check if performance metrics exceed thresholds"""
        
        threshold = self.config['performance_thresholds'].get(metric_name)
        if threshold and value > threshold:
            logger.warning(f"Performance threshold exceeded: {metric_name} = {value} (threshold: {threshold})")
            
            # Record threshold violation
            self.record_error(
                error_type='performance_threshold_violation',
                error_message=f"{metric_name} exceeded threshold",
                severity='warning',
                labels={'metric': metric_name, 'value': str(value), 'threshold': str(threshold)}
            )
    
    def _check_error_rate_thresholds(self):
        """Check error rate thresholds"""
        
        try:
            # Calculate error rate for last hour
            cutoff_time = time.time() - 3600  # 1 hour
            
            with self._lock:
                total_errors = sum(len([e for e in errors if e > cutoff_time]) 
                                 for errors in self.error_metrics.values())
                
                # Estimate total requests (this would be more accurate with actual request count)
                total_requests = len([m for m in self.metrics['request_duration'] 
                                   if m.timestamp > cutoff_time])
                
                if total_requests > 0:
                    error_rate = (total_errors / total_requests) * 100
                    self._check_performance_thresholds('error_rate_percent', error_rate)
        
        except Exception as e:
            logger.error(f"Failed to check error rate thresholds: {e}")
    
    def _start_metrics_collection(self):
        """Start background metrics collection thread"""
        def collection_loop():
            while True:
                try:
                    # Calculate and record performance metrics
                    self._calculate_performance_metrics()
                    
                    # Clean up old metrics
                    self._cleanup_old_metrics()
                    
                    time.sleep(60)  # Collect every minute
                    
                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
        
        collection_thread = threading.Thread(target=collection_loop, daemon=True)
        collection_thread.start()
    
    def _start_business_kpi_tracking(self):
        """Start business KPI tracking thread"""
        def kpi_loop():
            while True:
                try:
                    # Update business KPIs
                    self._update_business_kpis()
                    
                    time.sleep(self.config['business_kpi_interval'])
                    
                except Exception as e:
                    logger.error(f"Business KPI tracking error: {e}")
        
        kpi_thread = threading.Thread(target=kpi_loop, daemon=True)
        kpi_thread.start()
    
    def _calculate_performance_metrics(self):
        """Calculate performance metrics from collected data"""
        
        try:
            with self._lock:
                # Calculate latency percentiles
                if self.performance_metrics['request_duration']:
                    latencies = list(self.performance_metrics['request_duration'])
                    latencies.sort()
                    
                    p50 = latencies[int(len(latencies) * 0.5)]
                    p95 = latencies[int(len(latencies) * 0.95)]
                    p99 = latencies[int(len(latencies) * 0.99)]
                    
                    # Record percentile metrics
                    self._record_performance_metric('latency_p50', p50)
                    self._record_performance_metric('latency_p95', p95)
                    self._record_performance_metric('latency_p99', p99)
                    
                    # Update Prometheus metrics
                    if PROMETHEUS_AVAILABLE:
                        self.latency_p95.labels(
                            service=self.service_name,
                            endpoint='all'
                        ).set(p95 / 1000.0)  # Convert to seconds
                
                # Calculate throughput
                if self.performance_metrics['request_duration']:
                    # Calculate requests per second (simplified)
                    recent_requests = len([r for r in self.performance_metrics['request_duration'] 
                                        if r > time.time() - 60])  # Last minute
                    throughput = recent_requests / 60.0
                    
                    self._record_performance_metric('throughput_rps', throughput)
                    
                    # Update Prometheus metrics
                    if PROMETHEUS_AVAILABLE:
                        self.throughput.labels(
                            service=self.service_name,
                            endpoint='all'
                        ).set(throughput)
        
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
    
    def _record_performance_metric(self, metric_name: str, value: float):
        """Record calculated performance metric"""
        metric_point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels={'service': self.service_name, 'environment': self.environment},
            metric_name=metric_name,
            metric_type=MetricType.GAUGE
        )
        
        with self._lock:
            self.metrics[metric_name].append(metric_point)
    
    def _update_business_kpis(self):
        """Update business Key Performance Indicators"""
        
        try:
            with self._lock:
                # Revenue KPI
                if 'revenue' in self.business_metrics:
                    recent_revenue = list(self.business_metrics['revenue'])[-10:]  # Last 10 values
                    if recent_revenue:
                        current_revenue = recent_revenue[-1]
                        avg_revenue = sum(recent_revenue) / len(recent_revenue)
                        
                        trend = "up" if current_revenue > avg_revenue else "down" if current_revenue < avg_revenue else "stable"
                        
                        self.business_kpis['revenue'] = BusinessKPI(
                            name='Monthly Recurring Revenue',
                            value=current_revenue,
                            target=100000.0,  # $100K target
                            unit='USD',
                            trend=trend,
                            last_updated=datetime.now(),
                            description='Current monthly recurring revenue'
                        )
                
                # User KPI
                if 'active_users' in self.business_metrics:
                    recent_users = list(self.business_metrics['active_users'])[-10:]
                    if recent_users:
                        current_users = recent_users[-1]
                        avg_users = sum(recent_users) / len(recent_users)
                        
                        trend = "up" if current_users > avg_users else "down" if current_users < avg_users else "stable"
                        
                        self.business_kpis['active_users'] = BusinessKPI(
                            name='Active Users',
                            value=current_users,
                            target=1000.0,  # 1K users target
                            unit='users',
                            trend=trend,
                            last_updated=datetime.now(),
                            description='Number of active users'
                        )
        
        except Exception as e:
            logger.error(f"Failed to update business KPIs: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        
        try:
            cutoff_time = time.time() - (self.config['metrics_retention_hours'] * 3600)
            
            with self._lock:
                for metric_name in list(self.metrics.keys()):
                    self.metrics[metric_name] = [
                        point for point in self.metrics[metric_name]
                        if point.timestamp > cutoff_time
                    ]
                
                # Clean up old traces
                old_traces = [
                    span_id for span_id, span in self.traces.items()
                    if span.end_time and span.end_time < cutoff_time
                ]
                for span_id in old_traces:
                    del self.traces[span_id]
        
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        
        with self._lock:
            summary = {
                'service': self.service_name,
                'environment': self.environment,
                'timestamp': time.time(),
                'metrics': {},
                'business_kpis': {},
                'performance': {},
                'errors': {},
            }
            
            # Metrics summary
            for metric_name, points in self.metrics.items():
                if points:
                    recent_points = [p for p in points if p.timestamp > time.time() - 3600]  # Last hour
                    if recent_points:
                        values = [p.value for p in recent_points]
                        summary['metrics'][metric_name] = {
                            'count': len(recent_points),
                            'min': min(values),
                            'max': max(values),
                            'avg': sum(values) / len(values),
                        }
            
            # Business KPIs
            for kpi_name, kpi in self.business_kpis.items():
                summary['business_kpis'][kpi_name] = {
                    'name': kpi.name,
                    'value': kpi.value,
                    'target': kpi.target,
                    'unit': kpi.unit,
                    'trend': kpi.trend,
                    'last_updated': kpi.last_updated.isoformat(),
                }
            
            # Performance summary
            if self.performance_metrics['request_duration']:
                latencies = list(self.performance_metrics['request_duration'])
                summary['performance'] = {
                    'avg_latency_ms': sum(latencies) / len(latencies),
                    'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)],
                    'p99_latency_ms': sorted(latencies)[int(len(latencies) * 0.99)],
                    'total_requests': len(latencies),
                }
            
            # Error summary
            total_errors = sum(len(errors) for errors in self.error_metrics.values())
            summary['errors'] = {
                'total_errors': total_errors,
                'error_types': {error_type: len(errors) for error_type, errors in self.error_metrics.items()},
            }
            
            return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        
        try:
            summary = self.get_metrics_summary()
            
            # Determine overall health
            health_status = "healthy"
            issues = []
            
            # Check performance thresholds
            if 'performance' in summary:
                avg_latency = summary['performance'].get('avg_latency_ms', 0)
                if avg_latency > self.config['performance_thresholds']['response_time_ms']:
                    health_status = "degraded"
                    issues.append(f"High latency: {avg_latency:.2f}ms")
            
            # Check error rate
            if 'errors' in summary:
                total_errors = summary['errors']['total_errors']
                total_requests = summary['performance'].get('total_requests', 1)
                error_rate = (total_errors / total_requests) * 100
                
                if error_rate > self.config['performance_thresholds']['error_rate_percent']:
                    health_status = "unhealthy"
                    issues.append(f"High error rate: {error_rate:.2f}%")
            
            return {
                'status': health_status,
                'issues': issues,
                'timestamp': time.time(),
                'service': self.service_name,
                'environment': self.environment,
            }
        
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                'status': 'unknown',
                'issues': [f"Health check failed: {e}"],
                'timestamp': time.time(),
                'service': self.service_name,
                'environment': self.environment,
            } 