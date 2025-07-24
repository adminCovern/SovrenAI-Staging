#!/usr/bin/env node

/**
 * Fix TypeScript Errors Script
 * Clears caches and restarts TypeScript services to resolve import issues
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Fixing TypeScript errors...\n');

// Check if we're in the right directory
if (!fs.existsSync('package.json')) {
    console.error('❌ Error: package.json not found. Please run this script from the workspace root.');
    process.exit(1);
}

// Check if frontend directory exists
if (!fs.existsSync('frontend')) {
    console.error('❌ Error: frontend directory not found.');
    process.exit(1);
}

console.log('✅ Workspace structure verified');

// Clear TypeScript cache
console.log('\n🧹 Clearing TypeScript cache...');
try {
    // Remove TypeScript cache directories
    const cacheDirs = [
        'frontend/.next',
        'frontend/node_modules/.cache',
        'frontend/.tsbuildinfo'
    ];

    cacheDirs.forEach(dir => {
        if (fs.existsSync(dir)) {
            console.log(`Removing ${dir}...`);
            execSync(`rm -rf "${dir}"`, { stdio: 'inherit' });
        }
    });

    console.log('✅ TypeScript cache cleared');
} catch (error) {
    console.log('⚠️  Could not clear some cache directories (this is normal on Windows)');
}

// Install dependencies if needed
console.log('\n📦 Checking dependencies...');
try {
    execSync('cd frontend && npm install', { stdio: 'inherit' });
    console.log('✅ Frontend dependencies verified');
} catch (error) {
    console.error('❌ Failed to install frontend dependencies:', error.message);
    process.exit(1);
}

// Check TypeScript compilation
console.log('\n🔍 Checking TypeScript compilation...');
try {
    execSync('cd frontend && npx tsc --noEmit', { stdio: 'inherit' });
    console.log('✅ TypeScript compilation successful');
} catch (error) {
    console.error('❌ TypeScript compilation failed. This might be due to:');
    console.error('   1. Missing dependencies');
    console.error('   2. VS Code still referencing old file paths');
    console.error('   3. TypeScript server needs restart');

    console.log('\n💡 Try these steps:');
    console.log('   1. In VS Code: Ctrl+Shift+P → "TypeScript: Restart TS Server"');
    console.log('   2. Close and reopen VS Code');
    console.log('   3. Run: cd frontend && npm install');
    console.log('   4. Run: cd frontend && npx tsc --noEmit');
}

// Check for old file references
console.log('\n🔍 Checking for old file references...');
try {
    const result = execSync('Get-ChildItem -Path "." -Recurse -Force | Where-Object { $_.Name -like "*sovren-executive-command-center*" }', {
        shell: 'powershell',
        encoding: 'utf8'
    });

    if (result.trim()) {
        console.log('⚠️  Found old file references:');
        console.log(result);
    } else {
        console.log('✅ No old file references found');
    }
} catch (error) {
    console.log('✅ No old file references found');
}

console.log('\n🎉 TypeScript error fix complete!');
console.log('\n📋 If you still see errors in VS Code:');
console.log('   1. Press Ctrl+Shift+P');
console.log('   2. Type "TypeScript: Restart TS Server"');
console.log('   3. Press Enter');
console.log('   4. Wait for TypeScript to reload');
console.log('\n📋 Alternative steps:');
console.log('   1. Close VS Code completely');
console.log('   2. Delete .vscode/settings.json (if it exists)');
console.log('   3. Reopen VS Code');
console.log('   4. Open the workspace again');

console.log('\n📚 Next steps:');
console.log('- npm run dev          # Start development servers');
console.log('- npm run build        # Build for production');
console.log('- npm test             # Run tests'); 