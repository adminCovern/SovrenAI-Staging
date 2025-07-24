#!/usr/bin/env python3
"""
Test script for consciousness engine fix
"""

import sys
import os
import time

def test_consciousness_engine():
    """Test the consciousness engine startup"""
    print("Testing consciousness engine startup...")
    
    try:
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import the consciousness engine
        from core.consciousness.consciousness_engine import BayesianConsciousnessEngine
        
        print("✅ Consciousness engine imported successfully")
        
        # Test initialization
        print("Initializing consciousness engine...")
        engine = BayesianConsciousnessEngine()
        
        print("✅ Consciousness engine initialized successfully")
        
        # Test basic functionality
        status = engine.get_system_status()
        print(f"✅ System status: {status['state']}")
        
        print("✅ All tests passed! Consciousness engine is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_consciousness_engine()
    sys.exit(0 if success else 1) 