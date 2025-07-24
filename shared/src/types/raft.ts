/**
 * Shared RAFT Consensus Types
 * 
 * These types define the structure of RAFT consensus data that is shared
 * between the frontend and backend applications.
 */

export interface RaftNode {
  id: string
  address: string
  role: RaftRole
  term: number
  votedFor?: string
  log: RaftLogEntry[]
  commitIndex: number
  lastApplied: number
  nextIndex: Record<string, number>
  matchIndex: Record<string, number>
  lastHeartbeat: Date
}

export type RaftRole = 'follower' | 'candidate' | 'leader'

export interface RaftLogEntry {
  term: number
  index: number
  command: RaftCommand
  timestamp: Date
  quantumSignature: string
}

export interface RaftCommand {
  type: string
  data: any
  executiveId?: string
  requiresApproval: boolean
}

export interface RaftMessage {
  type: RaftMessageType
  term: number
  from: string
  to: string
  data: any
  timestamp: Date
}

export type RaftMessageType =
  | 'request_vote'
  | 'request_vote_response'
  | 'append_entries'
  | 'append_entries_response'
  | 'install_snapshot'
  | 'install_snapshot_response'

export interface RaftState {
  currentTerm: number
  votedFor?: string
  log: RaftLogEntry[]
  commitIndex: number
  lastApplied: number
  role: RaftRole
  leaderId?: string
  nodes: RaftNode[]
}

export interface RaftCluster {
  nodes: RaftNode[]
  leaderId?: string
  term: number
  health: ClusterHealth
  lastUpdate: Date
}

export interface ClusterHealth {
  healthy: boolean
  issues: string[]
  leaderElection: boolean
  replicationLag: number
} 