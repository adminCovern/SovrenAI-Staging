#!/usr/bin/env python3
"""
Test script to verify import fallbacks work correctly
"""

import sys
import os

# Add the parent directory to the path so we can import the shadow board system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all imports work correctly with fallbacks"""
    
    print("Testing import fallbacks...")
    
    try:
        from core.shadow_board.shadow_board_system import (
            ShadowBoardSystem, 
            ExecutivePersonalityEngine,
            ExecutiveRole,
            NUMPY_AVAILABLE,
            AIOHTTP_AVAILABLE,
            TORCH_AVAILABLE,
            TRANSFORMERS_AVAILABLE,
            SQLITE_AVAILABLE
        )
        
        print("✓ Successfully imported shadow board system")
        print(f"  - NumPy available: {NUMPY_AVAILABLE}")
        print(f"  - aiohttp available: {AIOHTTP_AVAILABLE}")
        print(f"  - PyTorch available: {TORCH_AVAILABLE}")
        print(f"  - Transformers available: {TRANSFORMERS_AVAILABLE}")
        print(f"  - SQLite3 available: {SQLITE_AVAILABLE}")
        
        # Test personality engine
        engine = ExecutivePersonalityEngine()
        personality = engine.generate_executive_personality(ExecutiveRole.CEO)
        print("✓ Successfully generated executive personality")
        
        # Test system initialization
        system = ShadowBoardSystem()
        print("✓ Successfully created shadow board system")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during import test: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 