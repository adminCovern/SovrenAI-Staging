#!/bin/bash
"""
Launch Sovren AI on Ubuntu Server
Production deployment script with proper environment setup
"""

set -e  # Exit on any error

echo "🚀 Launching Sovren AI on Ubuntu Server..."

# Set environment variables for production
export SOVREN_ENV=production
export SOVREN_SECURITY_KEY=aa9628c23683705c6c1eee9771bb3224f438333e925df0c5df2e88f0699603fd
export DATABASE_URL=postgresql://sovren:password@localhost/sovren_voice
export REDIS_URL=redis://localhost:6379/0
export SOVREN_LOG_LEVEL=INFO
export SOVREN_HOST=0.0.0.0
export SOVREN_PORT=8000
export SOVREN_MCP_ENABLED=1
export SOVREN_MCP_HOST=localhost
export SOVREN_MCP_PORT=9999

echo "✅ Environment variables set"

# Verify services are running
echo "🔍 Verifying services..."

# Check PostgreSQL
if pg_isready -h localhost -p 5432 -U sovren -d sovren_voice > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL is not running. Starting..."
    sudo systemctl start postgresql
    sleep 2
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running. Starting..."
    sudo systemctl start redis-server
    sleep 2
fi

# Verify models exist
echo "🔍 Verifying models..."
if [ -f "/data/sovren/models/whisper/ggml-large-v3.bin" ]; then
    echo "✅ Whisper model found"
else
    echo "❌ Whisper model not found"
    exit 1
fi

if [ -d "/data/sovren/models/tts" ] && [ "$(ls -A /data/sovren/models/tts)" ]; then
    echo "✅ TTS models found"
else
    echo "❌ TTS models not found"
    exit 1
fi

# Launch Sovren AI
echo "🚀 Starting Sovren AI..."
cd /data/sovren/sovren-ai
python scripts/launch_sovren.py 