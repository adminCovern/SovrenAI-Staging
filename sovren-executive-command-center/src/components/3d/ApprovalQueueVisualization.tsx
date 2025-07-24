'use client'

import React, { useRef, useEffect, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'
import { useAppSelector, useAppDispatch } from '../../hooks/useAppStore'
import { useCommandCenter } from '../../providers/CommandCenterProvider'
import type { ApprovalRequest } from '../../types'
import { useGesture } from '@use-gesture/react'
import { animated, useSpring } from '@react-spring/three'

interface ApprovalQueueVisualizationProps {
  position?: [number, number, number]
  rotation?: [number, number, number]
  scale?: number
  onApprove: (approvalId: string) => void
  onReject: (approvalId: string) => void
}

const ApprovalQueueVisualization: React.FC<ApprovalQueueVisualizationProps> = ({
  position = [0, 2, -3],
  rotation = [0, 0, 0],
  scale = 1,
  onApprove,
  onReject
}) => {
  const groupRef = useRef<THREE.Group>(null)
  const vortexRef = useRef<THREE.Group>(null)
  const { sceneManager } = useCommandCenter()
  const dispatch = useAppDispatch()

  // Get approvals from Redux store
  const approvals = useAppSelector((state: any) => state.approvals?.pendingApprovals || [])

  // Get particle effects manager (if available through public API)
  const particleEffectsManager = useMemo(() => {
    // Note: particleEffectsManager is private, so we'll handle effects differently
    return null
  }, [sceneManager])

  // Create vortex effect when approvals are present
  useEffect(() => {
    // Particle effects will be handled through the built-in vortex visualization
    // instead of accessing private particle effects manager
  }, [approvals.length, position])

  // Animation
  useFrame((state) => {
    if (!groupRef.current) return

    const time = state.clock.getElapsedTime()

    // Gentle floating animation
    groupRef.current.position.y = position[1] + Math.sin(time * 0.5) * 0.1

    // Subtle rotation
    groupRef.current.rotation.y = rotation[1] + Math.sin(time * 0.2) * 0.05

    // Animate vortex if present
    if (vortexRef.current && approvals.length > 0) {
      vortexRef.current.rotation.z += 0.01 * (approvals.length > 3 ? 2 : approvals.length > 1 ? 1.5 : 1)

      // Pulse based on urgency
      const pulseScale = 1 + Math.sin(time * 2) * 0.05
      vortexRef.current.scale.set(pulseScale, pulseScale, 1)
    }
  })

  // If no approvals, don't render anything
  if (approvals.length === 0) {
    return null
  }

  return (
    <group
      ref={groupRef}
      position={position}
      rotation={rotation}
      scale={[scale, scale, scale]}
    >
      {/* Vortex visualization */}
      <group ref={vortexRef}>
        {/* Outer ring */}
        <mesh>
          <ringGeometry args={[1.8, 2.0, 64]} />
          <meshBasicMaterial
            color={0xff4444}
            transparent
            opacity={0.6}
            side={THREE.DoubleSide}
          />
        </mesh>

        {/* Inner ring */}
        <mesh rotation={[0, 0, Math.PI / 4]}>
          <ringGeometry args={[1.6, 1.7, 64]} />
          <meshBasicMaterial
            color={0xff8866}
            transparent
            opacity={0.4}
            side={THREE.DoubleSide}
          />
        </mesh>

        {/* Center glow */}
        <mesh>
          <planeGeometry args={[1.5, 1.5]} />
          <meshBasicMaterial
            color={0xff2222}
            transparent
            opacity={0.2}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      </group>

      {/* Approval cards */}
      {approvals.map((approval: any, index: number) => (
        <ApprovalCard
          key={approval.id}
          approval={approval}
          index={index}
          totalApprovals={approvals.length}
          onApprove={() => onApprove(approval.id)}
          onReject={() => onReject(approval.id)}
        />
      ))}

      {/* Title */}
      <Html
        position={[0, 2.2, 0]}
        center
        distanceFactor={15}
      >
        <div style={{
          color: '#ff4444',
          fontSize: '16px',
          fontWeight: 'bold',
          textAlign: 'center',
          textShadow: '0 0 10px rgba(255, 68, 68, 0.7)',
          whiteSpace: 'nowrap'
        }}>
          PENDING APPROVALS
        </div>
      </Html>
    </group>
  )
}

interface ApprovalCardProps {
  approval: ApprovalRequest
  index: number
  totalApprovals: number
  onApprove: () => void
  onReject: () => void
}

const ApprovalCard: React.FC<ApprovalCardProps> = ({
  approval,
  index,
  totalApprovals,
  onApprove,
  onReject
}) => {
  const cardRef = useRef<THREE.Group>(null)

  // Calculate position in the vortex
  const angle = (index / totalApprovals) * Math.PI * 2
  const radius = 1.2
  const xPos = Math.cos(angle) * radius
  const yPos = Math.sin(angle) * radius

  // Animation
  useFrame((state) => {
    if (!cardRef.current) return

    const time = state.clock.getElapsedTime()

    // Rotate to face center
    cardRef.current.lookAt(0, 0, 0)

    // Orbit around center
    const orbitSpeed = 0.2 + (index * 0.05)
    const newAngle = angle + time * orbitSpeed
    cardRef.current.position.x = Math.cos(newAngle) * radius
    cardRef.current.position.y = Math.sin(newAngle) * radius

    // Pulse based on risk level
    const pulseIntensity = approval.riskLevel === 'critical' ? 0.15 :
      approval.riskLevel === 'high' ? 0.1 : 0.05
    const pulseScale = 1 + Math.sin(time * 2 + index) * pulseIntensity
    cardRef.current.scale.setScalar(pulseScale)
  })

  // Get color based on risk level
  const getCardColor = () => {
    switch (approval.riskLevel) {
      case 'critical': return '#ff2222'
      case 'high': return '#ff6622'
      case 'medium': return '#ffaa22'
      default: return '#4d7cff'
    }
  }

  // --- Swipe gesture logic ---
  const [{ x, opacity }, api] = useSpring(() => ({ x: 0, opacity: 1 }))
  const bind = useGesture({
    onDrag: ({ down, movement, velocity, direction, last }) => {
      // Robustly extract movement, direction, and velocity as numbers to resolve type issues
      const mx = Array.isArray(movement) && typeof movement[0] === 'number' ? movement[0] : 0;
      const dx = Array.isArray(direction) && typeof direction[0] === 'number' ? direction[0] : 0;
      // velocity may be a Vector2 or a number; ensure we extract the correct value
      let v = 0;
      if (typeof velocity === 'number') {
        v = velocity;
      } else if (Array.isArray(velocity) && typeof velocity[0] === 'number') {
        v = velocity[0];
      }
      api.start({ x: down ? mx : 0, opacity: 1 - Math.min(Math.abs(mx) / 200, 0.7) });
      if (last) {
        if (mx > 100 || (v > 1 && dx > 0)) {
          // Swipe right: approve
          api.start({ x: 300, opacity: 0, immediate: false });
          setTimeout(onApprove, 200);
        } else if (mx < -100 || (v > 1 && dx < 0)) {
          // Swipe left: reject
          api.start({ x: -300, opacity: 0, immediate: false });
          setTimeout(onReject, 200);
        } else {
          api.start({ x: 0, opacity: 1 });
        }
      }
    }
  }, { drag: { filterTaps: true } })
  // --- End swipe gesture logic ---

  // Extract numbers from spring values for position and opacity
  const animatedX = x.get()
  const animatedOpacity = opacity.get()

  return (
    <animated.group
      ref={cardRef}
      position={[xPos + animatedX / 100, yPos, 0]}
      scale={[0.8, 0.8, 0.8]}
      // Use Three.js event handler signature for onClick, onPointerDown, etc. if needed
      // Spread gesture bindings, but ensure correct event types for three-fiber
      {...(bind() as any)}
    >
      {/* Card background */}
      <mesh>
        <planeGeometry args={[2, 1.2]} />
        <meshPhysicalMaterial
          color={0x001133}
          transparent
          opacity={0.4}
          metalness={0.3}
          roughness={0.1}
          transmission={0.9}
          thickness={0.2}
          envMapIntensity={1.0}
          side={THREE.DoubleSide}
        />
      </mesh>
      {/* Card border */}
      <mesh position={[0, 0, 0.01]}>
        <planeGeometry args={[2.05, 1.25]} />
        <meshBasicMaterial
          color={new THREE.Color(getCardColor())}
          transparent
          opacity={0.6}
          wireframe={true}
        />
      </mesh>
      {/* Card content */}
      <Html
        position={[0, 0, 0.1]}
        center
        distanceFactor={10}
        transform
        style={{ opacity: animatedOpacity }}
      >
        <div style={{
          width: '200px',
          padding: '10px',
          backgroundColor: 'rgba(0, 10, 30, 0.8)',
          borderRadius: '5px',
          border: `1px solid ${getCardColor()}`,
          boxShadow: `0 0 15px ${getCardColor()}60`,
          color: '#ffffff',
          fontFamily: 'Arial, sans-serif',
          opacity: animatedOpacity
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 'bold',
            marginBottom: '5px',
            color: getCardColor(),
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>{approval.action.type.toUpperCase().replace('_', ' ')}</span>
            <span style={{
              backgroundColor: getCardColor(),
              color: 'white',
              padding: '2px 5px',
              borderRadius: '3px',
              fontSize: '10px'
            }}>
              {approval.riskLevel.toUpperCase()}
            </span>
          </div>

          <div style={{
            fontSize: '14px',
            fontWeight: 'bold',
            marginBottom: '5px'
          }}>
            {approval.action.description}
          </div>

          {approval.action.type === 'email_send' && approval.visualRepresentation.content.type === 'email_approval' && (
            <div style={{ fontSize: '11px', marginBottom: '10px' }}>
              <div style={{ marginBottom: '3px' }}>
                <strong>From:</strong> {approval.visualRepresentation.content.draft.from}
              </div>
              <div style={{ marginBottom: '3px' }}>
                <strong>To:</strong> {approval.visualRepresentation.content.draft.to.join(', ')}
              </div>
              <div style={{
                marginBottom: '5px',
                maxHeight: '60px',
                overflow: 'auto',
                padding: '5px',
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '3px',
                fontSize: '10px'
              }}>
                {approval.visualRepresentation.content.draft.body}
              </div>
            </div>
          )}

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '10px'
          }}>
            <button
              onClick={((e: any) => { e.stopPropagation(); onReject(); }) as any}
              style={{
                backgroundColor: '#ff4444',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                padding: '5px 10px',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 'bold'
              }}
            >
              REJECT
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onApprove();
              }}
              style={{
                backgroundColor: '#44ff44',
                color: 'black',
                border: 'none',
                borderRadius: '3px',
                padding: '5px 10px',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 'bold'
              }}
            >
              APPROVE
            </button>
          </div>
        </div>
      </Html>
    </animated.group>
  )
}

export default ApprovalQueueVisualization