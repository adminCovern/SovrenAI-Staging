#!/usr/bin/env python3
"""
Test Voice System Startup Step by Step
Identifies exactly what's causing the 90-second timeout
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test importing Voice System modules"""
    print("🔍 Testing imports...")
    start_time = time.time()
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from voice.voice_system import VoiceSystem, VoiceSystemConfig
        print(f"✅ Imports successful ({time.time() - start_time:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    start_time = time.time()
    
    try:
        from voice.voice_system import VoiceSystemConfig
        config = VoiceSystemConfig.from_env()
        print(f"✅ Configuration loaded ({time.time() - start_time:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("🔍 Testing database connection...")
    start_time = time.time()
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            database="sovren_voice",
            user="sovren",
            password="password",
            connect_timeout=10
        )
        conn.close()
        print(f"✅ Database connection successful ({time.time() - start_time:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    print("🔍 Testing Redis connection...")
    start_time = time.time()
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=10)
        r.ping()
        print(f"✅ Redis connection successful ({time.time() - start_time:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_model_loading():
    """Test model loading (this is likely the bottleneck)"""
    print("🔍 Testing model loading...")
    start_time = time.time()
    
    try:
        from voice.voice_system import WhisperASR, StyleTTS2, VoiceSystemConfig
        config = VoiceSystemConfig.from_env()
        
        # Test ASR model loading
        print("  Testing ASR model...")
        asr_start = time.time()
        asr = WhisperASR(config)
        print(f"  ✅ ASR model loaded ({time.time() - asr_start:.2f}s)")
        
        # Test TTS model loading
        print("  Testing TTS model...")
        tts_start = time.time()
        tts = StyleTTS2(config)
        print(f"  ✅ TTS model loaded ({time.time() - tts_start:.2f}s)")
        
        print(f"✅ All models loaded ({time.time() - start_time:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

async def test_voice_system_startup():
    """Test full Voice System startup"""
    print("🔍 Testing Voice System startup...")
    start_time = time.time()
    
    try:
        from voice.voice_system import VoiceSystem, VoiceSystemConfig
        config = VoiceSystemConfig.from_env()
        system = VoiceSystem(config)
        
        # Test startup with timeout
        await asyncio.wait_for(system.start(), timeout=120)
        print(f"✅ Voice System startup successful ({time.time() - start_time:.2f}s)")
        return True
    except asyncio.TimeoutError:
        print(f"❌ Voice System startup timed out after 120s")
        return False
    except Exception as e:
        print(f"❌ Voice System startup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Voice System Startup Components...")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Redis", test_redis),
        ("Model Loading", test_model_loading),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            results[name] = False
    
    # Test full startup
    print(f"\n--- Full Startup Test ---")
    try:
        results["Full Startup"] = asyncio.run(test_voice_system_startup())
    except Exception as e:
        print(f"Error in Full Startup: {e}")
        results["Full Startup"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if not results.get("Model Loading", False):
        print("• Model loading is the bottleneck - consider:")
        print("  - Using smaller models for faster startup")
        print("  - Loading models in background after startup")
        print("  - Increasing startup timeout")
    
    if not results.get("Full Startup", False):
        print("• Full startup failed - check individual component results above")

if __name__ == "__main__":
    main() 