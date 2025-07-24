# 🚀 SOVREN AI B200 Quick Start Guide

## Deploy Sovren AI to Your B200 Server in 3 Steps

---

## 📋 Prerequisites

Before starting, ensure your B200 server has:
- Ubuntu 22.04 LTS
- NVIDIA drivers 550+
- 64GB+ RAM
- 100GB+ free disk space
- Root/sudo access

---

## 🎯 Step 1: Upload and Prepare

### 1.1 Upload Sovren AI to your B200 server
```bash
# On your local machine, upload the code
scp -r sovren-ai/ user@your-b200-server:/tmp/
```

### 1.2 SSH into your B200 server
```bash
ssh user@your-b200-server
```

### 1.3 Navigate to the code directory
```bash
cd /tmp/sovren-ai
```

---

## 🔥 Step 2: Run Automated Deployment

### 2.1 Make the deployment script executable
```bash
chmod +x deploy_b200_complete.sh
```

### 2.2 Run the complete deployment
```bash
sudo ./deploy_b200_complete.sh
```

**This will automatically:**
- ✅ Install Python 3.12
- ✅ Install CUDA 12.0
- ✅ Build PyTorch for B200
- ✅ Deploy all Sovren AI components
- ✅ Configure services and firewall
- ✅ Run comprehensive tests
- ✅ Start all services

**Expected time: 2-3 hours** (mostly PyTorch compilation)

---

## 🎉 Step 3: Verify Deployment

### 3.1 Check service status
```bash
sudo systemctl status sovren-ai
```

### 3.2 Test API endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status
```

### 3.3 Check GPU utilization
```bash
nvidia-smi
```

### 3.4 View logs
```bash
sudo journalctl -u sovren-ai -f
```

---

## 🔧 Management Commands

### Service Management
```bash
# Start service
sudo systemctl start sovren-ai

# Stop service
sudo systemctl stop sovren-ai

# Restart service
sudo systemctl restart sovren-ai

# Check status
sudo systemctl status sovren-ai

# View logs
sudo journalctl -u sovren-ai -f
```

### System Monitoring
```bash
# Check GPU status
nvidia-smi

# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Status check
curl http://localhost:8000/api/v1/status

# Voice service
curl http://localhost:8001/status
```

---

## 🌐 Access Points

Once deployed, access Sovren AI at:

- **API Server**: http://your-server-ip:8000
- **Voice Service**: http://your-server-ip:8001
- **Admin Panel**: http://your-server-ip:8002
- **API Documentation**: http://your-server-ip:8000/docs

---

## 🔍 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u sovren-ai -f
   
   # Check permissions
   sudo chown -R sovren:sovren /data/sovren
   ```

2. **GPU not detected**
   ```bash
   # Check NVIDIA drivers
   nvidia-smi
   
   # Reinstall drivers if needed
   sudo apt install nvidia-driver-550
   ```

3. **Port already in use**
   ```bash
   # Find process using port
   sudo netstat -tlnp | grep :8000
   
   # Kill process
   sudo kill -9 <PID>
   ```

4. **Memory issues**
   ```bash
   # Check memory usage
   free -h
   
   # Restart service
   sudo systemctl restart sovren-ai
   ```

---

## 📊 Performance Optimization

### GPU Optimization
```bash
# Run GPU optimizer
cd /data/sovren/sovren-ai
source /opt/sovren-ai/bin/activate
python core/performance/gpu_optimizer.py
```

### Memory Optimization
```bash
# Configure huge pages
echo 'vm.nr_hugepages = 1024' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## 🔒 Security

### SSL/TLS Setup (Optional)
```bash
# Install Certbot
sudo apt install certbot

# Generate SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure SSL
sudo python3 scripts/configure_ssl.py
```

### Firewall Status
```bash
# Check firewall status
sudo ufw status

# Allow additional ports if needed
sudo ufw allow 443/tcp  # HTTPS
```

---

## 📈 Monitoring

### Install Monitoring Tools (Optional)
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

---

## ✅ Success Indicators

Your deployment is successful when:

- ✅ `sudo systemctl status sovren-ai` shows "active (running)"
- ✅ `curl http://localhost:8000/health` returns success
- ✅ `nvidia-smi` shows GPU utilization
- ✅ `sudo journalctl -u sovren-ai` shows no errors
- ✅ All API endpoints respond correctly

---

## 🆘 Support

If you encounter issues:

1. **Check logs**: `sudo journalctl -u sovren-ai -f`
2. **Run diagnostics**: `python3 scripts/diagnose_voice_system.py`
3. **Test components**: `python3 tests/elite_test_suite.py`
4. **Review deployment guide**: `B200_DEPLOYMENT_GUIDE.md`

---

## 🎯 Next Steps

After successful deployment:

1. **Configure your domain** and SSL certificates
2. **Set up monitoring** with Prometheus/Grafana
3. **Configure backups** for production data
4. **Test all features** thoroughly
5. **Document your setup** for team members

---

**🎉 Congratulations! Your B200 server is now running Sovren AI at maximum performance!**

The system is autonomous, secure, and ready for production use with all sophisticated features enabled. 