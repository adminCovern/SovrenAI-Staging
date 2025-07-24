#!/usr/bin/env node

/**
 * Setup script for Sovren AI Workspace
 * Installs dependencies and verifies the workspace configuration
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Setting up Sovren AI Workspace...\n');

// Check if we're in the right directory
if (!fs.existsSync('package.json')) {
    console.error('❌ Error: package.json not found. Please run this script from the workspace root.');
    process.exit(1);
}

// Check workspace structure
const requiredDirs = ['frontend', 'backend', 'shared'];
const missingDirs = requiredDirs.filter(dir => !fs.existsSync(dir));

if (missingDirs.length > 0) {
    console.error(`❌ Error: Missing required directories: ${missingDirs.join(', ')}`);
    process.exit(1);
}

console.log('✅ Workspace structure verified');

// Install root dependencies
console.log('\n📦 Installing root dependencies...');
try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✅ Root dependencies installed');
} catch (error) {
    console.error('❌ Failed to install root dependencies:', error.message);
    process.exit(1);
}

// Install frontend dependencies
console.log('\n📦 Installing frontend dependencies...');
try {
    execSync('cd frontend && npm install', { stdio: 'inherit' });
    console.log('✅ Frontend dependencies installed');
} catch (error) {
    console.error('❌ Failed to install frontend dependencies:', error.message);
    process.exit(1);
}

// Install shared dependencies
console.log('\n📦 Installing shared dependencies...');
try {
    execSync('cd shared && npm install', { stdio: 'inherit' });
    console.log('✅ Shared dependencies installed');
} catch (error) {
    console.error('❌ Failed to install shared dependencies:', error.message);
    process.exit(1);
}

// Build shared package
console.log('\n🔨 Building shared package...');
try {
    execSync('cd shared && npm run build', { stdio: 'inherit' });
    console.log('✅ Shared package built');
} catch (error) {
    console.error('❌ Failed to build shared package:', error.message);
    process.exit(1);
}

// Verify TypeScript compilation
console.log('\n🔍 Verifying TypeScript compilation...');
try {
    execSync('cd frontend && npx tsc --noEmit', { stdio: 'inherit' });
    console.log('✅ TypeScript compilation verified');
} catch (error) {
    console.error('❌ TypeScript compilation failed:', error.message);
    console.log('💡 This might be due to missing dependencies. Please check the error messages above.');
}

console.log('\n🎉 Workspace setup complete!');
console.log('\n📋 Next steps:');
console.log('1. Create a .env.local file with your configuration');
console.log('2. Run "npm run dev" to start development servers');
console.log('3. Open http://localhost:3000 to view the frontend');
console.log('4. Open http://localhost:3001 to view the backend API');

console.log('\n📚 Available commands:');
console.log('- npm run dev          # Start both frontend and backend');
console.log('- npm run dev:frontend # Start only frontend');
console.log('- npm run dev:backend  # Start only backend');
console.log('- npm run build        # Build all packages');
console.log('- npm test             # Run all tests');
console.log('- npm run lint         # Lint all code'); 