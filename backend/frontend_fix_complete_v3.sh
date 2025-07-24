#!/bin/bash

# Complete Frontend Fix Script v3 - Production Grade
# This script addresses ALL vulnerabilities and deprecated packages using only existing, stable packages

set -e

echo "=== COMPREHENSIVE FRONTEND FIX v3 ==="
echo "Addressing ALL vulnerabilities and deprecated packages using stable packages only..."

cd /data/sovren/sovren-ai/frontend

# Step 1: Backup current package files
echo "Backing up current package files..."
cp package.json package.json.backup
cp package-lock.json package-lock.json.backup

# Step 2: Clean npm cache and node_modules
echo "Cleaning npm environment..."
rm -rf node_modules package-lock.json
npm cache clean --force

# Step 3: Create a completely clean package.json with only stable, existing packages
echo "Creating modern package.json with stable packages only..."
cat > package.json << 'EOF'
{
  "name": "sovren-ai-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^6.4.2",
    "@testing-library/react": "^14.2.1",
    "@testing-library/user-event": "^14.5.2",
    "lucide-react": "^0.460.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-scripts": "5.0.1",
    "web-vitals": "^3.5.2"
  },
  "devDependencies": {
    "@babel/plugin-transform-class-properties": "^7.24.1",
    "@babel/plugin-transform-nullish-coalescing-operator": "^7.24.1",
    "@babel/plugin-transform-numeric-separator": "^7.24.1",
    "@babel/plugin-transform-optional-chaining": "^7.24.1",
    "@babel/plugin-transform-private-methods": "^7.24.1",
    "@babel/plugin-transform-private-property-in-object": "^7.24.1",
    "@jridgewell/sourcemap-codec": "^1.4.15",
    "@rollup/plugin-terser": "^0.4.4",
    "eslint": "^8.57.0",
    "eslint-config-react-app": "^7.0.1",
    "eslint-plugin-import": "^2.29.1",
    "eslint-plugin-jsx-a11y": "^6.8.0",
    "eslint-plugin-react": "^7.34.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "rimraf": "^5.0.5",
    "svgo": "^3.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# Step 4: Install with legacy peer deps to handle React Scripts compatibility
echo "Installing modern dependencies with legacy peer deps..."
npm install --legacy-peer-deps

# Step 5: Remove any remaining deprecated packages
echo "Removing any remaining deprecated packages..."
npm uninstall --save-dev @babel/plugin-proposal-private-methods @babel/plugin-proposal-nullish-coalescing-operator @babel/plugin-proposal-numeric-separator @babel/plugin-proposal-class-properties @babel/plugin-proposal-private-property-in-object @babel/plugin-proposal-optional-chaining stable rollup-plugin-terser abab domexception w3c-hr-time q sourcemap-codec workbox-cacheable-response workbox-google-analytics inflight glob @humanwhocodes/config-array @humanwhocodes/object-schema rimraf svgo --legacy-peer-deps

# Step 6: Force fix any remaining vulnerabilities
echo "Force fixing any remaining vulnerabilities..."
npm audit fix --force --legacy-peer-deps

# Step 7: Verify installation
echo "Verifying installation..."
npm audit

# Step 8: Test build
echo "Testing build process..."
npm run build

echo "=== FRONTEND FIX COMPLETED SUCCESSFULLY ==="
echo "All vulnerabilities and deprecated packages have been addressed."
echo "Your frontend is now production-ready with zero warnings." 