#!/usr/bin/env python3
"""
Test suite to verify import fixes work correctly
Tests that services can run without optional dependencies
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestImportFixes(unittest.TestCase):
    """Test that import fixes work correctly"""
    
    def test_data_ingestion_imports_without_optional_deps(self):
        """Test data ingestion service imports without optional dependencies"""
        with patch.dict('sys.modules', {
            'asyncpg': None,
            'redis': None,
            'pandas': None
        }):
            # Should not raise any import errors
            from api.data_ingestion import (
                DataPipeline, 
                DocumentExtractor, 
                IngestionHandler,
                initialize_connections
            )
            
            # Test that classes can be instantiated
            pipeline = DataPipeline()
            extractor = DocumentExtractor()
            
            self.assertIsNotNone(pipeline)
            self.assertIsNotNone(extractor)
    
    def test_rag_service_imports_without_optional_deps(self):
        """Test RAG service imports without optional dependencies"""
        with patch.dict('sys.modules', {
            'asyncpg': None,
            'redis': None,
            'sklearn': None
        }):
            # Should not raise any import errors
            from api.rag_service import (
                RAGEngine,
                B200VectorIndex,
                DocumentProcessor,
                RAGHandler,
                initialize_connections
            )
            
            # Test that classes can be instantiated
            engine = RAGEngine()
            index = B200VectorIndex()
            processor = DocumentProcessor()
            
            self.assertIsNotNone(engine)
            self.assertIsNotNone(index)
            self.assertIsNotNone(processor)
    
    def test_bayesian_engine_imports_without_gpu(self):
        """Test Bayesian engine imports without GPU dependencies"""
        with patch.dict('sys.modules', {
            'torch': None,
            'torch.nn': None,
            'torch.nn.functional': None
        }):
            # Should not raise any import errors
            from core.bayesian_engine.bayesian_engine import (
                BayesianEngine,
                Decision,
                Universe,
                BayesianConsciousnessInterface
            )
            
            # Test that classes can be instantiated
            engine = BayesianEngine(num_gpus=0)
            decision = Decision(
                decision_id="test",
                context={},
                options=["option1"],
                constraints={}
            )
            
            self.assertIsNotNone(engine)
            self.assertIsNotNone(decision)
    
    def test_redis_connection_handling(self):
        """Test Redis connection handling with and without redis package"""
        # Test without redis package
        with patch.dict('sys.modules', {'redis': None}):
            from api.data_ingestion import initialize_connections
            import asyncio
            
            # Should not raise any exceptions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(initialize_connections())
            finally:
                loop.close()
        
        # Test with redis package but connection failure
        mock_redis = MagicMock()
        mock_redis.Redis.side_effect = Exception("Connection failed")
        
        with patch.dict('sys.modules', {'redis': mock_redis}):
            from api.data_ingestion import initialize_connections
            import asyncio
            
            # Should handle connection failure gracefully
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(initialize_connections())
            finally:
                loop.close()
    
    def test_database_connection_handling(self):
        """Test database connection handling with and without asyncpg package"""
        # Test without asyncpg package
        with patch.dict('sys.modules', {'asyncpg': None}):
            from api.rag_service import initialize_connections
            import asyncio
            
            # Should not raise any exceptions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(initialize_connections())
            finally:
                loop.close()
    
    def test_pandas_fallback(self):
        """Test pandas fallback functionality"""
        with patch.dict('sys.modules', {'pandas': None}):
            from api.data_ingestion import DocumentExtractor
            import tempfile
            import os
            
            extractor = DocumentExtractor()
            
            # Create test CSV file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write("col1,col2\n1,2\n3,4")
                csv_file = f.name
            
            try:
                # Should fallback to text extraction
                import asyncio
                result = asyncio.run(extractor.extract(csv_file, 'csv'))
                
                self.assertEqual(result['type'], 'text')
                self.assertIn('CSV', result['content'])
            finally:
                os.unlink(csv_file)
    
    def test_numpy_fallback(self):
        """Test numpy fallback functionality"""
        with patch.dict('sys.modules', {'numpy': None}):
            from core.bayesian_engine.bayesian_engine import BayesianEngine, Decision
            import random
            
            # Mock random functions
            with patch('random.random', return_value=0.5):
                with patch('random.gauss', return_value=0.0):
                    engine = BayesianEngine(num_gpus=0)
                    
                    decision = Decision(
                        decision_id="test",
                        context={"value": 100},
                        options=["option1", "option2"],
                        constraints={}
                    )
                    
                    # Should work with fallback numpy
                    result = engine.make_decision(decision)
                    
                    self.assertIn('selected_option', result)
                    self.assertIn('confidence', result)
    
    def test_service_initialization(self):
        """Test that services can be initialized without optional dependencies"""
        with patch.dict('sys.modules', {
            'asyncpg': None,
            'redis': None,
            'pandas': None,
            'sklearn': None
        }):
            # Test data ingestion service
            from api.data_ingestion import main as data_main
            # Should not raise any exceptions during initialization
            
            # Test RAG service
            from api.rag_service import main as rag_main
            # Should not raise any exceptions during initialization
    
    def test_error_handling(self):
        """Test error handling for missing dependencies"""
        with patch.dict('sys.modules', {
            'asyncpg': None,
            'redis': None,
            'pandas': None
        }):
            from api.data_ingestion import DocumentExtractor
            
            extractor = DocumentExtractor()
            
            # Test CSV extraction without pandas
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write("test,data\n1,2")
                csv_file = f.name
            
            try:
                import asyncio
                result = asyncio.run(extractor.extract(csv_file, 'csv'))
                
                # Should fallback to text extraction
                self.assertEqual(result['type'], 'text')
            finally:
                os.unlink(csv_file)

if __name__ == '__main__':
    unittest.main() 