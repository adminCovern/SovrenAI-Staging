#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys

def test_imports():
    """Test all required imports"""
    try:
        import numpy as np
        print("✓ numpy imported successfully")
        
        import torch
        print("✓ torch imported successfully")
        
        import torchaudio
        print("✓ torchaudio imported successfully")
        
        import soundfile as sf
        print("✓ soundfile imported successfully")
        
        import aiohttp
        print("✓ aiohttp imported successfully")
        
        import websockets
        print("✓ websockets imported successfully")
        
        import librosa
        print("✓ librosa imported successfully")
        
        import sounddevice as sd
        print("✓ sounddevice imported successfully")
        
        from scipy import signal
        print("✓ scipy imported successfully")
        
        from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, relationship, scoped_session
        from sqlalchemy.pool import QueuePool
        print("✓ sqlalchemy imported successfully")
        
        from pydantic import BaseModel, Field, validator
        print("✓ pydantic imported successfully")
        
        import aiofiles
        print("✓ aiofiles imported successfully")
        
        import aiodns
        print("✓ aiodns imported successfully")
        
        import redis.asyncio as redis
        print("✓ redis imported successfully")
        
        from prometheus_client import Counter, Histogram, Gauge, generate_latest
        print("✓ prometheus_client imported successfully")
        
        import sentry_sdk
        print("✓ sentry_sdk imported successfully")
        
        from cryptography.fernet import Fernet
        print("✓ cryptography imported successfully")
        
        import base64
        print("✓ base64 imported successfully")
        
        print("\n🎉 All imports successful! The voice system should work correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 