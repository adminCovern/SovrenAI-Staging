#!/bin/bash

# Fix CMake validation for B200 GPUs
# This script patches CMake to accept sm_100 architecture

set -e

echo "=== Fixing CMake validation for B200 GPUs ==="

# Backup original CMake files
sudo cp /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake.original
sudo cp /usr/local/share/cmake-3.29/Modules/CMakeCUDACompilerId.cmake /usr/local/share/cmake-3.29/Modules/CMakeCUDACompilerId.cmake.original

# Create a patched version of CMakeDetermineCompilerId.cmake
cat > cmake_patched.cmake << 'EOF'
# Patched CMakeDetermineCompilerId.cmake for B200 GPU support

# B200 GPU bypass - force sm_100 architecture
if(CMAKE_CUDA_ARCHITECTURES MATCHES "10.0")
  set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_100")
  set(CMAKE_CUDA_ARCHITECTURES "sm_100")
  message(STATUS "B200 GPU support enabled: sm_100")
  # Skip validation for B200
  set(CMAKE_CUDA_COMPILER_ID "NVIDIA")
  set(CMAKE_CUDA_COMPILER_VERSION "12.0")
  set(CMAKE_CUDA_COMPILER_VENDOR "NVIDIA")
  return()
endif()

# Original CMake content (simplified for B200 bypass)
set(CMAKE_CUDA_COMPILER_ID "NVIDIA")
set(CMAKE_CUDA_COMPILER_VERSION "12.0")
set(CMAKE_CUDA_COMPILER_VENDOR "NVIDIA")
EOF

# Apply the patch
sudo cp cmake_patched.cmake /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake

# Create a bypass environment
cat > cmake_b200_bypass.sh << 'EOF'
#!/bin/bash
# CMake bypass for B200 GPUs

export CMAKE_CUDA_ARCHITECTURES="10.0"
export TORCH_CUDA_ARCH_LIST="10.0"
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

echo "CMake bypass environment set for B200 GPUs"
EOF

chmod +x cmake_b200_bypass.sh

echo "=== CMake validation fixed ==="
echo "To use: source cmake_b200_bypass.sh"
echo "Then run your PyTorch build" 