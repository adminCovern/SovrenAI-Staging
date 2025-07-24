/**
 * Shared Constants
 * 
 * This module contains constants that are shared between
 * frontend and backend applications.
 */

// System constants
export const SYSTEM_NAME = 'Sovren AI'
export const SYSTEM_VERSION = '1.0.0'
export const API_VERSION = 'v1'

// Executive roles
export const EXECUTIVE_ROLES = [
  'CEO',
  'CTO',
  'CFO',
  'COO',
  'CMO',
  'CHRO',
  'CLO',
  'CIO'
] as const

// Activity types
export const ACTIVITY_TYPES = [
  'idle',
  'email_composition',
  'calendar_scheduling',
  'crm_analysis',
  'voice_call',
  'decision_making',
  'approval_process',
  'system_monitoring'
] as const

// Integration types
export const INTEGRATION_TYPES = [
  'email',
  'calendar',
  'crm',
  'voice',
  'document',
  'analytics',
  'communication'
] as const

// Performance thresholds
export const PERFORMANCE_THRESHOLDS = {
  CPU_WARNING: 70,
  CPU_CRITICAL: 90,
  MEMORY_WARNING: 80,
  MEMORY_CRITICAL: 95,
  RESPONSE_TIME_WARNING: 1000,
  RESPONSE_TIME_CRITICAL: 5000,
  ERROR_RATE_WARNING: 5,
  ERROR_RATE_CRITICAL: 10
} as const

// WebSocket message types
export const WEBSOCKET_MESSAGE_TYPES = {
  EXECUTIVE_UPDATE: 'executive_update',
  ACTIVITY_EVENT: 'activity_event',
  PERFORMANCE_UPDATE: 'performance_update',
  APPROVAL_REQUEST: 'approval_request',
  RAFT_UPDATE: 'raft_update',
  HEARTBEAT: 'heartbeat',
  ERROR: 'error'
} as const

// RAFT consensus constants
export const RAFT_CONSTANTS = {
  ELECTION_TIMEOUT_MIN: 150,
  ELECTION_TIMEOUT_MAX: 300,
  HEARTBEAT_INTERVAL: 50,
  LEADER_LEASE_TIMEOUT: 100
} as const

// Security constants
export const SECURITY_CONSTANTS = {
  QUANTUM_SIGNATURE_ALGORITHM: 'SHA-512',
  ENCRYPTION_ALGORITHM: 'AES-256-GCM',
  TOKEN_LENGTH: 32,
  SALT_LENGTH: 16
} as const

// API endpoints
export const API_ENDPOINTS = {
  EXECUTIVES: '/api/executives',
  ACTIVITIES: '/api/activities',
  APPROVALS: '/api/approvals',
  PERFORMANCE: '/api/performance',
  RAFT: '/api/raft',
  INTEGRATIONS: '/api/integrations'
} as const

// Default configuration
export const DEFAULT_CONFIG = {
  WEBSOCKET_URL: 'ws://localhost:3001',
  API_BASE_URL: 'http://localhost:3000',
  FRONTEND_PORT: 3000,
  BACKEND_PORT: 3001,
  DATABASE_URL: 'postgresql://localhost:5432/sovren_ai'
} as const 