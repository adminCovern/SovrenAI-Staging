#!/usr/bin/env python3
"""
SOVREN AI - NUMA-Aware Memory Allocation System
Optimized for B200 hardware with 6 NUMA nodes and 2.3TB RAM
"""

import os
import sys
import mmap
import ctypes
import threading
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import psutil
import subprocess

logger = logging.getLogger('NUMAAllocator')

class MemoryType(Enum):
    """Memory allocation types"""
    SHARED = "shared"
    LOCAL = "local"
    INTERLEAVED = "interleaved"
    CACHE_ALIGNED = "cache_aligned"

@dataclass
class NUMAZone:
    """NUMA zone configuration"""
    node_id: int
    total_memory_gb: float
    available_memory_gb: float
    cpu_cores: List[int]
    memory_bandwidth_gbps: float
    latency_ns: float
    allocations: Dict[str, 'MemoryAllocation'] = field(default_factory=dict)

@dataclass
class MemoryAllocation:
    """Memory allocation details"""
    allocation_id: str
    size_bytes: int
    numa_node: int
    memory_type: MemoryType
    alignment: int
    created_at: float
    access_pattern: str
    pinned: bool = False
    shared: bool = False

class NUMAAllocator:
    """NUMA-aware memory allocation system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.numa_nodes = self.config['numa_nodes']
        self.total_memory_gb = self.config['total_memory_gb']
        self.memory_per_node = self.total_memory_gb / self.numa_nodes
        
        # Initialize NUMA zones
        self.numa_zones: Dict[int, NUMAZone] = {}
        self._init_numa_zones()
        
        # Memory pools for different allocation types
        self.memory_pools = self._init_memory_pools()
        
        # Performance tracking
        self.allocation_stats = defaultdict(lambda: defaultdict(int))
        self.bandwidth_stats = defaultdict(lambda: deque(maxlen=1000))
        self.latency_stats = defaultdict(lambda: deque(maxlen=1000))
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Start monitoring thread
        self._start_monitoring_thread()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for B200 system"""
        return {
            'numa_nodes': 6,
            'total_memory_gb': 2355.0,  # 2.3TB
            'memory_per_node_gb': 392.5,
            'cache_line_size': 64,
            'huge_page_size': 2 * 1024 * 1024,  # 2MB
            'allocation_alignment': 64,
            'max_allocation_gb': 100,
            'monitoring_interval': 5,
            'bandwidth_threshold_gbps': 300,
            'latency_threshold_ns': 100,
        }
    
    def _init_numa_zones(self):
        """Initialize NUMA zones based on system topology"""
        try:
            # Get NUMA topology information
            numa_info = self._get_numa_topology()
            
            for node_id in range(self.numa_nodes):
                zone = NUMAZone(
                    node_id=node_id,
                    total_memory_gb=self.memory_per_node,
                    available_memory_gb=self.memory_per_node,
                    cpu_cores=numa_info.get(f'node_{node_id}_cores', []),
                    memory_bandwidth_gbps=400.0,  # DDR4-6400 theoretical
                    latency_ns=80.0,  # Typical DDR4 latency
                )
                self.numa_zones[node_id] = zone
                
            logger.info(f"Initialized {len(self.numa_zones)} NUMA zones")
            
        except Exception as e:
            logger.error(f"Failed to initialize NUMA zones: {e}")
            # Fallback to basic configuration
            for node_id in range(self.numa_nodes):
                zone = NUMAZone(
                    node_id=node_id,
                    total_memory_gb=self.memory_per_node,
                    available_memory_gb=self.memory_per_node,
                    cpu_cores=list(range(node_id * 48, (node_id + 1) * 48)),
                    memory_bandwidth_gbps=400.0,
                    latency_ns=80.0,
                )
                self.numa_zones[node_id] = zone
    
    def _get_numa_topology(self) -> Dict[str, Any]:
        """Get NUMA topology information from system"""
        try:
            # Read NUMA topology from /sys
            topology = {}
            
            for node_id in range(self.numa_nodes):
                node_path = f"/sys/devices/system/node/node{node_id}"
                if os.path.exists(node_path):
                    # Get CPU cores for this node
                    cpu_list_path = f"{node_path}/cpulist"
                    if os.path.exists(cpu_list_path):
                        with open(cpu_list_path, 'r') as f:
                            cpu_list = f.read().strip()
                            topology[f'node_{node_id}_cores'] = self._parse_cpu_list(cpu_list)
                    
                    # Get memory information
                    meminfo_path = f"{node_path}/meminfo"
                    if os.path.exists(meminfo_path):
                        with open(meminfo_path, 'r') as f:
                            meminfo = f.read()
                            total_mem = self._parse_meminfo(meminfo, 'MemTotal')
                            free_mem = self._parse_meminfo(meminfo, 'MemFree')
                            topology[f'node_{node_id}_total_mb'] = total_mem
                            topology[f'node_{node_id}_free_mb'] = free_mem
            
            return topology
            
        except Exception as e:
            logger.warning(f"Could not read NUMA topology: {e}")
            return {}
    
    def _parse_cpu_list(self, cpu_list: str) -> List[int]:
        """Parse CPU list string (e.g., '0-47,96-143')"""
        try:
            cores = []
            for part in cpu_list.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    cores.extend(range(start, end + 1))
                else:
                    cores.append(int(part))
            return cores
        except Exception:
            return []
    
    def _parse_meminfo(self, meminfo: str, key: str) -> int:
        """Parse memory info from /proc/meminfo format"""
        try:
            for line in meminfo.split('\n'):
                if line.startswith(key + ':'):
                    return int(line.split()[1])
            return 0
        except Exception:
            return 0
    
    def _init_memory_pools(self) -> Dict[MemoryType, Dict[int, Any]]:
        """Initialize memory pools for different allocation types"""
        pools = {}
        
        for memory_type in MemoryType:
            pools[memory_type] = {}
            for node_id in range(self.numa_nodes):
                pools[memory_type][node_id] = {
                    'allocated_bytes': 0,
                    'max_bytes': int(self.memory_per_node * 1024 * 1024 * 1024 * 0.8),  # 80% of node memory
                    'allocations': {},
                    'fragmentation': 0.0,
                }
        
        return pools
    
    def allocate_numa_aware(self, size_bytes: int, affinity_node: Optional[int] = None,
                          memory_type: MemoryType = MemoryType.LOCAL,
                          alignment: Optional[int] = None) -> Optional[MemoryAllocation]:
        """Allocate memory with NUMA awareness"""
        
        try:
            with self._lock:
                # Determine target NUMA node
                target_node = self._select_numa_node(size_bytes, affinity_node, memory_type)
                if target_node is None:
                    logger.error(f"Cannot allocate {size_bytes} bytes - no suitable NUMA node")
                    return None
                
                # Check if allocation is possible
                if not self._can_allocate(target_node, size_bytes, memory_type):
                    logger.error(f"Insufficient memory on NUMA node {target_node}")
                    return None
                
                # Create allocation
                allocation = self._create_allocation(size_bytes, target_node, memory_type, alignment)
                if not allocation:
                    return None
                
                # Update tracking
                self._update_allocation_tracking(allocation)
                
                logger.info(f"Allocated {size_bytes} bytes on NUMA node {target_node}")
                return allocation
                
        except Exception as e:
            logger.error(f"Memory allocation failed: {e}")
            return None
    
    def _select_numa_node(self, size_bytes: int, affinity_node: Optional[int],
                         memory_type: MemoryType) -> Optional[int]:
        """Select optimal NUMA node for allocation"""
        
        if memory_type == MemoryType.INTERLEAVED:
            # For interleaved allocations, distribute across nodes
            return self._select_interleaved_node(size_bytes)
        
        elif affinity_node is not None:
            # Use specified affinity node if possible
            if self._can_allocate(affinity_node, size_bytes, memory_type):
                return affinity_node
            else:
                logger.warning(f"Affinity node {affinity_node} cannot accommodate allocation")
        
        # Find best available node
        best_node = None
        best_score = float('-inf')
        
        for node_id, zone in self.numa_zones.items():
            if not self._can_allocate(node_id, size_bytes, memory_type):
                continue
            
            # Calculate node score based on available memory and bandwidth
            available_memory = zone.available_memory_gb
            bandwidth = zone.memory_bandwidth_gbps
            fragmentation = self.memory_pools[memory_type][node_id]['fragmentation']
            
            score = (available_memory * 0.6 + bandwidth * 0.3 - fragmentation * 0.1)
            
            if score > best_score:
                best_score = score
                best_node = node_id
        
        return best_node
    
    def _select_interleaved_node(self, size_bytes: int) -> Optional[int]:
        """Select node for interleaved allocation"""
        # For interleaved allocations, start with node 0
        # In a real implementation, this would distribute across multiple nodes
        for node_id in range(self.numa_nodes):
            if self._can_allocate(node_id, size_bytes, MemoryType.INTERLEAVED):
                return node_id
        return None
    
    def _can_allocate(self, node_id: int, size_bytes: int, memory_type: MemoryType) -> bool:
        """Check if allocation is possible on specified node"""
        pool = self.memory_pools[memory_type][node_id]
        zone = self.numa_zones[node_id]
        
        # Check against pool limits
        if pool['allocated_bytes'] + size_bytes > pool['max_bytes']:
            return False
        
        # Check against zone available memory
        if size_bytes > zone.available_memory_gb * 1024 * 1024 * 1024:
            return False
        
        return True
    
    def _create_allocation(self, size_bytes: int, node_id: int, memory_type: MemoryType,
                          alignment: Optional[int]) -> Optional[MemoryAllocation]:
        """Create memory allocation"""
        
        try:
            allocation_id = f"alloc_{int(time.time() * 1000000)}"
            
            # Determine alignment - ensure it's not None
            if alignment is None:
                alignment = self.config['allocation_alignment']
            
            # Ensure alignment is a valid integer
            if alignment is None:
                alignment = 64  # Default cache line size
            
            aligned_size = ((size_bytes + alignment - 1) // alignment) * alignment
            
            # Create allocation object
            allocation = MemoryAllocation(
                allocation_id=allocation_id,
                size_bytes=aligned_size,
                numa_node=node_id,
                memory_type=memory_type,
                alignment=alignment or self.config['allocation_alignment'],
                created_at=time.time(),
                access_pattern="unknown",
                pinned=False,
                shared=(memory_type == MemoryType.SHARED),
            )
            
            # Update pool tracking
            pool = self.memory_pools[memory_type][node_id]
            pool['allocations'][allocation_id] = allocation
            pool['allocated_bytes'] += aligned_size
            
            # Update zone tracking
            zone = self.numa_zones[node_id]
            zone.allocations[allocation_id] = allocation
            zone.available_memory_gb -= aligned_size / (1024 * 1024 * 1024)
            
            return allocation
            
        except Exception as e:
            logger.error(f"Failed to create allocation: {e}")
            return None
    
    def _update_allocation_tracking(self, allocation: MemoryAllocation):
        """Update allocation statistics and tracking"""
        node_id = allocation.numa_node
        memory_type = allocation.memory_type
        
        # Update allocation stats
        self.allocation_stats[node_id][memory_type.value] += 1
        self.allocation_stats[node_id]['total_bytes'] += allocation.size_bytes
        
        # Update bandwidth and latency tracking
        zone = self.numa_zones[node_id]
        self.bandwidth_stats[node_id].append(zone.memory_bandwidth_gbps)
        self.latency_stats[node_id].append(zone.latency_ns)
    
    def deallocate(self, allocation_id: str) -> bool:
        """Deallocate memory"""
        
        try:
            with self._lock:
                # Find allocation
                allocation = None
                node_id = None
                memory_type = None
                
                for nid, zone in self.numa_zones.items():
                    if allocation_id in zone.allocations:
                        allocation = zone.allocations[allocation_id]
                        node_id = nid
                        memory_type = allocation.memory_type
                        break
                
                if not allocation:
                    logger.warning(f"Allocation {allocation_id} not found")
                    return False
                
                # Update pool tracking
                if node_id is not None and memory_type is not None:
                    pool = self.memory_pools[memory_type][node_id]
                    pool['allocated_bytes'] -= allocation.size_bytes
                    del pool['allocations'][allocation_id]
                    
                    # Update zone tracking
                    zone = self.numa_zones[node_id]
                    zone.available_memory_gb += allocation.size_bytes / (1024 * 1024 * 1024)
                    del zone.allocations[allocation_id]
                    
                    # Update fragmentation
                    self._update_fragmentation(node_id, memory_type)
                
                logger.info(f"Deallocated {allocation.size_bytes} bytes from node {node_id}")
                return True
                
        except Exception as e:
            logger.error(f"Deallocation failed: {e}")
            return False
    
    def _update_fragmentation(self, node_id: int, memory_type: MemoryType):
        """Update fragmentation metric for memory pool"""
        pool = self.memory_pools[memory_type][node_id]
        
        if pool['allocated_bytes'] == 0:
            pool['fragmentation'] = 0.0
            return
        
        # Calculate fragmentation based on allocation sizes
        allocations = list(pool['allocations'].values())
        if len(allocations) < 2:
            pool['fragmentation'] = 0.0
            return
        
        sizes = [alloc.size_bytes for alloc in allocations]
        mean_size = sum(sizes) / len(sizes)
        variance = sum((size - mean_size) ** 2 for size in sizes) / len(sizes)
        
        # Normalize fragmentation score
        pool['fragmentation'] = min(variance / (mean_size ** 2), 1.0)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        
        with self._lock:
            stats = {
                'numa_zones': {},
                'memory_pools': {},
                'performance_metrics': {},
                'allocation_stats': dict(self.allocation_stats),
            }
            
            # NUMA zone statistics
            for node_id, zone in self.numa_zones.items():
                stats['numa_zones'][node_id] = {
                    'total_memory_gb': zone.total_memory_gb,
                    'available_memory_gb': zone.available_memory_gb,
                    'utilization_percent': (1 - zone.available_memory_gb / zone.total_memory_gb) * 100,
                    'allocations_count': len(zone.allocations),
                    'memory_bandwidth_gbps': zone.memory_bandwidth_gbps,
                    'latency_ns': zone.latency_ns,
                }
            
            # Memory pool statistics
            for memory_type in MemoryType:
                stats['memory_pools'][memory_type.value] = {}
                for node_id in range(self.numa_nodes):
                    pool = self.memory_pools[memory_type][node_id]
                    stats['memory_pools'][memory_type.value][node_id] = {
                        'allocated_bytes': pool['allocated_bytes'],
                        'max_bytes': pool['max_bytes'],
                        'utilization_percent': (pool['allocated_bytes'] / pool['max_bytes']) * 100,
                        'allocations_count': len(pool['allocations']),
                        'fragmentation': pool['fragmentation'],
                    }
            
            # Performance metrics
            for node_id in range(self.numa_nodes):
                bandwidth_values = list(self.bandwidth_stats[node_id])
                latency_values = list(self.latency_stats[node_id])
                
                stats['performance_metrics'][node_id] = {
                    'avg_bandwidth_gbps': sum(bandwidth_values) / len(bandwidth_values) if bandwidth_values else 0,
                    'avg_latency_ns': sum(latency_values) / len(latency_values) if latency_values else 0,
                    'bandwidth_samples': len(bandwidth_values),
                    'latency_samples': len(latency_values),
                }
            
            return stats
    
    def optimize_memory_layout(self) -> Dict[str, Any]:
        """Optimize memory layout for better performance"""
        
        with self._lock:
            optimizations = {
                'defragmentation': {},
                'bandwidth_optimization': {},
                'cache_alignment': {},
            }
            
            # Defragmentation analysis
            for node_id in range(self.numa_nodes):
                for memory_type in MemoryType:
                    pool = self.memory_pools[memory_type][node_id]
                    if pool['fragmentation'] > 0.3:  # High fragmentation threshold
                        optimizations['defragmentation'][f'node_{node_id}_{memory_type.value}'] = {
                            'fragmentation': pool['fragmentation'],
                            'recommendation': 'Consider defragmentation',
                            'impact': 'Medium',
                        }
            
            # Bandwidth optimization
            for node_id, zone in self.numa_zones.items():
                if zone.available_memory_gb < zone.total_memory_gb * 0.1:  # Less than 10% available
                    optimizations['bandwidth_optimization'][f'node_{node_id}'] = {
                        'available_memory_gb': zone.available_memory_gb,
                        'recommendation': 'Consider freeing memory or redistributing allocations',
                        'impact': 'High',
                    }
            
            # Cache alignment optimization
            for node_id in range(self.numa_nodes):
                misaligned_count = 0
                for memory_type in MemoryType:
                    pool = self.memory_pools[memory_type][node_id]
                    for allocation in pool['allocations'].values():
                        if allocation.alignment < self.config['cache_line_size']:
                            misaligned_count += 1
                
                if misaligned_count > 0:
                    optimizations['cache_alignment'][f'node_{node_id}'] = {
                        'misaligned_allocations': misaligned_count,
                        'recommendation': 'Align allocations to cache line size',
                        'impact': 'Low',
                    }
            
            return optimizations
    
    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        def monitoring_loop():
            while True:
                try:
                    # Update bandwidth and latency metrics
                    self._update_performance_metrics()
                    
                    # Log memory statistics periodically
                    if int(time.time()) % 60 == 0:  # Every minute
                        stats = self.get_memory_stats()
                        logger.info(f"Memory stats: {stats['numa_zones']}")
                    
                    time.sleep(self.config['monitoring_interval'])
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    def _update_performance_metrics(self):
        """Update performance metrics from system"""
        try:
            # In a real implementation, this would read from hardware counters
            # For now, using simulated values
            for node_id in range(self.numa_nodes):
                zone = self.numa_zones[node_id]
                
                # Simulate bandwidth variation
                base_bandwidth = 400.0  # GB/s
                utilization = 1 - (zone.available_memory_gb / zone.total_memory_gb)
                current_bandwidth = base_bandwidth * (1 - utilization * 0.3)
                
                self.bandwidth_stats[node_id].append(current_bandwidth)
                
                # Simulate latency variation
                base_latency = 80.0  # ns
                current_latency = base_latency * (1 + utilization * 0.2)
                
                self.latency_stats[node_id].append(current_latency)
                
        except Exception as e:
            logger.error(f"Performance metrics update failed: {e}")
    
    def get_allocation_info(self, allocation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific allocation"""
        
        with self._lock:
            for node_id, zone in self.numa_zones.items():
                if allocation_id in zone.allocations:
                    allocation = zone.allocations[allocation_id]
                    return {
                        'allocation_id': allocation.allocation_id,
                        'size_bytes': allocation.size_bytes,
                        'numa_node': allocation.numa_node,
                        'memory_type': allocation.memory_type.value,
                        'alignment': allocation.alignment,
                        'created_at': allocation.created_at,
                        'access_pattern': allocation.access_pattern,
                        'pinned': allocation.pinned,
                        'shared': allocation.shared,
                    }
        
        return None
    
    def get_total_allocated_memory(self) -> int:
        """Get total allocated memory across all nodes"""
        
        with self._lock:
            total_bytes = 0
            for memory_type in MemoryType:
                for node_id in range(self.numa_nodes):
                    pool = self.memory_pools[memory_type][node_id]
                    total_bytes += pool['allocated_bytes']
            
            return total_bytes
    
    def get_memory_utilization(self) -> float:
        """Get overall memory utilization percentage"""
        total_allocated = self.get_total_allocated_memory()
        total_available = self.total_memory_gb * 1024 * 1024 * 1024
        return (total_allocated / total_available) * 100 