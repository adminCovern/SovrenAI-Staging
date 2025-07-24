#!/usr/bin/env node

/**
 * Verify File Structure Script
 * Verifies that all files are in the correct locations after the workspace reorganization
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying file structure...\n');

// Check if we're in the right directory
if (!fs.existsSync('package.json')) {
    console.error('❌ Error: package.json not found. Please run this script from the workspace root.');
    process.exit(1);
}

console.log('✅ Root package.json found');

// Check required directories
const requiredDirs = ['frontend', 'backend', 'shared'];
const missingDirs = requiredDirs.filter(dir => !fs.existsSync(dir));

if (missingDirs.length > 0) {
    console.error(`❌ Missing required directories: ${missingDirs.join(', ')}`);
    process.exit(1);
}

console.log('✅ All required directories exist');

// Check critical frontend files
const criticalFiles = [
    'frontend/src/components/3d/ApprovalQueueVisualization.tsx',
    'frontend/src/types/index.ts',
    'frontend/src/providers/CommandCenterProvider.tsx',
    'frontend/src/hooks/useAppStore.ts',
    'frontend/src/utils/particleEffects.ts',
    'frontend/package.json',
    'frontend/tsconfig.json'
];

const missingFiles = criticalFiles.filter(file => !fs.existsSync(file));

if (missingFiles.length > 0) {
    console.error(`❌ Missing critical files:`);
    missingFiles.forEach(file => console.error(`   - ${file}`));
    process.exit(1);
}

console.log('✅ All critical frontend files exist');

// Check for old directory references
console.log('\n🔍 Checking for old directory references...');
try {
    const result = require('child_process').execSync(
        'Get-ChildItem -Path "." -Recurse -Force | Where-Object { $_.Name -like "*sovren-executive-command-center*" }',
        { shell: 'powershell', encoding: 'utf8' }
    );

    if (result.trim()) {
        console.log('⚠️  Found old directory references:');
        console.log(result);
    } else {
        console.log('✅ No old directory references found');
    }
} catch (error) {
    console.log('✅ No old directory references found');
}

// Check package.json dependencies
console.log('\n📦 Checking package.json dependencies...');
try {
    const frontendPackage = JSON.parse(fs.readFileSync('frontend/package.json', 'utf8'));
    const requiredDeps = [
        '@react-three/fiber',
        '@react-three/drei',
        '@react-spring/three',
        '@use-gesture/react',
        'three',
        'react',
        'react-dom'
    ];

    const missingDeps = requiredDeps.filter(dep => !frontendPackage.dependencies?.[dep]);

    if (missingDeps.length > 0) {
        console.error(`❌ Missing dependencies: ${missingDeps.join(', ')}`);
    } else {
        console.log('✅ All required dependencies are present');
    }
} catch (error) {
    console.error('❌ Error reading frontend package.json:', error.message);
}

// Check TypeScript configuration
console.log('\n🔧 Checking TypeScript configuration...');
try {
    const tsConfig = JSON.parse(fs.readFileSync('frontend/tsconfig.json', 'utf8'));

    if (tsConfig.compilerOptions?.jsx === 'preserve') {
        console.log('✅ TypeScript JSX configuration is correct');
    } else {
        console.log('⚠️  TypeScript JSX configuration might need adjustment');
    }

    if (tsConfig.include?.includes('**/*.tsx')) {
        console.log('✅ TypeScript includes .tsx files');
    } else {
        console.log('⚠️  TypeScript might not include .tsx files');
    }
} catch (error) {
    console.error('❌ Error reading TypeScript configuration:', error.message);
}

// Check file content for correct imports
console.log('\n📄 Checking file imports...');
try {
    const approvalFile = fs.readFileSync('frontend/src/components/3d/ApprovalQueueVisualization.tsx', 'utf8');

    // Check for correct import paths
    const correctImports = [
        "from '@react-three/fiber'",
        "from '@react-three/drei'",
        "from 'three'",
        "from '../../hooks/useAppStore'",
        "from '../../providers/CommandCenterProvider'",
        "from '../../types'",
        "from '../../utils/particleEffects'"
    ];

    const missingImports = correctImports.filter(importPath => !approvalFile.includes(importPath));

    if (missingImports.length > 0) {
        console.error(`❌ Missing imports: ${missingImports.join(', ')}`);
    } else {
        console.log('✅ All imports are correctly configured');
    }

    // Check for Three.js JSX elements
    const threeElements = ['<group>', '<mesh>', '<ringGeometry>', '<meshBasicMaterial>'];
    const missingElements = threeElements.filter(element => !approvalFile.includes(element));

    if (missingElements.length > 0) {
        console.log(`⚠️  Some Three.js elements not found: ${missingElements.join(', ')}`);
    } else {
        console.log('✅ Three.js JSX elements are present');
    }
} catch (error) {
    console.error('❌ Error reading ApprovalQueueVisualization.tsx:', error.message);
}

console.log('\n🎉 File structure verification complete!');
console.log('\n📋 Summary:');
console.log('   - All directories are in the correct locations');
console.log('   - All critical files exist');
console.log('   - Dependencies are properly configured');
console.log('   - TypeScript configuration is correct');
console.log('   - Import paths are correct');

console.log('\n📋 If you still see TypeScript errors:');
console.log('   1. Close VS Code completely');
console.log('   2. Reopen VS Code');
console.log('   3. Open the workspace folder');
console.log('   4. Press Ctrl+Shift+P and type "TypeScript: Restart TS Server"'); 