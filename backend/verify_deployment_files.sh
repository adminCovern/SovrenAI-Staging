#!/bin/bash

# SOVREN AI - Deployment File Verification Script
# Checks for all required files before deployment

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if file exists and is readable
check_file() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        if [[ -r "$file" ]]; then
            success "✅ $description: $file"
            return 0
        else
            error "❌ $description: $file (not readable)"
            return 1
        fi
    else
        error "❌ $description: $file (missing)"
        return 1
    fi
}

# Check if script is executable
check_executable() {
    local file="$1"
    local description="$2"
    
    if check_file "$file" "$description"; then
        if [[ -x "$file" ]]; then
            success "✅ $description: $file (executable)"
            return 0
        else
            warning "⚠️  $description: $file (not executable)"
            chmod +x "$file" 2>/dev/null && success "✅ Made executable: $file" || warning "⚠️  Could not make executable: $file"
            return 0
        fi
    else
        return 1
    fi
}

# Check directory structure
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [[ -d "$dir" ]]; then
        success "✅ $description: $dir"
        return 0
    else
        error "❌ $description: $dir (missing)"
        return 1
    fi
}

# Main verification function
verify_deployment_files() {
    log "Starting deployment file verification..."
    
    local errors=0
    local warnings=0
    
    echo
    echo "=========================================="
    echo "🔍 SOVREN AI DEPLOYMENT FILE VERIFICATION"
    echo "=========================================="
    echo
    
    # Check root directory
    if [[ ! -d "." ]]; then
        error "❌ Not in sovren-ai directory"
        exit 1
    fi
    
    # Critical deployment scripts
    echo "📦 Checking deployment scripts..."
    echo "----------------------------------------"
    
    check_executable "deploy_b200_complete.sh" "B200 deployment script" || ((errors++))
    check_executable "deploy_frontend_sovrenai.sh" "Frontend deployment script" || ((errors++))
    
    # Backend critical files
    echo
    echo "🔧 Checking backend critical files..."
    echo "----------------------------------------"
    
    check_file "deployment/deploy_sovren.py" "Core deployment script" || ((errors++))
    check_file "scripts/deploy_sovren_b200_linux.py" "B200-specific deployment" || ((errors++))
    check_file "config/sovren_config.py" "Main configuration" || ((errors++))
    check_file "requirements.txt" "Python dependencies" || ((errors++))
    check_file "deployment/requirements.txt" "Deployment dependencies" || ((errors++))
    check_file "api/server.py" "Main API server" || ((errors++))
    check_file "core/main_integration_system.py" "Core integration" || ((errors++))
    check_file "voice/deploy.py" "Voice system deployment" || ((errors++))
    check_file "scripts/enterprise_mcp_server.py" "MCP server" || ((errors++))
    check_file "tests/elite_test_suite.py" "Test suite" || ((errors++))
    
    # Frontend critical files
    echo
    echo "🌐 Checking frontend critical files..."
    echo "----------------------------------------"
    
    check_file "frontend/package.json" "Node.js dependencies" || ((errors++))
    check_file "frontend/public/index.html" "Main HTML file" || ((errors++))
    check_file "frontend/public/manifest.json" "PWA manifest" || ((errors++))
    check_file "frontend/src/App.js" "Main React app" || ((errors++))
    check_file "frontend/src/index.js" "React entry point" || ((errors++))
    check_file "frontend/src/services/api.js" "API client" || ((errors++))
    check_file "frontend/src/contexts/AuthContext.js" "Auth context" || ((errors++))
    check_file "nginx_sovrenai_app.conf" "Nginx configuration" || ((errors++))
    
    # Configuration files
    echo
    echo "📋 Checking configuration files..."
    echo "----------------------------------------"
    
    check_file "SOVRENAI_APP_DEPLOYMENT_GUIDE.md" "Complete deployment guide" || ((warnings++))
    check_file "B200_DEPLOYMENT_GUIDE.md" "B200 deployment guide" || ((warnings++))
    check_file "QUICK_START_B200.md" "Quick start guide" || ((warnings++))
    check_file "scripts/deploy_config.yaml" "Deployment configuration" || ((warnings++))
    check_file "scripts/sovren-mcp.service" "Systemd service file" || ((warnings++))
    
    # Check directory structure
    echo
    echo "📁 Checking directory structure..."
    echo "----------------------------------------"
    
    check_directory "api" "API directory" || ((errors++))
    check_directory "core" "Core systems directory" || ((errors++))
    check_directory "database" "Database directory" || ((errors++))
    check_directory "voice" "Voice system directory" || ((errors++))
    check_directory "config" "Configuration directory" || ((errors++))
    check_directory "deployment" "Deployment scripts directory" || ((errors++))
    check_directory "scripts" "Utility scripts directory" || ((errors++))
    check_directory "tests" "Test suites directory" || ((errors++))
    check_directory "logs" "Logs directory" || ((warnings++))
    check_directory "docs" "Documentation directory" || ((warnings++))
    check_directory "frontend" "Frontend directory" || ((errors++))
    check_directory "frontend/src" "React source directory" || ((errors++))
    check_directory "frontend/public" "Static assets directory" || ((errors++))
    
    # Check for additional important files
    echo
    echo "🔍 Checking additional important files..."
    echo "----------------------------------------"
    
    # Backend additional files
    local backend_files=(
        "core/consciousness/consciousness_engine.py"
        "core/bayesian_engine/bayesian_engine.py"
        "core/agent_battalion/agent_battalion.py"
        "core/intelligence/advanced_intelligence_system.py"
        "core/interface/adaptive_interface_system.py"
        "core/integration/sophisticated_integration_system.py"
        "core/shadow_board/enhanced_shadow_board.py"
        "core/time_machine/time_machine_system.py"
        "core/security/adversarial_hardening.py"
        "core/performance/gpu_optimizer.py"
        "voice/awakening_handler.py"
        "database/connection.py"
        "database/models.py"
    )
    
    for file in "${backend_files[@]}"; do
        if [[ -f "$file" ]]; then
            success "✅ Backend file: $file"
        else
            warning "⚠️  Missing backend file: $file"
            ((warnings++))
        fi
    done
    
    # Frontend additional files
    local frontend_files=(
        "frontend/src/components/user/Login.js"
        "frontend/src/components/user/Dashboard.js"
        "frontend/src/components/admin/AdminLogin.js"
        "frontend/src/components/admin/AdminDashboard.js"
        "frontend/src/components/PrivateRoute.js"
        "frontend/src/components/AdminRoute.js"
    )
    
    for file in "${frontend_files[@]}"; do
        if [[ -f "$file" ]]; then
            success "✅ Frontend file: $file"
        else
            warning "⚠️  Missing frontend file: $file"
            ((warnings++))
        fi
    done
    
    # Check file sizes
    echo
    echo "📊 Checking file sizes..."
    echo "----------------------------------------"
    
    local total_size=$(du -sh . 2>/dev/null | cut -f1)
    echo "Total directory size: $total_size"
    
    # Check for large files that might cause issues
    local large_files=$(find . -type f -size +100M 2>/dev/null | head -5)
    if [[ -n "$large_files" ]]; then
        warning "⚠️  Large files detected (may slow upload):"
        echo "$large_files"
    fi
    
    # Summary
    echo
    echo "=========================================="
    echo "📋 VERIFICATION SUMMARY"
    echo "=========================================="
    echo
    
    if [[ $errors -eq 0 ]]; then
        success "✅ All critical files present!"
        echo
        if [[ $warnings -eq 0 ]]; then
            success "✅ No warnings - deployment ready!"
        else
            warning "⚠️  $warnings warnings (non-critical files missing)"
        fi
    else
        error "❌ $errors critical files missing!"
        echo
        error "Please ensure all critical files are present before deployment."
    fi
    
    echo
    echo "🚀 Next steps:"
    echo "1. Upload files to B200 server"
    echo "2. Run: chmod +x deploy_b200_complete.sh"
    echo "3. Run: sudo ./deploy_b200_complete.sh"
    echo "4. Run: chmod +x deploy_frontend_sovrenai.sh"
    echo "5. Run: sudo ./deploy_frontend_sovrenai.sh"
    echo
    
    if [[ $errors -gt 0 ]]; then
        exit 1
    else
        success "🎉 Deployment files verified successfully!"
        exit 0
    fi
}

# Run verification
verify_deployment_files 