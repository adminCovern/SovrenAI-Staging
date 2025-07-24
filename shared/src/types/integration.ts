/**
 * Shared Integration Types
 * 
 * These types define the structure of integration data that is shared
 * between the frontend and backend applications.
 */

export interface Integration {
  id: string
  type: IntegrationType
  provider: string
  status: IntegrationStatus
  configuration: IntegrationConfig
  lastSync: Date
  errorCount: number
  quantumSignature: string
}

export type IntegrationType =
  | 'email'
  | 'calendar'
  | 'crm'
  | 'voice'
  | 'document'
  | 'analytics'
  | 'communication'

export type IntegrationStatus =
  | 'connected'
  | 'disconnected'
  | 'error'
  | 'syncing'
  | 'maintenance'

export interface IntegrationConfig {
  endpoint: string
  credentials: Record<string, any>
  settings: Record<string, any>
  webhooks: WebhookConfig[]
}

export interface WebhookConfig {
  url: string
  events: string[]
  secret: string
  isActive: boolean
}

export interface IntegrationEvent {
  id: string
  integrationId: string
  type: string
  data: any
  timestamp: Date
  processed: boolean
}

export interface SyncResult {
  success: boolean
  recordsProcessed: number
  errors: string[]
  duration: number
  timestamp: Date
} 