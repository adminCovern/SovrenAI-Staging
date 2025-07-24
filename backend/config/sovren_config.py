"""
SOVREN AI - Master Configuration
Bare-metal deployment settings
"""

import os
from pathlib import Path

# Base paths
BASE_PATH = Path("/data/sovren")
LOG_PATH = BASE_PATH / "logs"
MODEL_PATH = BASE_PATH / "models"

# Hardware Configuration
HARDWARE = {
    "gpus": 8,  # B200 GPUs
    "gpu_memory": 192,  # GB per GPU
    "system_memory": 2300,  # GB total
    "cpu_cores": 288,  # Total threads
}

# Model Settings
MODELS = {
    "whisper": {
        "model_size": "large-v3",
        "device": "cuda",
        "compute_type": "float16",
        "batch_size": 16,
    },
    "xtts": {
        "model_path": str(MODEL_PATH / "xtts_v2"),
        "device": "cuda",
        "sample_rate": 24000,
    },
    "mixtral": {
        "model_name": "mixtral-8x7b",
        "tensor_parallel_size": 8,
        "max_batch_size": 50,
        "gpu_memory_utilization": 0.95,
    }
}

# Voice System
VOICE = {
    "vad_threshold": 0.5,
    "silence_duration": 0.8,
    "sample_rate": 16000,
    "chunk_length": 30,
    "overlap_length": 5,
}

# API Configuration
API = {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "cors_origins": ["*"],
    "max_request_size": 100 * 1024 * 1024,  # 100MB
}

# Skyetel Integration (ONLY permitted external API)
SKYETEL = {
    "api_endpoint": "https://api.skyetel.com/v1",
    "api_key": os.environ.get("SKYETEL_API_KEY", ""),
    "account_sid": os.environ.get("SKYETEL_ACCOUNT_SID", ""),
    "webhook_url": "https://your-domain.com/webhook/skyetel",
}

# Agent Battalion Configuration
AGENTS = {
    "STRIKE": {
        "priority": 1,
        "gpu_allocation": 2,
        "memory_limit": "400GB",
        "capabilities": ["rapid_response", "tactical_analysis", "threat_neutralization"]
    },
    "INTEL": {
        "priority": 2,
        "gpu_allocation": 1,
        "memory_limit": "300GB",
        "capabilities": ["data_analysis", "pattern_recognition", "predictive_modeling"]
    },
    "OPS": {
        "priority": 3,
        "gpu_allocation": 2,
        "memory_limit": "400GB",
        "capabilities": ["execution", "resource_management", "optimization"]
    },
    "SENTINEL": {
        "priority": 4,
        "gpu_allocation": 1,
        "memory_limit": "200GB",
        "capabilities": ["security", "monitoring", "threat_detection"]
    },
    "COMMAND": {
        "priority": 5,
        "gpu_allocation": 2,
        "memory_limit": "500GB",
        "capabilities": ["strategic_planning", "coordination", "decision_making"]
    }
}

# Shadow Board Advisors
SHADOW_BOARD = {
    "strategist": {
        "focus": "long_term_planning",
        "weight": 0.25
    },
    "ethicist": {
        "focus": "moral_implications",
        "weight": 0.20
    },
    "contrarian": {
        "focus": "alternative_perspectives",
        "weight": 0.20
    },
    "technologist": {
        "focus": "technical_feasibility",
        "weight": 0.20
    },
    "pragmatist": {
        "focus": "practical_implementation",
        "weight": 0.15
    }
}

# Time Machine Settings
TIME_MACHINE = {
    "max_checkpoints": 100,
    "checkpoint_interval": 300,  # seconds
    "state_compression": True,
    "quantum_branching": True,
}

# Security Configuration
SECURITY = {
    "encryption": "AES-256-GCM",
    "auth_timeout": 3600,  # seconds
    "max_attempts": 3,
    "lockout_duration": 900,  # seconds
    "audit_everything": True,
}

# Performance Targets
PERFORMANCE = {
    "asr_latency_ms": 150,
    "tts_latency_ms": 100,
    "llm_tokens_per_second": 11,  # 90ms per token
    "concurrent_sessions": 50,
    "uptime_target": 0.9999,  # 99.99%
}

# Operational Settings
OPERATIONS = {
    "auto_scaling": True,
    "health_check_interval": 30,
    "log_retention_days": 90,
    "backup_frequency": "daily",
    "autonomous_mode": True,
}