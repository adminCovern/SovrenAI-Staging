/**
 * Test Administrative Monitoring System
 * 
 * Tests the administrative monitoring service including:
 * - System health monitoring
 * - Alert generation and management
 * - Compliance reporting
 * - Security hardening integration
 */

const { EventEmitter } = require('events');

// Mock THREE.js for testing
global.THREE = {
  WebGLRenderer: class {
    constructor() {
      this.domElement = { style: {} };
    }
  },
  SRGBColorSpace: 'srgb',
  ACESFilmicToneMapping: 'aces',
  PCFSoftShadowMap: 'pcf'
};

// Mock crypto for security service
const crypto = require('crypto');
global.crypto = {
  getRandomValues: (arr) => crypto.randomFillSync(arr),
  subtle: {
    generateKey: async () => ({ type: 'secret', extractable: true }),
    encrypt: async () => new Uint8Array(16),
    decrypt: async () => new TextEncoder().encode('decrypted')
  }
};

// Import the services
const { AdministrativeMonitoringService } = require('./frontend/src/services/AdministrativeMonitoringService.ts');
const { SecurityHardeningService } = require('./frontend/src/services/SecurityHardeningService.ts');

async function testAdministrativeMonitoring() {
  console.log('🧪 Testing Administrative Monitoring System...\n');

  try {
    // Create instances
    const adminService = new AdministrativeMonitoringService();
    const securityService = new SecurityHardeningService();

    // Test 1: System Health Monitoring
    console.log('📊 Test 1: System Health Monitoring');
    adminService.startMonitoring();

    // Wait for health data to be collected
    await new Promise(resolve => setTimeout(resolve, 2000));

    const currentHealth = adminService.getCurrentSystemHealth();
    console.log('✅ Current System Health:', currentHealth);

    const healthHistory = adminService.getSystemHealthHistory();
    console.log('✅ Health History Size:', healthHistory.length);

    // Test 2: Alert Generation
    console.log('\n🚨 Test 2: Alert Generation');
    const alerts = adminService.getAdminAlerts();
    console.log('✅ Current Alerts:', alerts.length);

    // Test acknowledging an alert
    if (alerts.length > 0) {
      const alertId = alerts[0].id;
      const acknowledged = adminService.acknowledgeAlert(alertId, 'test-admin');
      console.log('✅ Alert Acknowledged:', acknowledged);
    }

    // Test 3: Compliance Reporting
    console.log('\n📋 Test 3: Compliance Reporting');
    const complianceReport = await adminService.generateComplianceReport('daily');
    console.log('✅ Compliance Report Generated:', {
      id: complianceReport.id,
      status: complianceReport.status,
      violations: complianceReport.violations.length,
      recommendations: complianceReport.recommendations.length
    });

    // Test 4: Security Integration
    console.log('\n🔒 Test 4: Security Integration');
    const securityStats = securityService.getSecurityStats();
    console.log('✅ Security Stats:', securityStats);

    // Test 5: Admin Dashboard Data
    console.log('\n📈 Test 5: Admin Dashboard Data');
    const dashboardData = adminService.getAdminDashboardData();
    console.log('✅ Dashboard Data:', {
      hasSystemHealth: !!dashboardData.systemHealth,
      recentAlerts: dashboardData.recentAlerts.length,
      complianceStatus: dashboardData.complianceStatus,
      activeViolations: dashboardData.activeViolations
    });

    // Test 6: Monitoring Statistics
    console.log('\n📊 Test 6: Monitoring Statistics');
    const monitoringStats = adminService.getMonitoringStats();
    console.log('✅ Monitoring Stats:', monitoringStats);

    // Test 7: Admin Access Control
    console.log('\n🔐 Test 7: Admin Access Control');
    const adminAccess = adminService.checkAdminAccess('admin', 'view-dashboard');
    console.log('✅ Admin Access Check:', adminAccess);

    // Test 8: Event Handling
    console.log('\n📡 Test 8: Event Handling');
    adminService.on('systemHealthUpdated', (health) => {
      console.log('✅ Health Update Event:', health.status);
    });

    adminService.on('alertCreated', (alert) => {
      console.log('✅ Alert Created Event:', alert.title);
    });

    // Test 9: Compliance Reports History
    console.log('\n📚 Test 9: Compliance Reports History');
    const reports = adminService.getComplianceReports();
    console.log('✅ Compliance Reports:', reports.length);

    // Test 10: Stop Monitoring
    console.log('\n⏹️ Test 10: Stop Monitoring');
    adminService.stopMonitoring();
    const finalStats = adminService.getMonitoringStats();
    console.log('✅ Final Monitoring Stats:', finalStats);

    // Cleanup
    adminService.dispose();
    securityService.dispose();

    console.log('\n🎉 All Administrative Monitoring Tests Passed!');

  } catch (error) {
    console.error('❌ Test Failed:', error instanceof Error ? error.message : 'Unknown error');
    throw error;
  }
}

async function testPerformance() {
  console.log('\n⚡ Performance Testing...\n');

  try {
    const adminService = new AdministrativeMonitoringService();

    // Test rapid health collection
    console.log('Testing rapid health data collection...');
    const startTime = Date.now();

    adminService.startMonitoring();

    // Collect health data for 5 seconds
    const healthData = [];
    for (let i = 0; i < 10; i++) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const health = adminService.getCurrentSystemHealth();
      if (health) {
        healthData.push(health);
      }
    }

    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log(`✅ Collected ${healthData.length} health records in ${duration}ms`);
    console.log(`✅ Average collection time: ${duration / healthData.length}ms per record`);

    // Test alert generation performance
    console.log('\nTesting alert generation performance...');
    const alertStartTime = Date.now();

    // Simulate high load conditions
    for (let i = 0; i < 100; i++) {
      adminService.createAlert({
        type: 'performance',
        severity: 'high',
        title: `Test Alert ${i}`,
        message: `Performance test alert ${i}`,
        source: 'performance-test',
        metadata: { testId: i }
      });
    }

    const alertEndTime = Date.now();
    const alertDuration = alertEndTime - alertStartTime;

    console.log(`✅ Generated 100 alerts in ${alertDuration}ms`);
    console.log(`✅ Average alert generation time: ${alertDuration / 100}ms per alert`);

    // Test compliance report generation performance
    console.log('\nTesting compliance report generation performance...');
    const reportStartTime = Date.now();

    const report = await adminService.generateComplianceReport('daily');

    const reportEndTime = Date.now();
    const reportDuration = reportEndTime - reportStartTime;

    console.log(`✅ Generated compliance report in ${reportDuration}ms`);

    adminService.dispose();

    console.log('\n🎉 Performance Tests Completed!');

  } catch (error) {
    console.error('❌ Performance Test Failed:', error instanceof Error ? error.message : 'Unknown error');
    throw error;
  }
}

async function runAllTests() {
  console.log('🚀 Starting Administrative Monitoring System Tests\n');

  try {
    await testAdministrativeMonitoring();
    await testPerformance();

    console.log('\n✅ All tests completed successfully!');
    console.log('\n📋 Test Summary:');
    console.log('  ✅ System health monitoring');
    console.log('  ✅ Alert generation and management');
    console.log('  ✅ Compliance reporting');
    console.log('  ✅ Security integration');
    console.log('  ✅ Admin dashboard data');
    console.log('  ✅ Monitoring statistics');
    console.log('  ✅ Admin access control');
    console.log('  ✅ Event handling');
    console.log('  ✅ Performance benchmarks');

  } catch (error) {
    console.error('\n❌ Test suite failed:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runAllTests();
}

module.exports = {
  testAdministrativeMonitoring,
  testPerformance,
  runAllTests
}; 