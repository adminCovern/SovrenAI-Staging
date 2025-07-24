# SOVREN AI - B200 Server Deployment Guide

## 🚀 Complete Production Deployment for B200 Infrastructure

This guide provides step-by-step instructions for deploying Sovren AI to your B200 server with bare metal installation and maximum performance optimization.

---

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04 LTS or later
- **CPU**: 64+ cores (B200 server)
- **RAM**: 2TB+ system memory
- **GPU**: 8+ B200 GPUs
- **Storage**: 10TB+ NVMe storage
- **Network**: 100Gbps+ connectivity

### Software Requirements
- Python 3.12+
- CUDA 12.0+
- NVIDIA drivers 550+
- Git
- CMake 3.25+

---

## 🔧 Step 1: System Preparation

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

### 1.2 Install Essential Dependencies
```bash
sudo apt install -y build-essential cmake git curl wget \
    python3-dev python3-pip python3-venv \
    libssl-dev libffi-dev libjpeg-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libgtk-3-dev libatlas-base-dev gfortran \
    libhdf5-dev libhdf5-serial-dev
```

### 1.3 Configure System Limits
```bash
# Add to /etc/security/limits.conf
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* soft nproc 32768" | sudo tee -a /etc/security/limits.conf
echo "* hard nproc 32768" | sudo tee -a /etc/security/limits.conf
```

---

## 🐍 Step 2: Python Environment Setup

### 2.1 Install Python 3.12
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-dev python3.12-venv
```

### 2.2 Create Virtual Environment
```bash
python3.12 -m venv /opt/sovren-ai
source /opt/sovren-ai/bin/activate
pip install --upgrade pip setuptools wheel
```

---

## 🔥 Step 3: CUDA and PyTorch Installation

### 3.1 Install CUDA Toolkit
```bash
# Download CUDA 12.0
wget https://developer.download.nvidia.com/compute/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux.run
sudo sh cuda_12.0.0_525.60.13_linux.run --silent --driver --toolkit --samples

# Add CUDA to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' | sudo tee -a /etc/profile
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' | sudo tee -a /etc/profile
source /etc/profile
```

### 3.2 Build PyTorch for B200
```bash
# Clone PyTorch
git clone https://github.com/pytorch/pytorch.git
cd pytorch

# Set environment variables for B200
export CMAKE_CUDA_ARCHITECTURES=10.0
export TORCH_CUDA_ARCH_LIST=10.0
export CUDA_ARCH_LIST=10.0
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export NVCC_FLAGS="-arch=sm_100"

# Build PyTorch
python setup.py install
```

---

## 🚀 Step 4: Deploy Sovren AI

### 4.1 Clone Repository
```bash
cd /opt
git clone https://github.com/your-repo/sovren-ai.git
cd sovren-ai
```

### 4.2 Install Python Dependencies
```bash
# Activate virtual environment
source /opt/sovren-ai/bin/activate

# Install requirements
pip install -r requirements.txt
pip install -r deployment/requirements.txt
```

### 4.3 Run Deployment Script
```bash
# Make deployment script executable
chmod +x deployment/deploy_sovren.py

# Run deployment as root
sudo python3 deployment/deploy_sovren.py
```

---

## 🔧 Step 5: System Configuration

### 5.1 Configure Services
```bash
# Create systemd service for Sovren AI
sudo tee /etc/systemd/system/sovren-ai.service << EOF
[Unit]
Description=Sovren AI Production Service
After=network.target

[Service]
Type=simple
User=sovren
Group=sovren
WorkingDirectory=/data/sovren
Environment=PATH=/opt/sovren-ai/bin
ExecStart=/opt/sovren-ai/bin/python /data/sovren/api/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create sovren user
sudo useradd -r -s /bin/false sovren
sudo mkdir -p /data/sovren
sudo chown -R sovren:sovren /data/sovren
```

### 5.2 Configure Firewall
```bash
# Allow necessary ports
sudo ufw allow 8000/tcp  # API Server
sudo ufw allow 8001/tcp  # Voice Service
sudo ufw allow 8002/tcp  # Admin Panel
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 6379/tcp  # Redis
sudo ufw allow 5060/tcp  # SIP
sudo ufw allow 10000:20000/udp  # RTP
```

---

## 🧪 Step 6: Testing and Validation

### 6.1 Run System Tests
```bash
# Run comprehensive test suite
python3 tests/elite_test_suite.py

# Test voice system
python3 scripts/test_voice_startup.py

# Test MCP server
python3 scripts/test_mcp_server.py
```

### 6.2 Performance Validation
```bash
# Test GPU performance
python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU count: {torch.cuda.device_count()}')
for i in range(torch.cuda.device_count()):
    print(f'GPU {i}: {torch.cuda.get_device_name(i)}')
"

# Test memory bandwidth
python3 core/performance/gpu_optimizer.py
```

---

## 📊 Step 7: Monitoring Setup

### 7.1 Install Monitoring Tools
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
sudo mv prometheus-* /opt/prometheus

# Install Grafana
wget https://dl.grafana.com/oss/release/grafana-10.0.3.linux-amd64.tar.gz
tar xvf grafana-*.tar.gz
sudo mv grafana-* /opt/grafana
```

### 7.2 Configure Monitoring
```bash
# Create Prometheus config
sudo tee /opt/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sovren-ai'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Start monitoring services
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

---

## 🔒 Step 8: Security Hardening

### 8.1 Configure Security
```bash
# Run security deployment
sudo python3 deployment/deploy_security_test.py

# Enable encryption
sudo python3 core/security/adversarial_hardening.py
```

### 8.2 SSL/TLS Setup
```bash
# Install Certbot
sudo apt install -y certbot

# Generate SSL certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com

# Configure SSL for services
sudo python3 scripts/configure_ssl.py
```

---

## 🚀 Step 9: Production Launch

### 9.1 Start All Services
```bash
# Start Sovren AI service
sudo systemctl enable sovren-ai
sudo systemctl start sovren-ai

# Start voice services
sudo python3 voice/deploy.py

# Start MCP server
sudo python3 scripts/deploy_mcp_server_b200_production.py
```

### 9.2 Verify Deployment
```bash
# Check service status
sudo systemctl status sovren-ai

# Check logs
tail -f /data/sovren/logs/deployment.log

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status
```

---

## 📈 Step 10: Performance Optimization

### 10.1 GPU Optimization
```bash
# Run GPU optimizer
python3 core/performance/gpu_optimizer.py

# Configure NUMA allocation
python3 core/performance/numa_allocator.py
```

### 10.2 Memory Optimization
```bash
# Configure huge pages
echo 'vm.nr_hugepages = 1024' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Optimize memory allocation
python3 core/performance/memory_optimizer.py
```

---

## 🔍 Troubleshooting

### Common Issues

1. **CUDA Installation Issues**
   ```bash
   # Check NVIDIA drivers
   nvidia-smi
   
   # Reinstall CUDA if needed
   sudo apt purge cuda*
   sudo apt autoremove
   # Follow Step 3.1 again
   ```

2. **PyTorch Build Issues**
   ```bash
   # Use alternative build method
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Service Startup Issues**
   ```bash
   # Check logs
   sudo journalctl -u sovren-ai -f
   
   # Restart service
   sudo systemctl restart sovren-ai
   ```

4. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Optimize memory
   python3 core/performance/memory_optimizer.py
   ```

---

## 📞 Support

For deployment issues:
1. Check logs: `/data/sovren/logs/`
2. Run diagnostics: `python3 scripts/diagnose_voice_system.py`
3. Test components: `python3 tests/elite_test_suite.py`

---

## ✅ Deployment Checklist

- [ ] System requirements met
- [ ] Python 3.12 installed
- [ ] CUDA 12.0 installed
- [ ] PyTorch built for B200
- [ ] Sovren AI deployed
- [ ] Services configured
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Security hardened
- [ ] Performance optimized
- [ ] All tests passed
- [ ] Services running
- [ ] SSL configured
- [ ] Backup configured

---

**🎯 Your B200 server is now ready to run Sovren AI at maximum performance!** 