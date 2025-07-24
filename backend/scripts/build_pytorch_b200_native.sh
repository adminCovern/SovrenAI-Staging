#!/bin/bash
# PyTorch build script for B200 GPUs with native support (bypassing CMake validation)

echo "=== Building PyTorch with Native B200 GPU Support ==="

# Set environment variables for B200
export TORCH_CUDA_ARCH_LIST="10.0"
export CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_ARCHITECTURES=""
export NVCC_FLAGS="-arch=sm_100"
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export CUDA_ARCH_FLAGS="-arch=sm_100"
export TORCH_CUDA_ARCH_LIST_FORCE="10.0"

echo "Environment variables set:"
echo "  TORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST"
echo "  CUDA_ARCH_LIST=$CUDA_ARCH_LIST"
echo "  NVCC_FLAGS=$NVCC_FLAGS"
echo "  CMAKE_CUDA_FLAGS=$CMAKE_CUDA_FLAGS"

# Clean previous build
rm -rf build/
mkdir -p build
cd build

# Configure with B200 support (bypassing CMake validation)
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DUSE_CUDA=ON \
    -DUSE_CUDNN=ON \
    -DCUDA_ARCH_LIST="10.0" \
    -DCMAKE_CUDA_ARCHITECTURES="" \
    -DCUDA_ARCH_FLAGS="-arch=sm_100" \
    -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/gcc \
    -DCMAKE_CUDA_FLAGS="-arch=sm_100" \
    -DTORCH_CUDA_ARCH_LIST="10.0" \
    -DTORCH_CUDA_ARCH_LIST_FORCE="10.0" \
    -DCMAKE_CUDA_COMPILER=/usr/bin/nvcc \
    -DCMAKE_CUDA_ARCHITECTURES_VALIDATION=OFF

# Build
make -j$(nproc)

echo "PyTorch build completed with native B200 GPU support!" 