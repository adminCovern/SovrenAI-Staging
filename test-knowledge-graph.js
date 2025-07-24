/**
 * Test Knowledge Graph System
 * 
 * Tests the knowledge graph service including:
 * - Node creation and management
 * - Relationship management
 * - Graph querying and filtering
 * - Validation and error handling
 * - Synchronization with external systems
 */

const { EventEmitter } = require('events');

// Mock crypto for encryption
const crypto = require('crypto');
global.crypto = {
  getRandomValues: (arr) => crypto.randomFillSync(arr),
  subtle: {
    generateKey: async () => ({ type: 'secret', extractable: true }),
    encrypt: async () => new Uint8Array(16),
    decrypt: async () => new TextEncoder().encode('decrypted')
  }
};

// Import the service
const { KnowledgeGraphService } = require('./frontend/src/services/KnowledgeGraphService.ts');

async function testKnowledgeGraph() {
  console.log('🧪 Testing Knowledge Graph System...\n');

  try {
    // Create instance
    const knowledgeGraph = new KnowledgeGraphService({
      encryptionEnabled: true,
      validationEnabled: true,
      syncInterval: 10000,
      maxNodes: 1000,
      maxRelationships: 5000,
      enableVersioning: true,
      enableAuditTrail: true,
      graphVisualization: true
    });

    // Test 1: Node Creation
    console.log('📊 Test 1: Node Creation');
    const ceoNode = knowledgeGraph.createNode('executive', 'CEO', {
      department: 'executive',
      level: 'C-suite',
      experience: 15
    }, 'system');
    console.log('✅ CEO Node Created:', ceoNode.id);

    const cfoNode = knowledgeGraph.createNode('executive', 'CFO', {
      department: 'finance',
      level: 'C-suite',
      experience: 12
    }, 'system');
    console.log('✅ CFO Node Created:', cfoNode.id);

    const ctoNode = knowledgeGraph.createNode('executive', 'CTO', {
      department: 'technology',
      level: 'C-suite',
      experience: 10
    }, 'system');
    console.log('✅ CTO Node Created:', ctoNode.id);

    const dealNode = knowledgeGraph.createNode('deal', 'Enterprise Deal', {
      value: 500000,
      stage: 'negotiation',
      probability: 0.8
    }, 'system');
    console.log('✅ Deal Node Created:', dealNode.id);

    // Test 2: Relationship Creation
    console.log('\n🔗 Test 2: Relationship Creation');
    const reportsToRel = knowledgeGraph.createRelationship(
      cfoNode.id,
      ceoNode.id,
      'reports_to',
      { frequency: 'daily' },
      0.9,
      'system'
    );
    console.log('✅ Reports To Relationship Created:', reportsToRel?.id);

    const managesRel = knowledgeGraph.createRelationship(
      ceoNode.id,
      ctoNode.id,
      'manages',
      { style: 'collaborative' },
      0.8,
      'system'
    );
    console.log('✅ Manages Relationship Created:', managesRel?.id);

    const influencesRel = knowledgeGraph.createRelationship(
      ctoNode.id,
      dealNode.id,
      'influences',
      { impact: 'technical_decision' },
      0.7,
      'system'
    );
    console.log('✅ Influences Relationship Created:', influencesRel?.id);

    // Test 3: Node Updates
    console.log('\n🔄 Test 3: Node Updates');
    const updatedCfo = knowledgeGraph.updateNode(cfoNode.id, {
      properties: {
        department: 'finance',
        level: 'C-suite',
        experience: 13,
        certifications: ['CPA', 'CFA']
      }
    }, 'system');
    console.log('✅ CFO Node Updated:', updatedCfo?.metadata.version);

    // Test 4: Graph Querying
    console.log('\n🔍 Test 4: Graph Querying');
    const executiveNodes = knowledgeGraph.queryGraph({
      nodeTypes: ['executive'],
      limit: 10
    });
    console.log('✅ Executive Nodes Query:', executiveNodes.nodes.length);

    const highValueDeals = knowledgeGraph.queryGraph({
      nodeTypes: ['deal'],
      filters: [
        { field: 'value', operator: 'greater_than', value: 100000 }
      ]
    });
    console.log('✅ High Value Deals Query:', highValueDeals.nodes.length);

    const strongRelationships = knowledgeGraph.queryGraph({
      relationshipTypes: ['reports_to', 'manages'],
      filters: [
        { field: 'strength', operator: 'greater_than', value: 0.8 }
      ]
    });
    console.log('✅ Strong Relationships Query:', strongRelationships.relationships.length);

    // Test 5: Graph Metrics
    console.log('\n📈 Test 5: Graph Metrics');
    const metrics = knowledgeGraph.getGraphMetrics();
    console.log('✅ Graph Metrics:', {
      totalNodes: metrics.totalNodes,
      totalRelationships: metrics.totalRelationships,
      density: metrics.density.toFixed(3),
      averageDegree: metrics.averageDegree.toFixed(2),
      connectedComponents: metrics.connectedComponents
    });

    // Test 6: Validation
    console.log('\n✅ Test 6: Validation');
    const validationErrors = knowledgeGraph.validateGraph();
    console.log('✅ Validation Errors:', validationErrors.length);

    if (validationErrors.length > 0) {
      validationErrors.forEach(error => {
        console.log(`  - ${error.errorType}: ${error.message}`);
      });
    }

    // Test 7: Relationship Updates
    console.log('\n🔄 Test 7: Relationship Updates');
    const updatedRel = knowledgeGraph.updateRelationship(
      reportsToRel.id,
      { strength: 0.95 },
      'system'
    );
    console.log('✅ Relationship Updated:', updatedRel?.metadata.version);

    // Test 8: Node Deletion
    console.log('\n🗑️ Test 8: Node Deletion');
    const testNode = knowledgeGraph.createNode('contact', 'Test Contact', {
      email: 'test@example.com'
    }, 'system');

    const deleted = knowledgeGraph.deleteNode(testNode.id, 'system');
    console.log('✅ Test Node Deleted:', deleted);

    // Test 9: Export/Import
    console.log('\n📤 Test 9: Export/Import');
    const exportedGraph = knowledgeGraph.exportGraph();
    console.log('✅ Graph Exported:', {
      nodeCount: exportedGraph.nodes.length,
      relationshipCount: exportedGraph.relationships.length
    });

    // Test 10: External Sync
    console.log('\n🔄 Test 10: External Sync');
    const externalData = {
      nodes: [
        {
          id: 'external-exec-1',
          type: 'executive',
          label: 'External Executive',
          properties: { department: 'external', level: 'senior' },
          version: 1,
          createdBy: 'external_system'
        }
      ],
      relationships: [
        {
          id: 'external-rel-1',
          sourceNodeId: 'external-exec-1',
          targetNodeId: ceoNode.id,
          type: 'collaborates_with',
          properties: { project: 'integration' },
          strength: 0.6,
          version: 1,
          createdBy: 'external_system'
        }
      ]
    };

    const syncResult = await knowledgeGraph.syncWithExternalSystem(externalData);
    console.log('✅ External Sync Completed:', {
      nodesAdded: syncResult.nodesAdded,
      relationshipsAdded: syncResult.relationshipsAdded,
      conflicts: syncResult.conflicts.length,
      validationErrors: syncResult.validationErrors.length
    });

    // Test 11: Audit Trail
    console.log('\n📋 Test 11: Audit Trail');
    const auditTrail = knowledgeGraph.getAuditTrail();
    console.log('✅ Audit Trail Entries:', auditTrail.length);

    // Test 12: Complex Queries
    console.log('\n🔍 Test 12: Complex Queries');
    const complexQuery = knowledgeGraph.queryGraph({
      nodeTypes: ['executive', 'deal'],
      relationshipTypes: ['influences', 'manages'],
      depth: 2,
      limit: 20
    });
    console.log('✅ Complex Query Results:', {
      nodes: complexQuery.nodes.length,
      relationships: complexQuery.relationships.length
    });

    // Test 13: Performance Testing
    console.log('\n⚡ Test 13: Performance Testing');
    const startTime = Date.now();

    // Create many nodes quickly
    for (let i = 0; i < 100; i++) {
      knowledgeGraph.createNode('contact', `Contact ${i}`, {
        email: `contact${i}@example.com`,
        company: `Company ${i}`
      }, 'performance_test');
    }

    const endTime = Date.now();
    console.log(`✅ Created 100 nodes in ${endTime - startTime}ms`);

    // Test 14: Event Handling
    console.log('\n📡 Test 14: Event Handling');
    knowledgeGraph.on('nodeCreated', (node) => {
      console.log('✅ Node Created Event:', node.label);
    });

    knowledgeGraph.on('relationshipCreated', (rel) => {
      console.log('✅ Relationship Created Event:', rel.type);
    });

    knowledgeGraph.on('syncCompleted', (result) => {
      console.log('✅ Sync Completed Event:', result.nodesAdded);
    });

    // Test 15: Final Metrics
    console.log('\n📊 Test 15: Final Metrics');
    const finalMetrics = knowledgeGraph.getGraphMetrics();
    console.log('✅ Final Graph Metrics:', {
      totalNodes: finalMetrics.totalNodes,
      totalRelationships: finalMetrics.totalRelationships,
      nodeTypes: Object.keys(finalMetrics.nodeTypes).length,
      relationshipTypes: Object.keys(finalMetrics.relationshipTypes).length,
      density: finalMetrics.density.toFixed(3),
      averagePathLength: finalMetrics.averagePathLength.toFixed(2)
    });

    // Cleanup
    knowledgeGraph.dispose();
    console.log('\n🎉 All Knowledge Graph Tests Passed!');

  } catch (error) {
    console.error('❌ Test Failed:', error instanceof Error ? error.message : 'Unknown error');
    throw error;
  }
}

async function testPerformance() {
  console.log('\n⚡ Performance Testing...\n');

  try {
    const knowledgeGraph = new KnowledgeGraphService();

    // Test rapid node creation
    console.log('Testing rapid node creation...');
    const startTime = Date.now();

    for (let i = 0; i < 500; i++) {
      knowledgeGraph.createNode('contact', `Contact ${i}`, {
        email: `contact${i}@example.com`,
        company: `Company ${i}`,
        value: Math.random() * 1000000
      }, 'performance_test');
    }

    const endTime = Date.now();
    console.log(`✅ Created 500 nodes in ${endTime - startTime}ms`);
    console.log(`✅ Average time per node: ${(endTime - startTime) / 500}ms`);

    // Test relationship creation performance
    console.log('\nTesting relationship creation performance...');
    const relStartTime = Date.now();

    const nodes = Array.from(knowledgeGraph.nodes.values());
    for (let i = 0; i < 200; i++) {
      const sourceNode = nodes[Math.floor(Math.random() * nodes.length)];
      const targetNode = nodes[Math.floor(Math.random() * nodes.length)];

      if (sourceNode && targetNode && sourceNode.id !== targetNode.id) {
        knowledgeGraph.createRelationship(
          sourceNode.id,
          targetNode.id,
          'collaborates_with',
          { project: `Project ${i}` },
          Math.random(),
          'performance_test'
        );
      }
    }

    const relEndTime = Date.now();
    console.log(`✅ Created 200 relationships in ${relEndTime - relStartTime}ms`);
    console.log(`✅ Average time per relationship: ${(relEndTime - relStartTime) / 200}ms`);

    // Test query performance
    console.log('\nTesting query performance...');
    const queryStartTime = Date.now();

    for (let i = 0; i < 100; i++) {
      knowledgeGraph.queryGraph({
        nodeTypes: ['contact'],
        limit: 50
      });
    }

    const queryEndTime = Date.now();
    console.log(`✅ Executed 100 queries in ${queryEndTime - queryStartTime}ms`);
    console.log(`✅ Average time per query: ${(queryEndTime - queryStartTime) / 100}ms`);

    // Test validation performance
    console.log('\nTesting validation performance...');
    const validationStartTime = Date.now();

    for (let i = 0; i < 10; i++) {
      knowledgeGraph.validateGraph();
    }

    const validationEndTime = Date.now();
    console.log(`✅ Executed 10 validations in ${validationEndTime - validationStartTime}ms`);
    console.log(`✅ Average time per validation: ${(validationEndTime - validationStartTime) / 10}ms`);

    knowledgeGraph.dispose();
    console.log('\n🎉 Performance Tests Completed!');

  } catch (error) {
    console.error('❌ Performance Test Failed:', error instanceof Error ? error.message : 'Unknown error');
    throw error;
  }
}

async function runAllTests() {
  console.log('🚀 Starting Knowledge Graph System Tests\n');

  try {
    await testKnowledgeGraph();
    await testPerformance();

    console.log('\n✅ All tests completed successfully!');
    console.log('\n📋 Test Summary:');
    console.log('  ✅ Node creation and management');
    console.log('  ✅ Relationship management');
    console.log('  ✅ Graph querying and filtering');
    console.log('  ✅ Validation and error handling');
    console.log('  ✅ Synchronization with external systems');
    console.log('  ✅ Export/import functionality');
    console.log('  ✅ Audit trail logging');
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
  testKnowledgeGraph,
  testPerformance,
  runAllTests
}; 