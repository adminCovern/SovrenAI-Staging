/**
 * Shared Authorization Types
 * 
 * These types define the structure of authorization and approval data
 * that is shared between the frontend and backend applications.
 */

import { Executive, Vector3 } from './executive'
import { NeuralPrediction } from './activity'

export interface ApprovalRequest {
  id: string
  action: ExecutiveAction
  executive: Executive
  estimatedValue: number
  riskLevel: RiskLevel
  context: ActionContext
  visualRepresentation: HolographicCard
  quantumSignature: string
  neuralPrediction?: NeuralPrediction
  timestamp: Date
  status: ApprovalStatus
}

export interface ExecutiveAction {
  id: string
  type: ActionType
  description: string
  parameters: Record<string, any>
  estimatedImpact: ImpactAssessment
  authorizationLevel: number
  quantumSignature: string
}

export type ActionType =
  | 'email_send'
  | 'calendar_schedule'
  | 'crm_update'
  | 'voice_call'
  | 'system_configuration'
  | 'data_export'
  | 'integration_connection'
  | 'performance_optimization'

export type RiskLevel =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export type ApprovalStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'cancelled'

export interface ActionContext {
  source: string
  target: string
  data: any
  metadata: Record<string, any>
  timestamp: Date
}

export interface HolographicCard {
  id: string
  title: string
  description: string
  visualData: any
  position: Vector3
  rotation: Vector3
  scale: Vector3
  animation: string
}

export interface ImpactAssessment {
  financial: number
  operational: number
  security: number
  compliance: number
  overall: number
}

export interface AuthorizationRule {
  id: string
  resource: string
  action: string
  roles: string[]
  conditions: AuthorizationCondition[]
  priority: number
  isActive: boolean
}

export interface AuthorizationCondition {
  field: string
  operator: 'equals' | 'not_equals' | 'greater_than' | 'less_than' | 'contains' | 'in'
  value: any
}

export interface AuthorizationResult {
  isAuthorized: boolean
  reason?: string
  requiredApproval?: boolean
  approvalLevel?: number
  quantumSignature: string
} 