/**
 * Shared Performance Types
 * 
 * These types define the structure of performance data that is shared
 * between the frontend and backend applications.
 */

export interface PerformanceMetrics {
  cpu: number
  memory: number
  network: NetworkMetrics
  storage: StorageMetrics
  responseTime: number
  throughput: number
  errorRate: number
  timestamp: Date
}

export interface NetworkMetrics {
  latency: number
  bandwidth: number
  packetLoss: number
  connections: number
}

export interface StorageMetrics {
  used: number
  available: number
  iops: number
  throughput: number
}

export interface PerformanceAlert {
  id: string
  type: AlertType
  severity: AlertSeverity
  message: string
  metrics: PerformanceMetrics
  timestamp: Date
  resolved: boolean
}

export type AlertType =
  | 'high_cpu'
  | 'high_memory'
  | 'high_latency'
  | 'high_error_rate'
  | 'low_throughput'
  | 'storage_full'
  | 'network_issue'

export type AlertSeverity =
  | 'info'
  | 'warning'
  | 'error'
  | 'critical'

export interface PerformanceThreshold {
  metric: string
  operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte'
  value: number
  duration: number
  action: string
} 