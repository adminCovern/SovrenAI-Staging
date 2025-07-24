#!/usr/bin/env python3
"""
Voice System Startup Diagnostics
Identifies what's causing the 90-second timeout
"""

import os
import sys
import time
import subprocess
import socket
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgresql():
    """Check PostgreSQL connectivity"""
    logger.info("🔍 Checking PostgreSQL connectivity...")
    try:
        # Test connection to PostgreSQL
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            database="sovren_voice",
            user="sovren",
            password="password",
            connect_timeout=5
        )
        conn.close()
        logger.info("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_redis():
    """Check Redis connectivity"""
    logger.info("🔍 Checking Redis connectivity...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
        r.ping()
        logger.info("✅ Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False

def check_models():
    """Check if required models exist"""
    logger.info("🔍 Checking model files...")
    
    whisper_path = Path('/data/sovren/models/whisper/ggml-large-v3.bin')
    tts_path = Path('/data/sovren/models/tts/')
    
    if whisper_path.exists():
        logger.info(f"✅ Whisper model found: {whisper_path}")
    else:
        logger.warning(f"⚠️  Whisper model not found: {whisper_path}")
    
    if tts_path.exists():
        logger.info(f"✅ TTS model directory found: {tts_path}")
    else:
        logger.warning(f"⚠️  TTS model directory not found: {tts_path}")
    
    return whisper_path.exists() and tts_path.exists()

def check_ports():
    """Check if required ports are available"""
    logger.info("🔍 Checking port availability...")
    
    ports_to_check = [8000, 6379, 5432]  # Voice, Redis, PostgreSQL
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                logger.info(f"✅ Port {port} is in use")
            else:
                logger.warning(f"⚠️  Port {port} is not in use")
        except Exception as e:
            logger.error(f"❌ Error checking port {port}: {e}")

def check_environment():
    """Check environment variables"""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = [
        'SOVREN_ENV',
        'SOVREN_SECURITY_KEY',
        'DATABASE_URL',
        'REDIS_URL'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"✅ {var} is set")
        else:
            logger.warning(f"⚠️  {var} is not set")

def test_voice_system_startup():
    """Test Voice System startup with timeout"""
    logger.info("🔍 Testing Voice System startup...")
    
    try:
        # Set environment variables if not present
        if not os.environ.get('DATABASE_URL'):
            os.environ['DATABASE_URL'] = 'postgresql://sovren:password@localhost/sovren_voice'
        
        if not os.environ.get('REDIS_URL'):
            os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
        
        # Import and test Voice System initialization
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from voice.voice_system import VoiceSystem, VoiceSystemConfig
        
        logger.info("✅ Voice System imports successful")
        
        # Test configuration loading
        config = VoiceSystemConfig.from_env()
        logger.info("✅ Voice System configuration loaded")
        
        # Test system initialization (without starting)
        system = VoiceSystem(config)
        logger.info("✅ Voice System initialization successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Voice System startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostics"""
    logger.info("🚀 Starting Voice System diagnostics...")
    
    print("\n" + "="*60)
    print("VOICE SYSTEM STARTUP DIAGNOSTICS")
    print("="*60)
    
    # Run all checks
    checks = [
        ("Environment Variables", check_environment),
        ("PostgreSQL", check_postgresql),
        ("Redis", check_redis),
        ("Model Files", check_models),
        ("Port Availability", check_ports),
        ("Voice System Startup", test_voice_system_startup)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            results[name] = check_func()
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if not results.get("PostgreSQL", False):
        print("• Install and start PostgreSQL server")
        print("• Create database 'sovren_voice' with user 'sovren'")
    
    if not results.get("Redis", False):
        print("• Install and start Redis server")
    
    if not results.get("Model Files", False):
        print("• Download required AI models to /data/sovren/models/")
    
    if not results.get("Voice System Startup", False):
        print("• Check Python dependencies and imports")
        print("• Verify all required packages are installed")

if __name__ == "__main__":
    main() 