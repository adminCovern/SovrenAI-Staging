#!/bin/bash
# SOVREN AI Complete Production Startup Script
# Starts all components including API, Frontend, and MCP servers

set -e

echo "🚀 Starting SOVREN AI Complete Production System..."

# Set environment variables
export SOVREN_ROOT="$(pwd)"
export SOVREN_LOG_LEVEL="INFO"
export SOVREN_DEBUG_MODE="false"
export SOVREN_PERFORMANCE_MODE="true"

# Create logs directory
mkdir -p logs

# Function to start a service with logging
start_service() {
    local service_name=$1
    local command=$2
    local log_file="logs/${service_name}.log"
    
    echo "🔧 Starting ${service_name}..."
    $command > $log_file 2>&1 &
    local pid=$!
    echo "✅ ${service_name} started with PID: $pid"
    echo $pid > "logs/${service_name}.pid"
}

# Start core AI systems
echo "🧠 Starting core AI systems..."
start_service "consciousness" "python core/consciousness/consciousness_engine.py"
start_service "bayesian" "python core/bayesian_engine/bayesian_engine.py"
start_service "agent_battalion" "python core/agent_battalion/agent_battalion.py"

# Start intelligence systems
echo "🧠 Starting intelligence systems..."
start_service "intelligence" "python core/intelligence/advanced_intelligence_system.py"
start_service "interface" "python core/interface/adaptive_interface_system.py"
start_service "integration" "python core/integration/sophisticated_integration_system.py"

# Start main integration system
echo "🔗 Starting main integration system..."
start_service "main_integration" "python core/main_integration_system.py"

# Start voice system
echo "🎤 Starting voice system..."
start_service "voice" "python voice/voice_system.py"

# Start shadow board
echo "👥 Starting shadow board..."
start_service "shadow_board" "python core/shadow_board/shadow_board_system.py"

# Start time machine
echo "⏰ Starting time machine..."
start_service "time_machine" "python core/time_machine/time_machine_system.py"

# Start security systems
echo "🔒 Starting security systems..."
start_service "security" "python core/security/security_system.py"
start_service "zero_knowledge" "python core/security/zero_knowledge_system.py"
start_service "adversarial" "python core/security/adversarial_hardening.py"

# Start API server
echo "🌐 Starting API server..."
start_service "api_server" "python api/server.py"

# Start MCP server
echo "🔌 Starting MCP server..."
if [ -f "scripts/enterprise_mcp_server.py" ]; then
    start_service "mcp_server" "python scripts/enterprise_mcp_server.py"
else
    echo "⚠️  MCP server script not found"
fi

# Start frontend server (React/Node.js)
echo "🎨 Starting frontend server..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install > ../logs/frontend_install.log 2>&1
        echo "🚀 Starting frontend development server..."
        npm start > ../logs/frontend.log 2>&1 &
        frontend_pid=$!
        echo "✅ Frontend started with PID: $frontend_pid"
        echo $frontend_pid > ../logs/frontend.pid
        cd ..
    else
        echo "⚠️  Frontend package.json not found"
    fi
else
    echo "⚠️  Frontend directory not found"
fi

# Start additional services if they exist
if [ -f "scripts/launch_sovren.py" ]; then
    echo "🚀 Starting launch script..."
    start_service "launch" "python scripts/launch_sovren.py"
fi

if [ -f "scripts/start_sovren_fixed.py" ]; then
    echo "🔧 Starting fixed startup script..."
    start_service "fixed_startup" "python scripts/start_sovren_fixed.py"
fi

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service status
echo "📊 Service Status:"
echo "=================="

# Check if API server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API Server: Running (http://localhost:8000)"
else
    echo "❌ API Server: Not responding"
fi

# Check if frontend server is running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend Server: Running (http://localhost:3000)"
else
    echo "❌ Frontend Server: Not responding"
fi

# Check if MCP server is running
if [ -f "logs/mcp_server.pid" ]; then
    mcp_pid=$(cat logs/mcp_server.pid)
    if ps -p $mcp_pid > /dev/null 2>&1; then
        echo "✅ MCP Server: Running (PID: $mcp_pid)"
    else
        echo "❌ MCP Server: Not running"
    fi
else
    echo "⚠️  MCP Server: PID file not found"
fi

# Show all running Python processes
echo ""
echo "🔍 All running Python processes:"
ps aux | grep python | grep -v grep

echo ""
echo "✅ SOVREN AI Complete Production System started successfully!"
echo "📊 Monitor logs at: logs/"
echo "🌐 API available at: http://localhost:8000"
echo "🎨 Frontend available at: http://localhost:3000"
echo "🔌 MCP Server: Check logs/mcp_server.log for status"

# Keep script running and show logs
echo ""
echo "📝 Showing recent logs (Ctrl+C to stop):"
tail -f logs/*.log 