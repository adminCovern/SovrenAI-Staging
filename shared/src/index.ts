/**
 * Shared types and utilities for Sovren AI Frontend and Backend
 * 
 * This package contains common interfaces, types, and utilities that are used
 * by both the frontend and backend applications to ensure type safety and
 * consistency across the entire Sovren AI system.
 */

// Core types
export * from './types/executive'
export { ActivityType } from './types/activity'
export * from './types/authorization'
export * from './types/integration'
// export * from './types/performance' // PerformanceMetrics already exported from executive
export * from './types/raft'

// Utilities
export * from './utils/validation'
export * from './utils/encryption'
export * from './utils/websocket'

// Constants
export * from './constants' 