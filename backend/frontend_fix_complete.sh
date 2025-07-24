#!/bin/bash

# Complete Frontend Fix Script - Production Grade
# This script addresses ALL vulnerabilities and deprecated packages

set -e

echo "=== COMPREHENSIVE FRONTEND FIX ==="
echo "Addressing ALL vulnerabilities and deprecated packages..."

cd /data/sovren/sovren-ai/frontend

# Step 1: Backup current package files
echo "Backing up current package files..."
cp package.json package.json.backup
cp package-lock.json package-lock.json.backup

# Step 2: Clean npm cache and node_modules
echo "Cleaning npm environment..."
rm -rf node_modules package-lock.json
npm cache clean --force

# Step 3: Update to latest React Scripts and core dependencies
echo "Updating to latest stable versions..."
npm install --save react@^18.3.1 react-dom@^18.3.1 react-scripts@^5.0.1

# Step 4: Install modern alternatives to deprecated packages
echo "Installing modern alternatives to deprecated packages..."

# Replace deprecated Babel plugins with modern transforms
npm install --save-dev @babel/plugin-transform-private-methods@^7.24.1 \
    @babel/plugin-transform-nullish-coalescing-operator@^7.24.1 \
    @babel/plugin-transform-numeric-separator@^7.24.1 \
    @babel/plugin-transform-class-properties@^7.24.1 \
    @babel/plugin-transform-private-property-in-object@^7.24.1 \
    @babel/plugin-transform-optional-chaining@^7.24.1

# Remove deprecated Babel plugins
npm uninstall @babel/plugin-proposal-private-methods \
    @babel/plugin-proposal-nullish-coalescing-operator \
    @babel/plugin-proposal-numeric-separator \
    @babel/plugin-proposal-class-properties \
    @babel/plugin-proposal-private-property-in-object \
    @babel/plugin-proposal-optional-chaining

# Update ESLint to latest version
npm install --save-dev eslint@^9.15.0 @eslint/config-array@^1.0.0 @eslint/object-schema@^1.0.0

# Replace deprecated packages with modern alternatives
npm install --save-dev @rollup/plugin-terser@^4.0.0 \
    @jridgewell/sourcemap-codec@^1.4.15 \
    svgo@^3.2.0 \
    rimraf@^6.0.1 \
    glob@^10.3.10

# Remove deprecated packages
npm uninstall stable rollup-plugin-terser abab domexception w3c-hr-time q sourcemap-codec \
    workbox-cacheable-response workbox-google-analytics inflight @humanwhocodes/config-array \
    @humanwhocodes/object-schema

# Step 5: Update all dependencies to latest secure versions
echo "Updating all dependencies to latest secure versions..."
npm update

# Step 6: Install missing modern packages
echo "Installing missing modern packages..."
npm install --save lucide-react@^0.460.0
npm install --save-dev @types/react@^18.3.12 @types/react-dom@^18.3.1

# Step 7: Force fix any remaining vulnerabilities
echo "Force fixing remaining vulnerabilities..."
npm audit fix --force

# Step 8: Verify the fix
echo "Verifying the fix..."
npm audit

# Step 9: Test the build
echo "Testing the build..."
npm run build

echo "=== FRONTEND FIX COMPLETE ==="
echo "All vulnerabilities and deprecated packages have been addressed."
echo "The frontend is now production-ready with modern, secure dependencies." 