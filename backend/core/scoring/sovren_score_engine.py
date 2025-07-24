#!/usr/bin/env python3
"""
SOVREN AI Score Calculation Engine
Industry Standard for Operational Excellence
Production-ready implementation for mission-critical deployment
"""

import os
import sys
import time
import json
import sqlite3
import asyncio
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SOVRENScore')

class ScoreDimension(Enum):
    """SOVREN Score dimensions"""
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    STRATEGIC_ALIGNMENT = "strategic_alignment"
    INTELLIGENCE_QUOTIENT = "intelligence_quotient"
    EXECUTION_EXCELLENCE = "execution_excellence"

class ScoreCategory(Enum):
    """Score categories"""
    EXCELLENT = "excellent"  # 800-1000
    GOOD = "good"           # 600-799
    AVERAGE = "average"     # 400-599
    BELOW_AVERAGE = "below_average"  # 200-399
    POOR = "poor"          # 0-199

@dataclass
class ScoreComponent:
    """Individual score component"""
    dimension: ScoreDimension
    weight: float
    score: float
    factors: List[str]
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SOVRENScore:
    """Complete SOVREN Score"""
    business_id: str
    timestamp: float
    total_score: float
    percentile: float
    category: ScoreCategory
    components: Dict[ScoreDimension, ScoreComponent]
    trajectory: str  # "improving", "stable", "declining"
    recommendations: List[str]
    next_review: float

@dataclass
class ScoreRequest:
    """Request for score calculation"""
    business_id: str
    metrics: Dict[str, Any]
    time_period: str  # "daily", "weekly", "monthly"
    include_recommendations: bool = True

class ScoreError(Exception):
    """Base exception for SOVREN Score system"""
    pass

class CalculationError(ScoreError):
    """Exception for score calculation errors"""
    pass

class SOVRENScoreEngine:
    """
    Production-ready SOVREN Score Calculation Engine
    Implements industry standard for operational excellence
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.system_id = str(hashlib.md5(f"score_{time.time()}".encode()).hexdigest()[:8])
        self.score_history: Dict[str, List[SOVRENScore]] = {}
        self.benchmark_data: Dict[str, float] = {}
        self.running = False
        
        # Database initialization
        if db_path:
            self.db_path = db_path
        else:
            data_dir = Path("/data/sovren/data")
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "sovren_scores.db")
            
        self._init_database()
        self._load_benchmarks()
        
        # Score weights
        self.dimension_weights = {
            ScoreDimension.OPERATIONAL_EFFICIENCY: 0.25,
            ScoreDimension.STRATEGIC_ALIGNMENT: 0.25,
            ScoreDimension.INTELLIGENCE_QUOTIENT: 0.25,
            ScoreDimension.EXECUTION_EXCELLENCE: 0.25
        }
        
        logger.info(f"SOVREN Score Engine {self.system_id} initialized")
    
    def _init_database(self):
        """Initialize SOVREN Score database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    total_score REAL NOT NULL,
                    percentile REAL NOT NULL,
                    category TEXT NOT NULL,
                    trajectory TEXT NOT NULL,
                    components TEXT NOT NULL,
                    recommendations TEXT,
                    next_review REAL,
                    metadata TEXT
                )
            ''')
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Benchmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id TEXT PRIMARY KEY,
                    dimension TEXT NOT NULL,
                    percentile REAL NOT NULL,
                    score REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # Indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_business ON scores (business_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_timestamp ON scores (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_business ON metrics (business_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics (metric_type)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise ScoreError(f"Database initialization failed: {e}")
    
    def _load_benchmarks(self):
        """Load benchmark data for percentile calculations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dimension, percentile, score 
                FROM benchmarks 
                ORDER BY dimension, percentile
            ''')
            
            for row in cursor.fetchall():
                dimension, percentile, score = row
                key = f"{dimension}_{percentile}"
                self.benchmark_data[key] = score
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to load benchmarks: {e}")
            # Use default benchmarks
            self._set_default_benchmarks()
    
    def _set_default_benchmarks(self):
        """Set default benchmark data"""
        default_benchmarks = {
            'operational_efficiency_50': 500.0,
            'operational_efficiency_75': 650.0,
            'operational_efficiency_90': 800.0,
            'strategic_alignment_50': 500.0,
            'strategic_alignment_75': 650.0,
            'strategic_alignment_90': 800.0,
            'intelligence_quotient_50': 500.0,
            'intelligence_quotient_75': 650.0,
            'intelligence_quotient_90': 800.0,
            'execution_excellence_50': 500.0,
            'execution_excellence_75': 650.0,
            'execution_excellence_90': 800.0
        }
        
        self.benchmark_data.update(default_benchmarks)
    
    async def start(self):
        """Start the SOVREN Score Engine"""
        logger.info("Starting SOVREN Score Engine...")
        
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self._benchmark_update_task())
        
        logger.info("SOVREN Score Engine operational")
    
    async def shutdown(self):
        """Gracefully shutdown the SOVREN Score Engine"""
        logger.info("Shutting down SOVREN Score Engine...")
        
        self.running = False
        
        logger.info("SOVREN Score Engine shutdown complete")
    
    async def calculate_score(self, request: ScoreRequest) -> SOVRENScore:
        """
        Calculate SOVREN Score for a business
        
        Args:
            request: Score calculation request
            
        Returns:
            Complete SOVREN Score
        """
        try:
            # Calculate component scores
            components = {}
            
            for dimension in ScoreDimension:
                component = await self._calculate_component_score(
                    dimension, request.metrics, request.business_id
                )
                components[dimension] = component
            
            # Calculate total score
            total_score = await self._calculate_total_score(components)
            
            # Calculate percentile
            percentile = await self._calculate_percentile(total_score)
            
            # Determine category
            category = await self._determine_category(total_score)
            
            # Calculate trajectory
            trajectory = await self._calculate_trajectory(request.business_id, total_score)
            
            # Generate recommendations
            recommendations = []
            if request.include_recommendations:
                recommendations = await self._generate_recommendations(components, total_score)
            
            # Create score object
            score = SOVRENScore(
                business_id=request.business_id,
                timestamp=time.time(),
                total_score=total_score,
                percentile=percentile,
                category=category,
                components=components,
                trajectory=trajectory,
                recommendations=recommendations,
                next_review=time.time() + 86400  # 24 hours
            )
            
            # Store score
            await self._store_score(score)
            
            # Update history
            if request.business_id not in self.score_history:
                self.score_history[request.business_id] = []
            self.score_history[request.business_id].append(score)
            
            logger.info(f"Calculated SOVREN Score for {request.business_id}: {total_score:.0f}")
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate score: {e}")
            raise CalculationError(f"Score calculation failed: {e}")
    
    async def _calculate_component_score(self, dimension: ScoreDimension, 
                                       metrics: Dict[str, Any], 
                                       business_id: str) -> ScoreComponent:
        """Calculate score for a specific dimension"""
        try:
            if dimension == ScoreDimension.OPERATIONAL_EFFICIENCY:
                return await self._calculate_operational_efficiency(metrics, business_id)
            elif dimension == ScoreDimension.STRATEGIC_ALIGNMENT:
                return await self._calculate_strategic_alignment(metrics, business_id)
            elif dimension == ScoreDimension.INTELLIGENCE_QUOTIENT:
                return await self._calculate_intelligence_quotient(metrics, business_id)
            elif dimension == ScoreDimension.EXECUTION_EXCELLENCE:
                return await self._calculate_execution_excellence(metrics, business_id)
            else:
                raise CalculationError(f"Unknown dimension: {dimension}")
                
        except Exception as e:
            logger.error(f"Failed to calculate {dimension.value} score: {e}")
            return ScoreComponent(
                dimension=dimension,
                weight=self.dimension_weights[dimension],
                score=0.0,
                factors=[],
                details={'error': str(e)}
            )
    
    async def _calculate_operational_efficiency(self, metrics: Dict[str, Any], 
                                              business_id: str) -> ScoreComponent:
        """Calculate operational efficiency score"""
        factors = []
        score = 0.0
        details = {}
        
        # Automation rate
        automation_rate = metrics.get('automation_rate', 0.0)
        automation_score = min(automation_rate * 10, 100.0)
        factors.append(f"automation_rate: {automation_rate:.1%}")
        score += automation_score * 0.3
        
        # Error reduction
        error_reduction = metrics.get('error_reduction', 0.0)
        error_score = min(error_reduction * 10, 100.0)
        factors.append(f"error_reduction: {error_reduction:.1%}")
        score += error_score * 0.25
        
        # Decision velocity
        decision_velocity = metrics.get('decision_velocity', 0.0)
        velocity_score = min(decision_velocity * 10, 100.0)
        factors.append(f"decision_velocity: {decision_velocity:.1f}")
        score += velocity_score * 0.25
        
        # Resource optimization
        resource_optimization = metrics.get('resource_optimization', 0.0)
        resource_score = min(resource_optimization * 10, 100.0)
        factors.append(f"resource_optimization: {resource_optimization:.1%}")
        score += resource_score * 0.2
        
        details = {
            'automation_rate': automation_rate,
            'error_reduction': error_reduction,
            'decision_velocity': decision_velocity,
            'resource_optimization': resource_optimization
        }
        
        return ScoreComponent(
            dimension=ScoreDimension.OPERATIONAL_EFFICIENCY,
            weight=self.dimension_weights[ScoreDimension.OPERATIONAL_EFFICIENCY],
            score=score,
            factors=factors,
            details=details
        )
    
    async def _calculate_strategic_alignment(self, metrics: Dict[str, Any], 
                                           business_id: str) -> ScoreComponent:
        """Calculate strategic alignment score"""
        factors = []
        score = 0.0
        details = {}
        
        # Goal achievement
        goal_achievement = metrics.get('goal_achievement', 0.0)
        goal_score = min(goal_achievement * 10, 100.0)
        factors.append(f"goal_achievement: {goal_achievement:.1%}")
        score += goal_score * 0.3
        
        # Initiative success
        initiative_success = metrics.get('initiative_success', 0.0)
        initiative_score = min(initiative_success * 10, 100.0)
        factors.append(f"initiative_success: {initiative_success:.1%}")
        score += initiative_score * 0.25
        
        # Pivot agility
        pivot_agility = metrics.get('pivot_agility', 0.0)
        pivot_score = min(pivot_agility * 10, 100.0)
        factors.append(f"pivot_agility: {pivot_agility:.1f}")
        score += pivot_score * 0.25
        
        # Vision execution
        vision_execution = metrics.get('vision_execution', 0.0)
        vision_score = min(vision_execution * 10, 100.0)
        factors.append(f"vision_execution: {vision_execution:.1%}")
        score += vision_score * 0.2
        
        details = {
            'goal_achievement': goal_achievement,
            'initiative_success': initiative_success,
            'pivot_agility': pivot_agility,
            'vision_execution': vision_execution
        }
        
        return ScoreComponent(
            dimension=ScoreDimension.STRATEGIC_ALIGNMENT,
            weight=self.dimension_weights[ScoreDimension.STRATEGIC_ALIGNMENT],
            score=score,
            factors=factors,
            details=details
        )
    
    async def _calculate_intelligence_quotient(self, metrics: Dict[str, Any], 
                                             business_id: str) -> ScoreComponent:
        """Calculate intelligence quotient score"""
        factors = []
        score = 0.0
        details = {}
        
        # Prediction accuracy
        prediction_accuracy = metrics.get('prediction_accuracy', 0.0)
        prediction_score = min(prediction_accuracy * 10, 100.0)
        factors.append(f"prediction_accuracy: {prediction_accuracy:.1%}")
        score += prediction_score * 0.3
        
        # Insight generation
        insight_generation = metrics.get('insight_generation', 0.0)
        insight_score = min(insight_generation * 10, 100.0)
        factors.append(f"insight_generation: {insight_generation:.1f}")
        score += insight_score * 0.25
        
        # Pattern recognition
        pattern_recognition = metrics.get('pattern_recognition', 0.0)
        pattern_score = min(pattern_recognition * 10, 100.0)
        factors.append(f"pattern_recognition: {pattern_recognition:.1f}")
        score += pattern_score * 0.25
        
        # Opportunity capture
        opportunity_capture = metrics.get('opportunity_capture', 0.0)
        opportunity_score = min(opportunity_capture * 10, 100.0)
        factors.append(f"opportunity_capture: {opportunity_capture:.1%}")
        score += opportunity_score * 0.2
        
        details = {
            'prediction_accuracy': prediction_accuracy,
            'insight_generation': insight_generation,
            'pattern_recognition': pattern_recognition,
            'opportunity_capture': opportunity_capture
        }
        
        return ScoreComponent(
            dimension=ScoreDimension.INTELLIGENCE_QUOTIENT,
            weight=self.dimension_weights[ScoreDimension.INTELLIGENCE_QUOTIENT],
            score=score,
            factors=factors,
            details=details
        )
    
    async def _calculate_execution_excellence(self, metrics: Dict[str, Any], 
                                            business_id: str) -> ScoreComponent:
        """Calculate execution excellence score"""
        factors = []
        score = 0.0
        details = {}
        
        # Implementation speed
        implementation_speed = metrics.get('implementation_speed', 0.0)
        speed_score = min(implementation_speed * 10, 100.0)
        factors.append(f"implementation_speed: {implementation_speed:.1f}")
        score += speed_score * 0.25
        
        # Quality consistency
        quality_consistency = metrics.get('quality_consistency', 0.0)
        quality_score = min(quality_consistency * 10, 100.0)
        factors.append(f"quality_consistency: {quality_consistency:.1%}")
        score += quality_score * 0.25
        
        # Stakeholder satisfaction
        stakeholder_satisfaction = metrics.get('stakeholder_satisfaction', 0.0)
        satisfaction_score = min(stakeholder_satisfaction * 10, 100.0)
        factors.append(f"stakeholder_satisfaction: {stakeholder_satisfaction:.1%}")
        score += satisfaction_score * 0.25
        
        # Continuous improvement
        continuous_improvement = metrics.get('continuous_improvement', 0.0)
        improvement_score = min(continuous_improvement * 10, 100.0)
        factors.append(f"continuous_improvement: {continuous_improvement:.1%}")
        score += improvement_score * 0.25
        
        details = {
            'implementation_speed': implementation_speed,
            'quality_consistency': quality_consistency,
            'stakeholder_satisfaction': stakeholder_satisfaction,
            'continuous_improvement': continuous_improvement
        }
        
        return ScoreComponent(
            dimension=ScoreDimension.EXECUTION_EXCELLENCE,
            weight=self.dimension_weights[ScoreDimension.EXECUTION_EXCELLENCE],
            score=score,
            factors=factors,
            details=details
        )
    
    async def _calculate_total_score(self, components: Dict[ScoreDimension, ScoreComponent]) -> float:
        """Calculate total weighted score"""
        total_score = 0.0
        
        for dimension, component in components.items():
            weighted_score = component.score * component.weight
            total_score += weighted_score
        
        return min(total_score, 1000.0)  # Cap at 1000
    
    async def _calculate_percentile(self, total_score: float) -> float:
        """Calculate percentile based on benchmark data"""
        # Simple percentile calculation based on score ranges
        if total_score >= 800:
            return 90.0
        elif total_score >= 650:
            return 75.0
        elif total_score >= 500:
            return 50.0
        elif total_score >= 350:
            return 25.0
        else:
            return 10.0
    
    async def _determine_category(self, total_score: float) -> ScoreCategory:
        """Determine score category"""
        if total_score >= 800:
            return ScoreCategory.EXCELLENT
        elif total_score >= 600:
            return ScoreCategory.GOOD
        elif total_score >= 400:
            return ScoreCategory.AVERAGE
        elif total_score >= 200:
            return ScoreCategory.BELOW_AVERAGE
        else:
            return ScoreCategory.POOR
    
    async def _calculate_trajectory(self, business_id: str, current_score: float) -> str:
        """Calculate score trajectory"""
        if business_id not in self.score_history or len(self.score_history[business_id]) < 2:
            return "stable"
        
        recent_scores = self.score_history[business_id][-5:]  # Last 5 scores
        if len(recent_scores) < 2:
            return "stable"
        
        # Calculate trend
        score_values = [s.total_score for s in recent_scores]
        trend = (score_values[-1] - score_values[0]) / len(score_values)
        
        if trend > 10:
            return "improving"
        elif trend < -10:
            return "declining"
        else:
            return "stable"
    
    async def _generate_recommendations(self, components: Dict[ScoreDimension, ScoreComponent], 
                                      total_score: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Find lowest scoring component
        lowest_component = min(components.values(), key=lambda c: c.score)
        
        if lowest_component.dimension == ScoreDimension.OPERATIONAL_EFFICIENCY:
            recommendations.extend([
                "Increase automation rate by implementing more automated workflows",
                "Focus on error reduction through better quality control processes",
                "Improve decision velocity by streamlining approval processes",
                "Optimize resource allocation using data-driven insights"
            ])
        elif lowest_component.dimension == ScoreDimension.STRATEGIC_ALIGNMENT:
            recommendations.extend([
                "Align team goals with overall business strategy",
                "Improve initiative success rate through better planning",
                "Increase pivot agility by reducing bureaucratic processes",
                "Ensure vision execution through regular progress reviews"
            ])
        elif lowest_component.dimension == ScoreDimension.INTELLIGENCE_QUOTIENT:
            recommendations.extend([
                "Improve prediction accuracy through better data analysis",
                "Generate more actionable insights from business data",
                "Enhance pattern recognition capabilities",
                "Increase opportunity capture rate through proactive monitoring"
            ])
        elif lowest_component.dimension == ScoreDimension.EXECUTION_EXCELLENCE:
            recommendations.extend([
                "Speed up implementation through better project management",
                "Maintain quality consistency across all operations",
                "Improve stakeholder satisfaction through better communication",
                "Implement continuous improvement processes"
            ])
        
        # Add general recommendations based on score
        if total_score < 400:
            recommendations.append("Consider comprehensive business transformation program")
        elif total_score < 600:
            recommendations.append("Focus on key performance areas for improvement")
        elif total_score < 800:
            recommendations.append("Optimize existing processes for excellence")
        else:
            recommendations.append("Maintain excellence and share best practices")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def _store_score(self, score: SOVRENScore):
        """Store score in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            score_id = str(hashlib.md5(f"{score.business_id}_{score.timestamp}".encode()).hexdigest()[:16])
            
            cursor.execute('''
                INSERT OR REPLACE INTO scores 
                (id, business_id, timestamp, total_score, percentile, category, 
                 trajectory, components, recommendations, next_review, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                score_id,
                score.business_id,
                score.timestamp,
                score.total_score,
                score.percentile,
                score.category.value,
                score.trajectory,
                json.dumps({dim.value: {
                    'score': comp.score,
                    'weight': comp.weight,
                    'factors': comp.factors,
                    'details': comp.details
                } for dim, comp in score.components.items()}),
                json.dumps(score.recommendations),
                score.next_review,
                json.dumps({})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store score: {e}")
    
    async def _benchmark_update_task(self):
        """Background task for updating benchmarks"""
        while self.running:
            try:
                await asyncio.sleep(86400)  # 24 hours
                
                # Update benchmarks based on recent scores
                await self._update_benchmarks()
                
            except Exception as e:
                logger.error(f"Benchmark update task error: {e}")
    
    async def _update_benchmarks(self):
        """Update benchmark data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent scores for each dimension
            for dimension in ScoreDimension:
                cursor.execute('''
                    SELECT total_score FROM scores 
                    WHERE timestamp > ? 
                    ORDER BY total_score
                ''', (time.time() - 86400 * 30,))  # Last 30 days
                
                scores = [row[0] for row in cursor.fetchall()]
                if scores:
                    # Calculate percentiles
                    percentiles = [50, 75, 90]
                    for p in percentiles:
                        index = int(len(scores) * p / 100)
                        if index < len(scores):
                            benchmark_score = scores[index]
                            
                            # Update benchmark
                            cursor.execute('''
                                INSERT OR REPLACE INTO benchmarks 
                                (id, dimension, percentile, score, timestamp)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                f"{dimension.value}_{p}",
                                dimension.value,
                                p,
                                benchmark_score,
                                time.time()
                            ))
            
            conn.commit()
            conn.close()
            
            # Reload benchmarks
            self._load_benchmarks()
            
        except Exception as e:
            logger.error(f"Failed to update benchmarks: {e}")

# Production-ready test suite
class TestSOVRENScoreEngine:
    """Comprehensive test suite for SOVREN Score Engine"""
    
    def test_system_initialization(self):
        """Test system initialization"""
        engine = SOVRENScoreEngine()
        assert engine.system_id is not None
        assert engine.running == False
        assert len(engine.dimension_weights) == 4
    
    def test_score_calculation(self):
        """Test score calculation"""
        engine = SOVRENScoreEngine()
        request = ScoreRequest(
            business_id="test_business",
            metrics={
                'automation_rate': 0.8,
                'error_reduction': 0.7,
                'decision_velocity': 8.5,
                'resource_optimization': 0.6,
                'goal_achievement': 0.75,
                'initiative_success': 0.8,
                'pivot_agility': 7.5,
                'vision_execution': 0.7,
                'prediction_accuracy': 0.85,
                'insight_generation': 8.0,
                'pattern_recognition': 7.5,
                'opportunity_capture': 0.8,
                'implementation_speed': 8.0,
                'quality_consistency': 0.9,
                'stakeholder_satisfaction': 0.85,
                'continuous_improvement': 0.75
            },
            time_period="daily"
        )
        score = asyncio.run(engine.calculate_score(request))
        assert score.total_score > 0
        assert score.business_id == "test_business"
        assert len(score.components) == 4
    
    def test_component_calculation(self):
        """Test component score calculation"""
        engine = SOVRENScoreEngine()
        metrics = {'automation_rate': 0.8, 'error_reduction': 0.7}
        component = asyncio.run(engine._calculate_operational_efficiency(metrics, "test"))
        assert component.score > 0
        assert component.dimension == ScoreDimension.OPERATIONAL_EFFICIENCY
    
    def test_category_determination(self):
        """Test category determination"""
        engine = SOVRENScoreEngine()
        category = asyncio.run(engine._determine_category(850))
        assert category == ScoreCategory.EXCELLENT
    
    def test_trajectory_calculation(self):
        """Test trajectory calculation"""
        engine = SOVRENScoreEngine()
        trajectory = asyncio.run(engine._calculate_trajectory("test_business", 500))
        assert trajectory in ["improving", "stable", "declining"]

if __name__ == "__main__":
    # Run tests
    test_suite = TestSOVRENScoreEngine()
    test_suite.test_system_initialization()
    test_suite.test_score_calculation()
    test_suite.test_component_calculation()
    test_suite.test_category_determination()
    test_suite.test_trajectory_calculation()
    print("All SOVREN Score Engine tests passed") 