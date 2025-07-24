// Core Executive Types
export interface Executive {
    id: string
    name: string
    role: ExecutiveRole
    avatar: AvatarConfig
    currentActivity: ActivityType
    capabilities: Capability[]
    authorizationLevel: number
    performance: PerformanceMetrics
}

export interface ExecutiveState {
    executive: Executive
    isActive: boolean
    currentTask: Task | null
    location: Vector3
    animation: AnimationState
    integrationStates: IntegrationState[]
}

export type ExecutiveRole =
    | 'CEO'
    | 'CFO'
    | 'CTO'
    | 'CMO'
    | 'COO'
    | 'CHRO'
    | 'CLO'
    | 'CSO'

export type ActivityType =
    | 'idle'
    | 'email'
    | 'call'
    | 'meeting'
    | 'crm'
    | 'analysis'
    | 'approval'

// 3D and Animation Types
export interface Vector3 {
    x: number
    y: number
    z: number
}

export interface AvatarConfig {
    modelPath: string
    animations: AnimationClip[]
    scale: Vector3
    position: Vector3
}

export interface AnimationState {
    current: string
    isPlaying: boolean
    loop: boolean
    speed: number
}

export interface AnimationClip {
    name: string
    duration: number
    path: string
}

// Activity and Task Types
export interface Task {
    id: string
    type: ActivityType
    description: string
    priority: Priority
    estimatedDuration: number
    requiredCapabilities: Capability[]
}

export interface ActivityEvent {
    id: string
    executiveId: string
    type: ActivityType
    timestamp: Date
    data: any
    impact: ImpactLevel
    requiresApproval: boolean
}

export type Priority = 'low' | 'medium' | 'high' | 'critical'
export type ImpactLevel = 'minimal' | 'moderate' | 'significant' | 'major'

// Authorization Types
export interface ApprovalRequest {
    id: string
    action: ExecutiveAction
    executive: Executive
    estimatedValue: number
    riskLevel: RiskLevel
    context: ActionContext
    visualRepresentation: HolographicCard
}

export interface ExecutiveAction {
    id: string
    type: ActionType
    description: string
    value: number
    riskLevel: RiskLevel
    requiredApproval: boolean
}

export type ActionType =
    | 'email_send'
    | 'meeting_schedule'
    | 'deal_advance'
    | 'expense_approve'
    | 'contract_sign'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface ActionContext {
    relatedEntities: string[]
    businessImpact: string
    timeline: string
    stakeholders: string[]
}

// Integration Types
export interface IntegrationState {
    type: IntegrationType
    status: ConnectionStatus
    lastSync: Date
    errorCount: number
    latency: number
}

export type IntegrationType = 'email' | 'calendar' | 'crm' | 'voice'
export type ConnectionStatus = 'connected' | 'disconnected' | 'error' | 'syncing'

// Capability Types
export interface Capability {
    name: string
    level: CapabilityLevel
    description: string
}

export type CapabilityLevel = 'basic' | 'intermediate' | 'advanced' | 'expert'

// Performance Types
export interface PerformanceMetrics {
    fps: number
    targetFPS: number
    isPerformant: boolean
    memory: MemoryUsage
    timestamp: number
}

export interface MemoryUsage {
    used: number
    total: number
    limit: number
}

// Visual Types
export interface HolographicCard {
    id: string
    position: Vector3
    content: any
    glowIntensity: number
    opacity: number
}

// WebSocket Types
export interface WebSocketMessage {
    type: MessageType
    payload: any
    timestamp: Date
    executiveId?: string
}

export type MessageType =
    | 'executive_update'
    | 'activity_event'
    | 'approval_request'
    | 'integration_sync'
    | 'performance_update'
    | 'raft_request_vote'
    | 'raft_vote_response'
    | 'raft_append_entries'
    | 'raft_append_response'
    | 'heartbeat'
    | 'heartbeat_response' 