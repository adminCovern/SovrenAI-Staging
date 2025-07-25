#!/bin/bash

# Fix for spandsp dependency issue
# FreeSWITCH requires spandsp >= 3.0

echo "Fixing spandsp dependency..."

# First, check what spandsp packages are available
echo "Available spandsp packages:"
apt search spandsp 2>/dev/null | grep -E "(spandsp|libspandsp)"

# Try installing different spandsp packages
echo "Installing spandsp packages..."
sudo apt install -y libspandsp-dev libspandsp2-dev

# Check if spandsp3 is available
if apt list spandsp3 2>/dev/null | grep -q spandsp3; then
    echo "Installing spandsp3..."
    sudo apt install -y spandsp3 libspandsp3-dev
fi

# If spandsp3 is not available, we may need to build it from source
if ! pkg-config --exists spandsp; then
    echo "spandsp3 not found in repositories, building from source..."
    
    # Install build dependencies for spandsp
    sudo apt install -y build-essential autoconf automake libtool pkg-config
    
    # Download and build spandsp from source
    cd /tmp
    wget https://www.soft-switch.org/downloads/spandsp/spandsp-3.0.0.tar.gz
    tar -xzf spandsp-3.0.0.tar.gz
    cd spandsp-3.0.0
    
    ./configure --prefix=/usr/local
    make
    sudo make install
    sudo ldconfig
    
    echo "spandsp built and installed from source"
fi

# Verify spandsp installation
echo "Checking spandsp installation:"
pkg-config --modversion spandsp 2>/dev/null || echo "spandsp not found via pkg-config"
ldconfig -p | grep spandsp || echo "spandsp libraries not found"

echo "spandsp fix completed" 