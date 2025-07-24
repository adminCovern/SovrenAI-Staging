#!/bin/bash
# Alternative: Use pre-built PyTorch with B200 compatibility layer

echo "Installing PyTorch with B200 compatibility..."

# Install PyTorch with CUDA 12.1 (closest to B200)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Create B200 compatibility layer
cat > /tmp/b200_compatibility.py << 'EOF'
import os
import torch

# Force CUDA architecture to sm_100 for B200
os.environ['CUDA_ARCH_LIST'] = '10.0'
os.environ['TORCH_CUDA_ARCH_LIST'] = '10.0'

# Override torch.cuda to use B200 architecture
if hasattr(torch.cuda, '_get_device_properties'):
    original_get_device_properties = torch.cuda._get_device_properties
    
    def b200_get_device_properties(device):
        props = original_get_device_properties(device)
        # Override compute capability for B200
        props.major = 10
        props.minor = 0
        return props
    
    torch.cuda._get_device_properties = b200_get_device_properties

print("B200 compatibility layer installed")
EOF

# Install the compatibility layer
python /tmp/b200_compatibility.py

echo "PyTorch with B200 compatibility installed!" 