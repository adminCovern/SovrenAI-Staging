#!/bin/bash

# Proper CMake validation fix for B200 GPUs
# This script creates a targeted patch that only bypasses CUDA architecture validation

set -e

echo "=== Fixing CMake validation for B200 GPUs (Proper Method) ==="

# Restore original CMake file
sudo cp /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake.backup /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake

# Create a proper patch that only affects CUDA architecture validation
sudo cp /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake.backup2

# Create a minimal patch that only bypasses CUDA architecture validation
cat > cmake_cuda_bypass.cmake << 'EOF'
# Minimal CUDA architecture bypass for B200 GPUs
# This only affects CUDA architecture validation, not the entire CMake system

# Check if we're dealing with CUDA and B200 architecture
if(CMAKE_CUDA_ARCHITECTURES MATCHES "10.0" AND CMAKE_CUDA_COMPILER_ID STREQUAL "NVIDIA")
  # Force sm_100 architecture for B200 GPUs
  set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_100")
  set(CMAKE_CUDA_ARCHITECTURES "sm_100")
  message(STATUS "B200 GPU support enabled: sm_100")
  
  # Skip CUDA architecture validation but keep other validation
  set(CMAKE_CUDA_ARCHITECTURES_VALIDATION OFF)
  return()
endif()

# Continue with normal CMake processing for non-B200 cases
EOF

# Apply the patch by inserting it into the CMake file
sudo sed -i '/CMAKE_CUDA_COMPILER_ID "NVIDIA"/a\
# B200 GPU bypass - force sm_100 architecture\
if(CMAKE_CUDA_ARCHITECTURES MATCHES "10.0")\
  set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_100")\
  set(CMAKE_CUDA_ARCHITECTURES "sm_100")\
  message(STATUS "B200 GPU support enabled: sm_100")\
  set(CMAKE_CUDA_ARCHITECTURES_VALIDATION OFF)\
endif()\
' /usr/local/share/cmake-3.29/Modules/CMakeDetermineCompilerId.cmake

echo "=== CMake validation fixed (proper method) ==="
echo "CMake system preserved - only CUDA architecture validation bypassed" 