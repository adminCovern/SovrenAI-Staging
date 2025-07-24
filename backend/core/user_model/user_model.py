#!/usr/bin/env python3
"""
SOVREN AI User Model
User behavior modeling and personalization
Production-ready implementation with enterprise standards
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    EXECUTIVE = "executive"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"

class UserPreference(str, Enum):
    """User preferences"""
    VOICE_INTERFACE = "voice_interface"
    TEXT_INTERFACE = "text_interface"
    NOTIFICATIONS_ENABLED = "notifications_enabled"
    EMAIL_SUMMARIES = "email_summaries"
    DARK_MODE = "dark_mode"

@dataclass
class UserProfile:
    """User profile model"""
    user_id: str
    name: str
    email: str
    role: UserRole
    company: Optional[str] = None
    department: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserBehavior:
    """User behavior model"""
    user_id: str
    session_count: int = 0
    total_session_time: float = 0.0
    average_session_time: float = 0.0
    favorite_features: List[str] = field(default_factory=list)
    common_queries: List[str] = field(default_factory=list)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)

class UserModel:
    """User model for behavior analysis and personalization"""
    
    def __init__(self):
        self.is_running = False
        self.user_profiles: Dict[str, UserProfile] = {}
        self.user_behaviors: Dict[str, UserBehavior] = {}
        self.user_sessions: Dict[str, List[Dict[str, Any]]] = {}
        
    async def start(self):
        """Start the user model"""
        try:
            self.is_running = True
            logger.info("User Model started successfully")
            
            # Start background user analysis tasks
            asyncio.create_task(self._background_user_analysis_loop())
            
        except Exception as e:
            logger.error(f"Failed to start user model: {e}")
            raise
    
    async def stop(self):
        """Stop the user model"""
        try:
            self.is_running = False
            logger.info("User Model stopped")
            
        except Exception as e:
            logger.error(f"Error stopping user model: {e}")
    
    async def create_user_profile(self, user_id: str, name: str, email: str,
                                role: UserRole, company: Optional[str] = None,
                                department: Optional[str] = None) -> UserProfile:
        """Create a new user profile"""
        try:
            profile = UserProfile(
                user_id=user_id,
                name=name,
                email=email,
                role=role,
                company=company,
                department=department
            )
            
            self.user_profiles[user_id] = profile
            
            # Initialize user behavior
            behavior = UserBehavior(user_id=user_id)
            self.user_behaviors[user_id] = behavior
            
            logger.info(f"Created user profile for {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.user_profiles.get(user_id)
    
    async def update_user_profile(self, user_id: str, 
                                updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile"""
        try:
            if user_id not in self.user_profiles:
                return None
            
            profile = self.user_profiles[user_id]
            
            # Update profile fields
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.last_active = datetime.utcnow()
            
            logger.info(f"Updated user profile for {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return None
    
    async def get_user_behavior(self, user_id: str) -> Optional[UserBehavior]:
        """Get user behavior by ID"""
        return self.user_behaviors.get(user_id)
    
    async def record_user_session(self, user_id: str, session_data: Dict[str, Any]):
        """Record a user session"""
        try:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            
            session_data['timestamp'] = datetime.utcnow()
            self.user_sessions[user_id].append(session_data)
            
            # Update user behavior
            if user_id in self.user_behaviors:
                behavior = self.user_behaviors[user_id]
                behavior.session_count += 1
                
                # Update session time
                session_duration = session_data.get('duration', 0)
                behavior.total_session_time += session_duration
                behavior.average_session_time = behavior.total_session_time / behavior.session_count
                
                # Update favorite features
                features_used = session_data.get('features_used', [])
                for feature in features_used:
                    if feature not in behavior.favorite_features:
                        behavior.favorite_features.append(feature)
                
                # Update common queries
                queries = session_data.get('queries', [])
                for query in queries:
                    if query not in behavior.common_queries:
                        behavior.common_queries.append(query)
            
            logger.info(f"Recorded session for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error recording user session: {e}")
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            if user_id in self.user_profiles:
                return self.user_profiles[user_id].preferences
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    async def update_user_preferences(self, user_id: str, 
                                    preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                profile.preferences.update(preferences)
                profile.last_active = datetime.utcnow()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    async def get_user_recommendations(self, user_id: str) -> List[str]:
        """Get personalized recommendations for user"""
        try:
            if user_id not in self.user_behaviors:
                return []
            
            behavior = self.user_behaviors[user_id]
            recommendations = []
            
            # Generate recommendations based on behavior
            if behavior.session_count > 10:
                recommendations.append("You're a power user! Consider advanced features.")
            
            if behavior.average_session_time > 300:  # 5 minutes
                recommendations.append("Long sessions detected. Try voice interface for efficiency.")
            
            if len(behavior.favorite_features) > 3:
                recommendations.append("You use many features. Consider custom workflows.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []
    
    async def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        try:
            if user_id not in self.user_sessions:
                return {}
            
            sessions = self.user_sessions[user_id]
            if not sessions:
                return {}
            
            # Analyze patterns
            patterns = {
                'total_sessions': len(sessions),
                'avg_session_duration': sum(s.get('duration', 0) for s in sessions) / len(sessions),
                'peak_usage_hours': self._analyze_peak_hours(sessions),
                'common_features': self._analyze_common_features(sessions),
                'query_patterns': self._analyze_query_patterns(sessions)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}
    
    def _analyze_peak_hours(self, sessions: List[Dict[str, Any]]) -> List[int]:
        """Analyze peak usage hours"""
        try:
            hours = []
            for session in sessions:
                timestamp = session.get('timestamp')
                if timestamp:
                    hours.append(timestamp.hour)
            
            # Find most common hours
            from collections import Counter
            hour_counts = Counter(hours)
            return [hour for hour, count in hour_counts.most_common(3)]
            
        except Exception:
            return []
    
    def _analyze_common_features(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Analyze commonly used features"""
        try:
            all_features = []
            for session in sessions:
                features = session.get('features_used', [])
                all_features.extend(features)
            
            from collections import Counter
            feature_counts = Counter(all_features)
            return [feature for feature, count in feature_counts.most_common(5)]
            
        except Exception:
            return []
    
    def _analyze_query_patterns(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze query patterns"""
        try:
            all_queries = []
            for session in sessions:
                queries = session.get('queries', [])
                all_queries.extend(queries)
            
            # Simple pattern analysis
            return {
                'total_queries': len(all_queries),
                'unique_queries': len(set(all_queries)),
                'avg_queries_per_session': len(all_queries) / len(sessions) if sessions else 0
            }
            
        except Exception:
            return {}
    
    async def _background_user_analysis_loop(self):
        """Background user analysis loop"""
        while self.is_running:
            try:
                # Perform periodic user analysis
                await self._analyze_all_users()
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in background user analysis loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _analyze_all_users(self):
        """Analyze all users"""
        try:
            for user_id in self.user_profiles.keys():
                try:
                    # Update user behavior patterns
                    patterns = await self.analyze_user_patterns(user_id)
                    
                    if user_id in self.user_behaviors:
                        behavior = self.user_behaviors[user_id]
                        behavior.interaction_patterns = patterns
                    
                except Exception as e:
                    logger.error(f"Error analyzing user {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in user analysis: {e}")

# Global instance
_user_model = None

def get_user_model() -> UserModel:
    """Get the global user model instance"""
    global _user_model
    if _user_model is None:
        _user_model = UserModel()
    return _user_model

async def start_user_model():
    """Start the global user model"""
    user_model = get_user_model()
    await user_model.start()

async def stop_user_model():
    """Stop the global user model"""
    global _user_model
    if _user_model:
        await _user_model.stop()
        _user_model = None 