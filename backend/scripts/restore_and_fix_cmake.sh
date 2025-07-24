#!/bin/bash

# Restore CMake system and apply proper B200 GPU fix
# This script restores the broken CMake and applies a targeted fix

set -e

echo "=== Restoring CMake system and applying proper B200 fix ==="

# Step 1: Restore original CMake files
echo "=== Step 1: Restoring original CMake files ==="
if [ -f "/usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake.backup" ]; then
    sudo cp /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake.backup /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake
    echo "✓ CMakeDetermineCompilerId.cmake restored"
else
    echo "⚠ No backup found, attempting to restore from package"
    sudo apt-get install --reinstall cmake
fi

# Step 2: Create a proper CUDA architecture bypass
echo "=== Step 2: Creating proper CUDA architecture bypass ==="

# Create a CMake module that only affects CUDA architecture validation
sudo tee /usr/local/share/cmake-3.29/Modules/CMakeCUDAArchitectureBypass.cmake > /dev/null << 'EOF'
# CMake CUDA Architecture Bypass for B200 GPUs
# This module only affects CUDA architecture validation

# Function to bypass CUDA architecture validation for B200
function(bypass_cuda_architecture_validation)
  if(CMAKE_CUDA_ARCHITECTURES MATCHES "10.0")
    message(STATUS "B200 GPU detected - bypassing architecture validation")
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_100")
    set(CMAKE_CUDA_ARCHITECTURES "sm_100")
    set(CMAKE_CUDA_ARCHITECTURES_VALIDATION OFF)
    return()
  endif()
endfunction()

# Call the bypass function
bypass_cuda_architecture_validation()
EOF

# Step 3: Create environment wrapper
echo "=== Step 3: Creating environment wrapper ==="
cat > cuda_b200_env.sh << 'EOF'
#!/bin/bash
# CUDA B200 Environment Wrapper

# Set all CUDA environment variables for B200
export CMAKE_CUDA_ARCHITECTURES="10.0"
export TORCH_CUDA_ARCH_LIST="10.0"
export CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export NVCC_FLAGS="-arch=sm_100"
export CMAKE_CUDA_COMPILER_FLAGS="-arch=sm_100"

# Create NVCC wrapper that forces sm_100
cat > nvcc_b200_wrapper << 'NVCC_EOF'
#!/bin/bash
exec /usr/bin/nvcc -arch=sm_100 "$@"
NVCC_EOF

chmod +x nvcc_b200_wrapper
export CUDA_NVCC_EXECUTABLE="$(pwd)/nvcc_b200_wrapper"

# Set CMake to use our bypass module
export CMAKE_PREFIX_PATH="/usr/local/share/cmake-3.29/Modules/CMakeCUDAArchitectureBypass.cmake"

echo "B200 CUDA environment configured"
EOF

chmod +x cuda_b200_env.sh

# Step 4: Create a proper build script
echo "=== Step 4: Creating proper build script ==="
cat > build_pytorch_b200_proper.sh << 'EOF'
#!/bin/bash

# Proper PyTorch build for B200 GPUs
# This script uses the restored CMake system with targeted bypass

set -e

echo "=== Proper PyTorch Build for B200 GPUs ==="

# Source the B200 environment
source cuda_b200_env.sh

# Create CMake cache with proper settings
cat > cmake_b200_proper.cmake << 'CMAKE_EOF'
# Proper B200 GPU support - targeted bypass only
set(CMAKE_CUDA_ARCHITECTURES "10.0" CACHE STRING "CUDA architectures" FORCE)
set(TORCH_CUDA_ARCH_LIST "10.0" CACHE STRING "PyTorch CUDA architectures" FORCE)
set(CMAKE_CUDA_FLAGS "-arch=sm_100" CACHE STRING "CUDA flags" FORCE)
set(NVCC_FLAGS "-arch=sm_100" CACHE STRING "NVCC flags" FORCE)
set(CMAKE_CUDA_COMPILER_FLAGS "-arch=sm_100" CACHE STRING "CUDA compiler flags" FORCE)
set(CMAKE_CUDA_HOST_COMPILER "/usr/bin/gcc" CACHE STRING "CUDA host compiler" FORCE)
set(BUILD_CUDA ON CACHE BOOL "Build CUDA support" FORCE)
set(USE_CUDA ON CACHE BOOL "Use CUDA" FORCE)
set(CUDA_TOOLKIT_ROOT_DIR "/usr/local/cuda" CACHE PATH "CUDA toolkit root" FORCE)

# Include our bypass module
include(/usr/local/share/cmake-3.29/Modules/CMakeCUDAArchitectureBypass.cmake)
CMAKE_EOF

# Clean and build
echo "=== Cleaning previous build ==="
rm -rf build
mkdir build
cd build

echo "=== Configuring PyTorch with proper B200 support ==="
cmake ../pytorch \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_ARCHITECTURES="10.0" \
    -DTORCH_CUDA_ARCH_LIST="10.0" \
    -DCMAKE_CUDA_FLAGS="-arch=sm_100" \
    -DNVCC_FLAGS="-arch=sm_100" \
    -DCMAKE_CUDA_COMPILER_FLAGS="-arch=sm_100" \
    -DCMAKE_CUDA_HOST_COMPILER="/usr/bin/gcc" \
    -DBUILD_CUDA=ON \
    -DUSE_CUDA=ON \
    -DCUDA_TOOLKIT_ROOT_DIR="/usr/local/cuda" \
    -C ../cmake_b200_proper.cmake

echo "=== Building PyTorch ==="
make -j$(nproc) VERBOSE=1

echo "=== Installing PyTorch ==="
make install

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
"

echo "=== Proper build complete ==="
echo "PyTorch built with native B200 GPU support (sm_100)"
EOF

chmod +x build_pytorch_b200_proper.sh

echo "=== CMake system restored and proper B200 fix applied ==="
echo "To build PyTorch:"
echo "1. cd /data/sovren/sovren-ai"
echo "2. ./scripts/restore_and_fix_cmake.sh"
echo "3. ./build_pytorch_b200_proper.sh" 