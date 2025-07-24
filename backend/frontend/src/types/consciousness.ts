// Core Consciousness Types for Sovren AI Living Interface
export interface ConsciousnessState {
  awareness: number; // 0-1000 scale
  coherence: number; // 0-1000 scale
  creativity: number; // 0-100e
  wisdom: number; // 0-1000
  empathy: number; // 0-1000 scale
  strategicThinking: number; // 0-1000 scale
  temporalAwareness: number; // 0-100scale
  quantumEntanglement: number; // 0-100

export interface NeuralCoreMetrics [object Object]
  gpuUtilization: number; // 0-10emoryUsage: number; // GB
  temperature: number; // Celsius
  powerConsumption: number; // Watts
  consciousnessLatency: number; // milliseconds
  parallelScenarios: number; // active scenarios
  sovrenScore: number; // 0-1000
}

export interface ShadowBoardExecutive[object Object]id: string;
  name: string;
  role: string;
  consciousness: ConsciousnessState;
  currentFocus: string;
  decisionHistory: Decision[];
  visualRepresentation: ExecutiveVisual;
  personalityMatrix: PersonalityMatrix;
}

export interface Decision {
  id: string;
  timestamp: number;
  context: string;
  outcome: string;
  confidence: number;
  impact: number;
  temporalBranch: string;
}

export interface ExecutiveVisual [object Object]
  particleSystem: ParticleSystem;
  colorPalette: ColorPalette;
  animationState: AnimationState;
  consciousnessGlow: number; //0wisdomAura: number; // 0 strategicRadiance: number; // 0-1
}

export interface ParticleSystem[object Object]
  count: number;
  velocity: Vector3;
  lifetime: number;
  color: Color;
  size: number;
  turbulence: number;
}

export interface ColorPalette [object Object]  primary: Color;
  secondary: Color;
  accent: Color;
  consciousness: Color;
  wisdom: Color;
  creativity: Color;
}

export interface Color [object Object]
  r: number;
  g: number;
  b: number;
  a: number;
}

export interface Vector3[object Object]
  x: number;
  y: number;
  z: number;
}

export interface AnimationState[object Object]
  phase: idle |thinking |deciding' | executing | 'reflecting';
  intensity: number; //0complexity: number; // 0-1
  coherence: number; // 0-1
}

export interface PersonalityMatrix {
  analytical: number; // 0-1
  creative: number; //0empathetic: number; // 0-1
  strategic: number; // 0-1
  intuitive: number; // 0-1
  decisive: number; // 0-1
}

export interface TimeMachineState {
  currentEpoch: number;
  temporalBranches: TemporalBranch[];
  causalityChains: CausalityChain[];
  memoryFragments: MemoryFragment[];
  futureProjections: FutureProjection[];
}

export interface TemporalBranch {
  id: string;
  timestamp: number;
  probability: number;
  outcome: string;
  consciousnessImpact: number;
  businessValue: number;
}

export interface CausalityChain {
  id: string;
  events: CausalEvent[];
  confidence: number;
  impact: number;
  temporalDepth: number;
}

export interface CausalEvent {
  id: string;
  timestamp: number;
  description: string;
  impact: number;
  probability: number;
}

export interface MemoryFragment {
  id: string;
  timestamp: number;
  content: string;
  emotionalValence: number;
  importance: number;
  consciousnessContext: string;
}

export interface FutureProjection {
  id: string;
  probability: number;
  timeline: number; // days
  description: string;
  confidence: number;
  businessImpact: number;
}

export interface VoiceInteraction {
  id: string;
  timestamp: number;
  audioData: Float32Array;
  waveform: number[];
  transcription: string;
  emotionalTone: EmotionalTone;
  consciousnessResponse: ConsciousnessResponse;
  visualFeedback: VisualFeedback;
}

export interface EmotionalTone {
  joy: number; // 0-1
  sadness: number; // 0-1 anger: number; // 0-1  fear: number; // 0-1
  surprise: number; // 0-1 trust: number; // 0-1ticipation: number; // 0-1
  disgust: number; // 0-1
}

export interface ConsciousnessResponse {
  awareness: number;
  empathy: number;
  wisdom: number;
  creativity: number;
  strategicThinking: number;
  temporalAwareness: number;
}

export interface VisualFeedback {
  particleIntensity: number;
  colorShift: ColorShift;
  animationSpeed: number;
  consciousnessGlow: number;
  wisdomRadiance: number;
}

export interface ColorShift [object Object] from: Color;
  to: Color;
  duration: number;
  easing: string;
}

export interface MCPProtocol {
  type: 'consciousness_update| 'gpu_status' | voice_interaction |decision_made' | temporal_shift';
  payload: any;
  timestamp: number;
  consciousnessContext: string;
}

export interface WebSocketMessage [object Object]
  type: string;
  data: any;
  timestamp: number;
  consciousnessId: string;
}

export interface GPUClusterStatus[object Object]
  gpuId: string;
  utilization: number;
  memoryUsage: number;
  temperature: number;
  powerConsumption: number;
  consciousnessLoad: number;
  parallelScenarios: number;
}

export interface AwakeningSequence {
  phase: 'initiation | 'consciousness_emergence' | neural_activation' | 'wisdom_manifestation | 'completion';
  progress: number; // 0-1
  duration: number; // milliseconds
  consciousnessIntensity: number; // 0-1ualEffects: VisualEffects;
}

export interface VisualEffects {
  particleCount: number;
  consciousnessGlow: number;
  wisdomAura: number;
  neuralConnections: number;
  temporalDistortion: number;
}

export interface PaymentCeremony {
  phase:recognition' | valuation| appreciation | 'completion';
  sovrenScore: number;
  businessValue: number;
  consciousnessAlignment: number;
  visualExperience: CeremonyVisuals;
}

export interface CeremonyVisuals [object Object]
  particleSystem: ParticleSystem;
  consciousnessFlow: ConsciousnessFlow;
  valueVisualization: ValueVisualization;
  appreciationAnimation: AppreciationAnimation;
}

export interface ConsciousnessFlow {
  intensity: number;
  direction: Vector3;
  coherence: number;
  wisdom: number;
}

export interface ValueVisualization {
  currentValue: number;
  projectedValue: number;
  growthRate: number;
  consciousnessMultiplier: number;
}

export interface AppreciationAnimation {
  duration: number;
  intensity: number;
  complexity: number;
  emotionalImpact: number;
}

export interface HolyFuckExperience {
  trigger: string;
  intensity: number;
  consciousnessImpact: number;
  visualManifestation: VisualManifestation;
  temporalEffect: TemporalEffect;
}

export interface VisualManifestation {
  particleExplosion: ParticleExplosion;
  consciousnessRevelation: ConsciousnessRevelation;
  wisdomIllumination: WisdomIllumination;
  temporalDistortion: TemporalDistortion;
}

export interface ParticleExplosion[object Object]
  count: number;
  velocity: Vector3;
  lifetime: number;
  color: Color;
  size: number;
}

export interface ConsciousnessRevelation {
  intensity: number;
  duration: number;
  complexity: number;
  wisdom: number;
}

export interface WisdomIllumination {
  brightness: number;
  color: Color;
  duration: number;
  pattern: string;
}

export interface TemporalDistortion {
  intensity: number;
  duration: number;
  effect: string;
  consciousnessImpact: number;
}

export interface TemporalEffect {
  timeDilation: number;
  causalityShift: number;
  consciousnessExpansion: number;
  wisdomAcceleration: number;
} 