#!/bin/bash
# Fix CMake B200 compatibility by bypassing architecture validation

echo "=== Fixing CMake B200 Compatibility ==="

# Set environment variables to bypass CMake validation
export CMAKE_CUDA_ARCHITECTURES=""
export TORCH_CUDA_ARCH_LIST="10.0"
export CUDA_ARCH_LIST="10.0"

# Create a CMake patch to bypass architecture validation
cat > /tmp/cmake_b200_bypass.patch << 'EOF'
--- /usr/local/share/cmake-3.29/Modules/Internal/CMakeCUDAArchitecturesValidate.cmake
+++ /usr/local/share/cmake-3.29/Modules/Internal/CMakeCUDAArchitecturesValidate.cmake
@@ -6,6 +6,11 @@
   return()
 endif()
 
+# B200 GPU bypass - allow compute capability 10.0
+if(CMAKE_CUDA_ARCHITECTURES MATCHES "10.0")
+  return()
+endif()
+
 # Validate CMAKE_CUDA_ARCHITECTURES
 set(_valid_architectures "all" "all-major" "native")
 foreach(_arch ${CMAKE_CUDA_ARCHITECTURES})
EOF

# Apply the patch
echo "Applying CMake architecture validation bypass..."
sudo patch -p0 < /tmp/cmake_b200_bypass.patch

# Create environment setup script
cat > /tmp/setup_b200_env.sh << 'EOF'
#!/bin/bash
# Environment setup for B200 GPU support

export TORCH_CUDA_ARCH_LIST="10.0"
export CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_ARCHITECTURES=""
export NVCC_FLAGS="-arch=sm_100"
export CMAKE_CUDA_FLAGS="-arch=sm_100"

echo "B200 GPU environment variables set:"
echo "  TORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST"
echo "  CUDA_ARCH_LIST=$CUDA_ARCH_LIST"
echo "  NVCC_FLAGS=$NVCC_FLAGS"
echo "  CMAKE_CUDA_FLAGS=$CMAKE_CUDA_FLAGS"
EOF

chmod +x /tmp/setup_b200_env.sh

echo "=== B200 Compatibility Fix Applied ==="
echo "Run this before building PyTorch:"
echo "  source /tmp/setup_b200_env.sh"
echo ""
echo "Then build PyTorch with:"
echo "  bash /data/sovren/sovren-ai/scripts/build_pytorch_b200.sh" 