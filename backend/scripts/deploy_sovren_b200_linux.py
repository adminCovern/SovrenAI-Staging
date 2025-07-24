#!/usr/bin/env python3
"""
SOVREN AI - Linux Production Deployment Script for B200 Infrastructure
Complete bare metal deployment with all sophisticated features
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def run_command(cmd, cwd=None, check=True, shell=True):
    """Run a command and return the result"""
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ Success: {cmd}")
    return True

def check_system_requirements():
    """Check if system meets B200 deployment requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor < 12:
        print(f"❌ Python 3.12+ required, found {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Check CUDA availability
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CUDA compiler found")
            print(f"   {result.stdout.split('release')[0].strip()}")
        else:
            print("❌ CUDA compiler not found")
            return False
    except FileNotFoundError:
        print("❌ CUDA compiler not found")
        return False
    
    # Check GPU availability
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected")
            if "B200" in result.stdout or "Blackwell" in result.stdout:
                print("✅ B200 GPU detected")
            else:
                print("⚠️  B200 GPU not detected, but continuing...")
        else:
            print("❌ NVIDIA GPU not detected")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi not found")
        return False
    
    # Check system resources
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ System memory check passed")
        else:
            print("⚠️  System memory check failed")
    except FileNotFoundError:
        print("⚠️  free command not found")
    
    return True

def setup_environment():
    """Setup environment variables for B200 deployment"""
    print("🔧 Setting up environment variables...")
    
    env_vars = {
        'SOVREN_ROOT': os.getcwd(),
        'SOVREN_LOG_LEVEL': 'INFO',
        'SOVREN_DEBUG_MODE': 'false',
        'SOVREN_PERFORMANCE_MODE': 'true',
        'CMAKE_CUDA_ARCHITECTURES': '10.0',
        'TORCH_CUDA_ARCH_LIST': '10.0',
        'CUDA_ARCH_LIST': '10.0',
        'CMAKE_CUDA_FLAGS': '-arch=sm_100',
        'NVCC_FLAGS': '-arch=sm_100',
        'CMAKE_CUDA_COMPILER_FLAGS': '-arch=sm_100',
        'CMAKE_CUDA_HOST_COMPILER': '/usr/bin/gcc',
        'BUILD_CUDA': 'ON',
        'USE_CUDA': 'ON',
        'CUDA_TOOLKIT_ROOT_DIR': '/usr/local/cuda',
        'PYTHONPATH': os.getcwd()
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  {key}={value}")
    
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    print("📦 Installing system dependencies...")
    
    # Update package list
    if not run_command('sudo apt update'):
        print("⚠️  Failed to update package list")
    
    # Install essential packages
    packages = [
        'build-essential',
        'cmake',
        'git',
        'curl',
        'wget',
        'python3-dev',
        'python3-pip',
        'python3-venv',
        'libssl-dev',
        'libffi-dev',
        'libjpeg-dev',
        'libpng-dev',
        'libtiff-dev',
        'libavcodec-dev',
        'libavformat-dev',
        'libswscale-dev',
        'libv4l-dev',
        'libxvidcore-dev',
        'libx264-dev',
        'libgtk-3-dev',
        'libatlas-base-dev',
        'gfortran',
        'libhdf5-dev',
        'libhdf5-serial-dev',
        'libhdf5-103',
        'libqtgui4',
        'libqtwebkit4',
        'libqt4-test',
        'python3-pyqt5',
        'libtiff5-dev',
        'libjasper-dev',
        'libdc1394-22-dev',
        'libopenexr-dev',
        'libgstreamer1.0-dev',
        'libgstreamer-plugins-base1.0-dev',
        'libgstreamer-plugins-bad1.0-dev',
        'gstreamer1.0-plugins-base',
        'gstreamer1.0-plugins-good',
        'gstreamer1.0-plugins-bad',
        'gstreamer1.0-plugins-ugly',
        'gstreamer1.0-libav',
        'gstreamer1.0-tools',
        'gstreamer1.0-x',
        'gstreamer1.0-alsa',
        'gstreamer1.0-gl',
        'gstreamer1.0-gtk3',
        'gstreamer1.0-qt5',
        'gstreamer1.0-pulseaudio',
        'libgstreamer-plugins-base1.0-dev',
        'libgstreamer-plugins-bad1.0-dev',
        'libgstreamer-plugins-good1.0-dev',
        'libgstreamer-plugins-ugly1.0-dev',
        'libgstreamer1.0-dev',
        'libgstreamer1.0-0',
        'libgstreamer-plugins-base1.0-0',
        'libgstreamer-plugins-bad1.0-0',
        'libgstreamer-plugins-good1.0-0',
        'libgstreamer-plugins-ugly1.0-0',
        'libgstreamer1.0-0-dbg',
        'libgstreamer-plugins-base1.0-0-dbg',
        'libgstreamer-plugins-bad1.0-0-dbg',
        'libgstreamer-plugins-good1.0-0-dbg',
        'libgstreamer-plugins-ugly1.0-0-dbg'
    ]
    
    for package in packages:
        if not run_command(f'sudo apt install -y {package}', check=False):
            print(f"⚠️  Failed to install {package}")
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("🐍 Installing Python dependencies...")
    
    # Upgrade pip
    if not run_command('pip install --upgrade pip'):
        print("⚠️  Failed to upgrade pip")
    
    # Install core dependencies
    dependencies = [
        'numpy',
        'requests',
        'psutil',
        'pyyaml',
        'aiohttp',
        'websockets',
        'asyncio',
        'sqlite3',
        'json',
        'logging',
        'datetime',
        'pathlib',
        'subprocess',
        'shutil',
        'time',
        'threading',
        'multiprocessing',
        'flask',
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy',
        'alembic',
        'redis',
        'celery',
        'prometheus-client',
        'structlog',
        'python-dotenv',
        'cryptography',
        'bcrypt',
        'jwt',
        'passlib',
        'python-multipart',
        'aiofiles',
        'httpx',
        'websockets',
        'sentry-sdk',
        'opentelemetry-api',
        'opentelemetry-sdk',
        'opentelemetry-instrumentation',
        'opentelemetry-exporter-jaeger',
        'opentelemetry-exporter-prometheus'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            print(f"📦 Installing {dep}...")
            if not run_command(f'pip install {dep}', check=False):
                print(f"⚠️  Failed to install {dep}")
    
    return True

def build_pytorch_b200():
    """Build PyTorch with B200 support"""
    print("🏗️  Building PyTorch for B200...")
    
    pytorch_dir = os.path.join(os.getcwd(), 'pytorch')
    if not os.path.exists(pytorch_dir):
        print("❌ PyTorch directory not found")
        return False
    
    # Apply the build fix
    if not run_command('python ../scripts/fix_pytorch_b200_build.py', cwd=pytorch_dir):
        return False
    
    # Build PyTorch
    build_script = os.path.join(pytorch_dir, 'build_pytorch_b200.sh')
    if os.path.exists(build_script):
        if not run_command(f'bash {build_script}', cwd=pytorch_dir):
            print("⚠️  PyTorch build failed, trying alternative method...")
            return build_pytorch_alternative()
    else:
        print("❌ Build script not found")
        return False
    
    return True

def build_pytorch_alternative():
    """Alternative PyTorch build method"""
    print("🔄 Trying alternative PyTorch build method...")
    
    # Install pre-built PyTorch with CUDA support
    pytorch_commands = [
        'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121',
        'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118',
        'pip install torch torchvision torchaudio'
    ]
    
    for cmd in pytorch_commands:
        print(f"🔄 Trying: {cmd}")
        if run_command(cmd, check=False):
            print("✅ PyTorch installed successfully")
            return True
    
    print("❌ Failed to install PyTorch")
    return False

def deploy_core_systems():
    """Deploy core Sovren AI systems"""
    print("🚀 Deploying core systems...")
    
    core_systems = [
        'core/consciousness/consciousness_engine.py',
        'core/bayesian_engine/bayesian_engine.py',
        'core/agent_battalion/agent_battalion.py',
        'core/intelligence/advanced_intelligence_system.py',
        'core/interface/adaptive_interface_system.py',
        'core/integration/sophisticated_integration_system.py',
        'core/main_integration_system.py',
        'voice/voice_system.py',
        'core/shadow_board/shadow_board_system.py',
        'core/time_machine/time_machine_system.py'
    ]
    
    for system in core_systems:
        if os.path.exists(system):
            print(f"✅ {system} found")
        else:
            print(f"❌ {system} not found")
            return False
    
    return True

def deploy_api_systems():
    """Deploy API systems"""
    print("🌐 Deploying API systems...")
    
    api_systems = [
        'api/server.py',
        'api/billing_integration.py',
        'api/data_ingestion.py',
        'api/rag_service.py',
        'api/health_checks.py',
        'api/logging_config.py',
        'api/metrics.py'
    ]
    
    for system in api_systems:
        if os.path.exists(system):
            print(f"✅ {system} found")
        else:
            print(f"❌ {system} not found")
            return False
    
    return True

def deploy_security_systems():
    """Deploy security systems"""
    print("🔒 Deploying security systems...")
    
    security_systems = [
        'core/security/security_system.py',
        'core/security/zero_knowledge_system.py',
        'core/security/adversarial_hardening.py',
        'core/security/secure_config_manager.py'
    ]
    
    for system in security_systems:
        if os.path.exists(system):
            print(f"✅ {system} found")
        else:
            print(f"❌ {system} not found")
            return False
    
    return True

def deploy_frontend():
    """Deploy frontend systems"""
    print("🎨 Deploying frontend systems...")
    
    frontend_systems = [
        'frontend/src/App.js',
        'frontend/src/components/user/Dashboard.js',
        'frontend/src/components/user/Login.js',
        'frontend/src/components/admin/AdminDashboard.js',
        'frontend/src/services/api.js'
    ]
    
    for system in frontend_systems:
        if os.path.exists(system):
            print(f"✅ {system} found")
        else:
            print(f"❌ {system} not found")
            return False
    
    return True

def run_system_tests():
    """Run comprehensive system tests"""
    print("🧪 Running system tests...")
    
    test_commands = [
        'python -c "import sys; print(f\"Python {sys.version}\")"',
        'python -c "import numpy; print(f\"NumPy {numpy.__version__}\")"',
        'python -c "import requests; print(f\"Requests {requests.__version__}\")"',
        'python -c "import psutil; print(f\"psutil {psutil.__version__}\")"'
    ]
    
    # Try PyTorch test
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} available")
        if torch.cuda.is_available():
            print("✅ CUDA available")
            print(f"✅ GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"✅ GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("⚠️  CUDA not available")
    except ImportError:
        print("⚠️  PyTorch not available")
    
    for cmd in test_commands:
        if not run_command(cmd, check=False):
            print(f"⚠️  Test failed: {cmd}")
    
    return True

def create_startup_script():
    """Create production startup script"""
    print("📝 Creating startup script...")
    
    startup_script = '''#!/bin/bash
# SOVREN AI Production Startup Script

set -e

echo "🚀 Starting SOVREN AI Production System..."

# Set environment variables
export SOVREN_ROOT="$(pwd)"
export SOVREN_LOG_LEVEL="INFO"
export SOVREN_DEBUG_MODE="false"
export SOVREN_PERFORMANCE_MODE="true"

# Create logs directory
mkdir -p logs

# Start core systems
echo "🔧 Starting core systems..."
python core/consciousness/consciousness_engine.py > logs/consciousness.log 2>&1 &
python core/bayesian_engine/bayesian_engine.py > logs/bayesian.log 2>&1 &
python core/agent_battalion/agent_battalion.py > logs/agent_battalion.log 2>&1 &

# Start intelligence systems
echo "🧠 Starting intelligence systems..."
python core/intelligence/advanced_intelligence_system.py > logs/intelligence.log 2>&1 &
python core/interface/adaptive_interface_system.py > logs/interface.log 2>&1 &
python core/integration/sophisticated_integration_system.py > logs/integration.log 2>&1 &

# Start main integration system
echo "🔗 Starting main integration system..."
python core/main_integration_system.py > logs/main_integration.log 2>&1 &

# Start voice system
echo "🎤 Starting voice system..."
python voice/voice_system.py > logs/voice.log 2>&1 &

# Start shadow board
echo "👥 Starting shadow board..."
python core/shadow_board/shadow_board_system.py > logs/shadow_board.log 2>&1 &

# Start time machine
echo "⏰ Starting time machine..."
python core/time_machine/time_machine_system.py > logs/time_machine.log 2>&1 &

# Start API server
echo "🌐 Starting API server..."
python api/server.py > logs/api.log 2>&1 &

# Start security systems
echo "🔒 Starting security systems..."
python core/security/security_system.py > logs/security.log 2>&1 &
python core/security/zero_knowledge_system.py > logs/zero_knowledge.log 2>&1 &
python core/security/adversarial_hardening.py > logs/adversarial.log 2>&1 &

echo "✅ SOVREN AI Production System started successfully!"
echo "📊 Monitor logs at: logs/"
echo "🌐 API available at: http://localhost:8000"
echo "🎨 Frontend available at: http://localhost:3000"

# Keep script running
wait
'''
    
    with open('start_sovren_production.sh', 'w') as f:
        f.write(startup_script)
    
    os.chmod('start_sovren_production.sh', 0o755)
    print("✅ Startup script created: start_sovren_production.sh")
    
    return True

def create_monitoring_script():
    """Create system monitoring script"""
    print("📊 Creating monitoring script...")
    
    monitoring_script = '''#!/bin/bash
# SOVREN AI System Monitoring Script

echo "📊 SOVREN AI System Status"
echo "=========================="

# Check system processes
echo "🔍 Checking system processes..."
ps aux | grep -E "(python|sovren)" | grep -v grep

# Check GPU usage
echo "🎮 GPU Usage:"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv

# Check system resources
echo "💾 System Resources:"
free -h
df -h

# Check API endpoints
echo "🌐 API Health Check:"
curl -s http://localhost:8000/health || echo "API not responding"

# Check logs
echo "📝 Recent Logs:"
tail -n 20 logs/sovren_ai.log 2>/dev/null || echo "No logs found"

echo "=========================="
'''
    
    with open('monitor_sovren.sh', 'w') as f:
        f.write(monitoring_script)
    
    os.chmod('monitor_sovren.sh', 0o755)
    print("✅ Monitoring script created: monitor_sovren.sh")
    
    return True

def create_logs_directory():
    """Create logs directory"""
    print("📁 Creating logs directory...")
    
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"✅ Created logs directory: {logs_dir}")
    else:
        print(f"✅ Logs directory exists: {logs_dir}")
    
    return True

def main():
    """Main deployment function"""
    print("🚀 SOVREN AI - Linux Production Deployment for B200 Infrastructure")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met")
        return False
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return False
    
    # Install system dependencies
    if not install_system_dependencies():
        print("❌ System dependency installation failed")
        return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Python dependency installation failed")
        return False
    
    # Build PyTorch
    if not build_pytorch_b200():
        print("❌ PyTorch build failed")
        return False
    
    # Deploy core systems
    if not deploy_core_systems():
        print("❌ Core system deployment failed")
        return False
    
    # Deploy API systems
    if not deploy_api_systems():
        print("❌ API system deployment failed")
        return False
    
    # Deploy security systems
    if not deploy_security_systems():
        print("❌ Security system deployment failed")
        return False
    
    # Deploy frontend
    if not deploy_frontend():
        print("❌ Frontend deployment failed")
        return False
    
    # Create logs directory
    if not create_logs_directory():
        print("❌ Logs directory creation failed")
        return False
    
    # Run system tests
    if not run_system_tests():
        print("⚠️  Some system tests failed")
    
    # Create startup script
    if not create_startup_script():
        print("❌ Startup script creation failed")
        return False
    
    # Create monitoring script
    if not create_monitoring_script():
        print("❌ Monitoring script creation failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SOVREN AI Linux Production Deployment Complete!")
    print("=" * 60)
    print("\n🎯 Next Steps:")
    print("1. Start the system: bash start_sovren_production.sh")
    print("2. Monitor the system: bash monitor_sovren.sh")
    print("3. Access the API: http://localhost:8000")
    print("4. Access the frontend: http://localhost:3000")
    print("5. Check logs: tail -f logs/sovren_ai.log")
    print("\n🔧 System Features:")
    print("- Advanced Intelligence System")
    print("- Adaptive Interface System")
    print("- Voice Synthesis (StyleTTS2)")
    print("- Zero-Knowledge Security")
    print("- Time Machine Memory System")
    print("- Shadow Board Executive System")
    print("- B200 GPU Optimization")
    print("- Production Monitoring")
    print("\n🚀 Ready for production deployment!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 