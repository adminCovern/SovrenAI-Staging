#!/usr/bin/env python3
"""
SOVREN AI MCP SERVER DEPLOYMENT - SIMPLE
Deploys the user's original MCP server script as a production service
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Deploy the MCP server as a production service"""
    print("=" * 60)
    print("SOVREN AI MCP SERVER DEPLOYMENT")
    print("=" * 60)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        sys.exit(1)
    
    # Step 1: Install dependencies
    print("\n1. Installing dependencies...")
    try:
        # Update package list
        subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
        
        # Check what Python versions are available
        result = subprocess.run(['apt-cache', 'search', 'python3'], capture_output=True, text=True)
        available_pythons = result.stdout
        
        # Try to install Python 3.12, fall back to 3.11, then 3.10
        python_versions = ['python3.12', 'python3.11', 'python3.10']
        python_installed = None
        
        for version in python_versions:
            try:
                print(f"   Trying to install {version}...")
                subprocess.run(['apt-get', 'install', '-y', version], check=True, capture_output=True)
                python_installed = version
                print(f"   ✅ {version} installed successfully")
                break
            except subprocess.CalledProcessError:
                print(f"   ❌ {version} not available, trying next version...")
                continue
        
        if not python_installed:
            print("❌ No suitable Python version found. Available versions:")
            print(available_pythons)
            sys.exit(1)
        
        # Install pip for the installed Python version
        pip_package = f"{python_installed}-pip"
        try:
            subprocess.run(['apt-get', 'install', '-y', pip_package], check=True, capture_output=True)
            print(f"   ✅ {pip_package} installed")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  {pip_package} not available, trying alternative...")
            # Try installing pip via get-pip.py
            subprocess.run(['curl', 'https://bootstrap.pypa.io/get-pip.py', '-o', 'get-pip.py'], check=True, capture_output=True)
            subprocess.run([python_installed, 'get-pip.py'], check=True, capture_output=True)
            os.remove('get-pip.py')
            print(f"   ✅ pip installed via get-pip.py")
        
        # Install psutil
        try:
            subprocess.run([python_installed, '-m', 'pip', 'install', 'psutil'], check=True, capture_output=True)
            print(f"   ✅ psutil installed")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to install psutil via pip: {e}")
            # Try apt package
            try:
                subprocess.run(['apt-get', 'install', '-y', 'python3-psutil'], check=True, capture_output=True)
                print(f"   ✅ psutil installed via apt")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install psutil")
                sys.exit(1)
        
        print("✅ Dependencies installed")
        
        # Store the Python version for later use
        with open("/opt/sovren/python_version.txt", "w") as f:
            f.write(python_installed)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Available Python packages:")
        subprocess.run(['apt-cache', 'search', 'python3'], capture_output=False)
        sys.exit(1)
    
    # Step 2: Create service user
    print("\n2. Creating service user...")
    try:
        subprocess.run(['useradd', '-r', '-s', '/bin/false', 'sovrenmcp'], capture_output=True)
        print("✅ Service user created")
    except subprocess.CalledProcessError:
        print("ℹ️  Service user already exists")
    
    # Step 3: Deploy MCP server
    print("\n3. Deploying MCP server...")
    install_path = Path("/opt/sovren/mcp")
    install_path.mkdir(parents=True, exist_ok=True)
    
    # Copy the MCP server script (assuming it's in the current directory)
    mcp_script = Path("mcp_server.py")
    if not mcp_script.exists():
        print("❌ MCP server script not found. Please ensure mcp_server.py is in the current directory.")
        sys.exit(1)
    
    shutil.copy2(mcp_script, install_path / "mcp_server.py")
    os.chmod(install_path / "mcp_server.py", 0o750)
    subprocess.run(['chown', 'sovrenmcp:sovrenmcp', str(install_path / "mcp_server.py")], check=True)
    print("✅ MCP server deployed")
    
    # Step 4: Create systemd service
    print("\n4. Creating systemd service...")
    
    # Get the installed Python version
    try:
        with open("/opt/sovren/python_version.txt", "r") as f:
            python_version = f.read().strip()
    except FileNotFoundError:
        python_version = "python3"  # fallback
    
    service_content = f"""[Unit]
Description=SOVREN AI MCP Server
After=network.target

[Service]
Type=simple
User=sovrenmcp
Group=sovrenmcp
WorkingDirectory=/opt/sovren/mcp
ExecStart=/usr/bin/{python_version} /opt/sovren/mcp/mcp_server.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/sovren-mcp-server.log
StandardError=append:/var/log/sovren-mcp-server.log
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
"""
    
    with open("/etc/systemd/system/sovren-mcp.service", "w") as f:
        f.write(service_content)
    
    # Reload systemd and enable service
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'enable', 'sovren-mcp'], check=True)
    print("✅ Systemd service created")
    
    # Step 5: Start service
    print("\n5. Starting MCP server...")
    try:
        subprocess.run(['systemctl', 'start', 'sovren-mcp'], check=True)
        print("✅ MCP server started")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start service: {e}")
        sys.exit(1)
    
    # Step 6: Verify service
    print("\n6. Verifying service...")
    try:
        result = subprocess.run(['systemctl', 'is-active', 'sovren-mcp'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip() == 'active':
            print("✅ MCP server is running")
        else:
            print(f"⚠️  Service status: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Service verification failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 SOVREN AI MCP SERVER DEPLOYMENT COMPLETE")
    print("=" * 60)
    print("\nService Information:")
    print(f"  Service: sovren-mcp")
    print(f"  Port: 9999")
    print(f"  Logs: /var/log/sovren-mcp-server.log")
    print(f"  Status: sudo systemctl status sovren-mcp")
    print(f"  Restart: sudo systemctl restart sovren-mcp")
    print(f"  Stop: sudo systemctl stop sovren-mcp")
    print("\nThe MCP server is now running as a production service!")

if __name__ == "__main__":
    main() 