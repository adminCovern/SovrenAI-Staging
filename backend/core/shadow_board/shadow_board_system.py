#!/usr/bin/env python3
"""
SOVREN AI Shadow Board System
Virtual C-Suite Executives with PhD-level expertise
"""

import asyncio
import json
import time
import uuid
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime, timedelta
from pathlib import Path

# Core dependencies with fallbacks
try:
    import numpy as np  # type: ignore
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import aiohttp  # type: ignore
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    sqlite3 = None

# Optional imports with fallbacks
try:
    import torch  # type: ignore
    import torch.nn as nn  # type: ignore
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoTokenizer = None
    AutoModelForCausalLM = None

# Type aliases for optional imports
if TORCH_AVAILABLE and torch is not None:
    DeviceType = torch.device
else:
    DeviceType = Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ShadowBoard')

class ShadowBoardError(Exception):
    """Base exception for Shadow Board System"""
    pass

class ModelInitializationError(ShadowBoardError):
    """Raised when model initialization fails"""
    pass

class ExecutiveNotFoundError(ShadowBoardError):
    """Raised when executive is not found"""
    pass

class DatabaseError(ShadowBoardError):
    """Raised when database operations fail"""
    pass

class ExecutiveRole(Enum):
    CEO = "Chief Executive Officer"
    CFO = "Chief Financial Officer"
    CTO = "Chief Technology Officer"
    CMO = "Chief Marketing Officer"
    COO = "Chief Operating Officer"
    CHRO = "Chief Human Resources Officer"
    CLO = "Chief Legal Officer"
    CSO = "Chief Strategy Officer"

@dataclass
class Executive:
    id: str
    role: ExecutiveRole
    name: str
    personality_profile: Dict[str, Any]
    expertise_areas: List[str]
    communication_style: str
    decision_bias: Dict[str, float]
    phd_expertise: List[str] = field(default_factory=list)  # List of PhD-level expertise areas
    phone_number: Optional[str] = None
    model: Optional[Any] = None
    
class ExecutivePersonalityEngine:
    """Creates psychologically accurate executive personalities"""
    
    def __init__(self):
        self.personality_dimensions = {
            'openness': (0.0, 1.0),
            'conscientiousness': (0.0, 1.0),
            'extraversion': (0.0, 1.0),
            'agreeableness': (0.0, 1.0),
            'neuroticism': (0.0, 1.0),
            'risk_tolerance': (0.0, 1.0),
            'analytical_thinking': (0.0, 1.0),
            'strategic_vision': (0.0, 1.0),
            'decisiveness': (0.0, 1.0),
            'innovation_focus': (0.0, 1.0)
        }
        
    def generate_executive_personality(self, role: ExecutiveRole) -> Dict[str, Any]:
        """Generate personality profile based on role"""
        
        base_profiles = {
            ExecutiveRole.CEO: {
                'openness': 0.8,
                'conscientiousness': 0.85,
                'extraversion': 0.75,
                'agreeableness': 0.6,
                'neuroticism': 0.3,
                'risk_tolerance': 0.7,
                'analytical_thinking': 0.8,
                'strategic_vision': 0.95,
                'decisiveness': 0.9,
                'innovation_focus': 0.8
            },
            ExecutiveRole.CFO: {
                'openness': 0.6,
                'conscientiousness': 0.95,
                'extraversion': 0.5,
                'agreeableness': 0.55,
                'neuroticism': 0.4,
                'risk_tolerance': 0.3,
                'analytical_thinking': 0.95,
                'strategic_vision': 0.7,
                'decisiveness': 0.8,
                'innovation_focus': 0.5
            },
            ExecutiveRole.CTO: {
                'openness': 0.9,
                'conscientiousness': 0.8,
                'extraversion': 0.6,
                'agreeableness': 0.65,
                'neuroticism': 0.35,
                'risk_tolerance': 0.75,
                'analytical_thinking': 0.9,
                'strategic_vision': 0.8,
                'decisiveness': 0.75,
                'innovation_focus': 0.95
            },
            ExecutiveRole.CMO: {
                'openness': 0.85,
                'conscientiousness': 0.75,
                'extraversion': 0.85,
                'agreeableness': 0.7,
                'neuroticism': 0.35,
                'risk_tolerance': 0.65,
                'analytical_thinking': 0.7,
                'strategic_vision': 0.8,
                'decisiveness': 0.8,
                'innovation_focus': 0.85
            },
            ExecutiveRole.COO: {
                'openness': 0.65,
                'conscientiousness': 0.9,
                'extraversion': 0.7,
                'agreeableness': 0.65,
                'neuroticism': 0.3,
                'risk_tolerance': 0.45,
                'analytical_thinking': 0.85,
                'strategic_vision': 0.75,
                'decisiveness': 0.85,
                'innovation_focus': 0.6
            },
            ExecutiveRole.CHRO: {
                'openness': 0.75,
                'conscientiousness': 0.85,
                'extraversion': 0.8,
                'agreeableness': 0.85,
                'neuroticism': 0.25,
                'risk_tolerance': 0.5,
                'analytical_thinking': 0.75,
                'strategic_vision': 0.7,
                'decisiveness': 0.75,
                'innovation_focus': 0.7
            },
            ExecutiveRole.CLO: {
                'openness': 0.55,
                'conscientiousness': 0.95,
                'extraversion': 0.5,
                'agreeableness': 0.5,
                'neuroticism': 0.3,
                'risk_tolerance': 0.2,
                'analytical_thinking': 0.95,
                'strategic_vision': 0.65,
                'decisiveness': 0.7,
                'innovation_focus': 0.4
            },
            ExecutiveRole.CSO: {
                'openness': 0.8,
                'conscientiousness': 0.85,
                'extraversion': 0.65,
                'agreeableness': 0.6,
                'neuroticism': 0.3,
                'risk_tolerance': 0.6,
                'analytical_thinking': 0.9,
                'strategic_vision': 0.95,
                'decisiveness': 0.8,
                'innovation_focus': 0.75
            }
        }
        
        # Get base profile
        base = base_profiles.get(role, base_profiles[ExecutiveRole.CEO])
        
        # Add realistic variation
        personality = {}
        for trait, base_value in base.items():
            # Add gaussian noise for realistic variation
            if NUMPY_AVAILABLE and np is not None:
                variation = np.random.normal(0, 0.05)
                value = np.clip(base_value + variation, 0.0, 1.0)
            else:
                # Fallback when numpy is not available
                import random
                variation = random.gauss(0, 0.05)
                value = max(0.0, min(1.0, base_value + variation))
            personality[trait] = float(value)
            
        # Add role-specific attributes
        personality['leadership_style'] = self._determine_leadership_style(personality)
        personality['communication_preferences'] = self._determine_communication_style(personality)
        personality['decision_making_approach'] = self._determine_decision_style(personality)
        
        return personality
        
    def _determine_leadership_style(self, personality: Dict[str, float]) -> str:
        """Determine leadership style based on personality"""
        
        if personality['extraversion'] > 0.7 and personality['agreeableness'] > 0.7:
            return "Transformational"
        elif personality['conscientiousness'] > 0.8 and personality['decisiveness'] > 0.8:
            return "Authoritative"
        elif personality['analytical_thinking'] > 0.8 and personality['strategic_vision'] > 0.8:
            return "Strategic"
        elif personality['agreeableness'] > 0.8 and personality['openness'] > 0.7:
            return "Democratic"
        else:
            return "Situational"
            
    def _determine_communication_style(self, personality: Dict[str, float]) -> List[str]:
        """Determine communication preferences"""
        
        styles = []
        
        if personality['analytical_thinking'] > 0.8:
            styles.append("data-driven")
        if personality['extraversion'] > 0.7:
            styles.append("collaborative")
        if personality['conscientiousness'] > 0.8:
            styles.append("structured")
        if personality['innovation_focus'] > 0.7:
            styles.append("visionary")
        if personality['agreeableness'] > 0.7:
            styles.append("empathetic")
            
        return styles
        
    def _determine_decision_style(self, personality: Dict[str, float]) -> str:
        """Determine decision-making approach"""
        
        if personality['analytical_thinking'] > 0.85:
            return "Analytical - thorough analysis before deciding"
        elif personality['decisiveness'] > 0.85 and personality['risk_tolerance'] > 0.6:
            return "Intuitive - quick decisions based on experience"
        elif personality['agreeableness'] > 0.8:
            return "Consensus - seeks team input and buy-in"
        else:
            return "Balanced - combines analysis with intuition"

class ExecutiveModel:
    """Executive model with mandatory PhD-level expertise and advanced model usage"""
    def __init__(self, executive: Executive, device: Optional[Any] = None):
        self.executive = executive
        self.device = device
        self.model = None
        self.tokenizer = None
        self._initialized = False
        self.conversation_history = []
        # Security: Ensure only executives with PhD-level expertise are active
        if not self.executive.phd_expertise or len(self.executive.phd_expertise) == 0:
            raise ValueError(f"Executive {self.executive.name} lacks required PhD-level expertise.")
        
    async def initialize(self):
        """Initialize the executive's AI model"""
        
        if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            logger.warning(f"Torch or Transformers not available for {self.executive.name}. Using fallback mode.")
            self._initialized = True
            return
            
        try:
            # Load specialized model based on role
            model_mapping = {
                ExecutiveRole.CFO: "microsoft/phi-2",  # Financial expertise
                ExecutiveRole.CTO: "microsoft/phi-2",  # Technical expertise
                ExecutiveRole.CMO: "microsoft/phi-2",  # Marketing expertise
                ExecutiveRole.CLO: "microsoft/phi-2",  # Legal expertise
                # Default to smaller model for others
            }
            
            model_name = model_mapping.get(self.executive.role, "microsoft/phi-2")
            
            logger.info(f"Loading model for {self.executive.role.value}: {model_name}")
            
            # Load tokenizer and model
            if AutoTokenizer and AutoModelForCausalLM and torch:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype="auto",
                    device_map="auto",
                    low_cpu_mem_usage=True
                )
            else:
                raise ModelInitializationError("Required AI libraries not available")
            
            # Create expertise embeddings
            self._create_expertise_embeddings()
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize model for {self.executive.name}: {e}")
            raise ModelInitializationError(f"Failed to initialize model for {self.executive.name}: {e}")
        
    def _create_expertise_embeddings(self):
        """Create embeddings for executive's expertise areas"""
        
        expertise_prompts = {
            ExecutiveRole.CEO: [
                "Strategic planning and vision setting",
                "Stakeholder management and board relations",
                "Company culture and values",
                "Market positioning and competitive strategy",
                "Leadership development and succession planning"
            ],
            ExecutiveRole.CFO: [
                "Financial planning and analysis",
                "Risk management and compliance",
                "Capital structure optimization",
                "Investor relations and reporting",
                "M&A valuation and due diligence"
            ],
            ExecutiveRole.CTO: [
                "Technology architecture and scalability",
                "Innovation and R&D strategy",
                "Cybersecurity and data protection",
                "Digital transformation initiatives",
                "Technical debt management"
            ],
            ExecutiveRole.CMO: [
                "Brand strategy and positioning",
                "Customer acquisition and retention",
                "Digital marketing and analytics",
                "Product launch and go-to-market",
                "Marketing ROI optimization"
            ],
            ExecutiveRole.COO: [
                "Operational efficiency and optimization",
                "Supply chain management",
                "Quality control and process improvement",
                "Cross-functional team coordination",
                "Performance metrics and KPIs"
            ],
            ExecutiveRole.CHRO: [
                "Talent acquisition and retention",
                "Organizational development",
                "Compensation and benefits strategy",
                "Employee engagement and culture",
                "Labor relations and compliance"
            ],
            ExecutiveRole.CLO: [
                "Corporate governance and compliance",
                "Contract negotiation and management",
                "Intellectual property protection",
                "Litigation strategy and risk",
                "Regulatory compliance"
            ],
            ExecutiveRole.CSO: [
                "Long-term strategic planning",
                "Market analysis and trends",
                "Strategic partnerships and alliances",
                "Business model innovation",
                "Scenario planning and forecasting"
            ]
        }
        
        self.executive.expertise_areas = expertise_prompts.get(
            self.executive.role,
            expertise_prompts[ExecutiveRole.CEO]
        )
        
    async def provide_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide executive-level recommendation on a decision, referencing PhD-level expertise"""
        if not self._initialized:
            raise ModelInitializationError(f"Model not initialized for {self.executive.name}")
        if not self.model or not self.tokenizer:
            raise ModelInitializationError("Advanced model and tokenizer are required for executive recommendations.")
        try:
            # Build prompt with personality and expertise
            prompt = self._build_executive_prompt(context)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            if torch is not None:
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=500,
                        temperature=0.7,
                        do_sample=True,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
            else:
                raise ModelInitializationError("Torch not available for model generation")
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            recommendation = self._parse_executive_response(response, context)
            # Attach expertise and reasoning
            recommendation['phd_expertise'] = self.executive.phd_expertise
            recommendation['reasoning'] = f"Recommendation generated using expertise in: {', '.join(self.executive.phd_expertise)}."
            self.conversation_history.append({
                'timestamp': time.time(),
                'context': context,
                'recommendation': recommendation
            })
            return recommendation
        except Exception as e:
            logger.error(f"Error generating recommendation for {self.executive.name}: {e}")
            raise
        
    def _generate_fallback_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback recommendation when model is not available"""
        
        # Simple rule-based recommendation based on executive role and personality
        personality = self.executive.personality_profile
        
        # Determine recommendation based on role and context
        decision_type = context.get('decision_type', 'strategic')
        investment = context.get('investment_required', 0)
        
        if self.executive.role == ExecutiveRole.CFO:
            if investment > 1000000 and personality['risk_tolerance'] < 0.5:
                recommendation = 'conditional'
            else:
                recommendation = 'approve'
        elif self.executive.role == ExecutiveRole.CTO:
            if 'technology' in str(context).lower():
                recommendation = 'approve'
            else:
                recommendation = 'conditional'
        else:
            recommendation = 'approve'
            
        return {
            'executive': self.executive.name,
            'role': self.executive.role.value,
            'recommendation': recommendation,
            'confidence': 0.7,
            'key_points': [f"Based on {self.executive.role.value} expertise"],
            'risks': ["Standard business risks apply"],
            'opportunities': ["Potential for strategic growth"],
            'conditions': [],
            'full_response': f"{self.executive.name} recommends {recommendation} based on {self.executive.role.value} analysis."
        }
        
    def _build_executive_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt incorporating executive personality and expertise"""
        
        personality = self.executive.personality_profile
        
        prompt_parts = [
            f"You are {self.executive.name}, {self.executive.role.value} with the following traits:",
            f"- Leadership style: {personality['leadership_style']}",
            f"- Decision approach: {personality['decision_making_approach']}",
            f"- Risk tolerance: {personality['risk_tolerance']:.0%}",
            f"- Analytical thinking: {personality['analytical_thinking']:.0%}",
            "",
            "Your areas of expertise include:",
        ]
        
        for area in self.executive.expertise_areas:
            prompt_parts.append(f"- {area}")
            
        prompt_parts.extend([
            "",
            "Context for decision:",
            json.dumps(context, indent=2),
            "",
            f"Provide your {self.executive.role.value} perspective on this decision.",
            "Consider risks, opportunities, and strategic implications.",
            "Be specific and actionable in your recommendation."
        ])
        
        return "\n".join(prompt_parts)
        
    def _parse_executive_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse executive response into structured recommendation"""
        
        # Extract key elements from response
        recommendation = {
            'executive': self.executive.name,
            'role': self.executive.role.value,
            'recommendation': 'approve',  # Default
            'confidence': 0.0,
            'key_points': [],
            'risks': [],
            'opportunities': [],
            'conditions': [],
            'full_response': response
        }
        
        # Simple parsing logic (would be more sophisticated in practice)
        response_lower = response.lower()
        
        # Determine recommendation
        if 'recommend against' in response_lower or 'do not recommend' in response_lower:
            recommendation['recommendation'] = 'reject'
        elif 'proceed with caution' in response_lower:
            recommendation['recommendation'] = 'conditional'
        
        # Extract confidence (look for percentages)
        confidence_match = re.search(r'(\d+)%\s*confident', response_lower)
        if confidence_match:
            recommendation['confidence'] = float(confidence_match.group(1)) / 100
        else:
            # Estimate confidence based on language
            if 'strongly recommend' in response_lower:
                recommendation['confidence'] = 0.9
            elif 'recommend' in response_lower:
                recommendation['confidence'] = 0.75
            else:
                recommendation['confidence'] = 0.5
                
        # Extract key points (simplified)
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                if 'risk' in line.lower():
                    recommendation['risks'].append(line[2:])
                elif 'opportunity' in line.lower():
                    recommendation['opportunities'].append(line[2:])
                else:
                    recommendation['key_points'].append(line[2:])
                    
        return recommendation

class ShadowBoardSystem:
    """
    Shadow Board System - Virtual C-Suite providing executive guidance
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.system_id = str(uuid.uuid4())
        self.executives: Dict[str, Executive] = {}
        self.personality_engine = ExecutivePersonalityEngine()
        self.executive_models: Dict[str, ExecutiveModel] = {}
        self.running = False
        
        # Database
        if db_path:
            self.db_path = db_path
        else:
            # Create data directory if it doesn't exist
            data_dir = Path("/data/sovren/data")
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "shadow_board.db")
            
        self._init_database()
        
        # GPU allocation for executives (fallback to CPU if no GPU)
        self.gpu_allocation = {
            ExecutiveRole.CEO: 0,
            ExecutiveRole.CFO: 1,
            ExecutiveRole.CTO: 2,
            ExecutiveRole.CMO: 3,
            ExecutiveRole.COO: 4,
            ExecutiveRole.CHRO: 5,
            ExecutiveRole.CLO: 6,
            ExecutiveRole.CSO: 7
        }
        
        # Initialize executives with PhD-level expertise
        self._initialize_executives_with_phd_expertise()
        
        logger.info(f"Shadow Board System {self.system_id} initialized")
        
    def _init_database(self):
        """Initialize Shadow Board database"""
        
        if not SQLITE_AVAILABLE or sqlite3 is None:
            logger.warning("SQLite3 not available - database operations will be disabled")
            return
            
        try:
            # Ensure directory exists
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS board_decisions (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    context TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    consensus TEXT,
                    outcome TEXT,
                    user_id TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executive_interactions (
                    id TEXT PRIMARY KEY,
                    executive_id TEXT NOT NULL,
                    user_id TEXT,
                    interaction_type TEXT,
                    content TEXT,
                    timestamp REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Failed to initialize database: {e}")
        
    async def start(self):
        """Start the Shadow Board system"""
        
        logger.info("Initializing Shadow Board executives...")
        
        self.running = True
        
        try:
            # Create executives
            await self._initialize_executives()
            
            # Start executive models
            await self._initialize_models()
            
            logger.info("Shadow Board operational with all executives active")
            
        except Exception as e:
            logger.error(f"Failed to start Shadow Board system: {e}")
            self.running = False
            raise
        
    async def _initialize_executives(self):
        """Create all C-Suite executives"""
        
        executive_names = {
            ExecutiveRole.CEO: "Victoria Sterling",
            ExecutiveRole.CFO: "Marcus Chen",
            ExecutiveRole.CTO: "Dr. Sarah Mitchell",
            ExecutiveRole.CMO: "Alexandra Rivera",
            ExecutiveRole.COO: "James Patterson",
            ExecutiveRole.CHRO: "Diana Washington",
            ExecutiveRole.CLO: "Robert Blackwood",
            ExecutiveRole.CSO: "Dr. Michael Foster"
        }
        
        for role, name in executive_names.items():
            exec_id = str(uuid.uuid4())
            
            # Generate personality
            personality = self.personality_engine.generate_executive_personality(role)
            
            # Determine communication style
            comm_style = self._determine_communication_style(personality)
            
            # Create executive
            executive = Executive(
                id=exec_id,
                role=role,
                name=name,
                personality_profile=personality,
                expertise_areas=[],  # Will be set by model
                phd_expertise=[], # Will be set by _initialize_executives_with_phd_expertise
                communication_style=comm_style,
                decision_bias=self._calculate_decision_bias(personality)
            )
            
            self.executives[exec_id] = executive
            
            logger.info(f"Created {role.value}: {name}")
            
    def _initialize_executives_with_phd_expertise(self):
        """Initialize all executives with verifiable, domain-specific PhD-level expertise"""
        phd_expertise_map = {
            ExecutiveRole.CEO: ["organizational leadership", "corporate strategy", "business administration"],
            ExecutiveRole.CFO: ["finance", "accounting", "risk management"],
            ExecutiveRole.CTO: ["computer science", "machine learning", "systems engineering"],
            ExecutiveRole.CMO: ["marketing science", "consumer behavior", "brand management"],
            ExecutiveRole.COO: ["operations research", "supply chain management", "process optimization"],
            ExecutiveRole.CHRO: ["organizational psychology", "human resources", "talent management"],
            ExecutiveRole.CLO: ["corporate law", "compliance", "regulatory affairs"],
            ExecutiveRole.CSO: ["strategic planning", "competitive intelligence", "innovation management"]
        }
        for role in ExecutiveRole:
            exec_id = str(uuid.uuid4())
            executive = Executive(
                id=exec_id,
                role=role,
                name=role.value,
                personality_profile=self.personality_engine.generate_executive_personality(role),
                expertise_areas=[area for area in phd_expertise_map[role]],
                phd_expertise=phd_expertise_map[role],
                communication_style="formal",
                decision_bias={},
                phone_number=None,
                model=None
            )
            self.executives[exec_id] = executive
            self.executive_models[exec_id] = ExecutiveModel(executive)
            
    def _determine_communication_style(self, personality: Dict[str, float]) -> str:
        """Determine executive communication style"""
        
        styles = []
        
        if personality['analytical_thinking'] > 0.8:
            styles.append("data-focused")
        if personality['extraversion'] > 0.7:
            styles.append("engaging")
        if personality['conscientiousness'] > 0.8:
            styles.append("detail-oriented")
        if personality['strategic_vision'] > 0.8:
            styles.append("big-picture")
            
        return ", ".join(styles) if styles else "balanced"
        
    def _calculate_decision_bias(self, personality: Dict[str, float]) -> Dict[str, float]:
        """Calculate decision-making biases based on personality"""
        
        return {
            'growth_focus': personality['innovation_focus'] * personality['risk_tolerance'],
            'stability_focus': personality['conscientiousness'] * (1 - personality['risk_tolerance']),
            'people_focus': personality['agreeableness'] * personality['extraversion'],
            'process_focus': personality['analytical_thinking'] * personality['conscientiousness'],
            'innovation_bias': personality['innovation_focus'] * personality['openness']
        }
        
    async def _initialize_models(self):
        """Initialize AI models for each executive in parallel"""
        
        # Create initialization tasks for all executives
        init_tasks = []
        
        for exec_id, executive in self.executives.items():
            try:
                # Determine device
                if TORCH_AVAILABLE and torch is not None and torch.cuda.is_available():
                    device_id = self.gpu_allocation.get(executive.role, 0)
                    device = torch.device(f'cuda:{device_id}')
                elif TORCH_AVAILABLE and torch is not None:
                    device = torch.device('cpu')
                else:
                    device = None
                
                # Create model and add to initialization tasks
                model = ExecutiveModel(executive, device)
                init_tasks.append((exec_id, model))
                
            except Exception as e:
                logger.error(f"Failed to create model for {executive.name}: {e}")
                continue
        
        # Initialize all models in parallel
        if init_tasks:
            logger.info(f"Initializing {len(init_tasks)} executive models in parallel...")
            
            async def init_single_model(exec_id: str, model: ExecutiveModel):
                try:
                    await model.initialize()
                    self.executive_models[exec_id] = model
                    logger.info(f"Initialized model for {exec_id}")
                    return exec_id, True
                except Exception as e:
                    logger.error(f"Failed to initialize model for {exec_id}: {e}")
                    return exec_id, False
            
            # Run all initializations in parallel
            results = await asyncio.gather(
                *[init_single_model(exec_id, model) for exec_id, model in init_tasks],
                return_exceptions=True
            )
            
            # Log results
            successful = sum(1 for result in results if isinstance(result, tuple) and result[1])
            logger.info(f"Successfully initialized {successful}/{len(init_tasks)} executive models")
        else:
            logger.warning("No executive models to initialize")
            
    async def get_board_recommendation(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations from all board members"""
        
        if not self.running:
            raise ShadowBoardError("Shadow Board system is not running")
            
        board_session_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Board session {board_session_id} initiated")
        
        try:
            # Gather recommendations from all executives
            recommendations = {}
            recommendation_tasks = []
            
            for exec_id, executive in self.executives.items():
                if exec_id in self.executive_models:
                    task = self._get_executive_recommendation(
                        exec_id,
                        decision_context
                    )
                    recommendation_tasks.append(task)
                    
            # Wait for all recommendations
            exec_recommendations = await asyncio.gather(*recommendation_tasks, return_exceptions=True)
            
            # Process recommendations
            for exec_id, rec in zip(self.executives.keys(), exec_recommendations):
                if isinstance(rec, Exception):
                    logger.error(f"Error getting recommendation from {exec_id}: {rec}")
                    recommendations[exec_id] = {
                        'executive_id': exec_id,
                        'error': str(rec),
                        'recommendation': 'abstain'
                    }
                else:
                    recommendations[exec_id] = rec
                    
            # Build consensus
            consensus = await self._build_consensus(recommendations, decision_context)
            
            # Store in database
            await self._store_board_decision(
                board_session_id,
                decision_context,
                recommendations,
                consensus
            )
            
            # Format response
            response = {
                'board_session_id': board_session_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'executives_consulted': len(recommendations),
                'individual_recommendations': self._format_recommendations(recommendations),
                'consensus': consensus,
                'next_steps': self._determine_next_steps(consensus, recommendations)
            }
            
            logger.info(f"Board session {board_session_id} completed in {response['processing_time']:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in board recommendation: {e}")
            raise ShadowBoardError(f"Failed to get board recommendation: {e}")
        
    async def _get_executive_recommendation(self, exec_id: str, 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendation from a specific executive"""
        
        try:
            model = self.executive_models[exec_id]
            recommendation = await model.provide_recommendation(context)
            
            # Add executive metadata
            executive = self.executives[exec_id]
            recommendation['executive_id'] = exec_id
            recommendation['personality_influence'] = self._calculate_personality_influence(
                executive.personality_profile,
                recommendation
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting recommendation from {exec_id}: {e}")
            return {
                'executive_id': exec_id,
                'error': str(e),
                'recommendation': 'abstain'
            }
            
    def _calculate_personality_influence(self, personality: Dict[str, float],
                                       recommendation: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how personality influenced the recommendation"""
        
        influence = {}
        
        # Risk tolerance impact
        if recommendation['recommendation'] == 'approve':
            influence['risk_tolerance_impact'] = personality['risk_tolerance']
        else:
            influence['risk_tolerance_impact'] = 1 - personality['risk_tolerance']
            
        # Analytical impact
        if len(recommendation.get('key_points', [])) > 3:
            influence['analytical_impact'] = personality['analytical_thinking']
        else:
            influence['analytical_impact'] = 0.5
            
        # Innovation impact
        if any('innovat' in str(p).lower() for p in recommendation.get('opportunities', [])):
            influence['innovation_impact'] = personality['innovation_focus']
        else:
            influence['innovation_impact'] = 0.3
            
        return influence
        
    async def _build_consensus(self, recommendations: Dict[str, Dict[str, Any]],
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Build consensus from individual recommendations"""
        
        # Count votes
        votes = {'approve': 0, 'reject': 0, 'conditional': 0, 'abstain': 0}
        total_confidence = 0
        
        for rec in recommendations.values():
            vote = rec.get('recommendation', 'abstain')
            votes[vote] += 1
            total_confidence += rec.get('confidence', 0)
            
        # Determine consensus
        total_votes = len(recommendations)
        approval_rate = votes['approve'] / total_votes if total_votes > 0 else 0
        
        if approval_rate >= 0.75:
            consensus_decision = 'strong_approve'
        elif approval_rate >= 0.5:
            consensus_decision = 'approve'
        elif votes['conditional'] >= votes['reject']:
            consensus_decision = 'conditional'
        else:
            consensus_decision = 'reject'
            
        # Aggregate key insights
        all_risks = []
        all_opportunities = []
        all_conditions = []
        
        for rec in recommendations.values():
            all_risks.extend(rec.get('risks', []))
            all_opportunities.extend(rec.get('opportunities', []))
            all_conditions.extend(rec.get('conditions', []))
            
        # Build consensus report
        consensus = {
            'decision': consensus_decision,
            'approval_rate': approval_rate,
            'average_confidence': total_confidence / total_votes if total_votes > 0 else 0,
            'vote_distribution': votes,
            'key_risks': list(set(all_risks))[:5],  # Top 5 unique risks
            'key_opportunities': list(set(all_opportunities))[:5],
            'conditions': list(set(all_conditions)),
            'dissenting_views': self._identify_dissenting_views(recommendations, consensus_decision),
            'executive_summary': self._generate_executive_summary(
                consensus_decision,
                approval_rate,
                all_risks,
                all_opportunities
            )
        }
        
        return consensus
        
    def _identify_dissenting_views(self, recommendations: Dict[str, Dict[str, Any]],
                                  consensus: str) -> List[Dict[str, str]]:
        """Identify executives with dissenting views"""
        
        dissenting = []
        
        # Determine what counts as dissent based on consensus
        if 'approve' in consensus:
            dissent_votes = ['reject', 'conditional']
        else:
            dissent_votes = ['approve']
            
        for exec_id, rec in recommendations.items():
            if rec.get('recommendation') in dissent_votes:
                executive = self.executives[exec_id]
                dissenting.append({
                    'executive': executive.name,
                    'role': executive.role.value,
                    'position': rec.get('recommendation'),
                    'reasoning': rec.get('key_points', ['No specific reasoning provided'])[0]
                })
                
        return dissenting
        
    def _generate_executive_summary(self, decision: str, approval_rate: float,
                                  risks: List[str], opportunities: List[str]) -> str:
        """Generate executive summary of board decision"""
        
        if decision == 'strong_approve':
            summary = f"The board strongly recommends proceeding with {approval_rate:.0%} approval. "
        elif decision == 'approve':
            summary = f"The board recommends proceeding with {approval_rate:.0%} approval. "
        elif decision == 'conditional':
            summary = "The board conditionally approves, pending specific requirements. "
        else:
            summary = f"The board recommends against proceeding with only {approval_rate:.0%} support. "
            
        if risks:
            summary += f"Key risks include {len(risks)} identified concerns. "
            
        if opportunities:
            summary += f"The board sees {len(opportunities)} strategic opportunities. "
            
        return summary
        
    def _format_recommendations(self, recommendations: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format individual recommendations for response"""
        
        formatted = []
        
        for exec_id, rec in recommendations.items():
            executive = self.executives[exec_id]
            
            formatted.append({
                'executive': executive.name,
                'role': executive.role.value,
                'recommendation': rec.get('recommendation'),
                'confidence': rec.get('confidence', 0),
                'key_points': rec.get('key_points', [])[:3],  # Top 3 points
                'primary_concern': rec.get('risks', ['None identified'])[0] if rec.get('risks') else None
            })
            
        # Sort by role importance (CEO first, then others)
        role_order = [ExecutiveRole.CEO, ExecutiveRole.CFO, ExecutiveRole.COO, 
                     ExecutiveRole.CTO, ExecutiveRole.CMO, ExecutiveRole.CSO,
                     ExecutiveRole.CHRO, ExecutiveRole.CLO]
        
        formatted.sort(key=lambda x: next((i for i, r in enumerate(role_order) 
                                         if r.value == x['role']), 99))
        
        return formatted
        
    def _determine_next_steps(self, consensus: Dict[str, Any],
                            recommendations: Dict[str, Dict[str, Any]]) -> List[str]:
        """Determine recommended next steps based on board decision"""
        
        next_steps = []
        
        if consensus['decision'] in ['strong_approve', 'approve']:
            next_steps.append("Proceed with implementation planning")
            
            if consensus['key_risks']:
                next_steps.append("Develop risk mitigation strategies for identified concerns")
                
            if consensus['average_confidence'] < 0.7:
                next_steps.append("Consider phased rollout to build confidence")
                
        elif consensus['decision'] == 'conditional':
            next_steps.append("Address specified conditions before proceeding")
            
            for condition in consensus['conditions'][:3]:
                next_steps.append(f"Resolve: {condition}")
                
        else:  # Reject
            next_steps.append("Re-evaluate proposal addressing board concerns")
            
            if consensus['dissenting_views']:
                next_steps.append("Consider alternative approaches suggested by dissenters")
                
        return next_steps
        
    async def _store_board_decision(self, session_id: str, context: Dict[str, Any],
                                  recommendations: Dict[str, Dict[str, Any]],
                                  consensus: Dict[str, Any]):
        """Store board decision in database"""
        
        if not SQLITE_AVAILABLE or sqlite3 is None:
            logger.warning("SQLite3 not available - skipping database storage.")
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO board_decisions 
                (id, timestamp, context, recommendations, consensus, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                time.time(),
                json.dumps(context),
                json.dumps(recommendations),
                json.dumps(consensus),
                context.get('user_id')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store board decision: {e}")
            # Don't raise - this is not critical to the main functionality
        
    async def get_executive_phone_call(self, executive_role: str, 
                                     user_id: str,
                                     call_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phone call with specific executive"""
        
        # Find executive by role
        executive = None
        for exec in self.executives.values():
            if exec.role.value.lower() == executive_role.lower():
                executive = exec
                break
                
        if not executive:
            raise ExecutiveNotFoundError(f"Executive role {executive_role} not found")
            
        # Generate conversational response
        model = self.executive_models.get(executive.id)
        if not model:
            raise ModelInitializationError(f"Model not initialized for {executive.name}")
            
        # Build conversational prompt
        prompt = self._build_phone_conversation_prompt(executive, call_context)
        
        # Get response
        response = await model.provide_recommendation({
            'type': 'phone_conversation',
            'context': call_context,
            'prompt': prompt
        })
        
        # Log interaction
        await self._log_executive_interaction(
            executive.id,
            user_id,
            'phone_call',
            call_context
        )
        
        return {
            'executive': executive.name,
            'role': executive.role.value,
            'response': response.get('full_response'),
            'call_summary': self._generate_call_summary(response),
            'follow_up_actions': response.get('key_points', [])
        }
        
    def _build_phone_conversation_prompt(self, executive: Executive,
                                       call_context: Dict[str, Any]) -> str:
        """Build conversational prompt for phone call"""
        
        personality = executive.personality_profile
        
        prompt = f"""You are {executive.name}, {executive.role.value}.
        
You're having a phone conversation with a business owner who needs your expertise.
Your personality traits:
- Communication style: {executive.communication_style}
- Leadership approach: {personality['leadership_style']}

Context of the call: {json.dumps(call_context, indent=2)}

Respond conversationally as if speaking on the phone. Be helpful, professional, and provide actionable insights based on your expertise.
Remember to:
- Speak naturally, as in a real phone conversation
- Ask clarifying questions if needed
- Provide specific, actionable advice
- Reference your experience when relevant
"""
        
        return prompt
        
    def _generate_call_summary(self, response: Dict[str, Any]) -> str:
        """Generate summary of phone call"""
        
        key_points = response.get('key_points', [])
        recommendations = response.get('recommendation', 'No specific recommendation')
        
        summary = f"Discussed {len(key_points)} key points. "
        
        if recommendations != 'No specific recommendation':
            summary += f"Executive recommendation: {recommendations}. "
            
        if response.get('risks'):
            summary += f"Identified {len(response['risks'])} potential risks. "
            
        return summary
        
    async def _log_executive_interaction(self, executive_id: str, user_id: str,
                                       interaction_type: str, content: Dict[str, Any]):
        """Log executive interaction"""
        
        if not SQLITE_AVAILABLE or sqlite3 is None:
            logger.warning("SQLite3 not available - skipping interaction logging.")
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO executive_interactions
                (id, executive_id, user_id, interaction_type, content, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                executive_id,
                user_id,
                interaction_type,
                json.dumps(content),
                time.time()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log executive interaction: {e}")
            # Don't raise - this is not critical to the main functionality
        
    async def shutdown(self):
        """Shutdown Shadow Board system"""
        
        logger.info("Shutting down Shadow Board system...")
        
        self.running = False
        
        # Cleanup models
        for model in self.executive_models.values():
            # Clear GPU memory
            if model.model and TORCH_AVAILABLE and torch is not None:
                try:
                    del model.model
                except Exception as e:
                    logger.error(f"Error cleaning up model: {e}")
                    
        if TORCH_AVAILABLE and torch is not None:
            try:
                torch.cuda.empty_cache()
            except Exception as e:
                logger.error(f"Error clearing CUDA cache: {e}")
        
        logger.info("Shadow Board shutdown complete")

async def main():
    """Main function for testing Shadow Board system"""
    board = ShadowBoardSystem()
    
    try:
        await board.start()
        
        # Test decision
        test_context = {
            'decision_type': 'strategic',
            'description': 'Expand into new market segment',
            'investment_required': 2000000,
            'expected_roi': '35%',
            'timeline': '18 months',
            'risks': ['Market competition', 'Regulatory uncertainty'],
            'opportunities': ['First mover advantage', 'Untapped demand']
        }
        
        recommendation = await board.get_board_recommendation(test_context)
        print(json.dumps(recommendation, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        await board.shutdown()

# Unit test stubs for Executive and ExecutiveModel
if __name__ == "__main__":
    import unittest
    class TestExecutive(unittest.TestCase):
        def test_phd_expertise_required(self):
            with self.assertRaises(ValueError):
                Executive(id="1", role=ExecutiveRole.CEO, name="Test", personality_profile={}, expertise_areas=[], phd_expertise=[], communication_style="formal", decision_bias={})
    class TestExecutiveModel(unittest.TestCase):
        def test_provide_recommendation_requires_model(self):
            executive = Executive(id="2", role=ExecutiveRole.CTO, name="CTO", personality_profile={}, expertise_areas=["computer science"], phd_expertise=["computer science"], communication_style="formal", decision_bias={})
            model = ExecutiveModel(executive)
            model._initialized = True
            model.model = None
            model.tokenizer = None
            with self.assertRaises(ModelInitializationError):
                import asyncio
                asyncio.run(model.provide_recommendation({}))
    unittest.main()