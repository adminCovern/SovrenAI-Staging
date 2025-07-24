#!/bin/bash
# Production Deployment Script for Sovren AI
# Handles PostgreSQL authentication, environment setup, and service launch

set -e  # Exit on any error

echo "=== Sovren AI Production Deployment ==="
echo "Timestamp: $(date)"
echo "Hostname: $(hostname)"
echo "User: $(whoami)"

# Configuration
SOVREN_HOME="/data/sovren/sovren-ai"
SOVREN_ENV="production"
SOVREN_SECURITY_KEY="sovren_ai_secure_key_2024_b200_gpu_deployment"
POSTGRES_PASSWORD="sovren_secure_password_2024"
REDIS_HOST="127.0.0.1"
REDIS_PORT="6379"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "This script should not be run as root"
fi

# Function to check service status
check_service() {
    local service_name=$1
    local port=$2
    
    if pgrep -f "$service_name" > /dev/null; then
        log "✓ $service_name is running"
        return 0
    else
        warning "$service_name is not running"
        return 1
    fi
}

# Function to check port availability
check_port() {
    local port=$1
    if netstat -tuln | grep ":$port " > /dev/null; then
        warning "Port $port is already in use"
        return 1
    else
        log "✓ Port $port is available"
        return 0
    fi
}

# Step 1: Verify system requirements
log "Step 1: Verifying system requirements..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
if [[ "$PYTHON_VERSION" == 3.12* ]]; then
    log "✓ Python $PYTHON_VERSION detected"
else
    error "Python 3.12+ required, found $PYTHON_VERSION"
fi

# Check CUDA
if command -v nvidia-smi > /dev/null; then
    log "✓ NVIDIA drivers detected"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | while read line; do
        log "  GPU: $line"
    done
else
    error "NVIDIA drivers not found"
fi

# Check CUDA toolkit
if command -v nvcc > /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | cut -d' ' -f6 | cut -d',' -f1)
    log "✓ CUDA $CUDA_VERSION detected"
else
    error "CUDA toolkit not found"
fi

# Step 2: Verify and configure PostgreSQL
log "Step 2: Configuring PostgreSQL..."

# Check if PostgreSQL is running
if systemctl is-active --quiet postgresql; then
    log "✓ PostgreSQL service is running"
else
    error "PostgreSQL service is not running"
fi

# Test PostgreSQL connection
if PGPASSWORD="$POSTGRES_PASSWORD" psql -U sovren -d sovren_voice -h localhost -c "SELECT 1;" > /dev/null 2>&1; then
    log "✓ PostgreSQL authentication working"
else
    warning "PostgreSQL authentication failed, attempting to fix..."
    
    # Set password for sovren user
    sudo -u postgres psql -c "ALTER USER sovren PASSWORD '$POSTGRES_PASSWORD';" || error "Failed to set PostgreSQL password"
    
    # Test connection again
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -U sovren -d sovren_voice -h localhost -c "SELECT 1;" > /dev/null 2>&1; then
        log "✓ PostgreSQL authentication fixed"
    else
        error "PostgreSQL authentication still failing"
    fi
fi

# Step 3: Verify Redis
log "Step 3: Verifying Redis..."

if systemctl is-active --quiet redis-server; then
    log "✓ Redis service is running"
else
    error "Redis service is not running"
fi

# Test Redis connection
if redis-cli ping > /dev/null 2>&1; then
    log "✓ Redis connection working"
else
    error "Redis connection failed"
fi

# Step 4: Set environment variables
log "Step 4: Setting environment variables..."

export SOVREN_ENV="$SOVREN_ENV"
export SOVREN_SECURITY_KEY="$SOVREN_SECURITY_KEY"
export PGPASSWORD="$POSTGRES_PASSWORD"
export CUDA_VISIBLE_DEVICES="0,1,2,3"  # Use first 4 GPUs for Sovren AI

# Create environment file
cat > "$SOVREN_HOME/.env" << EOF
SOVREN_ENV=$SOVREN_ENV
SOVREN_SECURITY_KEY=$SOVREN_SECURITY_KEY
PGPASSWORD=$POSTGRES_PASSWORD
CUDA_VISIBLE_DEVICES=0,1,2,3
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
EOF

log "✓ Environment variables set"

# Step 5: Check port availability
log "Step 5: Checking port availability..."

PORTS=(8000 8001 8002 8003 8004 9999 6379 5432)
for port in "${PORTS[@]}"; do
    check_port "$port"
done

# Step 6: Kill any existing Sovren processes
log "Step 6: Cleaning up existing processes..."

pkill -f "consciousness_engine" || true
pkill -f "bayesian_engine" || true
pkill -f "agent_battalion" || true
pkill -f "voice_system" || true
pkill -f "api_server" || true

sleep 2

# Step 7: Launch Sovren AI services
log "Step 7: Launching Sovren AI services..."

cd "$SOVREN_HOME"

# Launch Consciousness Engine
log "Starting Consciousness Engine..."
nohup python3 core/consciousness/consciousness_engine.py > logs/consciousness.log 2>&1 &
CONSCIOUSNESS_PID=$!
sleep 3

# Launch Bayesian Engine
log "Starting Bayesian Engine..."
nohup python3 core/bayesian_engine/bayesian_engine.py > logs/bayesian.log 2>&1 &
BAYESIAN_PID=$!
sleep 3

# Launch Agent Battalion
log "Starting Agent Battalion..."
nohup python3 core/agent_battalion/agent_battalion.py > logs/agent_battalion.log 2>&1 &
BATTALION_PID=$!
sleep 3

# Launch Voice System (restricted to GPUs 0-3)
log "Starting Voice System..."
CUDA_VISIBLE_DEVICES=0,1,2,3 nohup python3 voice/voice_system.py > logs/voice.log 2>&1 &
VOICE_PID=$!
sleep 3

# Launch API Server
log "Starting API Server..."
nohup python3 api/server.py > logs/api.log 2>&1 &
API_PID=$!
sleep 3

# Step 8: Verify all services are running
log "Step 8: Verifying service status..."

SERVICES=(
    "consciousness_engine:Consciousness Engine"
    "bayesian_engine:Bayesian Engine"
    "agent_battalion:Agent Battalion"
    "voice_system:Voice System"
    "api_server:API Server"
)

ALL_RUNNING=true
for service in "${SERVICES[@]}"; do
    IFS=':' read -r process_name display_name <<< "$service"
    if check_service "$process_name"; then
        log "✓ $display_name is running"
    else
        error "$display_name failed to start"
        ALL_RUNNING=false
    fi
done

# Step 9: Health check
log "Step 9: Performing health checks..."

# Check API endpoints
sleep 5
if curl -s http://localhost:8000/health > /dev/null; then
    log "✓ API Server health check passed"
else
    warning "API Server health check failed"
fi

# Check Redis
if redis-cli ping | grep -q "PONG"; then
    log "✓ Redis health check passed"
else
    warning "Redis health check failed"
fi

# Check PostgreSQL
if PGPASSWORD="$POSTGRES_PASSWORD" psql -U sovren -d sovren_voice -h localhost -c "SELECT 1;" > /dev/null 2>&1; then
    log "✓ PostgreSQL health check passed"
else
    warning "PostgreSQL health check failed"
fi

# Step 10: Final status
log "Step 10: Deployment Summary"

if $ALL_RUNNING; then
    echo -e "${GREEN}"
    echo "=========================================="
    echo "🎉 Sovren AI Deployment Successful! 🎉"
    echo "=========================================="
    echo -e "${NC}"
    
    echo "Service Status:"
    echo "  • Consciousness Engine: Running (PID: $CONSCIOUSNESS_PID)"
    echo "  • Bayesian Engine: Running (PID: $BAYESIAN_PID)"
    echo "  • Agent Battalion: Running (PID: $BATTALION_PID)"
    echo "  • Voice System: Running (PID: $VOICE_PID)"
    echo "  • API Server: Running (PID: $API_PID)"
    echo ""
    echo "Access Points:"
    echo "  • API Server: http://localhost:8000"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • Redis: localhost:6379"
    echo "  • PostgreSQL: localhost:5432"
    echo ""
    echo "Log Files:"
    echo "  • Consciousness: logs/consciousness.log"
    echo "  • Bayesian: logs/bayesian.log"
    echo "  • Agent Battalion: logs/agent_battalion.log"
    echo "  • Voice System: logs/voice.log"
    echo "  • API Server: logs/api.log"
    echo ""
    echo "Environment: $SOVREN_ENV"
    echo "GPUs Used: 0,1,2,3 (B200 compatibility mode)"
    echo ""
    echo "To monitor logs: tail -f logs/*.log"
    echo "To stop services: pkill -f 'consciousness_engine|bayesian_engine|agent_battalion|voice_system|api_server'"
    
else
    error "Deployment failed - some services are not running"
fi

echo ""
log "Deployment completed at $(date)" 