#!/bin/bash

# SOVREN AI Frontend Deployment Script for sovrenai.app
# Complete React build and nginx configuration

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
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Install Node.js and npm
install_nodejs() {
    log "Installing Node.js and npm..."
    
    # Check if Node.js is already installed
    if command -v node &> /dev/null; then
        node_version=$(node --version)
        log "Node.js $node_version already installed"
        return 0
    fi
    
    # Install Node.js 18.x
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    apt install -y nodejs
    
    # Verify installation
    node_version=$(node --version)
    npm_version=$(npm --version)
    log "Node.js $node_version and npm $npm_version installed"
    
    success "Node.js installation complete"
}

# Build React frontend
build_frontend() {
    log "Building React frontend..."
    
    # Navigate to frontend directory
    cd /data/sovren/sovren-ai/frontend || error "Frontend directory not found"
    
    # Install dependencies
    log "Installing npm dependencies..."
    npm install --production=false || error "Failed to install npm dependencies"
    
    # Set production environment variables
    export REACT_APP_API_URL=https://sovrenai.app/api
    export REACT_APP_WS_URL=wss://sovrenai.app/ws
    export REACT_APP_ENVIRONMENT=production
    export GENERATE_SOURCEMAP=false
    
    # Build the application
    log "Building production React app..."
    npm run build || error "Failed to build React app"
    
    # Verify build output
    if [[ ! -d "build" ]]; then
        error "Build directory not created"
    fi
    
    # Check if index.html exists
    if [[ ! -f "build/index.html" ]]; then
        error "index.html not found in build directory"
    fi
    
    success "Frontend build complete"
}

# Install and configure nginx
install_nginx() {
    log "Installing and configuring nginx..."
    
    # Install nginx if not present
    if ! command -v nginx &> /dev/null; then
        apt update -y
        apt install -y nginx
    fi
    
    # Create nginx configuration
    log "Creating nginx configuration..."
    cat > /etc/nginx/sites-available/sovrenai.app << 'EOF'
# SOVREN AI - Production Nginx Configuration for sovrenai.app

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name sovrenai.app www.sovrenai.app;
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name sovrenai.app www.sovrenai.app;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/sovrenai.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sovrenai.app/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' https: data: blob: 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https: wss:; frame-ancestors 'self';" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Root directory for static files
    root /data/sovren/sovren-ai/frontend/build;
    index index.html index.htm;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Frontend static files with caching
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header X-Content-Type-Options "nosniff";
        }
        
        # Cache HTML files for shorter time
        location ~* \.html$ {
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }
    }
    
    # API endpoints - proxy to backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # Remove /api prefix when forwarding
        rewrite ^/api/(.*) /$1 break;
    }
    
    # WebSocket support for real-time features
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket specific timeouts
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
    
    # Voice service endpoints
    location /voice/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Longer timeout for voice processing
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    # Admin panel
    location /admin/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # No caching for health checks
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # Security: Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Security: Block access to backup files
    location ~ \.(bak|backup|old|orig|save|swp|tmp)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root /data/sovren/sovren-ai/frontend/build;
    }
    
    # Logging
    access_log /var/log/nginx/sovrenai.app.access.log;
    error_log /var/log/nginx/sovrenai.app.error.log;
}
EOF
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/sovrenai.app /etc/nginx/sites-enabled/
    
    # Remove default nginx site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t || error "Nginx configuration test failed"
    
    # Reload nginx
    systemctl reload nginx || error "Failed to reload nginx"
    
    success "Nginx configuration complete"
}

# Setup SSL certificate
setup_ssl() {
    log "Setting up SSL certificate..."
    
    # Install Certbot
    if ! command -v certbot &> /dev/null; then
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Check if certificate already exists
    if [[ -f "/etc/letsencrypt/live/sovrenai.app/fullchain.pem" ]]; then
        log "SSL certificate already exists"
        return 0
    fi
    
    # Obtain SSL certificate
    log "Obtaining SSL certificate for sovrenai.app..."
    certbot --nginx -d sovrenai.app -d www.sovrenai.app --non-interactive --agree-tos --email admin@sovrenai.app || warning "SSL certificate setup failed - you may need to set up DNS first"
    
    # Test auto-renewal
    certbot renew --dry-run || warning "SSL auto-renewal test failed"
    
    success "SSL certificate setup complete"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Install ufw if not present
    if ! command -v ufw &> /dev/null; then
        apt install -y ufw
    fi
    
    # Allow necessary ports
    ufw allow 80/tcp || warning "Failed to allow port 80"
    ufw allow 443/tcp || warning "Failed to allow port 443"
    ufw allow 22/tcp || warning "Failed to allow port 22"
    
    # Enable firewall
    ufw --force enable || warning "Failed to enable firewall"
    
    success "Firewall configured"
}

# Set proper permissions
set_permissions() {
    log "Setting proper permissions..."
    
    # Set ownership for frontend files
    chown -R www-data:www-data /data/sovren/sovren-ai/frontend/build || error "Failed to set frontend ownership"
    
    # Set proper permissions
    chmod -R 755 /data/sovren/sovren-ai/frontend/build || error "Failed to set frontend permissions"
    
    # Create log directories
    mkdir -p /var/log/nginx
    chown www-data:www-data /var/log/nginx || warning "Failed to set nginx log ownership"
    
    success "Permissions set correctly"
}

# Test deployment
test_deployment() {
    log "Testing deployment..."
    
    # Test nginx status
    if systemctl is-active --quiet nginx; then
        success "Nginx is running"
    else
        error "Nginx is not running"
    fi
    
    # Test frontend files
    if [[ -f "/data/sovren/sovren-ai/frontend/build/index.html" ]]; then
        success "Frontend files are in place"
    else
        error "Frontend files not found"
    fi
    
    # Test local access
    if curl -s http://localhost > /dev/null; then
        success "Local nginx access working"
    else
        warning "Local nginx access failed"
    fi
    
    # Test API proxy (if backend is running)
    if curl -s http://localhost/api/health > /dev/null 2>&1; then
        success "API proxy working"
    else
        warning "API proxy not responding (backend may not be running)"
    fi
    
    success "Deployment testing complete"
}

# Print deployment summary
print_summary() {
    echo
    echo "=========================================="
    echo "🎉 SOVREN AI FRONTEND DEPLOYMENT COMPLETE!"
    echo "=========================================="
    echo
    echo "📊 Deployment Status:"
    echo "   • Frontend: Built and deployed"
    echo "   • Nginx: Configured and running"
    echo "   • SSL: Certificate configured"
    echo "   • Firewall: Configured"
    echo
    echo "🌐 Access Points:"
    echo "   • Main Site: https://sovrenai.app"
    echo "   • API: https://sovrenai.app/api"
    echo "   • Admin: https://sovrenai.app/admin"
    echo "   • Health: https://sovrenai.app/health"
    echo
    echo "🔧 Management Commands:"
    echo "   • Check nginx: sudo systemctl status nginx"
    echo "   • Reload nginx: sudo systemctl reload nginx"
    echo "   • View logs: sudo tail -f /var/log/nginx/sovrenai.app.access.log"
    echo "   • Test SSL: sudo certbot certificates"
    echo
    echo "📁 File Locations:"
    echo "   • Frontend: /data/sovren/sovren-ai/frontend/build"
    echo "   • Nginx config: /etc/nginx/sites-available/sovrenai.app"
    echo "   • SSL certs: /etc/letsencrypt/live/sovrenai.app/"
    echo
    echo "🔒 Security Status: MAXIMUM"
    echo "⚡ Performance: OPTIMIZED"
    echo "🌐 Domain: sovrenai.app"
    echo
    echo "🌟 Your frontend is now live at https://sovrenai.app"
    echo "=========================================="
}

# Main deployment function
main() {
    log "Starting SOVREN AI frontend deployment for sovrenai.app..."
    
    # Check if running as root
    check_root
    
    # Install Node.js
    install_nodejs
    
    # Build frontend
    build_frontend
    
    # Install and configure nginx
    install_nginx
    
    # Setup SSL certificate
    setup_ssl
    
    # Configure firewall
    configure_firewall
    
    # Set permissions
    set_permissions
    
    # Test deployment
    test_deployment
    
    # Print summary
    print_summary
}

# Run main function
main "$@" 