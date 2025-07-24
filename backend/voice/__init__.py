"""
SOVREN AI Voice System
Production-grade voice interface with ASR, TTS, and telephony integration
"""

__version__ = "1.0.0"
__author__ = "SOVREN AI"
__license__ = "Proprietary"

# Import main components
from voice.voice_system import (
    VoiceSystem,
    VoiceSession,
    VoiceSystemConfig,
    VoiceState,
    CallState,
    AudioQuality,
    VoiceSessionCreate,
    VoiceSessionResponse,
    PhoneCallRequest,
    VoiceSystemError,
    TranscriptionError,
    SynthesisError,
    TelephonyError,
    SessionNotFoundError,
)

# Import interfaces for extensibility
from voice.voice_system import (
    ASRInterface,
    TTSInterface,
    TelephonyInterface,
)

# Import implementations
from voice.voice_system import (
    WhisperASR,
    StyleTTS2,
    SkyetelIntegration,
)

# Convenience imports
from voice.logging_config import setup_logging

__all__ = [
    # Main system
    "VoiceSystem",
    "VoiceSystemConfig",
    "VoiceSession",
    # Enums
    "VoiceState",
    "CallState", 
    "AudioQuality",
    # API Models
    "VoiceSessionCreate",
    "VoiceSessionResponse",
    "PhoneCallRequest",
    # Exceptions
    "VoiceSystemError",
    "TranscriptionError",
    "SynthesisError",
    "TelephonyError",
    "SessionNotFoundError",
    # Interfaces
    "ASRInterface",
    "TTSInterface",
    "TelephonyInterface",
    # Implementations
    "WhisperASR",
    "StyleTTS2",
    "SkyetelIntegration",
    # Utilities
    "setup_logging",
]

## No package-level logging configuration needed here