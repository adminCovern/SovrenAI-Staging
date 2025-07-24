/**
 * Shared Executive Types
 * 
 * These types define the structure of executive data that is shared
 * between the frontend and backend applications.
 */

export interface Executive {
  id: string
  name: string
  role: ExecutiveRole
  avatar: AvatarConfig
  currentActivity: ActivityType
  capabilities: Capability[]
  authorizationLevel: number
  performance: PerformanceMetrics
  location: Vector3
  isActive: boolean
  lastActive: Date
  quantumSignature: string
}

export interface ExecutiveState {
  executive: Executive
  isActive: boolean
  currentTask: Task | null
  location: Vector3
  animation: AnimationState
  integrationStates: IntegrationState[]
  lastUpdate: Date
}

export type ExecutiveRole =
  | 'CEO'
  | 'CTO'
  | 'CFO'
  | 'COO'
  | 'CMO'
  | 'CHRO'
  | 'CLO'
  | 'CIO'

export interface AvatarConfig {
  model: string
  texture: string
  animations: string[]
  scale: Vector3
  position: Vector3
  rotation: Vector3
}

export interface Vector3 {
  x: number
  y: number
  z: number
}

export interface AnimationState {
  current: string
  blendTime: number
  speed: number
  loop: boolean
}

export interface Task {
  id: string
  type: string
  description: string
  priority: number
  estimatedDuration: number
  startTime: Date
  endTime?: Date
  status: 'pending' | 'active' | 'completed' | 'failed'
}

export interface IntegrationState {
  type: 'email' | 'calendar' | 'crm' | 'voice'
  isConnected: boolean
  lastSync: Date
  error?: string
}

export interface Capability {
  id: string
  name: string
  description: string
  isEnabled: boolean
  authorizationRequired: boolean
}

export interface PerformanceMetrics {
  efficiency: number
  accuracy: number
  speed: number
  reliability: number
  lastUpdated: Date
}

export type ActivityType =
  | 'idle'
  | 'email_composition'
  | 'calendar_scheduling'
  | 'crm_analysis'
  | 'voice_call'
  | 'decision_making'
  | 'approval_process'
  | 'system_monitoring' 