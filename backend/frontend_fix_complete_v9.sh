#!/bin/bash

# Complete Frontend Fix Script - Production Grade v9
# This script completely replaces problematic dependencies with modern, secure alternatives

set -e

echo "=== COMPREHENSIVE FRONTEND FIX v9 ==="
echo "Completely replacing problematic dependencies with modern alternatives..."

cd /data/sovren/sovren-ai/frontend

# Step 1: Backup current package files
echo "Backing up current package files..."
cp package.json package.json.backup
cp package-lock.json package-lock.json.backup

# Step 2: Clean npm cache and node_modules
echo "Cleaning npm environment..."
rm -rf node_modules package-lock.json
npm cache clean --force

# Step 3: Create a completely new package.json with modern dependencies
echo "Creating modern package.json with secure dependencies..."
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
    "web-vitals": "^3.5.2"
  },
  "devDependencies": {
    "@babel/core": "^7.24.1",
    "@babel/preset-env": "^7.24.1",
    "@babel/preset-react": "^7.24.1",
    "@eslint/config-array": "^1.0.0",
    "@eslint/object-schema": "^1.0.0",
    "@rollup/plugin-babel": "^6.0.4",
    "@rollup/plugin-commonjs": "^26.0.0",
    "@rollup/plugin-node-resolve": "^16.0.0",
    "@rollup/plugin-terser": "^0.4.4",
    "@rollup/plugin-url": "^8.0.2",
    "@svgr/rollup": "^9.0.0",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.15.0",
    "eslint-plugin-react": "^7.37.2",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.14",
    "postcss": "^8.4.49",
    "rollup": "^4.21.1",
    "rollup-plugin-postcss": "^4.0.2",
    "typescript": "^5.6.3",
    "vite": "^5.4.10"
  },
  "scripts": {
    "start": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx"
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

# Step 4: Create Vite configuration for React
echo "Creating Vite configuration..."
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'build',
    sourcemap: true
  }
})
EOF

# Step 5: Create PostCSS configuration
echo "Creating PostCSS configuration..."
cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    autoprefixer: {},
  },
}
EOF

# Step 6: Create ESLint configuration
echo "Creating ESLint configuration..."
cat > .eslintrc.js << 'EOF'
module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: ['react', 'react-hooks'],
  rules: {
    'react/react-in-jsx-scope': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
}
EOF

# Step 7: Install modern dependencies
echo "Installing modern, secure dependencies..."
npm install --legacy-peer-deps

# Step 8: Verify no vulnerabilities
echo "Verifying security..."
npm audit

# Step 9: Test build
echo "Testing build process..."
npm run build

echo "=== FRONTEND FIX v9 COMPLETED SUCCESSFULLY ==="
echo "All vulnerabilities eliminated. Modern, secure frontend ready for production." 