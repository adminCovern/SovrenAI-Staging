#!/usr/bin/env python3
"""
Test suite for SOVREN AI API Services
Tests both data ingestion and RAG services with optional dependencies
"""

import unittest
import asyncio
import tempfile
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestDataIngestionService(unittest.TestCase):
    """Test data ingestion service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_path = os.path.join(self.temp_dir, 'uploads')
        self.processed_path = os.path.join(self.temp_dir, 'processed')
        os.makedirs(self.upload_path, exist_ok=True)
        os.makedirs(self.processed_path, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('api.data_ingestion.asyncpg', None)
    @patch('api.data_ingestion.redis', None)
    @patch('api.data_ingestion.pd', None)
    def test_service_initialization_without_optional_deps(self):
        """Test service initializes correctly without optional dependencies"""
        from api.data_ingestion import DataPipeline, DocumentExtractor
        
        # Should not raise any exceptions
        pipeline = DataPipeline()
        extractor = DocumentExtractor()
        
        self.assertIsNotNone(pipeline)
        self.assertIsNotNone(extractor)
    
    def test_document_extractor_text(self):
        """Test text document extraction"""
        from api.data_ingestion import DocumentExtractor
        
        extractor = DocumentExtractor()
        
        # Create test file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write("Test document content")
        
        # Test extraction
        result = asyncio.run(extractor.extract(test_file, 'text'))
        
        self.assertEqual(result['type'], 'text')
        self.assertIn('Test document content', result['content'])
        self.assertIn('lines', result['metadata'])
        self.assertIn('characters', result['metadata'])
    
    def test_data_pipeline_job_submission(self):
        """Test job submission to data pipeline"""
        from api.data_ingestion import DataPipeline
        
        pipeline = DataPipeline()
        
        # Test job submission
        job_data = {
            'user_id': 'test_user',
            'type': 'file',
            'data': {
                'file_path': '/tmp/test.txt',
                'file_type': 'text',
                'title': 'Test Document'
            }
        }
        
        job_id = asyncio.run(pipeline.submit_job(job_data))
        
        self.assertIsInstance(job_id, str)
        self.assertGreater(len(job_id), 0)

class TestRAGService(unittest.TestCase):
    """Test RAG service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, 'indexes')
        os.makedirs(self.index_path, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('api.rag_service.asyncpg', None)
    @patch('api.rag_service.redis', None)
    def test_service_initialization_without_optional_deps(self):
        """Test service initializes correctly without optional dependencies"""
        from api.rag_service import RAGEngine, B200VectorIndex
        
        # Should not raise any exceptions
        engine = RAGEngine()
        index = B200VectorIndex()
        
        self.assertIsNotNone(engine)
        self.assertIsNotNone(index)
    
    def test_vector_index_operations(self):
        """Test vector index operations"""
        from api.rag_service import B200VectorIndex
        import numpy as np
        
        index = B200VectorIndex(dimension=3)
        
        # Test adding vectors
        vectors = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        metadata = [{'id': '1'}, {'id': '2'}]
        
        result = index.add_vectors(vectors, metadata)
        self.assertTrue(result)
        self.assertEqual(index.index_size, 2)
    
    def test_document_processor(self):
        """Test document processing"""
        from api.rag_service import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test text chunking
        text = "This is a test document with multiple sentences. It should be chunked properly."
        chunks = processor._chunk_text(text)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
    
    def test_rag_engine_document_addition(self):
        """Test adding documents to RAG engine"""
        from api.rag_service import RAGEngine
        
        engine = RAGEngine()
        
        # Test document addition
        document = {
            'title': 'Test Document',
            'content': 'This is a test document for RAG processing.',
            'type': 'text'
        }
        
        result = asyncio.run(engine.add_document('test_user', document))
        
        self.assertIn('doc_id', result)
        self.assertIn('chunks_added', result)
        self.assertEqual(result['status'], 'indexed')

class TestBayesianEngine(unittest.TestCase):
    """Test Bayesian engine functionality"""
    
    def test_engine_initialization(self):
        """Test Bayesian engine initialization"""
        from core.bayesian_engine.bayesian_engine import BayesianEngine, Decision
        
        engine = BayesianEngine(num_gpus=0)  # No GPUs for testing
        
        self.assertIsNotNone(engine)
        self.assertEqual(engine.num_gpus, 0)
    
    def test_decision_making(self):
        """Test decision making process"""
        from core.bayesian_engine.bayesian_engine import BayesianEngine, Decision
        
        engine = BayesianEngine(num_gpus=0)
        
        decision = Decision(
            decision_id="test_decision",
            context={"revenue": 100000, "growth": 0.1},
            options=["expand", "consolidate", "pivot"],
            constraints={"risk_tolerance": 0.5},
            universes_to_simulate=2
        )
        
        result = engine.make_decision(decision)
        
        self.assertIn('selected_option', result)
        self.assertIn('confidence', result)
        self.assertIn('outcome_prediction', result)
        self.assertIn('reasoning', result)
        
        # Verify selected option is one of the original options
        self.assertIn(result['selected_option'], decision.options)
        
        # Verify confidence is between 0 and 1
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from data ingestion to RAG to decision making"""
        from api.data_ingestion import DataPipeline, DocumentExtractor
        from api.rag_service import RAGEngine
        from core.bayesian_engine.bayesian_engine import BayesianEngine, Decision
        
        # Initialize all components
        pipeline = DataPipeline()
        rag_engine = RAGEngine()
        bayesian_engine = BayesianEngine(num_gpus=0)
        
        # Test document processing
        extractor = DocumentExtractor()
        test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        test_file.write("This is a test document for the complete workflow.")
        test_file.close()
        
        # Extract document
        extracted = asyncio.run(extractor.extract(test_file.name, 'text'))
        self.assertEqual(extracted['type'], 'text')
        
        # Add to RAG
        document = {
            'title': 'Test Document',
            'content': extracted['content'],
            'type': 'text'
        }
        
        rag_result = asyncio.run(rag_engine.add_document('test_user', document))
        self.assertEqual(rag_result['status'], 'indexed')
        
        # Make decision based on knowledge
        decision = Decision(
            decision_id="integration_test",
            context={"document_count": 1, "user_id": "test_user"},
            options=["process_more", "analyze_current", "wait"],
            constraints={},
            universes_to_simulate=2
        )
        
        decision_result = bayesian_engine.make_decision(decision)
        self.assertIn('selected_option', decision_result)
        
        # Cleanup
        os.unlink(test_file.name)

if __name__ == '__main__':
    unittest.main() 