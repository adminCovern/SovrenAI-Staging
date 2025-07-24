/**
 * Shared WebSocket Utilities
 * 
 * This module provides WebSocket utilities for real-time communication
 * between frontend and backend applications.
 */

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: Date
  id?: string
  quantumSignature?: string
}

export interface WebSocketConnection {
  id: string
  url: string
  status: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastMessage?: WebSocketMessage
  lastHeartbeat?: Date
  reconnectAttempts: number
}

export interface WebSocketConfig {
  url: string
  protocols?: string[]
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
  timeout: number
}

export interface WebSocketEvent {
  type: 'open' | 'message' | 'close' | 'error'
  data?: any
  timestamp: Date
}

/**
 * Create a WebSocket message with quantum signature
 */
export function createWebSocketMessage(
  type: string,
  payload: any,
  id?: string
): WebSocketMessage {
  const message: WebSocketMessage = {
    type,
    payload,
    timestamp: new Date(),
    id: id || generateMessageId()
  }

  return message
}

/**
 * Generate a unique message ID
 */
export function generateMessageId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Validate WebSocket message structure
 */
export function isValidWebSocketMessage(message: any): message is WebSocketMessage {
  return (
    typeof message === 'object' &&
    typeof message.type === 'string' &&
    message.payload !== undefined &&
    message.timestamp instanceof Date
  )
}

/**
 * Create a heartbeat message
 */
export function createHeartbeatMessage(): WebSocketMessage {
  return createWebSocketMessage('heartbeat', { timestamp: Date.now() })
}

/**
 * Check if a message is a heartbeat
 */
export function isHeartbeatMessage(message: WebSocketMessage): boolean {
  return message.type === 'heartbeat'
}

/**
 * Default WebSocket configuration
 */
export const DEFAULT_WEBSOCKET_CONFIG: WebSocketConfig = {
  url: 'ws://localhost:3001',
  reconnectInterval: 5000,
  maxReconnectAttempts: 10,
  heartbeatInterval: 30000,
  timeout: 10000
} 