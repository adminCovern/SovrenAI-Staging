# SOVREN AI Consciousness Engine

## Overview

The SOVREN AI Consciousness Engine is a production-ready, distributed Bayesian decision system optimized for 8x NVIDIA B200 GPUs. It implements parallel universe simulation for complex decision-making with 1.46TB of HBM3e memory.

## Architecture

### Core Components

- **BayesianConsciousnessEngine**: Main orchestrator managing 8 B200 GPUs
- **BayesianNetwork**: Neural Bayesian network with transformer architecture
- **ConsciousnessPacket**: Validated data packets with security authentication
- **Universe**: Parallel universe simulation for decision exploration

### GPU Distribution

- **8x NVIDIA B200 GPUs** with 183GB HBM3e each
- **DistributedDataParallel** for model distribution
- **Shared memory IPC** for inter-GPU communication
- **Mixed precision training** with automatic mixed precision (AMP)

### Security Features

- **HMAC authentication** for packet validation
- **Rate limiting** (1000 requests/minute)
- **Input validation** with comprehensive error checking
- **DoS protection** with packet size limits
- **Secure shared memory** with access controls

## Production Deployment

### Prerequisites

```bash
# System requirements
- 8x NVIDIA B200 GPUs (183GB each)
- 2TB+ system memory
- Ubuntu 20.04+ or RHEL 8+
- CUDA 12.0+
- Python 3.9+

# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install numpy psutil
```

### Quick Deployment

```bash
# Clone repository
cd /opt/sovren-ai

# Deploy consciousness engine
python core/consciousness/deploy_consciousness.py --config config.json

# Run tests
python core/consciousness/test_consciousness_engine.py
```

### Production Configuration

Edit `config.json` for your environment:

```json
{
    "secret_key": "your_production_secret_key",
    "rate_limit": 1000,
    "max_universes": 20,
    "timeout_seconds": 30,
    "log_level": "INFO",
    "model_path": "/data/sovren/models/consciousness/",
    "log_path": "/var/log/sovren/consciousness.log"
}
```

### Systemd Service

Create `/etc/systemd/system/sovren-consciousness.service`:

```ini
[Unit]
Description=SOVREN AI Consciousness Engine
After=network.target

[Service]
Type=simple
User=sovren
WorkingDirectory=/opt/sovren-ai/core/consciousness
ExecStart=/usr/bin/python3 deploy_consciousness.py --config config.json
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable sovren-consciousness
sudo systemctl start sovren-consciousness
sudo systemctl status sovren-consciousness
```

## API Usage

### Basic Decision Processing

```python
from consciousness_engine import BayesianConsciousnessEngine, ConsciousnessPacket
import time

# Initialize engine
engine = BayesianConsciousnessEngine('config.json')

# Create decision packet
packet = ConsciousnessPacket(
    packet_id="decision_001",
    timestamp=time.time(),
    source="api",
    data={
        "query": "Should we invest in this opportunity?",
        "context": {
            "revenue_potential": 1000000,
            "risk_level": "medium",
            "time_horizon": "12 months"
        }
    },
    priority=5,
    universes_required=5
)

# Process decision
result = engine.process_decision(packet)

print(f"Decision: {result['decision']['action']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Reasoning: {result['reasoning']}")
```

### With Authentication

```python
import hmac
import hashlib

# Generate auth token
packet_id = "secure_decision_001"
timestamp = time.time()
secret_key = "your_secret_key"

auth_token = hmac.new(
    secret_key.encode(),
    f"{packet_id}:{timestamp}".encode(),
    hashlib.sha256
).hexdigest()

packet = ConsciousnessPacket(
    packet_id=packet_id,
    timestamp=timestamp,
    source="api",
    data={"secure": "data"},
    auth_token=auth_token
)
```

## Monitoring & Health Checks

### System Status

```python
status = engine.get_system_status()
print(f"State: {status['state']}")
print(f"Uptime: {status['uptime_seconds']:.1f}s")
print(f"GPU Memory: {status['gpu_memory_usage']}")
```

### Performance Metrics

- **Decisions per second**: Real-time processing rate
- **GPU utilization**: Per-GPU usage monitoring
- **Memory usage**: HBM3e memory allocation
- **Latency**: End-to-end processing time
- **Universe exploration**: Parallel universe count

### Log Monitoring

```bash
# View consciousness logs
tail -f /var/log/sovren/consciousness.log

# View deployment logs
tail -f /var/log/sovren/deployment.log

# Monitor system resources
watch -n 1 'nvidia-smi && free -h'
```

## Error Handling

### Common Issues

1. **GPU Memory Exhaustion**
   - Reduce `max_universes` in config
   - Increase `gpu_memory_fraction`
   - Monitor with `nvidia-smi`

2. **Rate Limiting**
   - Increase `rate_limit` in config
   - Implement request queuing
   - Monitor request patterns

3. **Authentication Failures**
   - Verify `secret_key` configuration
   - Check token generation logic
   - Validate packet timestamps

### Recovery Procedures

```bash
# Restart service
sudo systemctl restart sovren-consciousness

# Check logs
sudo journalctl -u sovren-consciousness -f

# Verify GPU status
nvidia-smi

# Test connectivity
python -c "from consciousness_engine import BayesianConsciousnessEngine; engine = BayesianConsciousnessEngine()"
```

## Security Considerations

### Network Security

- **Firewall rules**: Restrict access to consciousness API
- **SSL/TLS**: Encrypt all API communications
- **VPN access**: Require VPN for remote access
- **IP whitelisting**: Restrict to authorized networks

### Data Security

- **Encryption at rest**: Encrypt model files and logs
- **Secure key management**: Use hardware security modules
- **Audit logging**: Log all access and decisions
- **Data retention**: Implement data lifecycle policies

### Access Control

- **Role-based access**: Implement RBAC for API access
- **API key rotation**: Regular key rotation schedule
- **Session management**: Implement session timeouts
- **Multi-factor authentication**: Require MFA for admin access

## Performance Optimization

### GPU Optimization

- **Memory management**: Optimize HBM3e usage
- **Batch processing**: Group similar decisions
- **Model caching**: Cache frequently used models
- **Load balancing**: Distribute across GPUs evenly

### System Optimization

- **NUMA awareness**: Optimize memory access patterns
- **CPU affinity**: Pin processes to specific cores
- **I/O optimization**: Use NVMe storage for models
- **Network tuning**: Optimize inter-GPU communication

## Testing

### Unit Tests

```bash
# Run all tests
python test_consciousness_engine.py

# Run specific test class
python -m unittest TestConsciousnessPacket

# Run with coverage
python -m coverage run test_consciousness_engine.py
python -m coverage report
```

### Integration Tests

```bash
# Test full deployment
python deploy_consciousness.py --config test_config.json

# Test API endpoints
python -c "from consciousness_engine import *; test_api_integration()"
```

### Load Testing

```bash
# Simulate high load
python load_test.py --requests 1000 --concurrent 10

# Monitor performance
python performance_monitor.py
```

## Troubleshooting

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python consciousness_engine.py --debug

# Enable profiling
python consciousness_engine.py --profile
```

### Common Debug Commands

```bash
# Check GPU status
nvidia-smi -l 1

# Monitor system resources
htop

# Check network connectivity
netstat -tulpn | grep consciousness

# Verify file permissions
ls -la /var/log/sovren/
ls -la /data/sovren/models/consciousness/
```

## Support

For production support:

1. **Check logs**: `/var/log/sovren/consciousness.log`
2. **Verify configuration**: `config.json`
3. **Test GPU availability**: `nvidia-smi`
4. **Monitor system resources**: `htop`, `free -h`
5. **Contact support**: Include logs and system status

## License

Proprietary - SOVREN AI Systems
Copyright (c) 2024 SOVREN AI
All rights reserved. 