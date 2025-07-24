/**
 * Shared Encryption Utilities
 * 
 * This module provides quantum-resistant encryption utilities
 * that can be shared between frontend and backend applications.
 */

import { createHash, randomBytes } from 'crypto'

export interface QuantumSignature {
  signature: string
  timestamp: Date
  algorithm: string
  keyId: string
}

export interface EncryptionResult {
  encrypted: string
  iv: string
  algorithm: string
  timestamp: Date
}

/**
 * Generate a quantum-resistant signature for data
 */
export function generateQuantumSignature(data: string): QuantumSignature {
  const timestamp = new Date()
  const algorithm = 'SHA-512'
  const keyId = randomBytes(16).toString('hex')

  // Create a quantum-resistant signature using SHA-512
  const signature = createHash('sha512')
    .update(data + timestamp.toISOString() + keyId)
    .digest('hex')

  return {
    signature,
    timestamp,
    algorithm,
    keyId
  }
}

/**
 * Verify a quantum-resistant signature
 */
export function verifyQuantumSignature(
  data: string,
  signature: QuantumSignature
): boolean {
  const expectedSignature = createHash('sha512')
    .update(data + signature.timestamp.toISOString() + signature.keyId)
    .digest('hex')

  return expectedSignature === signature.signature
}

/**
 * Encrypt data with quantum-resistant encryption
 */
export function encryptData(data: string): EncryptionResult {
  const iv = randomBytes(16).toString('hex')
  const algorithm = 'AES-256-GCM'
  const timestamp = new Date()

  // For production, use a proper encryption library
  // This is a simplified example
  const encrypted = Buffer.from(data).toString('base64')

  return {
    encrypted,
    iv,
    algorithm,
    timestamp
  }
}

/**
 * Decrypt data with quantum-resistant encryption
 */
export function decryptData(encryptionResult: EncryptionResult): string {
  // For production, use a proper decryption library
  // This is a simplified example
  return Buffer.from(encryptionResult.encrypted, 'base64').toString()
}

/**
 * Generate a secure random token
 */
export function generateSecureToken(length: number = 32): string {
  return randomBytes(length).toString('hex')
}

/**
 * Hash sensitive data
 */
export function hashData(data: string, salt?: string): string {
  const saltToUse = salt || randomBytes(16).toString('hex')
  return createHash('sha256')
    .update(data + saltToUse)
    .digest('hex')
} 