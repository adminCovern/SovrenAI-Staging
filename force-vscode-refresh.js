#!/usr/bin/env node

/**
 * Force VS Code Refresh Script
 * Forces VS Code to recognize the new file structure and clear all caches
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔄 Forcing VS Code refresh...\n');

// Check if we're in the right directory
if (!fs.existsSync('package.json')) {
    console.error('❌ Error: package.json not found. Please run this script from the workspace root.');
    process.exit(1);
}

console.log('✅ Workspace structure verified');

// Clear all possible caches
console.log('\n🧹 Clearing all caches...');

const cacheDirs = [
    'frontend/.next',
    'frontend/node_modules/.cache',
    'frontend/.tsbuildinfo',
    'node_modules/.cache',
    '.vscode/settings.json'
];

cacheDirs.forEach(dir => {
    if (fs.existsSync(dir)) {
        try {
            console.log(`Removing ${dir}...`);
            execSync(`rm -rf "${dir}"`, { stdio: 'inherit' });
        } catch (error) {
            console.log(`Could not remove ${dir} (this is normal on Windows)`);
        }
    }
});

// Remove any remaining old references
console.log('\n🔍 Removing old file references...');
try {
    execSync('Get-ChildItem -Path "." -Recurse -Force | Where-Object { $_.Name -like "*sovren-executive-command-center*" } | Remove-Item -Recurse -Force', {
        shell: 'powershell',
        stdio: 'inherit'
    });
} catch (error) {
    console.log('No old references found to remove');
}

// Reinstall dependencies to ensure clean state
console.log('\n📦 Reinstalling dependencies...');
try {
    execSync('npm install', { stdio: 'inherit' });
    execSync('cd frontend && npm install', { stdio: 'inherit' });
    execSync('cd ../shared && npm install', { stdio: 'inherit' });
    console.log('✅ Dependencies reinstalled');
} catch (error) {
    console.error('❌ Failed to reinstall dependencies:', error.message);
    process.exit(1);
}

// Build shared package
console.log('\n🔨 Building shared package...');
try {
    execSync('cd shared && npm run build', { stdio: 'inherit' });
    console.log('✅ Shared package built');
} catch (error) {
    console.error('❌ Failed to build shared package:', error.message);
}

// Verify TypeScript compilation
console.log('\n🔍 Verifying TypeScript compilation...');
try {
    execSync('cd frontend && npx tsc --noEmit', { stdio: 'inherit' });
    console.log('✅ TypeScript compilation successful');
} catch (error) {
    console.error('❌ TypeScript compilation failed:', error.message);
}

console.log('\n🎉 VS Code refresh complete!');
console.log('\n📋 IMPORTANT: Now do the following in VS Code:');
console.log('   1. Close VS Code completely');
console.log('   2. Reopen VS Code');
console.log('   3. Open the workspace folder: Sovren-Frontend');
console.log('   4. Wait for TypeScript to initialize');
console.log('   5. If you still see errors, press Ctrl+Shift+P and type "TypeScript: Restart TS Server"');

console.log('\n📚 Alternative approach:');
console.log('   1. Delete the entire .vscode folder');
console.log('   2. Close VS Code');
console.log('   3. Reopen VS Code');
console.log('   4. Open the workspace folder');

console.log('\n📋 Expected result:');
console.log('   - All TypeScript errors should be resolved');
console.log('   - File paths should show "frontend/" instead of "sovren-executive-command-center/"');
console.log('   - All imports should resolve correctly');
console.log('   - Three.js JSX elements should be recognized'); 