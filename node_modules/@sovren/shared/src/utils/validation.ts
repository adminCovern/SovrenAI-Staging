/**
 * Shared Validation Utilities
 * 
 * This module provides type-safe validation utilities using Zod
 * that can be shared between frontend and backend applications.
 */

import { z } from 'zod'

// Executive validation schemas
export const ExecutiveSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  role: z.enum(['CEO', 'CTO', 'CFO', 'COO', 'CMO', 'CHRO', 'CLO', 'CIO']),
  currentActivity: z.enum([
    'idle',
    'email_composition',
    'calendar_scheduling',
    'crm_analysis',
    'voice_call',
    'decision_making',
    'approval_process',
    'system_monitoring'
  ]),
  authorizationLevel: z.number().min(0).max(10),
  isActive: z.boolean(),
  lastActive: z.date(),
  quantumSignature: z.string()
})

// Activity validation schemas
export const ActivityEventSchema = z.object({
  id: z.string().uuid(),
  executiveId: z.string().uuid(),
  type: z.string(),
  timestamp: z.date(),
  data: z.any(),
  impact: z.enum(['low', 'medium', 'high', 'critical']),
  requiresApproval: z.boolean(),
  quantumSignature: z.string()
})

// Authorization validation schemas
export const ApprovalRequestSchema = z.object({
  id: z.string().uuid(),
  action: z.object({
    id: z.string().uuid(),
    type: z.string(),
    description: z.string(),
    parameters: z.record(z.any()),
    authorizationLevel: z.number().min(0).max(10),
    quantumSignature: z.string()
  }),
  estimatedValue: z.number().min(0),
  riskLevel: z.enum(['low', 'medium', 'high', 'critical']),
  status: z.enum(['pending', 'approved', 'rejected', 'cancelled']),
  timestamp: z.date(),
  quantumSignature: z.string()
})

// Performance validation schemas
export const PerformanceMetricsSchema = z.object({
  cpu: z.number().min(0).max(100),
  memory: z.number().min(0).max(100),
  responseTime: z.number().min(0),
  throughput: z.number().min(0),
  errorRate: z.number().min(0).max(100),
  timestamp: z.date()
})

// Validation functions
export function validateExecutive(data: unknown) {
  return ExecutiveSchema.parse(data)
}

export function validateActivityEvent(data: unknown) {
  return ActivityEventSchema.parse(data)
}

export function validateApprovalRequest(data: unknown) {
  return ApprovalRequestSchema.parse(data)
}

export function validatePerformanceMetrics(data: unknown) {
  return PerformanceMetricsSchema.parse(data)
}

// Type guards
export function isExecutive(data: unknown): data is any {
  return ExecutiveSchema.safeParse(data).success
}

export function isActivityEvent(data: unknown): data is any {
  return ActivityEventSchema.safeParse(data).success
}

export function isApprovalRequest(data: unknown): data is any {
  return ApprovalRequestSchema.safeParse(data).success
}

export function isPerformanceMetrics(data: unknown): data is any {
  return PerformanceMetricsSchema.safeParse(data).success
} 