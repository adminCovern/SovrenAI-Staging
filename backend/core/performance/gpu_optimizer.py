#!/usr/bin/env python3
"""
SOVREN AI - B200 GPU Optimization System
Optimized for 8x NVIDIA B200 GPUs with 640GB total memory
"""

import os
import sys
import time
import threading
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import subprocess

logger = logging.getLogger('GPUOptimizer')

class GPUState(Enum):
    """GPU operational states"""
    IDLE = "idle"
    LOADING = "loading"
    COMPUTING = "computing"
    MEMORY_FULL = "memory_full"
    ERROR = "error"

class ModelType(Enum):
    """AI model types"""
    WHISPER = "whisper"
    STYLETTS2 = "styletts2"
    MIXTRAL = "mixtral"
    BAYESIAN = "bayesian"
    CUSTOM = "custom"

@dataclass
class GPUInfo:
    """GPU hardware information"""
    gpu_id: int
    total_memory_gb: float
    available_memory_gb: float
    compute_capability: str
    sm_count: int
    memory_bandwidth_gbps: float
    fp16_tflops: float
    fp8_tflops: float
    state: GPUState
    temperature_celsius: float
    power_watts: float
    utilization_percent: float

@dataclass
class ModelAllocation:
    """Model allocation on GPU"""
    model_id: str
    model_type: ModelType
    gpu_id: int
    memory_gb: float
    compute_cores: int
    batch_size: int
    precision: str
    created_at: float
    last_used: float
    performance_score: float

class B200Optimizer:
    """B200-specific GPU optimization system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.gpu_count = self.config['gpu_count']
        self.total_memory_gb = self.config['total_memory_gb']
        self.memory_per_gpu = self.config['memory_per_gpu']
        
        # GPU management
        self.gpus: Dict[int, GPUInfo] = {}
        self.model_allocations: Dict[str, ModelAllocation] = {}
        self.gpu_managers: Dict[int, 'GPUManager'] = {}
        
        # Performance tracking
        self.performance_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.memory_usage = defaultdict(lambda: deque(maxlen=1000))
        self.temperature_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize GPU system
        self._init_gpu_system()
        
        # Start monitoring thread
        self._start_monitoring_thread()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for B200 system"""
        return {
            'gpu_count': 8,
            'total_memory_gb': 640.0,  # 8x 80GB
            'memory_per_gpu': 80.0,
            'max_memory_utilization': 0.95,
            'temperature_threshold': 85.0,
            'power_threshold': 700.0,  # Watts
            'monitoring_interval': 1,
            'model_configs': {
                'whisper': {
                    'memory_gb': 15.0,
                    'compute_cores': 4,
                    'batch_size': 16,
                    'precision': 'fp16',
                    'target_latency_ms': 150,
                },
                'styletts2': {
                    'memory_gb': 8.0,
                    'compute_cores': 2,
                    'batch_size': 8,
                    'precision': 'fp16',
                    'target_latency_ms': 100,
                },
                'mixtral': {
                    'memory_gb': 24.0,
                    'compute_cores': 8,
                    'batch_size': 4,
                    'precision': 'fp8',
                    'target_latency_ms': 90,
                },
            },
        }
    
    def _init_gpu_system(self):
        """Initialize GPU system and managers"""
        try:
            for gpu_id in range(self.gpu_count):
                # Initialize GPU info
                gpu_info = GPUInfo(
                    gpu_id=gpu_id,
                    total_memory_gb=self.memory_per_gpu,
                    available_memory_gb=self.memory_per_gpu,
                    compute_capability="9.0",
                    sm_count=144,
                    memory_bandwidth_gbps=1000.0,
                    fp16_tflops=10000.0,
                    fp8_tflops=20000.0,
                    state=GPUState.IDLE,
                    temperature_celsius=45.0,
                    power_watts=200.0,
                    utilization_percent=0.0,
                )
                self.gpus[gpu_id] = gpu_info
                
                # Initialize GPU manager
                self.gpu_managers[gpu_id] = GPUManager(gpu_id, gpu_info, self.config)
            
            logger.info(f"Initialized {len(self.gpus)} B200 GPUs")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPU system: {e}")
    
    def optimize_model_placement(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize model placement across GPUs"""
        
        try:
            with self._lock:
                model_type = ModelType(model_config['type'])
                model_id = model_config.get('model_id', f"{model_type.value}_{int(time.time())}")
                
                # Get model requirements
                requirements = self.config['model_configs'].get(model_type.value, {})
                memory_gb = requirements.get('memory_gb', 10.0)
                compute_cores = requirements.get('compute_cores', 2)
                
                # Find optimal GPU
                optimal_gpu = self._find_optimal_gpu(memory_gb, compute_cores, model_type)
                if optimal_gpu is None:
                    return {
                        'success': False,
                        'error': 'No suitable GPU available',
                        'model_id': model_id,
                    }
                
                # Create allocation
                allocation = ModelAllocation(
                    model_id=model_id,
                    model_type=model_type,
                    gpu_id=optimal_gpu,
                    memory_gb=memory_gb,
                    compute_cores=compute_cores,
                    batch_size=requirements.get('batch_size', 1),
                    precision=requirements.get('precision', 'fp16'),
                    created_at=time.time(),
                    last_used=time.time(),
                    performance_score=0.0,
                )
                
                # Update GPU state
                gpu = self.gpus[optimal_gpu]
                gpu.available_memory_gb -= memory_gb
                gpu.state = GPUState.LOADING
                
                # Store allocation
                self.model_allocations[model_id] = allocation
                
                # Optimize for performance
                optimization_result = self._optimize_for_performance(allocation)
                
                logger.info(f"Model {model_id} allocated to GPU {optimal_gpu}")
                
                return {
                    'success': True,
                    'model_id': model_id,
                    'gpu_id': optimal_gpu,
                    'memory_gb': memory_gb,
                    'optimization': optimization_result,
                }
                
        except Exception as e:
            logger.error(f"Model placement optimization failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_id': model_id if 'model_id' in locals() else 'unknown',
            }
    
    def _find_optimal_gpu(self, memory_gb: float, compute_cores: int, model_type: ModelType) -> Optional[int]:
        """Find optimal GPU for model allocation"""
        
        best_gpu = None
        best_score = float('-inf')
        
        for gpu_id, gpu in self.gpus.items():
            # Check if GPU can accommodate the model
            if gpu.available_memory_gb < memory_gb:
                continue
            
            if gpu.state == GPUState.ERROR:
                continue
            
            # Calculate GPU score based on multiple factors
            memory_score = gpu.available_memory_gb / self.memory_per_gpu
            utilization_score = 1 - (gpu.utilization_percent / 100)
            temperature_score = 1 - (gpu.temperature_celsius / self.config['temperature_threshold'])
            
            # Weighted score
            score = (memory_score * 0.4 + utilization_score * 0.4 + temperature_score * 0.2)
            
            # Prefer GPUs with similar models for better batching
            similar_models = sum(1 for alloc in self.model_allocations.values() 
                               if alloc.gpu_id == gpu_id and alloc.model_type == model_type)
            if similar_models > 0:
                score += 0.1  # Bonus for co-location
            
            if score > best_score:
                best_score = score
                best_gpu = gpu_id
        
        return best_gpu
    
    def _optimize_for_performance(self, allocation: ModelAllocation) -> Dict[str, Any]:
        """Optimize model for maximum performance"""
        
        gpu = self.gpus[allocation.gpu_id]
        model_config = self.config['model_configs'].get(allocation.model_type.value, {})
        
        optimizations = {
            'memory_optimization': {},
            'compute_optimization': {},
            'batch_optimization': {},
            'precision_optimization': {},
        }
        
        # Memory optimization
        memory_utilization = (gpu.total_memory_gb - gpu.available_memory_gb) / gpu.total_memory_gb
        if memory_utilization > 0.8:
            optimizations['memory_optimization'] = {
                'action': 'Enable memory pooling',
                'expected_improvement': '10-15% memory efficiency',
                'priority': 'High',
            }
        
        # Compute optimization
        if allocation.compute_cores < 4:
            optimizations['compute_optimization'] = {
                'action': 'Increase compute cores allocation',
                'expected_improvement': '20-30% throughput increase',
                'priority': 'Medium',
            }
        
        # Batch optimization
        current_batch = allocation.batch_size
        optimal_batch = model_config.get('optimal_batch_size', current_batch * 2)
        if current_batch < optimal_batch:
            optimizations['batch_optimization'] = {
                'action': f'Increase batch size from {current_batch} to {optimal_batch}',
                'expected_improvement': '15-25% throughput increase',
                'priority': 'Medium',
            }
        
        # Precision optimization
        if allocation.precision == 'fp16' and model_config.get('supports_fp8', False):
            optimizations['precision_optimization'] = {
                'action': 'Switch to FP8 precision',
                'expected_improvement': '30-50% speedup',
                'priority': 'High',
            }
        
        return optimizations
    
    def load_balance_models(self) -> Dict[str, Any]:
        """Load balance models across GPUs for optimal performance"""
        
        with self._lock:
            balance_result = {
                'migrations': [],
                'performance_improvement': 0.0,
                'memory_optimization': 0.0,
            }
            
            # Calculate current load distribution
            gpu_loads = defaultdict(list)
            for allocation in self.model_allocations.values():
                gpu_loads[allocation.gpu_id].append(allocation)
            
            # Find overloaded and underloaded GPUs
            avg_load = len(self.model_allocations) / self.gpu_count
            overloaded_gpus = []
            underloaded_gpus = []
            
            for gpu_id in range(self.gpu_count):
                load = len(gpu_loads[gpu_id])
                if load > avg_load * 1.5:
                    overloaded_gpus.append(gpu_id)
                elif load < avg_load * 0.5:
                    underloaded_gpus.append(gpu_id)
            
            # Migrate models from overloaded to underloaded GPUs
            for overloaded_gpu in overloaded_gpus:
                for underloaded_gpu in underloaded_gpus:
                    if not gpu_loads[overloaded_gpu]:
                        break
                    
                    # Find best model to migrate
                    best_model = None
                    best_score = float('-inf')
                    
                    for allocation in gpu_loads[overloaded_gpu]:
                        if self._can_migrate_model(allocation, underloaded_gpu):
                            score = self._calculate_migration_score(allocation, overloaded_gpu, underloaded_gpu)
                            if score > best_score:
                                best_score = score
                                best_model = allocation
                    
                    if best_model:
                        # Perform migration
                        migration_result = self._migrate_model(best_model, underloaded_gpu)
                        if migration_result['success']:
                            balance_result['migrations'].append(migration_result)
                            gpu_loads[overloaded_gpu].remove(best_model)
                            gpu_loads[underloaded_gpu].append(best_model)
            
            # Calculate improvements
            balance_result['performance_improvement'] = self._calculate_performance_improvement()
            balance_result['memory_optimization'] = self._calculate_memory_optimization()
            
            return balance_result
    
    def _can_migrate_model(self, allocation: ModelAllocation, target_gpu: int) -> bool:
        """Check if model can be migrated to target GPU"""
        target_gpu_info = self.gpus[target_gpu]
        return target_gpu_info.available_memory_gb >= allocation.memory_gb
    
    def _calculate_migration_score(self, allocation: ModelAllocation, source_gpu: int, target_gpu: int) -> float:
        """Calculate score for model migration"""
        source_gpu_info = self.gpus[source_gpu]
        target_gpu_info = self.gpus[target_gpu]
        
        # Prefer migrations that reduce load imbalance
        source_load = len([a for a in self.model_allocations.values() if a.gpu_id == source_gpu])
        target_load = len([a for a in self.model_allocations.values() if a.gpu_id == target_gpu])
        
        load_improvement = source_load - target_load
        
        # Consider memory availability
        memory_score = target_gpu_info.available_memory_gb / self.memory_per_gpu
        
        # Consider GPU utilization
        utilization_score = 1 - (target_gpu_info.utilization_percent / 100)
        
        return load_improvement * 0.6 + memory_score * 0.3 + utilization_score * 0.1
    
    def _migrate_model(self, allocation: ModelAllocation, target_gpu: int) -> Dict[str, Any]:
        """Migrate model to target GPU"""
        try:
            source_gpu = allocation.gpu_id
            
            # Update GPU memory
            source_gpu_info = self.gpus[source_gpu]
            target_gpu_info = self.gpus[target_gpu]
            
            source_gpu_info.available_memory_gb += allocation.memory_gb
            target_gpu_info.available_memory_gb -= allocation.memory_gb
            
            # Update allocation
            allocation.gpu_id = target_gpu
            allocation.last_used = time.time()
            
            logger.info(f"Migrated model {allocation.model_id} from GPU {source_gpu} to GPU {target_gpu}")
            
            return {
                'success': True,
                'model_id': allocation.model_id,
                'source_gpu': source_gpu,
                'target_gpu': target_gpu,
                'memory_gb': allocation.memory_gb,
            }
            
        except Exception as e:
            logger.error(f"Model migration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_id': allocation.model_id,
            }
    
    def _calculate_performance_improvement(self) -> float:
        """Calculate overall performance improvement from load balancing"""
        # Simulate performance improvement based on load distribution
        gpu_loads = defaultdict(int)
        for allocation in self.model_allocations.values():
            gpu_loads[allocation.gpu_id] += 1
        
        if not gpu_loads:
            return 0.0
        
        avg_load = sum(gpu_loads.values()) / len(gpu_loads)
        variance = sum((load - avg_load) ** 2 for load in gpu_loads.values()) / len(gpu_loads)
        
        # Convert variance to improvement percentage
        improvement = min(variance * 10, 25.0)  # Cap at 25% improvement
        return improvement
    
    def _calculate_memory_optimization(self) -> float:
        """Calculate memory optimization percentage"""
        total_allocated = sum(alloc.memory_gb for alloc in self.model_allocations.values())
        total_available = self.total_memory_gb
        
        utilization = total_allocated / total_available
        optimization = (1 - utilization) * 100  # Higher optimization for lower utilization
        
        return max(optimization, 0.0)
    
    def get_gpu_stats(self) -> Dict[str, Any]:
        """Get comprehensive GPU statistics"""
        
        with self._lock:
            stats = {
                'gpus': {},
                'model_allocations': {},
                'performance_metrics': {},
                'load_balancing': {},
            }
            
            # GPU statistics
            for gpu_id, gpu in self.gpus.items():
                stats['gpus'][gpu_id] = {
                    'total_memory_gb': gpu.total_memory_gb,
                    'available_memory_gb': gpu.available_memory_gb,
                    'utilization_percent': gpu.utilization_percent,
                    'temperature_celsius': gpu.temperature_celsius,
                    'power_watts': gpu.power_watts,
                    'state': gpu.state.value,
                    'memory_bandwidth_gbps': gpu.memory_bandwidth_gbps,
                    'fp16_tflops': gpu.fp16_tflops,
                    'fp8_tflops': gpu.fp8_tflops,
                }
            
            # Model allocation statistics
            for model_id, allocation in self.model_allocations.items():
                stats['model_allocations'][model_id] = {
                    'model_type': allocation.model_type.value,
                    'gpu_id': allocation.gpu_id,
                    'memory_gb': allocation.memory_gb,
                    'batch_size': allocation.batch_size,
                    'precision': allocation.precision,
                    'performance_score': allocation.performance_score,
                    'created_at': allocation.created_at,
                    'last_used': allocation.last_used,
                }
            
            # Performance metrics
            for gpu_id in range(self.gpu_count):
                performance_values = list(self.performance_metrics[gpu_id])
                memory_values = list(self.memory_usage[gpu_id])
                temperature_values = list(self.temperature_history[gpu_id])
                
                stats['performance_metrics'][gpu_id] = {
                    'avg_performance': sum(performance_values) / len(performance_values) if performance_values else 0,
                    'avg_memory_usage': sum(memory_values) / len(memory_values) if memory_values else 0,
                    'avg_temperature': sum(temperature_values) / len(temperature_values) if temperature_values else 0,
                    'samples': len(performance_values),
                }
            
            # Load balancing statistics
            gpu_loads = defaultdict(int)
            for allocation in self.model_allocations.values():
                gpu_loads[allocation.gpu_id] += 1
            
            stats['load_balancing'] = {
                'gpu_loads': dict(gpu_loads),
                'total_models': len(self.model_allocations),
                'avg_load_per_gpu': len(self.model_allocations) / self.gpu_count if self.gpu_count > 0 else 0,
                'load_variance': np.var(list(gpu_loads.values())) if gpu_loads else 0,
            }
            
            return stats
    
    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        def monitoring_loop():
            while True:
                try:
                    # Update GPU metrics
                    self._update_gpu_metrics()
                    
                    # Log GPU statistics periodically
                    if int(time.time()) % 30 == 0:  # Every 30 seconds
                        stats = self.get_gpu_stats()
                        logger.info(f"GPU stats: {stats['gpus']}")
                    
                    time.sleep(self.config['monitoring_interval'])
                    
                except Exception as e:
                    logger.error(f"GPU monitoring error: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    def _update_gpu_metrics(self):
        """Update GPU performance metrics"""
        try:
            for gpu_id in range(self.gpu_count):
                gpu = self.gpus[gpu_id]
                
                # Simulate performance metrics
                base_performance = 100.0
                utilization_factor = gpu.utilization_percent / 100
                temperature_factor = 1 - (gpu.temperature_celsius / self.config['temperature_threshold'])
                
                current_performance = base_performance * utilization_factor * temperature_factor
                self.performance_metrics[gpu_id].append(current_performance)
                
                # Update memory usage
                memory_usage = (gpu.total_memory_gb - gpu.available_memory_gb) / gpu.total_memory_gb * 100
                self.memory_usage[gpu_id].append(memory_usage)
                
                # Update temperature
                self.temperature_history[gpu_id].append(gpu.temperature_celsius)
                
                # Update GPU state based on conditions
                if gpu.temperature_celsius > self.config['temperature_threshold']:
                    gpu.state = GPUState.ERROR
                elif gpu.available_memory_gb < 1.0:
                    gpu.state = GPUState.MEMORY_FULL
                elif len([a for a in self.model_allocations.values() if a.gpu_id == gpu_id]) > 0:
                    gpu.state = GPUState.COMPUTING
                else:
                    gpu.state = GPUState.IDLE
                
        except Exception as e:
            logger.error(f"GPU metrics update failed: {e}")
    
    def deallocate_model(self, model_id: str) -> bool:
        """Deallocate model from GPU"""
        
        try:
            with self._lock:
                if model_id not in self.model_allocations:
                    logger.warning(f"Model {model_id} not found")
                    return False
                
                allocation = self.model_allocations[model_id]
                gpu = self.gpus[allocation.gpu_id]
                
                # Free GPU memory
                gpu.available_memory_gb += allocation.memory_gb
                
                # Remove allocation
                del self.model_allocations[model_id]
                
                logger.info(f"Deallocated model {model_id} from GPU {allocation.gpu_id}")
                return True
                
        except Exception as e:
            logger.error(f"Model deallocation failed: {e}")
            return False
    
    def get_total_allocated_memory(self) -> float:
        """Get total allocated GPU memory"""
        return sum(alloc.memory_gb for alloc in self.model_allocations.values())
    
    def get_gpu_utilization(self) -> float:
        """Get overall GPU utilization percentage"""
        total_allocated = self.get_total_allocated_memory()
        return (total_allocated / self.total_memory_gb) * 100


class GPUManager:
    """Individual GPU manager"""
    
    def __init__(self, gpu_id: int, gpu_info: GPUInfo, config: Dict[str, Any]):
        self.gpu_id = gpu_id
        self.gpu_info = gpu_info
        self.config = config
        self.allocations: List[ModelAllocation] = []
    
    def get_load(self) -> float:
        """Get current GPU load"""
        return len(self.allocations) / 10.0  # Normalize to 0-1 range
    
    def can_allocate(self, memory_gb: float) -> bool:
        """Check if GPU can allocate memory"""
        return self.gpu_info.available_memory_gb >= memory_gb
    
    def allocate_memory(self, memory_gb: float) -> bool:
        """Allocate memory on GPU"""
        if not self.can_allocate(memory_gb):
            return False
        
        self.gpu_info.available_memory_gb -= memory_gb
        return True
    
    def free_memory(self, memory_gb: float):
        """Free memory on GPU"""
        self.gpu_info.available_memory_gb += memory_gb 