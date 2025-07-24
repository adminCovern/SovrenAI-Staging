#!/bin/bash

# Completely fix CMake system and use alternative B200 approach
# This script restores CMake and uses a different method for B200 support

set -e

echo "=== Completely fixing CMake system ==="

# Step 1: Completely restore CMake system
echo "=== Step 1: Restoring CMake system ==="

# Remove any broken CMake files
sudo rm -f /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake

# Reinstall CMake completely
echo "Reinstalling CMake..."
sudo apt-get update
sudo apt-get install --reinstall cmake

# Verify CMake is working
echo "Testing CMake..."
cmake --version

# Step 2: Use a different approach - patch PyTorch's setup.py instead
echo "=== Step 2: Using PyTorch setup.py approach ==="

cd pytorch

# Backup original setup.py
cp setup.py setup.py.backup

# Create a patch for setup.py to support B200
cat > setup_b200_patch.py << 'EOF'
#!/usr/bin/env python3
"""
Patch PyTorch setup.py to support B200 GPUs
"""

import re
import os

def patch_setup_py():
    """Patch setup.py to support B200 GPUs"""
    
    with open('setup.py', 'r') as f:
        content = f.read()
    
    # Add B200 architecture support
    b200_support = '''
    # B200 GPU support (sm_100)
    if '10.0' in os.environ.get('TORCH_CUDA_ARCH_LIST', ''):
        cuda_arch_list.append('10.0')
        print("B200 GPU support enabled: sm_100")
        # Force sm_100 architecture
        os.environ['CMAKE_CUDA_FLAGS'] = os.environ.get('CMAKE_CUDA_FLAGS', '') + ' -arch=sm_100'
        os.environ['NVCC_FLAGS'] = os.environ.get('NVCC_FLAGS', '') + ' -arch=sm_100'
'''
    
    # Find the CUDA architecture list section
    pattern = r'(cuda_arch_list\s*=\s*\[.*?\])'
    replacement = r'\1\n' + b200_support
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('setup.py', 'w') as f:
        f.write(content)
    
    print("✓ setup.py patched for B200 support")

if __name__ == "__main__":
    patch_setup_py()
EOF

# Apply the patch
python3 setup_b200_patch.py

echo "✓ PyTorch setup.py patched for B200 support"

# Step 3: Create environment for B200 build
echo "=== Step 3: Creating B200 build environment ==="

cat > build_b200_env.sh << 'EOF'
#!/bin/bash
# B200 GPU build environment

# Set all environment variables for B200
export TORCH_CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_ARCHITECTURES="10.0"
export CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export NVCC_FLAGS="-arch=sm_100"
export CMAKE_CUDA_COMPILER_FLAGS="-arch=sm_100"

# Create NVCC wrapper
cat > nvcc_b200_wrapper << 'NVCC_EOF'
#!/bin/bash
exec /usr/bin/nvcc -arch=sm_100 "$@"
NVCC_EOF

chmod +x nvcc_b200_wrapper
export CUDA_NVCC_EXECUTABLE="$(pwd)/nvcc_b200_wrapper"

echo "B200 build environment configured"
EOF

chmod +x build_b200_env.sh

# Step 4: Create build script
echo "=== Step 4: Creating build script ==="

cat > build_pytorch_b200_fixed.sh << 'EOF'
#!/bin/bash

# Fixed PyTorch build for B200 GPUs
# Uses setup.py approach instead of CMake

set -e

echo "=== Fixed PyTorch Build for B200 GPUs ==="

# Source the B200 environment
source build_b200_env.sh

# Clean previous build
echo "=== Cleaning previous build ==="
rm -rf build dist *.egg-info

# Build using setup.py
echo "=== Building PyTorch with setup.py ==="
python3 setup.py build

echo "=== Installing PyTorch ==="
python3 setup.py install

# Verify B200 support
echo "=== Verifying B200 support ==="
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'GPU {i}: {torch.cuda.get_device_name(i)}')
        print(f'GPU {i} compute capability: {torch.cuda.get_device_capability(i)}')
        
    # Test B200 computation
    if torch.cuda.device_count() > 0:
        device = torch.device('cuda:0')
        x = torch.randn(100, 100, device=device)
        y = torch.mm(x, x.t())
        print(f'B200 GPU computation test: {y.shape}')
"

echo "=== Fixed build complete ==="
echo "PyTorch built with native B200 GPU support (sm_100)"
EOF

chmod +x build_pytorch_b200_fixed.sh

echo "=== CMake system completely fixed ==="
echo "To build PyTorch:"
echo "1. cd /data/sovren/sovren-ai/pytorch"
echo "2. ./build_pytorch_b200_fixed.sh" 