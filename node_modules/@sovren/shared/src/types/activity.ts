/**
 * Shared Activity Types
 * 
 * These types define the structure of activity data that is shared
 * between the frontend and backend applications.
 */

export interface ActivityEvent {
  id: string
  executiveId: string
  type: ActivityType
  timestamp: Date
  data: any
  impact: ImpactLevel
  requiresApproval: boolean
  quantumSignature: string
  neuralPrediction?: NeuralPrediction
}

export interface ActivityType {
  id: string
  name: string
  category: ActivityCategory
  description: string
  estimatedDuration: number
  authorizationRequired: boolean
  priority: number
}

export type ActivityCategory =
  | 'communication'
  | 'decision_making'
  | 'system_management'
  | 'data_analysis'
  | 'approval_process'
  | 'integration_sync'
  | 'performance_monitoring'
  | 'security_audit'

export type ImpactLevel =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export interface NeuralPrediction {
  confidence: number
  predictedOutcome: string
  riskAssessment: number
  recommendedAction: string
  timestamp: Date
}

export interface ActivityStream {
  events: ActivityEvent[]
  totalCount: number
  filteredCount: number
  lastUpdate: Date
}

export interface ActivityFilter {
  executiveIds?: string[]
  types?: string[]
  categories?: ActivityCategory[]
  dateRange?: {
    start: Date
    end: Date
  }
  impactLevels?: ImpactLevel[]
  requiresApproval?: boolean
} 