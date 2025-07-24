# SOVREN AI Launcher - Troubleshooting Guide

## Common Issues and Solutions

### 1. Import Errors

#### Problem: "Import could not be resolved from source"
**Solution:**
```bash
# Install missing dependencies
python scripts/fix_imports.py

# Or install all dependencies
python scripts/install_dependencies.py
```

#### Problem: "Module not found" errors
**Solution:**
```bash
# Check if packages are installed
pip list | grep psutil
pip list | grep PyYAML
pip list | grep requests

# Install missing packages
pip install psutil PyYAML requests cryptography
```

### 2. Type Checking Issues

#### Problem: Pyright/PyLance import warnings
**Solution:**
```bash
# Run type checking verification
python scripts/check_types.py

# Install type checking tools
pip install pyright mypy

# Configure your IDE to use the pyrightconfig.json
```

#### Problem: Test file import warnings
**Solution:**
```bash
# Setup test environment
python scripts/setup_test_env.py

# Run test validation
python scripts/test_launch_sovren.py

# Check test dependencies
python scripts/check_types.py
```

#### Problem: "reportMissingModuleSource" warnings
**Solution:**
- The `pyrightconfig.json` file disables these warnings
- Type stubs are provided in `scripts/typings/`
- Add `# type: ignore` comments for external imports

### 3. Installation Issues

#### Problem: Permission denied errors
**Solution:**
```bash
# Use virtual environment
python -m venv sovren_env
source sovren_env/bin/activate  # Linux/Mac
# or
sovren_env\Scripts\activate     # Windows

# Install dependencies
pip install -r scripts/requirements.txt
```

#### Problem: Python version compatibility
**Solution:**
```bash
# Check Python version
python --version

# Must be Python 3.8+
# If using older version, upgrade Python
```

### 4. Runtime Issues

#### Problem: "psutil not found" at runtime
**Solution:**
```bash
# Install psutil
pip install psutil>=5.9.0

# Or run the fix script
python scripts/fix_imports.py
```

#### Problem: "yaml not found" at runtime
**Solution:**
```bash
# Install PyYAML
pip install PyYAML>=6.0

# Or run the fix script
python scripts/fix_imports.py
```

### 5. IDE Configuration

#### VS Code Configuration
Add to `.vscode/settings.json`:
```json
{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.autoSearchPaths": true,
    "python.analysis.extraPaths": ["./scripts/typings"]
}
```

#### PyCharm Configuration
1. Go to Settings → Project → Python Interpreter
2. Add `scripts/typings` to Python Path
3. Install required packages via PyCharm package manager

### 6. Type Stub Issues

#### Problem: Type stubs not recognized
**Solution:**
```bash
# Create typings directory
mkdir -p scripts/typings

# Ensure __init__.py exists
touch scripts/typings/__init__.py

# Run type checking
python scripts/check_types.py
```

### 7. Development Environment

#### Setting up for development:
```bash
# Install development dependencies
pip install -r scripts/requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run type checking
python scripts/check_types.py

# Run tests
python scripts/test_launch_sovren.py
```

### 8. Production Deployment Issues

#### Problem: Directory permissions
**Solution:**
```bash
# Create required directories with proper permissions
sudo mkdir -p /data/sovren/{models,logs,voice,config,temp,certs}
sudo chown -R $USER:$USER /data/sovren
chmod 700 /data/sovren
```

#### Problem: Environment variables not set
**Solution:**
```bash
# Set required environment variables
export SOVREN_SECURITY_KEY="your-secure-key-here"
export SOVREN_ENV="production"
export SOVREN_LOG_LEVEL="INFO"
```

### 9. Performance Issues

#### Problem: High memory usage
**Solution:**
- Check memory limits in `deploy_config.yaml`
- Monitor with: `python scripts/launch_sovren.py --monitor-resources`
- Adjust service memory limits as needed

#### Problem: Slow startup
**Solution:**
- Check startup timeouts in configuration
- Monitor GPU availability: `nvidia-smi`
- Verify network connectivity

### 10. Security Issues

#### Problem: Authentication failures
**Solution:**
```bash
# Check security configuration
python scripts/launch_sovren.py --validate-security

# Verify security key
echo $SOVREN_SECURITY_KEY

# Check logs for authentication errors
tail -f /data/sovren/logs/sovren_launcher.log | grep AUTH
```

### 11. Network Issues

#### Problem: Health check failures
**Solution:**
```bash
# Test network connectivity
curl http://localhost:8001/health

# Check if services are running
ps aux | grep python

# Verify port availability
netstat -tlnp | grep :8001
```

### 12. Logging Issues

#### Problem: No logs generated
**Solution:**
```bash
# Check log directory permissions
ls -la /data/sovren/logs/

# Set log level
export SOVREN_LOG_LEVEL=DEBUG

# Check if logging is working
python scripts/launch_sovren.py --verbose
```

## Quick Diagnostic Commands

```bash
# Check system health
python scripts/launch_sovren.py --check-prerequisites

# Verify dependencies
python scripts/fix_imports.py

# Run type checking
python scripts/check_types.py

# Test installation
python scripts/test_launch_sovren.py

# Monitor resources
python scripts/launch_sovren.py --monitor-resources
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: `/data/sovren/logs/sovren_launcher.log`
2. **Run diagnostics**: `python scripts/check_types.py`
3. **Verify installation**: `python scripts/install_dependencies.py`
4. **Check documentation**: `cat scripts/README.md`

For enterprise support:
- Email: support@sovren-ai.com
- Documentation: https://docs.sovren-ai.com
- Issues: https://github.com/sovren-ai/sovren-ai/issues 