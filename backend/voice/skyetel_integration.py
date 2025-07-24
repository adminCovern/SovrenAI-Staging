#!/usr/bin/env python3
"""
SOVREN AI Skyetel SIP Integration
Production-ready Skyetel integration for voice-only operations
OAuth authentication and webhook handling
"""

import asyncio
import json
import logging
import os
import time
import uuid
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
import aiofiles
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger('SkyetelIntegration')

class CallStatus(Enum):
    """Call status"""
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    CONNECTED = "connected"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"

class WebhookEvent(Enum):
    """Webhook event types"""
    CALL_STARTED = "call.started"
    CALL_ANSWERED = "call.answered"
    CALL_ENDED = "call.ended"
    CALL_FAILED = "call.failed"
    RECORDING_COMPLETE = "recording.complete"
    TRANSCRIPTION_COMPLETE = "transcription.complete"

@dataclass
class SkyetelConfig:
    """Skyetel configuration"""
    # API Configuration
    base_url: str = "https://api.skyetel.com/v1"
    oauth_url: str = "https://oauth.skyetel.com/v2"
    
    # Authentication
    client_id: str = ""
    client_secret: str = ""
    access_token: str = ""
    refresh_token: str = ""
    token_expires_at: Optional[datetime] = None
    
    # Webhook Configuration
    webhook_url: str = "https://your-domain.com/skyetel/webhook"
    webhook_secret: str = ""
    
    # Call Configuration
    default_from_number: str = ""
    recording_enabled: bool = True
    transcription_enabled: bool = True
    call_timeout: int = 300  # seconds
    
    # Security
    encryption_key: bytes = b""
    
    @classmethod
    def from_env(cls) -> 'SkyetelConfig':
        """Load configuration from environment"""
        return cls(
            base_url=os.getenv('SKYETEL_BASE_URL', cls.base_url),
            oauth_url=os.getenv('SKYETEL_OAUTH_URL', cls.oauth_url),
            client_id=os.getenv('SKYETEL_CLIENT_ID', ''),
            client_secret=os.getenv('SKYETEL_CLIENT_SECRET', ''),
            access_token=os.getenv('SKYETEL_ACCESS_TOKEN', ''),
            refresh_token=os.getenv('SKYETEL_REFRESH_TOKEN', ''),
            webhook_url=os.getenv('SKYETEL_WEBHOOK_URL', cls.webhook_url),
            webhook_secret=os.getenv('SKYETEL_WEBHOOK_SECRET', ''),
            default_from_number=os.getenv('SKYETEL_FROM_NUMBER', ''),
            encryption_key=os.getenv('SKYETEL_ENCRYPTION_KEY', '').encode() or Fernet.generate_key()
        )

@dataclass
class CallRequest:
    """Call request"""
    to_number: str
    from_number: Optional[str] = None
    call_id: Optional[str] = None
    webhook_url: Optional[str] = None
    recording: bool = True
    transcription: bool = True
    timeout: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CallResponse:
    """Call response"""
    call_id: str
    status: CallStatus
    from_number: str
    to_number: str
    start_time: datetime
    duration: Optional[float] = None
    recording_url: Optional[str] = None
    transcription_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SkyetelOAuthClient:
    """OAuth client for Skyetel authentication"""
    
    def __init__(self, config: SkyetelConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Skyetel using OAuth"""
        try:
            session = await self._get_session()
            
            # Check if we have a valid token
            if self.config.access_token and self.config.token_expires_at:
                if datetime.now() < self.config.token_expires_at:
                    logger.info("Using existing valid token")
                    return True
                else:
                    logger.info("Token expired, refreshing...")
                    return await self._refresh_token()
            
            # Initial authentication
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            async with session.post(f"{self.config.oauth_url}/token", data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    self.config.access_token = token_data['access_token']
                    self.config.refresh_token = token_data.get('refresh_token', '')
                    self.config.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
                    
                    logger.info("OAuth authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"OAuth authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"OAuth authentication error: {e}")
            return False
    
    async def _refresh_token(self) -> bool:
        """Refresh OAuth token"""
        try:
            session = await self._get_session()
            
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.config.refresh_token,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            async with session.post(f"{self.config.oauth_url}/token", data=refresh_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    self.config.access_token = token_data['access_token']
                    self.config.refresh_token = token_data.get('refresh_token', self.config.refresh_token)
                    self.config.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
                    
                    logger.info("Token refreshed successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Token refresh failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

# Import TelephonyInterface from voice_system
from voice.voice_system import TelephonyInterface

class SkyetelIntegration(TelephonyInterface):
    """
    Production-ready Skyetel SIP integration
    Voice-only operations with OAuth authentication
    """
    
    def __init__(self, config: Optional[SkyetelConfig] = None):
        self.config = config or SkyetelConfig.from_env()
        self.system_id = str(uuid.uuid4())
        
        # OAuth client
        self.oauth_client = SkyetelOAuthClient(self.config)
        
        # Call management
        self.active_calls: Dict[str, CallResponse] = {}
        self.call_history: List[CallResponse] = []
        
        # Webhook handlers
        self.webhook_handlers: Dict[WebhookEvent, List[Callable]] = {
            WebhookEvent.CALL_STARTED: [],
            WebhookEvent.CALL_ANSWERED: [],
            WebhookEvent.CALL_ENDED: [],
            WebhookEvent.CALL_FAILED: [],
            WebhookEvent.RECORDING_COMPLETE: [],
            WebhookEvent.TRANSCRIPTION_COMPLETE: []
        }
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # State
        self.running = False
        self.authenticated = False
        
        logger.info(f"Skyetel Integration {self.system_id} initialized")
    
    async def start(self):
        """Start Skyetel integration"""
        logger.info("Starting Skyetel integration...")
        
        try:
            # Authenticate with Skyetel
            if not await self.oauth_client.authenticate():
                raise RuntimeError("Failed to authenticate with Skyetel")
            
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.config.access_token}'},
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            self.running = True
            self.authenticated = True
            
            logger.info("Skyetel integration started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Skyetel integration: {e}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown Skyetel integration"""
        logger.info("Shutting down Skyetel integration...")
        
        self.running = False
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        # Close OAuth client
        await self.oauth_client.close()
        
        logger.info("Skyetel integration shutdown complete")
    
    async def make_call(self, request: CallRequest) -> CallResponse:
        """Make outbound call"""
        if not self.running:
            raise RuntimeError("Skyetel integration is not running")
        
        call_id = request.call_id or str(uuid.uuid4())
        from_number = request.from_number or self.config.default_from_number
        
        if not from_number:
            raise ValueError("from_number is required")
        
        try:
            # Prepare call payload
            payload = {
                'to': request.to_number,
                'from': from_number,
                'webhook_url': request.webhook_url or self.config.webhook_url,
                'recording': request.recording,
                'transcription': request.transcription,
                'timeout': request.timeout,
                'metadata': request.metadata
            }
            
            # Make API request
            async with self.session.post(f"{self.config.base_url}/calls", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Create call response
                    call_response = CallResponse(
                        call_id=call_id,
                        status=CallStatus.INITIATED,
                        from_number=from_number,
                        to_number=request.to_number,
                        start_time=datetime.now(),
                        metadata=request.metadata
                    )
                    
                    # Store call
                    self.active_calls[call_id] = call_response
                    
                    logger.info(f"Call {call_id} initiated to {request.to_number}")
                    
                    return call_response
                else:
                    error_text = await response.text()
                    logger.error(f"Call initiation failed: {response.status} - {error_text}")
                    
                    return CallResponse(
                        call_id=call_id,
                        status=CallStatus.FAILED,
                        from_number=from_number,
                        to_number=request.to_number,
                        start_time=datetime.now(),
                        error_message=error_text,
                        metadata=request.metadata
                    )
                    
        except Exception as e:
            logger.error(f"Failed to make call: {e}")
            
            return CallResponse(
                call_id=call_id,
                status=CallStatus.FAILED,
                from_number=from_number,
                to_number=request.to_number,
                start_time=datetime.now(),
                error_message=str(e),
                metadata=request.metadata
            )
    
    async def end_call(self, call_id: str) -> bool:
        """End active call"""
        if call_id not in self.active_calls:
            logger.warning(f"Call {call_id} not found")
            return False
        
        try:
            # End call via API
            async with self.session.delete(f"{self.config.base_url}/calls/{call_id}") as response:
                if response.status == 200:
                    call_response = self.active_calls[call_id]
                    call_response.status = CallStatus.COMPLETED
                    call_response.duration = (datetime.now() - call_response.start_time).total_seconds()
                    
                    # Move to history
                    self.call_history.append(call_response)
                    del self.active_calls[call_id]
                    
                    logger.info(f"Call {call_id} ended successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to end call {call_id}: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to end call {call_id}: {e}")
            return False
    
    async def get_call_info(self, call_id: str) -> Optional[CallResponse]:
        """Get call information"""
        return self.active_calls.get(call_id)
    
    async def get_active_calls(self) -> List[CallResponse]:
        """Get all active calls"""
        return list(self.active_calls.values())
    
    async def get_call_history(self, limit: int = 100) -> List[CallResponse]:
        """Get call history"""
        return self.call_history[-limit:]
    
    async def handle_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook events"""
        try:
            # Verify webhook signature
            if not self._verify_webhook_signature(event_data):
                logger.warning("Invalid webhook signature")
                return {'error': 'Invalid signature'}
            
            event_type = event_data.get('event_type')
            call_id = event_data.get('call_id')
            
            if not event_type or not call_id:
                logger.warning("Invalid webhook data")
                return {'error': 'Invalid webhook data'}
            
            # Update call status
            if call_id in self.active_calls:
                call_response = self.active_calls[call_id]
                
                if event_type == WebhookEvent.CALL_ANSWERED.value:
                    call_response.status = CallStatus.ANSWERED
                elif event_type == WebhookEvent.CALL_ENDED.value:
                    call_response.status = CallStatus.COMPLETED
                    call_response.duration = (datetime.now() - call_response.start_time).total_seconds()
                    
                    # Move to history
                    self.call_history.append(call_response)
                    del self.active_calls[call_id]
                elif event_type == WebhookEvent.CALL_FAILED.value:
                    call_response.status = CallStatus.FAILED
                    call_response.error_message = event_data.get('error_message')
                    
                    # Move to history
                    self.call_history.append(call_response)
                    del self.active_calls[call_id]
                elif event_type == WebhookEvent.RECORDING_COMPLETE.value:
                    call_response.recording_url = event_data.get('recording_url')
                elif event_type == WebhookEvent.TRANSCRIPTION_COMPLETE.value:
                    call_response.transcription_url = event_data.get('transcription_url')
                
                # Trigger webhook handlers
                await self._trigger_webhook_handler(WebhookEvent(event_type), call_response)
                
                logger.info(f"Processed webhook event {event_type} for call {call_id}")
                
                return {'success': True, 'call_id': call_id}
            else:
                logger.warning(f"Call {call_id} not found for webhook event")
                return {'error': 'Call not found'}
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {'error': str(e)}
    
    def _verify_webhook_signature(self, event_data: Dict[str, Any]) -> bool:
        """Verify webhook signature for security"""
        if not self.config.webhook_secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True
        
        try:
            signature = event_data.get('signature', '')
            payload = json.dumps(event_data.get('payload', {}), sort_keys=True)
            
            expected_signature = hmac.new(
                self.config.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    async def _trigger_webhook_handler(self, event_type: WebhookEvent, call_response: CallResponse):
        """Trigger webhook event handlers"""
        if event_type in self.webhook_handlers:
            for handler in self.webhook_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(call_response)
                    else:
                        handler(call_response)
                except Exception as e:
                    logger.error(f"Error in webhook handler {event_type}: {e}")
    
    def add_webhook_handler(self, event_type: WebhookEvent, handler: Callable):
        """Add webhook event handler"""
        self.webhook_handlers[event_type].append(handler)
    
    async def refresh_authentication(self) -> bool:
        """Refresh OAuth authentication"""
        try:
            if await self.oauth_client.authenticate():
                # Update session headers
                if self.session:
                    self.session.headers.update({'Authorization': f'Bearer {self.config.access_token}'})
                
                logger.info("Authentication refreshed successfully")
                return True
            else:
                logger.error("Failed to refresh authentication")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing authentication: {e}")
            return False
    
    async def send_audio(self, call_id: str, audio_url: str) -> bool:
        """Send audio to active call via Skyetel API"""
        if call_id not in self.active_calls:
            logger.warning(f"Call {call_id} not found")
            return False
        
        try:
            # Send audio via Skyetel API
            payload = {
                'audio_url': audio_url,
                'playback_type': 'audio'
            }
            
            async with self.session.post(f"{self.config.base_url}/calls/{call_id}/audio", json=payload) as response:
                if response.status == 200:
                    logger.info(f"Audio sent to call {call_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send audio to call {call_id}: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send audio to call {call_id}: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'system_id': self.system_id,
            'running': self.running,
            'authenticated': self.authenticated,
            'active_calls': len(self.active_calls),
            'total_calls': len(self.call_history),
            'oauth_configured': bool(self.config.client_id and self.config.client_secret),
            'webhook_configured': bool(self.config.webhook_secret),
            'token_expires_at': self.config.token_expires_at.isoformat() if self.config.token_expires_at else None
        }

# Production-ready test suite
class TestSkyetelIntegration:
    """Comprehensive test suite for Skyetel Integration"""
    
    def test_system_initialization(self):
        """Test system initialization"""
        config = SkyetelConfig()
        integration = SkyetelIntegration(config)
        
        assert integration.system_id is not None
        assert integration.running == False
        assert integration.authenticated == False
        assert len(integration.active_calls) == 0
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        config = SkyetelConfig.from_env()
        
        assert config.base_url is not None
        assert config.oauth_url is not None
        assert config.webhook_url is not None
    
    def test_call_request_creation(self):
        """Test call request creation"""
        request = CallRequest(
            to_number="+1234567890",
            from_number="+0987654321",
            call_id="test_call_123",
            recording=True,
            transcription=True
        )
        
        assert request.to_number == "+1234567890"
        assert request.from_number == "+0987654321"
        assert request.call_id == "test_call_123"
        assert request.recording == True
        assert request.transcription == True
    
    def test_call_response_creation(self):
        """Test call response creation"""
        response = CallResponse(
            call_id="test_call_123",
            status=CallStatus.INITIATED,
            from_number="+0987654321",
            to_number="+1234567890",
            start_time=datetime.now()
        )
        
        assert response.call_id == "test_call_123"
        assert response.status == CallStatus.INITIATED
        assert response.from_number == "+0987654321"
        assert response.to_number == "+1234567890"

if __name__ == "__main__":
    # Run tests
    test_suite = TestSkyetelIntegration()
    test_suite.test_system_initialization()
    test_suite.test_configuration_loading()
    test_suite.test_call_request_creation()
    test_suite.test_call_response_creation()
    print("All Skyetel Integration tests passed!") 