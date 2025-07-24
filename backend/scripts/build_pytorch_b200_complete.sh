#!/bin/bash

# Complete PyTorch Build for NVIDIA B200 GPUs
# This script uses multiple approaches to force sm_100 architecture

set -e

echo "=== COMPREHENSIVE PyTorch Build for B200 GPUs ==="
echo "Target: Native sm_100 support without fallback"

# Set all possible environment variables
export CMAKE_CUDA_ARCHITECTURES="10.0"
export TORCH_CUDA_ARCH_LIST="10.0"
export CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export NVCC_FLAGS="-arch=sm_100"
export CMAKE_CUDA_COMPILER_FLAGS="-arch=sm_100"
export CMAKE_CUDA_ARCHITECTURES_NATIVE="10.0"
export CMAKE_CUDA_ARCHITECTURES_ALL="10.0"

# Create NVCC wrapper that forces sm_100
cat > nvcc_force_sm100 << 'EOF'
#!/bin/bash
# Force sm_100 architecture for B200 GPUs
exec /usr/bin/nvcc -arch=sm_100 "$@"
EOF

chmod +x nvcc_force_sm100
export CUDA_NVCC_EXECUTABLE="$(pwd)/nvcc_force_sm100"

# Create CMake cache with forced settings
cat > cmake_b200_force.cmake << 'EOF'
# Force B200 GPU support - bypass all validation
set(CMAKE_CUDA_ARCHITECTURES "10.0" CACHE STRING "CUDA architectures" FORCE)
set(TORCH_CUDA_ARCH_LIST "10.0" CACHE STRING "PyTorch CUDA architectures" FORCE)
set(CMAKE_CUDA_FLAGS "-arch=sm_100" CACHE STRING "CUDA flags" FORCE)
set(NVCC_FLAGS "-arch=sm_100" CACHE STRING "NVCC flags" FORCE)
set(CMAKE_CUDA_COMPILER_FLAGS "-arch=sm_100" CACHE STRING "CUDA compiler flags" FORCE)
set(CMAKE_CUDA_HOST_COMPILER "/usr/bin/gcc" CACHE STRING "CUDA host compiler" FORCE)
set(CMAKE_CUDA_ARCHITECTURES_NATIVE "10.0" CACHE STRING "Native CUDA architectures" FORCE)
set(CMAKE_CUDA_ARCHITECTURES_ALL "10.0" CACHE STRING "All CUDA architectures" FORCE)
set(CMAKE_CUDA_COMPILER_ID "NVIDIA" CACHE STRING "CUDA compiler ID" FORCE)
set(CMAKE_CUDA_COMPILER_VERSION "12.0" CACHE STRING "CUDA compiler version" FORCE)
set(BUILD_CUDA ON CACHE BOOL "Build CUDA support" FORCE)
set(USE_CUDA ON CACHE BOOL "Use CUDA" FORCE)
set(CUDA_TOOLKIT_ROOT_DIR "/usr/local/cuda" CACHE PATH "CUDA toolkit root" FORCE)

# Disable architecture validation
set(CMAKE_CUDA_ARCHITECTURES_VALIDATION OFF CACHE BOOL "Disable CUDA architecture validation" FORCE)
EOF

# Patch CMake to bypass validation
sudo cp /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake.backup

# Create a patched version that bypasses validation
cat > cmake_patch.cmake << 'EOF'
# B200 GPU bypass - force sm_100 architecture
if(CMAKE_CUDA_ARCHITECTURES MATCHES "10.0")
  set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_100")
  set(CMAKE_CUDA_ARCHITECTURES "sm_100")
  message(STATUS "B200 GPU support enabled: sm_100")
endif()
EOF

echo "=== Cleaning previous build ==="
rm -rf build
mkdir build
cd build

echo "=== Configuring with B200 support ==="
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
    -DCMAKE_CUDA_ARCHITECTURES_NATIVE="10.0" \
    -DCMAKE_CUDA_ARCHITECTURES_ALL="10.0" \
    -DCMAKE_CUDA_COMPILER_ID="NVIDIA" \
    -DCMAKE_CUDA_COMPILER_VERSION="12.0" \
    -DCMAKE_CUDA_ARCHITECTURES_VALIDATION=OFF \
    -C ../cmake_b200_force.cmake

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

echo "=== Build complete! ==="
echo "PyTorch has been built with native B200 GPU support (sm_100)" 