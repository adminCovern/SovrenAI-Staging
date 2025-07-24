#!/usr/bin/env python3
"""
Test Voice System Startup on Ubuntu Server
Quick test to verify Voice System starts properly
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Set environment variables for server
os.environ['SOVREN_ENV'] = 'production'
os.environ['SOVREN_SECURITY_KEY'] = 'aa9628c23683705c6c1eee9771bb3224f438333e925df0c5df2e88f0699603fd'
os.environ['DATABASE_URL'] = 'postgresql://sovren:password@localhost/sovren_voice'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['SOVREN_LOG_LEVEL'] = 'INFO'
os.environ['SOVREN_HOST'] = '0.0.0.0'
os.environ['SOVREN_PORT'] = '8000'

def test_voice_system():
    """Test Voice System startup"""
    print("🚀 Testing Voice System on Ubuntu Server...")
    start_time = time.time()
    
    try:
        # Import and test
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from voice.voice_system import VoiceSystem, VoiceSystemConfig
        
        print("✅ Imports successful")
        
        # Create system
        config = VoiceSystemConfig.from_env()
        system = VoiceSystem(config)
        
        print("✅ System created")
        
        # Test startup
        async def start_system():
            await system.start()
            print("✅ Voice System started successfully")
            await system.shutdown()
        
        asyncio.run(start_system())
        
        elapsed = time.time() - start_time
        print(f"✅ Voice System test completed in {elapsed:.2f} seconds")
        return True
        
    except Exception as e:
        print(f"❌ Voice System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_voice_system()
    sys.exit(0 if success else 1) 