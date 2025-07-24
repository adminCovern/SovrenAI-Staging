# SOVREN AI Voice System

Enterprise-grade voice interface with real-time ASR, TTS, and telephony integration.

## Overview

The SOVREN Voice System is a production-ready voice interface solution that provides:

- **Real-time Speech Recognition** - Using Whisper ASR for accurate transcription
- **Natural Speech Synthesis** - StyleTTS2 integration for lifelike voice output  
- **Telephony Integration** - Skyetel integration for phone call handling
- **WebSocket Streaming** - Real-time bidirectional audio streaming
- **Enterprise Features** - Monitoring, logging, security, and scalability

## Architecture

The system follows enterprise design patterns with:

- **Interface-based Design** - Pluggable ASR/TTS/Telephony implementations
- **Circuit Breakers** - Fault tolerance and graceful degradation
- **Rate Limiting** - Protection against abuse
- **Connection Pooling** - Efficient resource management
- **Event-driven Architecture** - Async processing with pub/sub
- **Comprehensive Monitoring** - Prometheus metrics and health checks

## Features

### Core Capabilities

- Multi-language speech recognition
- Multiple voice profiles for synthesis
- Real-time audio streaming
- Phone call initiation and management
- Session management with persistence
- Audio recording and playback

### Production Features

- **High Availability** - Automatic failover and recovery
- **Scalability** - Handle 100+ concurrent sessions
- **Security** - API key authentication, encryption, audit logging
- **Monitoring** - Prometheus metrics, health endpoints, alerting
- **Performance** - Sub-second latency, efficient caching
- **Reliability** - Retry logic, circuit breakers, error recovery

## Installation

### System Requirements

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- FFmpeg for audio processing
- PortAudio for audio capture
- PostgreSQL or SQLite for persistence
- Redis for caching and pub/sub

### Quick Start

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y ffmpeg portaudio19-dev libsndfile1
   
   # macOS
   brew install ffmpeg portaudio
   ```

2. **Install Python packages:**
   ```bash
   pip install -r voice/requirements.txt
   ```

3. **Configure environment:**
   ```bash
   export SKYETEL_USERNAME="your_username"
   export SKYETEL_PASSWORD="your_password"
   export DATABASE_URL="postgresql://user:pass@localhost/sovren_voice"
   export REDIS_URL="redis://localhost:6379/0"
   ```

4. **Run the system:**
   ```bash
   python -m voice.voice_system
   ```

### Production Deployment

For production deployment, use the automated deployment script:

```bash
sudo python voice/deploy.py
```

This will:
- Check prerequisites
- Create system directories
- Install dependencies
- Configure the service
- Set up monitoring
- Create systemd service (Linux)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `DATABASE_URL` | Database connection string | sqlite:///voice.db |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `WHISPER_MODEL_PATH` | Path to Whisper model | /data/sovren/models/whisper/ggml-large-v3.bin |
| `STYLETTS2_MODEL_PATH` | Path to TTS model | /data/sovren/models/tts |
| `METRICS_PORT` | Prometheus metrics port | 9090 |
| `WEBSOCKET_PORT` | WebSocket server port | 8765 |

### Configuration File

Create a `config.json` file:

```json
{
  "voice_system": {
    "sample_rate": 16000,
    "chunk_size": 1024,
    "max_concurrent_sessions": 100,
    "transcription_timeout": 30.0,
    "synthesis_timeout": 20.0
  },
  "security": {
    "enable_auth": true,
    "api_key_header": "X-API-Key"
  },
  "monitoring": {
    "enable_metrics": true,
    "enable_health_check": true
  }
}
```

## API Usage

### WebSocket API

Connect to the WebSocket server for real-time communication:

```python
import asyncio
import websockets
import json

async def voice_client():
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Start a voice session
        await websocket.send(json.dumps({
            'type': 'start_session',
            'data': {
                'user_id': 'user123',
                'language': 'en',
                'quality': 'high'
            }
        }))
        
        # Receive session info
        response = await websocket.recv()
        session_data = json.loads(response)
        session_id = session_data['session']['id']
        
        # Stream audio chunks
        # ... send audio data ...
```

### Python API

```python
from voice import VoiceSystem, VoiceSessionCreate

# Initialize system
system = VoiceSystem()
await system.start()

# Create a session
request = VoiceSessionCreate(
    user_id="user123",
    language="en",
    quality="high"
)
session = await system.create_voice_session(request)

# Process audio
# ... handle audio streaming ...

# End session
await system.end_session(session.id)
```

### Phone Call API

```python
from voice import PhoneCallRequest

# Make an outbound call
call_request = PhoneCallRequest(
    to_number="+1234567890",
    from_number="+0987654321",
    user_id="user123",
    initial_message="Hello, this is SOVREN AI calling."
)
result = await system.initiate_phone_call(call_request)
```

## Monitoring

### Prometheus Metrics

The system exposes metrics at `http://localhost:9090/metrics`:

- `voice_sessions_total` - Total number of sessions
- `voice_sessions_active` - Currently active sessions
- `transcription_duration_seconds` - ASR processing time
- `synthesis_duration_seconds` - TTS processing time
- `voice_system_errors_total` - Error counts by type

### Health Check

Health endpoint: `http://localhost:8080/health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "models": "ok"
  }
}
```

### Logging

Structured JSON logs are written to:
- `/var/log/sovren/voice/voice.log` - All logs
- `/var/log/sovren/voice/voice_errors.log` - Errors only

## Security

### Authentication

All API requests require authentication:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8080/api/voice/sessions
```

### Encryption

- All sensitive data is encrypted at rest
- TLS required for production deployments
- Audio streams are encrypted in transit

### Audit Logging

All actions are logged with:
- User ID
- Timestamp
- Action performed
- IP address
- Request ID

## Performance Tuning

### Optimization Tips

1. **Model Loading**
   - Pre-load models on startup
   - Use GPU acceleration when available
   - Cache frequently used voices

2. **Audio Processing**
   - Adjust chunk size for latency/quality tradeoff
   - Enable noise suppression for better accuracy
   - Use appropriate sample rates

3. **Database**
   - Use PostgreSQL for production
   - Enable connection pooling
   - Index frequently queried fields

4. **Redis**
   - Configure appropriate memory limits
   - Use Redis Cluster for high availability
   - Enable persistence for critical data

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all packages from requirements.txt are installed
   - Check Python version (3.10+)

2. **Audio Issues**
   - Verify PortAudio installation
   - Check microphone permissions
   - Test with `python -m sounddevice`

3. **Model Loading**
   - Verify model files exist at configured paths
   - Check file permissions
   - Ensure sufficient memory

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m voice.voice_system
```

## Development

### Running Tests

```bash
pytest voice/tests/ -v --cov=voice
```

### Code Quality

```bash
# Format code
black voice/

# Type checking
mypy voice/

# Linting
ruff voice/
```

### Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write comprehensive docstrings
4. Include unit tests for new features
5. Update documentation

## License

Proprietary - SOVREN AI

## Support

For support, contact: support@sovrenai.com

---

Built with ❤️ by SOVREN AI 