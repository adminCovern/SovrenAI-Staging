#!/usr/bin/env python3
"""
PyTorch B200 GPU Support Patch
This script patches PyTorch's build system to support NVIDIA B200 GPUs (sm_100)
"""

import os
import re
import shutil
import subprocess
import sys

def patch_cmake_files():
    """Patch CMake files to support B200 GPUs"""
    
    # Patch cuda.cmake
    cuda_cmake_path = "cmake/public/cuda.cmake"
    if os.path.exists(cuda_cmake_path):
        print(f"Patching {cuda_cmake_path}...")
        
        with open(cuda_cmake_path, 'r') as f:
            content = f.read()
        
        # Add B200 support
        b200_support = '''
# B200 GPU Support (sm_100)
if(TORCH_CUDA_ARCH_LIST MATCHES "10.0")
  set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_100")
  set(CMAKE_CUDA_ARCHITECTURES "sm_100")
  message(STATUS "B200 GPU support enabled: sm_100")
endif()
'''
        
        # Insert after CUDA architecture detection
        pattern = r'(set\(CMAKE_CUDA_ARCHITECTURES.*?\))'
        replacement = r'\1\n' + b200_support
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(cuda_cmake_path, 'w') as f:
            f.write(content)
        
        print("✓ cuda.cmake patched")

def patch_setup_py():
    """Patch setup.py to support B200 GPUs"""
    
    setup_py_path = "setup.py"
    if os.path.exists(setup_py_path):
        print(f"Patching {setup_py_path}...")
        
        with open(setup_py_path, 'r') as f:
            content = f.read()
        
        # Add B200 architecture
        b200_arch = '''
    # B200 GPU support
    if '10.0' in os.environ.get('TORCH_CUDA_ARCH_LIST', ''):
        cuda_arch_list.append('10.0')
        print("B200 GPU support enabled: sm_100")
'''
        
        # Find CUDA architecture list
        pattern = r'(cuda_arch_list\s*=\s*\[.*?\])'
        replacement = r'\1\n' + b200_arch
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(setup_py_path, 'w') as f:
            f.write(content)
        
        print("✓ setup.py patched")

def patch_nvcc_flags():
    """Patch NVCC flags to force sm_100"""
    
    # Create environment override
    env_patch = '''
# B200 GPU Environment Override
export CMAKE_CUDA_FLAGS="-arch=sm_100"
export NVCC_FLAGS="-arch=sm_100"
export TORCH_CUDA_ARCH_LIST="10.0"
export CMAKE_CUDA_ARCHITECTURES="10.0"
'''
    
    with open("b200_env.sh", 'w') as f:
        f.write(env_patch)
    
    os.chmod("b200_env.sh", 0o755)
    print("✓ Environment override created")

def create_nvcc_wrapper():
    """Create NVCC wrapper that forces sm_100"""
    
    wrapper_content = '''#!/bin/bash
# NVCC wrapper for B200 GPUs
exec /usr/bin/nvcc -arch=sm_100 "$@"
'''
    
    with open("nvcc_b200", 'w') as f:
        f.write(wrapper_content)
    
    os.chmod("nvcc_b200", 0o755)
    print("✓ NVCC wrapper created")

def main():
    """Main patch function"""
    
    print("=== PyTorch B200 GPU Support Patch ===")
    
    # Check if we're in PyTorch directory
    if not os.path.exists("setup.py"):
        print("Error: Must run from PyTorch source directory")
        sys.exit(1)
    
    # Create backup
    backup_dir = "pytorch_backup_$(date +%Y%m%d_%H%M%S)"
    print(f"Creating backup: {backup_dir}")
    shutil.copytree(".", f"../{backup_dir}", ignore=shutil.ignore_patterns("build", "*.pyc", "__pycache__"))
    
    # Apply patches
    patch_cmake_files()
    patch_setup_py()
    patch_nvcc_flags()
    create_nvcc_wrapper()
    
    print("\n=== Patch Complete ===")
    print("To build PyTorch with B200 support:")
    print("1. source b200_env.sh")
    print("2. export CUDA_NVCC_EXECUTABLE=$(pwd)/nvcc_b200")
    print("3. python setup.py build")
    print("4. python setup.py install")

if __name__ == "__main__":
    main() 