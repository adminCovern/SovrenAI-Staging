#!/usr/bin/env python3
"""
Analyze deployment package contents and verify all required files are present.
"""

import tarfile
import os
import json
from pathlib import Path

def analyze_deployment_package(package_path):
    """Analyze the deployment package and return its contents."""
    if not os.path.exists(package_path):
        return None, f"Package {package_path} not found"
    
    try:
        with tarfile.open(package_path, 'r:gz') as tar:
            contents = tar.getnames()
            return contents, None
    except Exception as e:
        return None, f"Error reading package: {e}"

def get_required_files():
    """Define all required files for deployment."""
    return {
        # Backend core files
        'api/': 'Backend API directory',
        'core/': 'Core Sovren AI modules',
        'database/': 'Database models and connection',
        'scripts/': 'Deployment and utility scripts',
        'config/': 'Configuration files',
        'consciousness/': 'Consciousness engine',
        'voice/': 'Voice processing modules',
        
        # Critical backend files
        'requirements.txt': 'Python dependencies',
        'mcp_server.py': 'Main MCP server',
        'deploy_b200_complete.sh': 'B200 deployment script',
        'nginx_sovrenai_app.conf': 'Nginx configuration',
        'deploy_frontend_sovrenai.sh': 'Frontend deployment script',
        
        # Frontend files
        'frontend/': 'Frontend React app',
        'frontend/src/': 'React source code',
        'frontend/public/': 'Public assets',
        'frontend/package.json': 'Frontend dependencies',
        'frontend/index.html': 'Main HTML file',
        'frontend/manifest.json': 'PWA manifest',
        
        # Documentation and guides
        'B200_DEPLOYMENT_GUIDE.md': 'B200 deployment guide',
        'SOVRENAI_APP_DEPLOYMENT_GUIDE.md': 'Complete deployment guide',
        'DEPLOYMENT_FILE_LIST.md': 'File list documentation',
        'YOUR_DESKTOP_FILE_LOCATIONS.md': 'File locations guide',
        'verify_deployment_files.sh': 'Verification script',
        
        # Configuration files
        'pyrightconfig.json': 'Type checking config',
        'QUICK_START_B200.md': 'Quick start guide',
        'PRODUCTION_READY_STATUS.md': 'Production status',
        
        # Test files
        'tests/': 'Test suite',
        'test_consciousness_fix.py': 'Consciousness test',
        
        # Deployment scripts
        'deployment/': 'Deployment scripts directory',
        'scripts/admin_configure_stripe.py': 'Stripe configuration',
        'scripts/build_pytorch_b200_complete.sh': 'PyTorch build script',
        'scripts/build_pytorch_b200_direct.sh': 'Direct PyTorch build',
    }

def check_package_completeness(package_contents, required_files):
    """Check if the package contains all required files."""
    missing_files = []
    present_files = []
    partial_matches = []
    
    for required_file, description in required_files.items():
        found = False
        for content in package_contents:
            # Check for exact matches or directory matches
            if (content.endswith(required_file) or 
                content.startswith(f"./{required_file}") or
                content.startswith(required_file)):
                present_files.append((required_file, description))
                found = True
                break
        
        if not found:
            # Check for partial matches (directories)
            if required_file.endswith('/'):
                for content in package_contents:
                    if (content.startswith(required_file) or 
                        content.startswith(f"./{required_file}")):
                        partial_matches.append((required_file, description))
                        found = True
                        break
        
        if not found:
            missing_files.append((required_file, description))
    
    return present_files, missing_files, partial_matches

def main():
    """Main analysis function."""
    package_path = 'sovren-ai-deployment.tar.gz'
    
    print("🔍 Analyzing deployment package...")
    print(f"Package: {package_path}")
    print("=" * 60)
    
    # Analyze package contents
    contents, error = analyze_deployment_package(package_path)
    if error:
        print(f"❌ Error: {error}")
        return
    
    if contents:
        print(f"📦 Package contains {len(contents)} files/directories")
    else:
        print("📦 Package appears to be empty or corrupted")
        return
    print()
    
    # Get required files
    required_files = get_required_files()
    
    # Check completeness
    present, missing, partial = check_package_completeness(contents, required_files)
    
    # Report results
    print("✅ PRESENT FILES:")
    print("-" * 40)
    for file_path, description in present:
        print(f"  ✓ {file_path} - {description}")
    
    print()
    print("📁 PARTIAL MATCHES (Directories):")
    print("-" * 40)
    for file_path, description in partial:
        print(f"  📁 {file_path} - {description}")
    
    print()
    if missing:
        print("❌ MISSING FILES:")
        print("-" * 40)
        for file_path, description in missing:
            print(f"  ✗ {file_path} - {description}")
    else:
        print("🎉 ALL REQUIRED FILES ARE PRESENT!")
    
    print()
    print("📊 SUMMARY:")
    print(f"  Total required: {len(required_files)}")
    print(f"  Present: {len(present)}")
    print(f"  Partial matches: {len(partial)}")
    print(f"  Missing: {len(missing)}")
    
    if missing:
        print("\n⚠️  WARNING: Some required files are missing!")
        print("   You may need to recreate the deployment package.")
    else:
        print("\n✅ SUCCESS: Package contains all required files!")
        print("   Ready for deployment to B200 server.")

if __name__ == "__main__":
    main() 