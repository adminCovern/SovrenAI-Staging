#!/usr/bin/env python3
"""
Unit tests for SOVREN AI Bayesian Decision Engine
"""

import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

from bayesian_engine import (
    BayesianEngine, 
    Decision, 
    Universe, 
    BayesianEngineError,
    BayesianConsciousnessInterface
)

class TestBayesianEngine(unittest.TestCase):
    """Test cases for BayesianEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_decisions.db')
        
        # Initialize engine with test database
        self.engine = BayesianEngine(num_gpus=0, db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.num_gpus, 0)  # No GPU in test environment
        self.assertIsNotNone(self.engine.stats)
        self.assertEqual(self.engine.stats['decisions_made'], 0)
    
    def test_decision_creation(self):
        """Test Decision dataclass creation"""
        decision = Decision(
            decision_id="test_decision",
            context={"revenue": 100000, "growth": 0.1},
            options=["option1", "option2", "option3"],
            constraints={"risk": 0.5},
            priority=2,
            universes_to_simulate=5
        )
        
        self.assertEqual(decision.decision_id, "test_decision")
        self.assertEqual(len(decision.options), 3)
        self.assertEqual(decision.universes_to_simulate, 5)
    
    def test_universe_creation(self):
        """Test Universe dataclass creation"""
        universe = Universe(
            universe_id="test_universe",
            decision_id="test_decision",
            probability=0.5,
            state={"entropy": 0.8},
            outcome=0.75,
            confidence=0.9
        )
        
        self.assertEqual(universe.universe_id, "test_universe")
        self.assertEqual(universe.outcome, 0.75)
        self.assertEqual(universe.confidence, 0.9)
    
    def test_calculate_priors_uniform(self):
        """Test prior calculation with uniform distribution"""
        decision = Decision(
            decision_id="test",
            context={},
            options=["A", "B", "C"],
            constraints={}
        )
        
        priors = self.engine._calculate_priors(decision)
        
        self.assertEqual(len(priors), 3)
        self.assertAlmostEqual(sum(priors.values()), 1.0)
        for prior in priors.values():
            self.assertAlmostEqual(prior, 1.0/3.0)
    
    def test_simulate_universes(self):
        """Test universe simulation"""
        decision = Decision(
            decision_id="test",
            context={"value": 100},
            options=["A", "B"],
            constraints={},
            universes_to_simulate=3
        )
        
        priors = {"A": 0.5, "B": 0.5}
        universes = self.engine._simulate_universes(decision, priors)
        
        self.assertEqual(len(universes), 3)
        for universe in universes:
            self.assertIsInstance(universe, Universe)
            self.assertIsInstance(universe.outcome, float)
            self.assertGreaterEqual(universe.outcome, 0.0)
            self.assertLessEqual(universe.outcome, 1.0)
    
    def test_calculate_likelihoods(self):
        """Test likelihood calculation"""
        decision = Decision(
            decision_id="test",
            context={},
            options=["A", "B"],
            constraints={}
        )
        
        # Create test universes
        universes = [
            Universe("u1", "test", 0.5, {"state": 1}, 0.8),
            Universe("u2", "test", 0.5, {"state": 2}, 0.6)
        ]
        
        likelihoods = self.engine._calculate_likelihoods(universes, decision)
        
        self.assertEqual(len(likelihoods), 2)  # Two options
        for option in ["A", "B"]:
            self.assertIn(option, likelihoods)
            self.assertEqual(len(likelihoods[option]), 2)  # Two universes
            for likelihood in likelihoods[option].values():
                self.assertGreaterEqual(likelihood, 0.0)
                self.assertLessEqual(likelihood, 1.0)
    
    def test_calculate_posteriors(self):
        """Test posterior probability calculation"""
        priors = {"A": 0.5, "B": 0.5}
        likelihoods = {
            "A": {"u1": 0.8, "u2": 0.6},
            "B": {"u1": 0.4, "u2": 0.9}
        }
        
        posteriors = self.engine._calculate_posteriors(priors, likelihoods)
        
        self.assertEqual(len(posteriors), 2)
        self.assertAlmostEqual(sum(posteriors.values()), 1.0)
        for posterior in posteriors.values():
            self.assertGreaterEqual(posterior, 0.0)
            self.assertLessEqual(posterior, 1.0)
    
    def test_select_best_option(self):
        """Test best option selection"""
        options = ["A", "B", "C"]
        posteriors = {"A": 0.3, "B": 0.6, "C": 0.1}
        
        best_option, confidence = self.engine._select_best_option(options, posteriors)
        
        self.assertEqual(best_option, "B")
        self.assertEqual(confidence, 0.6)
    
    def test_predict_outcome(self):
        """Test outcome prediction"""
        universes = [
            Universe("u1", "test", 0.5, {}, 0.8),
            Universe("u2", "test", 0.5, {}, 0.6)
        ]
        
        outcome = self.engine._predict_outcome("test_option", universes)
        
        self.assertIsInstance(outcome, float)
        self.assertGreaterEqual(outcome, 0.0)
        self.assertLessEqual(outcome, 1.0)
    
    def test_generate_reasoning(self):
        """Test reasoning generation"""
        decision = Decision(
            decision_id="test_decision",
            context={},
            options=["A", "B"],
            constraints={}
        )
        
        posteriors = {"A": 0.7, "B": 0.3}
        universes = [
            Universe("u1", "test", 0.5, {}, 0.8),
            Universe("u2", "test", 0.5, {}, 0.6)
        ]
        
        reasoning = self.engine._generate_reasoning(
            decision, "A", posteriors, universes
        )
        
        self.assertIsInstance(reasoning, str)
        self.assertIn("test_decision", reasoning)
        self.assertIn("A", reasoning)
        self.assertIn("70.00%", reasoning)
    
    def test_make_decision_integration(self):
        """Test complete decision making process"""
        decision = Decision(
            decision_id="integration_test",
            context={"revenue": 500000, "growth": 0.15},
            options=["expand", "consolidate", "pivot"],
            constraints={"risk": 0.6},
            universes_to_simulate=3
        )
        
        result = self.engine.make_decision(decision)
        
        # Verify result structure
        required_keys = [
            'decision_id', 'selected_option', 'confidence', 
            'outcome_prediction', 'universes_simulated', 
            'processing_time_ms', 'reasoning'
        ]
        
        for key in required_keys:
            self.assertIn(key, result)
        
        # Verify data types and ranges
        self.assertEqual(result['decision_id'], "integration_test")
        self.assertIn(result['selected_option'], decision.options)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        self.assertGreaterEqual(result['outcome_prediction'], 0.0)
        self.assertLessEqual(result['outcome_prediction'], 1.0)
        self.assertEqual(result['universes_simulated'], 3)
        self.assertGreater(result['processing_time_ms'], 0.0)
    
    def test_empty_options_error(self):
        """Test error handling for empty options"""
        decision = Decision(
            decision_id="error_test",
            context={},
            options=[],  # Empty options
            constraints={}
        )
        
        with self.assertRaises(BayesianEngineError):
            self.engine.make_decision(decision)
    
    def test_stats_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.engine.get_stats()
        
        # Make a decision
        decision = Decision(
            decision_id="stats_test",
            context={},
            options=["A", "B"],
            constraints={}
        )
        
        self.engine.make_decision(decision)
        
        updated_stats = self.engine.get_stats()
        
        self.assertEqual(updated_stats['decisions_made'], 
                        initial_stats['decisions_made'] + 1)
        self.assertGreater(updated_stats['average_time_ms'], 0.0)
    
    def test_database_recording(self):
        """Test database recording functionality"""
        decision = Decision(
            decision_id="db_test",
            context={"test": "data"},
            options=["A", "B"],
            constraints={}
        )
        
        # Make decision and verify database recording
        result = self.engine.make_decision(decision)
        
        # Verify database file exists
        self.assertTrue(os.path.exists(self.db_path))
        
        # Verify database contains the decision
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT decision_id FROM decisions WHERE decision_id = ?", 
                      ("db_test",))
        rows = cursor.fetchall()
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "db_test")
        
        conn.close()

class TestBayesianConsciousnessInterface(unittest.TestCase):
    """Test cases for BayesianConsciousnessInterface class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = BayesianEngine(num_gpus=0)
        self.interface = BayesianConsciousnessInterface(self.engine)
    
    @patch('asyncio.create_task')
    async def test_conscious_decision(self, mock_create_task):
        """Test consciousness-informed decision making"""
        context = {"consciousness_level": 0.8}
        options = ["meditate", "analyze", "intuit"]
        
        result = await self.interface.conscious_decision(context, options)
        
        # Verify consciousness-specific fields
        self.assertTrue(result['consciousness_informed'])
        self.assertIn('quantum_coherence', result)
        self.assertGreaterEqual(result['quantum_coherence'], 0.0)
        self.assertLessEqual(result['quantum_coherence'], 1.0)
        
        # Verify standard decision fields
        self.assertIn('selected_option', result)
        self.assertIn('confidence', result)

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'error_test.db')
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_database_initialization_error(self):
        """Test handling of database initialization errors"""
        # Create a path that can't be written to
        invalid_path = "/invalid/path/that/cannot/be/created.db"
        
        with self.assertRaises(BayesianEngineError):
            BayesianEngine(num_gpus=0, db_path=invalid_path)
    
    def test_invalid_decision_data(self):
        """Test handling of invalid decision data"""
        engine = BayesianEngine(num_gpus=0, db_path=self.db_path)
        
        # Test with empty options list
        decision = Decision(
            decision_id="invalid_test",
            context={},
            options=[],  # Invalid - empty list
            constraints={}
        )
        
        with self.assertRaises(BayesianEngineError):
            engine.make_decision(decision)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 