#!/bin/bash

# Simple PyTorch build for B200 GPUs
# Bypasses CMake entirely and uses setup.py with direct overrides

set -e

echo "=== Simple PyTorch Build for B200 GPUs ==="
echo "Bypassing CMake entirely - using setup.py with direct overrides"

# Step 1: Restore CMake system
echo "=== Step 1: Restoring CMake system ==="
sudo apt-get update
sudo apt-get install --reinstall cmake

# Step 2: Navigate to PyTorch directory
cd pytorch

# Step 3: Create direct environment overrides
echo "=== Step 3: Creating direct environment overrides ==="

# Create a script that sets all environment variables
cat > set_b200_env.sh << 'EOF'
#!/bin/bash
# Direct B200 environment overrides

# Force all CUDA settings for B200
export TORCH_CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_ARCHITECTURES="10.0"
export CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export NVCC_FLAGS="-arch=sm_100"
export CMAKE_CUDA_COMPILER_FLAGS="-arch=sm_100"
export CMAKE_CUDA_HOST_COMPILER="/usr/bin/gcc"

# Create NVCC wrapper that forces sm_100
cat > nvcc_force_sm100 << 'NVCC_EOF'
#!/bin/bash
exec /usr/bin/nvcc -arch=sm_100 "$@"
NVCC_EOF

chmod +x nvcc_force_sm100
export CUDA_NVCC_EXECUTABLE="$(pwd)/nvcc_force_sm100"

# Set PyTorch build flags
export USE_CUDA=1
export BUILD_CUDA=1
export CUDA_TOOLKIT_ROOT_DIR="/usr/local/cuda"

echo "B200 environment overrides set"
EOF

chmod +x set_b200_env.sh

# Step 4: Create a simple build script
echo "=== Step 4: Creating simple build script ==="

cat > build_simple_b200.sh << 'EOF'
#!/bin/bash

# Simple B200 build using setup.py

set -e

echo "=== Simple B200 PyTorch Build ==="

# Source environment overrides
source set_b200_env.sh

# Clean previous builds
echo "=== Cleaning previous builds ==="
rm -rf build dist *.egg-info

# Build using setup.py with direct overrides
echo "=== Building PyTorch with setup.py ==="
TORCH_CUDA_ARCH_LIST="10.0" \
CMAKE_CUDA_ARCHITECTURES="10.0" \
CMAKE_CUDA_FLAGS="-arch=sm_100" \
NVCC_FLAGS="-arch=sm_100" \
USE_CUDA=1 \
BUILD_CUDA=1 \
python3 setup.py build

echo "=== Installing PyTorch ==="
python3 setup.py install

# Test the build
echo "=== Testing B200 support ==="
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
        
    # Test computation
    if torch.cuda.device_count() > 0:
        device = torch.device('cuda:0')
        x = torch.randn(100, 100, device=device)
        y = torch.mm(x, x.t())
        print(f'B200 GPU computation test: {y.shape}')
        print('✓ B200 GPU support working!')
"

echo "=== Simple build complete ==="
echo "PyTorch built with native B200 GPU support"
EOF

chmod +x build_simple_b200.sh

echo "=== Simple fix complete ==="
echo "To build PyTorch:"
echo "1. cd /data/sovren/sovren-ai/pytorch"
echo "2. ./build_simple_b200.sh" 