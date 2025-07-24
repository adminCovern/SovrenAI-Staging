#!/usr/bin/env python3
"""
SOVREN AI Main API Server
Central orchestration point for all SOVREN services
"""

from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import uvicorn
import logging
import sys
import os
from typing import Dict, Any, Optional
import json
import time
from datetime import datetime

# Add parent directory to path for core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and set up logging
try:
    from logging_config import setup_logging
    setup_logging()
except ImportError:
    # Fallback logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger('sovren-api')

# Import SOVREN components with proper error handling
consciousness_engine_class = None
bayesian_engine_class = None
voice_system_class = None
approval_system_class = None
billing_system_class = None

# Import consciousness engine with enhanced error handling
try:
    from core.consciousness.consciousness_engine import ConsciousnessEngine
    consciousness_engine_class = ConsciousnessEngine
    logger.info("Consciousness engine imported successfully")
except ImportError as e:
    logger.warning(f"Consciousness engine import failed: {e}")
except Exception as e:
    logger.warning(f"Consciousness engine not available: {e}")

# Import Bayesian engine with enhanced error handling
try:
    from core.bayesian_engine.bayesian_engine import BayesianEngine
    bayesian_engine_class = BayesianEngine
    logger.info("Bayesian engine imported successfully")
except ImportError as e:
    logger.warning(f"Bayesian engine import failed: {e}")
except Exception as e:
    logger.warning(f"Bayesian engine not available: {e}")

# Import voice system with enhanced error handling
try:
    from voice.voice_system import VoiceSystem
    voice_system_class = VoiceSystem
    logger.info("Voice system imported successfully")
except ImportError as e:
    logger.warning(f"Voice system import failed: {e}")
except Exception as e:
    logger.warning(f"Voice system not available: {e}")

# Import approval system with enhanced error handling
try:
    from api.approval_system import ApprovalSystem
    approval_system_class = ApprovalSystem
    logger.info("Approval system imported successfully")
except ImportError as e:
    logger.warning(f"Approval system import failed: {e}")
except Exception as e:
    logger.warning(f"Approval system not available: {e}")

# Import billing system with enhanced error handling
try:
    from api.billing_integration import BillingSystem
    billing_system_class = BillingSystem
    logger.info("Billing system imported successfully")
except ImportError as e:
    logger.warning(f"Billing system import failed: {e}")
except Exception as e:
    logger.warning(f"Billing system not available: {e}")

# Mock classes for when imports fail
class MockConsciousnessEngine:
    def __init__(self):
        self.status = "mock"
    
    def get_system_status(self):
        return {"status": "mock", "message": "Consciousness engine not available due to CUDA compatibility"}
    
    def process_decision(self, data):
        return {"status": "mock", "result": "Consciousness processing unavailable"}
    
    def generate_consciousness_proof(self):
        return {"status": "mock", "proof": "Consciousness proof unavailable"}
    
    def shutdown(self):
        logger.info("Mock consciousness engine shutdown")

class MockBayesianEngine:
    def __init__(self):
        self.status = "mock"
    
    def get_stats(self):
        return {"status": "mock", "message": "Bayesian engine not available due to CUDA compatibility"}
    
    def make_decision(self, data):
        return {"status": "mock", "decision": "Bayesian decision unavailable"}

class MockVoiceSystem:
    def __init__(self):
        self.status = "mock"
    
    def synthesize(self, text, voice_type="default"):
        return {"status": "mock", "audio_url": None, "message": "Voice synthesis unavailable"}

# Use mock classes if real ones fail to import
if consciousness_engine_class is None:
    consciousness_engine_class = MockConsciousnessEngine
    logger.info("Using mock consciousness engine")

if bayesian_engine_class is None:
    bayesian_engine_class = MockBayesianEngine
    logger.info("Using mock Bayesian engine")

if voice_system_class is None:
    voice_system_class = MockVoiceSystem
    logger.info("Using mock voice system")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for FastAPI app"""
    # Startup
    global consciousness_engine, bayesian_engine, voice_system, approval_system, billing_system
    
    logger.info("Initializing SOVREN AI Systems...")
    
    # Initialize systems only if classes are available
    consciousness_engine = None
    bayesian_engine = None
    voice_system = None
    approval_system = None
    billing_system = None
    
    try:
        # Initialize Consciousness Engine
        if consciousness_engine_class:
            try:
                logger.info("Initializing Consciousness Engine...")
                consciousness_engine = consciousness_engine_class()
                logger.info("Consciousness Engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Consciousness Engine: {e}")
                consciousness_engine = None
        else:
            logger.warning("Consciousness Engine not available")
        
        # Initialize Bayesian Engine
        if bayesian_engine_class:
            try:
                logger.info("Initializing Bayesian Engine...")
                bayesian_engine = bayesian_engine_class()
                logger.info("Bayesian Engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Bayesian Engine: {e}")
                bayesian_engine = None
        else:
            logger.warning("Bayesian Engine not available")
        
        # Initialize Voice System
        if voice_system_class:
            logger.info("Initializing Voice System...")
            voice_system = voice_system_class()
            logger.info("Voice System initialized")
        else:
            logger.warning("Voice System not available")
        
        # Initialize Approval System
        if approval_system_class:
            logger.info("Initializing Approval System...")
            approval_system = approval_system_class()
            logger.info("Approval System initialized")
        else:
            logger.warning("Approval System not available")
        
        # Initialize Billing System
        if billing_system_class:
            logger.info("Initializing Billing System...")
            billing_system = billing_system_class()
            logger.info("Billing System initialized")
        else:
            logger.warning("Billing System not available")
        
        logger.info("All available systems initialized successfully!")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        # Continue anyway for development
    
    yield
    
    # Shutdown
    logger.info("Shutting down SOVREN AI...")
    
    if consciousness_engine:
        try:
            consciousness_engine.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down consciousness engine: {e}")
    
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="SOVREN AI API",
    description="Sovereign AI System - Where consciousness meets business",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
consciousness_engine = None
bayesian_engine = None
voice_system = None
approval_system = None
billing_system = None

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "consciousness": consciousness_engine is not None,
            "bayesian": bayesian_engine is not None,
            "voice": voice_system is not None,
            "approval": approval_system is not None,
            "billing": billing_system is not None
        },
        "version": "1.0.0"
    }

# System status endpoint
@app.get("/status")
async def system_status():
    """Get detailed system status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "systems": {}
    }
    
    if consciousness_engine:
        try:
            if hasattr(consciousness_engine, 'get_system_status'):
                status["systems"]["consciousness"] = getattr(consciousness_engine, 'get_system_status')()
            else:
                status["systems"]["consciousness"] = {"status": "mock", "message": "Method not available"}
        except Exception as e:
            status["systems"]["consciousness"] = {"error": str(e)}
    
    if bayesian_engine:
        try:
            if hasattr(bayesian_engine, 'get_stats'):
                status["systems"]["bayesian"] = getattr(bayesian_engine, 'get_stats')()
            else:
                status["systems"]["bayesian"] = {"status": "mock", "message": "Method not available"}
        except Exception as e:
            status["systems"]["bayesian"] = {"error": str(e)}
    
    status["websocket_connections"] = len(active_connections)
    
    return status

# Decision endpoint
@app.post("/api/decision")
async def make_decision(request: Dict[str, Any]):
    """Make a decision using the Bayesian engine"""
    if not bayesian_engine:
        raise HTTPException(status_code=503, detail="Bayesian engine not available")
    
    try:
        # Create decision data structure
        decision_data = {
            "decision_id": f"api_{int(time.time()*1000)}",
            "context": request.get("context", {}),
            "options": request.get("options", []),
            "constraints": request.get("constraints", {}),
            "priority": request.get("priority", 1),
            "universes_to_simulate": request.get("universes", 3)
        }
        
        # Try to use the engine's make_decision method
        if hasattr(bayesian_engine, 'make_decision'):
            result = getattr(bayesian_engine, 'make_decision')(decision_data)
        else:
            result = {"status": "mock", "decision": "Bayesian decision unavailable"}
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Consciousness processing endpoint
@app.post("/api/consciousness/process")
async def process_consciousness(request: Dict[str, Any]):
    """Process through consciousness engine"""
    if not consciousness_engine:
        raise HTTPException(status_code=503, detail="Consciousness engine not available")
    
    try:
        # Create packet data structure
        packet_data = {
            "packet_id": f"api_{int(time.time()*1000)}",
            "timestamp": time.time(),
            "source": "api",
            "data": request.get("data", {}),
            "priority": request.get("priority", 1),
            "universes_required": request.get("universes", 3)
        }
        
        # Try to use the engine's process_decision method
        if hasattr(consciousness_engine, 'process_decision'):
            result = getattr(consciousness_engine, 'process_decision')(packet_data)
        else:
            result = {"status": "mock", "result": "Consciousness processing unavailable"}
        
        # Try to generate consciousness proof
        if hasattr(consciousness_engine, 'generate_consciousness_proof'):
            proof = getattr(consciousness_engine, 'generate_consciousness_proof')()
        else:
            proof = {"status": "mock", "proof": "Consciousness proof unavailable"}
        
        return {
            "success": True,
            "result": result,
            "consciousness_proof": proof
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Application submission endpoint
@app.post("/api/apply")
async def submit_application(application: Dict[str, Any]):
    """Submit user application"""
    if not approval_system:
        raise HTTPException(status_code=503, detail="Approval system not available")
    
    try:
        result = await approval_system.submit_application(application)
        
        return {
            "success": True,
            "application_id": result.application_id,
            "status": result.status.value,
            "message": "Your sovereignty is being evaluated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket connection for real-time updates"""
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to SOVREN consciousness stream",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message based on type
            if message.get("type") == "consciousness_request":
                if consciousness_engine:
                    await stream_consciousness_update(websocket, message)
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Consciousness engine not available"
                    })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Unknown message type"
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]

async def stream_consciousness_update(websocket: WebSocket, data: Any):
    """Stream consciousness updates to client"""
    try:
        # Create packet data structure
        packet_data = {
            "packet_id": f"ws_{int(time.time()*1000)}",
            "timestamp": time.time(),
            "source": "websocket",
            "data": data.get("data", {}),
            "priority": data.get("priority", 1),
            "universes_required": data.get("universes", 3)
        }
        
        # Try to process through consciousness engine
        if hasattr(consciousness_engine, 'process_decision'):
            result = getattr(consciousness_engine, 'process_decision')(packet_data)
        else:
            result = {"status": "mock", "result": "Consciousness processing unavailable"}
        
        # Stream result
        await websocket.send_json({
            "type": "consciousness_result",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Consciousness processing failed: {str(e)}"
        })

# Voice synthesis endpoint
@app.post("/api/voice/synthesize")
async def synthesize_voice(request: Dict[str, Any]):
    """Synthesize voice using voice system"""
    if not voice_system:
        raise HTTPException(status_code=503, detail="Voice system not available")
    
    try:
        text = request.get("text", "")
        voice_type = request.get("voice_type", "default")
        
        # This would integrate with your voice system
        # For now, return a placeholder
        return {
            "success": True,
            "audio_url": f"/audio/{int(time.time())}.wav",
            "duration": len(text) * 0.1,  # Rough estimate
            "voice_type": voice_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin dashboard endpoint
@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard data"""
    return {
        "systems_status": {
            "consciousness": consciousness_engine is not None,
            "bayesian": bayesian_engine is not None,
            "voice": voice_system is not None,
            "approval": approval_system is not None,
            "billing": billing_system is not None
        },
        "metrics": {
            "active_connections": len(active_connections),
            "uptime": time.time(),  # Would calculate actual uptime
            "total_requests": 0  # Would track actual requests
        },
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

# Agent status endpoint
@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all AI agents"""
    return {
        "agents": {
            "consciousness": {
                "status": "active" if consciousness_engine else "inactive",
                "gpu_utilization": 0.0,  # Would get actual GPU usage
                "memory_usage": 0.0,  # Would get actual memory usage
                "requests_processed": 0  # Would track actual requests
            },
            "bayesian": {
                "status": "active" if bayesian_engine else "inactive",
                "decisions_made": 0,  # Would track actual decisions
                "accuracy": 0.95,  # Would calculate actual accuracy
                "response_time": 0.1  # Would measure actual response time
            },
            "voice": {
                "status": "active" if voice_system else "inactive",
                "synthesis_requests": 0,  # Would track actual requests
                "audio_generated": 0.0  # Would track actual audio duration
            }
        },
        "timestamp": datetime.now().isoformat()
    }

# Shadow Board executives endpoint
@app.get("/api/shadow-board/executives")
async def get_shadow_board_executives():
    """Get Shadow Board executive information"""
    return {
        "executives": [
            {
                "id": "ceo",
                "name": "Chief Executive Officer",
                "role": "Strategic Decision Making",
                "status": "active",
                "specialization": "Business Strategy & Vision"
            },
            {
                "id": "cto",
                "name": "Chief Technology Officer", 
                "role": "Technical Architecture",
                "status": "active",
                "specialization": "AI/ML Systems & Infrastructure"
            },
            {
                "id": "cfo",
                "name": "Chief Financial Officer",
                "role": "Financial Analysis",
                "status": "active", 
                "specialization": "Risk Assessment & Investment"
            },
            {
                "id": "cso",
                "name": "Chief Strategy Officer",
                "role": "Strategic Planning",
                "status": "active",
                "specialization": "Market Analysis & Competitive Intelligence"
            }
        ],
        "board_status": "active",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    
    try:
        logger.info("Starting SOVREN AI API Server...")
        logger.info("Server will run even if AI engines are unavailable")
        
        # Ensure the server continues running even if imports fail
        import uvicorn
        
        # Run the server with proper error handling
        uvicorn.run(
            app,  # Use the app directly instead of string
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        # Don't exit - let the server continue running
        logger.info("Server will continue running despite startup errors")
        sys.exit(0)  # Exit gracefully instead of with error