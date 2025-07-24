#!/usr/bin/env python3
"""
SOVREN AI Database Models
PostgreSQL schema with all required tables for production deployment
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, 
    JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB

Base = declarative_base()

class Company(Base):
    """Company information and configuration"""
    __tablename__ = 'companies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    industry = Column(String(100))
    size = Column(String(50))  # small, medium, large
    revenue_range = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    configuration = Column(JSONB)  # Company-specific configuration
    
    # Relationships
    user_sessions = relationship("UserSession", back_populates="company")
    shadow_board_members = relationship("ShadowBoardMember", back_populates="company")
    consciousness_data = relationship("ConsciousnessData", back_populates="company")
    
    __table_args__ = (
        Index('idx_companies_domain', 'domain'),
        Index('idx_companies_industry', 'industry'),
    )

class UserSession(Base):
    """User session and interaction data"""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    session_data = Column(JSONB)  # Session-specific data
    approval_status = Column(String(50), default='pending')  # pending, approved, rejected
    payment_status = Column(String(50), default='pending')  # pending, completed, failed
    
    # Relationships
    company = relationship("Company", back_populates="user_sessions")
    awakening_events = relationship("AwakeningEvent", back_populates="user_session")
    payment_ceremonies = relationship("PaymentCeremony", back_populates="user_session")
    first_contact_events = relationship("FirstContactEvent", back_populates="user_session")
    amazement_events = relationship("AmazementEvent", back_populates="user_session")
    
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_company_id', 'company_id'),
        Index('idx_user_sessions_approval_status', 'approval_status'),
    )

class ShadowBoardMember(Base):
    """Shadow Board executive members"""
    __tablename__ = 'shadow_board_members'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)  # CEO, CFO, CTO, etc.
    expertise = Column(String(255))
    personality_profile = Column(JSONB)
    voice_synthesis_config = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="shadow_board_members")
    consciousness_data = relationship("ConsciousnessData", back_populates="shadow_board_member")
    
    __table_args__ = (
        Index('idx_shadow_board_members_company_id', 'company_id'),
        Index('idx_shadow_board_members_role', 'role'),
        UniqueConstraint('company_id', 'role', name='uq_company_role'),
    )

class ConsciousnessData(Base):
    """Consciousness engine data and states"""
    __tablename__ = 'consciousness_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    shadow_board_member_id = Column(UUID(as_uuid=True), ForeignKey('shadow_board_members.id'))
    consciousness_level = Column(Float, default=0.0)  # 0.0 to 1.0
    decision_paths = Column(Integer, default=0)
    uncertainty_quantification = Column(JSONB)
    real_time_optimization = Column(Boolean, default=True)
    consciousness_state = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="consciousness_data")
    shadow_board_member = relationship("ShadowBoardMember", back_populates="consciousness_data")
    
    __table_args__ = (
        Index('idx_consciousness_data_company_id', 'company_id'),
        Index('idx_consciousness_data_consciousness_level', 'consciousness_level'),
    )

class TimeMachineEvent(Base):
    """Time Machine Memory System events"""
    __tablename__ = 'time_machine_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    event_type = Column(String(100), nullable=False)  # decision, outcome, scenario
    event_data = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
    causality_chain = Column(JSONB)  # Causal relationships
    counterfactual_scenarios = Column(JSONB)
    business_impact = Column(Float)
    confidence_score = Column(Float)
    
    # Relationships
    company = relationship("Company")
    
    __table_args__ = (
        Index('idx_time_machine_events_company_id', 'company_id'),
        Index('idx_time_machine_events_event_type', 'event_type'),
        Index('idx_time_machine_events_timestamp', 'timestamp'),
    )

class AwakeningEvent(Base):
    """Awakening sequence events"""
    __tablename__ = 'awakening_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'), nullable=False)
    awakening_state = Column(String(50), nullable=False)  # initiated, analyzing, visualizing, presenting, complete
    neural_visualization = Column(JSONB)
    business_analysis = Column(JSONB)
    interface_state = Column(JSONB)
    elapsed_ms = Column(Float)
    value_identified = Column(Float)
    opportunities = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_session = relationship("UserSession", back_populates="awakening_events")
    
    __table_args__ = (
        Index('idx_awakening_events_user_session_id', 'user_session_id'),
        Index('idx_awakening_events_awakening_state', 'awakening_state'),
    )

class PaymentCeremony(Base):
    """Payment ceremony events"""
    __tablename__ = 'payment_ceremonies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'), nullable=False)
    ceremony_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    payment_method = Column(String(50))
    kill_bill_integration = Column(Boolean, default=True)
    stripe_primary = Column(Boolean, default=True)
    zoho_fallback = Column(Boolean, default=True)
    celebration_sequence = Column(JSONB)
    payment_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_session = relationship("UserSession", back_populates="payment_ceremonies")
    
    __table_args__ = (
        Index('idx_payment_ceremonies_user_session_id', 'user_session_id'),
        Index('idx_payment_ceremonies_ceremony_id', 'ceremony_id'),
        Index('idx_payment_ceremonies_payment_status', 'payment_status'),
    )

class FirstContactEvent(Base):
    """First contact protocol events"""
    __tablename__ = 'first_contact_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'), nullable=False)
    company_name = Column(String(255))
    business_data = Column(JSONB)
    pre_analysis = Column(JSONB)
    presentation_data = Column(JSONB)
    predictive_needs = Column(JSONB)
    contact_status = Column(String(50), default='initiated')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_session = relationship("UserSession", back_populates="first_contact_events")
    
    __table_args__ = (
        Index('idx_first_contact_events_user_session_id', 'user_session_id'),
        Index('idx_first_contact_events_contact_status', 'contact_status'),
    )

class AmazementEvent(Base):
    """Daily amazement engine events"""
    __tablename__ = 'amazement_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'), nullable=False)
    daily_value = Column(JSONB)
    presentation = Column(JSONB)
    interface_evolution = Column(JSONB)
    amazement_score = Column(Float)
    event_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_session = relationship("UserSession", back_populates="amazement_events")
    
    __table_args__ = (
        Index('idx_amazement_events_user_session_id', 'user_session_id'),
        Index('idx_amazement_events_event_date', 'event_date'),
        Index('idx_amazement_events_amazement_score', 'amazement_score'),
    )

class BayesianEngineData(Base):
    """Bayesian engine data and models"""
    __tablename__ = 'bayesian_engine_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    model_type = Column(String(100), nullable=False)
    model_data = Column(JSONB)
    prior_distributions = Column(JSONB)
    posterior_distributions = Column(JSONB)
    uncertainty_quantification = Column(JSONB)
    model_version = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    
    __table_args__ = (
        Index('idx_bayesian_engine_data_company_id', 'company_id'),
        Index('idx_bayesian_engine_data_model_type', 'model_type'),
    )

class SecurityEvent(Base):
    """Security and adversarial hardening events"""
    __tablename__ = 'security_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    event_type = Column(String(100), nullable=False)  # threat_detected, attack_mitigated, audit_completed
    threat_level = Column(String(50))  # low, medium, high, critical
    event_data = Column(JSONB)
    mitigation_actions = Column(JSONB)
    audit_trail = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    
    __table_args__ = (
        Index('idx_security_events_company_id', 'company_id'),
        Index('idx_security_events_event_type', 'event_type'),
        Index('idx_security_events_threat_level', 'threat_level'),
        Index('idx_security_events_created_at', 'created_at'),
    )

class ZeroKnowledgeProof(Base):
    """Zero-knowledge trust system proofs"""
    __tablename__ = 'zero_knowledge_proofs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    proof_type = Column(String(100), nullable=False)  # authentication, authorization, verification
    proof_data = Column(JSONB)
    cryptographic_parameters = Column(JSONB)
    verification_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company")
    
    __table_args__ = (
        Index('idx_zero_knowledge_proofs_company_id', 'company_id'),
        Index('idx_zero_knowledge_proofs_proof_type', 'proof_type'),
        Index('idx_zero_knowledge_proofs_verification_status', 'verification_status'),
    )

class SystemMetrics(Base):
    """System performance and monitoring metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    metric_type = Column(String(100), nullable=False)  # performance, security, user_experience
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float)
    metric_data = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    
    __table_args__ = (
        Index('idx_system_metrics_company_id', 'company_id'),
        Index('idx_system_metrics_metric_type', 'metric_type'),
        Index('idx_system_metrics_timestamp', 'timestamp'),
    )

# Database session factory
def create_session_factory(database_url: str):
    """Create SQLAlchemy session factory"""
    from sqlalchemy import create_engine
    engine = create_engine(database_url)
    return sessionmaker(bind=engine)

# Database initialization
def init_database(database_url: str):
    """Initialize database with all tables"""
    from sqlalchemy import create_engine
    engine = create_engine(database_url)
    Base.metadata.create_all(engine) 