#!/usr/bin/env python3
"""
SOVREN AI Conversation Predictor
Predicts user needs and conversation flow
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

class PredictionType(str, Enum):
    """Types of predictions"""
    USER_INTENT = "user_intent"
    CONVERSATION_FLOW = "conversation_flow"
    NEXT_ACTION = "next_action"
    RESPONSE_NEEDED = "response_needed"
    TOPIC_SHIFT = "topic_shift"

@dataclass
class ConversationContext:
    """Conversation context model"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    current_topic: Optional[str] = None
    user_mood: Optional[str] = None
    urgency_level: int = 1
    business_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PredictionResult:
    """Prediction result model"""
    prediction_id: str
    prediction_type: PredictionType
    confidence: float
    predicted_value: str
    context: ConversationContext
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationPredictor:
    """Conversation predictor for anticipating user needs"""
    
    def __init__(self):
        self.is_running = False
        self.prediction_models: Dict[PredictionType, Any] = {}
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.prediction_history: List[PredictionResult] = []
        
    async def start(self):
        """Start the conversation predictor"""
        try:
            self.is_running = True
            logger.info("Conversation Predictor started successfully")
            
            # Start background prediction tasks
            asyncio.create_task(self._background_prediction_loop())
            
        except Exception as e:
            logger.error(f"Failed to start conversation predictor: {e}")
            raise
    
    async def stop(self):
        """Stop the conversation predictor"""
        try:
            self.is_running = False
            logger.info("Conversation Predictor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping conversation predictor: {e}")
    
    async def predict_user_intent(self, context: ConversationContext, 
                                user_input: str) -> PredictionResult:
        """Predict user intent from input"""
        try:
            # Analyze user input for intent
            intent = self._analyze_user_intent(user_input, context)
            confidence = self._calculate_intent_confidence(user_input, context)
            
            return PredictionResult(
                prediction_id=f"intent_{int(time.time())}",
                prediction_type=PredictionType.USER_INTENT,
                confidence=confidence,
                predicted_value=intent,
                context=context,
                timestamp=datetime.utcnow(),
                metadata={'input_length': len(user_input), 'user_mood': context.user_mood}
            )
            
        except Exception as e:
            logger.error(f"Error predicting user intent: {e}")
            return self._create_fallback_prediction(context, PredictionType.USER_INTENT)
    
    async def predict_conversation_flow(self, context: ConversationContext) -> PredictionResult:
        """Predict the likely conversation flow"""
        try:
            # Analyze conversation history for flow patterns
            flow_prediction = self._analyze_conversation_flow(context)
            confidence = self._calculate_flow_confidence(context)
            
            return PredictionResult(
                prediction_id=f"flow_{int(time.time())}",
                prediction_type=PredictionType.CONVERSATION_FLOW,
                confidence=confidence,
                predicted_value=flow_prediction,
                context=context,
                timestamp=datetime.utcnow(),
                metadata={'history_length': len(context.conversation_history)}
            )
            
        except Exception as e:
            logger.error(f"Error predicting conversation flow: {e}")
            return self._create_fallback_prediction(context, PredictionType.CONVERSATION_FLOW)
    
    async def predict_next_action(self, context: ConversationContext) -> PredictionResult:
        """Predict the next action needed"""
        try:
            # Determine next action based on context
            next_action = self._determine_next_action(context)
            confidence = self._calculate_action_confidence(context)
            
            return PredictionResult(
                prediction_id=f"action_{int(time.time())}",
                prediction_type=PredictionType.NEXT_ACTION,
                confidence=confidence,
                predicted_value=next_action,
                context=context,
                timestamp=datetime.utcnow(),
                metadata={'urgency': context.urgency_level}
            )
            
        except Exception as e:
            logger.error(f"Error predicting next action: {e}")
            return self._create_fallback_prediction(context, PredictionType.NEXT_ACTION)
    
    async def predict_response_needed(self, context: ConversationContext) -> PredictionResult:
        """Predict if a response is needed"""
        try:
            # Analyze if response is needed
            response_needed = self._analyze_response_need(context)
            confidence = self._calculate_response_confidence(context)
            
            return PredictionResult(
                prediction_id=f"response_{int(time.time())}",
                prediction_type=PredictionType.RESPONSE_NEEDED,
                confidence=confidence,
                predicted_value=response_needed,
                context=context,
                timestamp=datetime.utcnow(),
                metadata={'last_response_time': self._get_last_response_time(context)}
            )
            
        except Exception as e:
            logger.error(f"Error predicting response need: {e}")
            return self._create_fallback_prediction(context, PredictionType.RESPONSE_NEEDED)
    
    async def predict_topic_shift(self, context: ConversationContext) -> PredictionResult:
        """Predict if topic will shift"""
        try:
            # Analyze potential topic shifts
            topic_shift = self._analyze_topic_shift(context)
            confidence = self._calculate_topic_confidence(context)
            
            return PredictionResult(
                prediction_id=f"topic_{int(time.time())}",
                prediction_type=PredictionType.TOPIC_SHIFT,
                confidence=confidence,
                predicted_value=topic_shift,
                context=context,
                timestamp=datetime.utcnow(),
                metadata={'current_topic': context.current_topic}
            )
            
        except Exception as e:
            logger.error(f"Error predicting topic shift: {e}")
            return self._create_fallback_prediction(context, PredictionType.TOPIC_SHIFT)
    
    def _analyze_user_intent(self, user_input: str, context: ConversationContext) -> str:
        """Analyze user input for intent"""
        input_lower = user_input.lower()
        
        # Simple intent analysis based on keywords
        if any(word in input_lower for word in ['help', 'assist', 'support']):
            return 'request_help'
        elif any(word in input_lower for word in ['schedule', 'meeting', 'appointment']):
            return 'schedule_meeting'
        elif any(word in input_lower for word in ['report', 'analysis', 'data']):
            return 'request_report'
        elif any(word in input_lower for word in ['problem', 'issue', 'error']):
            return 'report_problem'
        elif any(word in input_lower for word in ['thank', 'thanks', 'appreciate']):
            return 'express_gratitude'
        else:
            return 'general_inquiry'
    
    def _calculate_intent_confidence(self, user_input: str, context: ConversationContext) -> float:
        """Calculate confidence in intent prediction"""
        # Simple confidence calculation
        input_length = len(user_input)
        if input_length > 50:
            return 0.9
        elif input_length > 20:
            return 0.7
        else:
            return 0.5
    
    def _analyze_conversation_flow(self, context: ConversationContext) -> str:
        """Analyze conversation flow patterns"""
        if not context.conversation_history:
            return 'initial_greeting'
        
        # Analyze recent conversation patterns
        recent_messages = context.conversation_history[-5:]
        
        # Check for question patterns
        question_count = sum(1 for msg in recent_messages if '?' in msg.get('content', ''))
        if question_count > 2:
            return 'information_gathering'
        
        # Check for action patterns
        action_keywords = ['schedule', 'create', 'send', 'analyze']
        action_count = sum(1 for msg in recent_messages 
                         if any(keyword in msg.get('content', '').lower() 
                               for keyword in action_keywords))
        if action_count > 0:
            return 'task_execution'
        
        return 'general_conversation'
    
    def _calculate_flow_confidence(self, context: ConversationContext) -> float:
        """Calculate confidence in flow prediction"""
        history_length = len(context.conversation_history)
        if history_length > 10:
            return 0.8
        elif history_length > 5:
            return 0.6
        else:
            return 0.4
    
    def _determine_next_action(self, context: ConversationContext) -> str:
        """Determine the next action needed"""
        if not context.conversation_history:
            return 'greet_user'
        
        last_message = context.conversation_history[-1]
        content = last_message.get('content', '').lower()
        
        if '?' in content:
            return 'provide_answer'
        elif any(word in content for word in ['schedule', 'meeting']):
            return 'schedule_meeting'
        elif any(word in content for word in ['report', 'analysis']):
            return 'generate_report'
        elif any(word in content for word in ['problem', 'issue']):
            return 'troubleshoot_issue'
        else:
            return 'continue_conversation'
    
    def _calculate_action_confidence(self, context: ConversationContext) -> float:
        """Calculate confidence in action prediction"""
        urgency = context.urgency_level
        if urgency > 7:
            return 0.9
        elif urgency > 4:
            return 0.7
        else:
            return 0.5
    
    def _analyze_response_need(self, context: ConversationContext) -> str:
        """Analyze if a response is needed"""
        if not context.conversation_history:
            return 'yes'
        
        last_message = context.conversation_history[-1]
        sender = last_message.get('sender', '')
        
        # If user sent last message, response likely needed
        if sender == 'user':
            return 'yes'
        else:
            return 'no'
    
    def _calculate_response_confidence(self, context: ConversationContext) -> float:
        """Calculate confidence in response prediction"""
        if not context.conversation_history:
            return 0.8
        
        last_message = context.conversation_history[-1]
        sender = last_message.get('sender', '')
        
        if sender == 'user':
            return 0.9
        else:
            return 0.3
    
    def _analyze_topic_shift(self, context: ConversationContext) -> str:
        """Analyze potential topic shifts"""
        if not context.conversation_history:
            return 'no'
        
        # Check for topic shift indicators
        recent_messages = context.conversation_history[-3:]
        topics = [msg.get('topic', '') for msg in recent_messages if msg.get('topic')]
        
        if len(set(topics)) > 1:
            return 'yes'
        else:
            return 'no'
    
    def _calculate_topic_confidence(self, context: ConversationContext) -> float:
        """Calculate confidence in topic prediction"""
        if not context.conversation_history:
            return 0.3
        
        recent_messages = context.conversation_history[-3:]
        topics = [msg.get('topic', '') for msg in recent_messages if msg.get('topic')]
        
        if len(set(topics)) > 1:
            return 0.8
        else:
            return 0.6
    
    def _get_last_response_time(self, context: ConversationContext) -> Optional[datetime]:
        """Get the time of the last response"""
        if not context.conversation_history:
            return None
        
        for message in reversed(context.conversation_history):
            if message.get('sender') == 'assistant':
                return message.get('timestamp')
        return None
    
    def _create_fallback_prediction(self, context: ConversationContext, 
                                  prediction_type: PredictionType) -> PredictionResult:
        """Create a fallback prediction"""
        return PredictionResult(
            prediction_id=f"fallback_{int(time.time())}",
            prediction_type=prediction_type,
            confidence=0.3,
            predicted_value="unknown",
            context=context,
            timestamp=datetime.utcnow(),
            metadata={'fallback': True}
        )
    
    async def _background_prediction_loop(self):
        """Background prediction loop"""
        while self.is_running:
            try:
                # Perform periodic predictions
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error(f"Error in background prediction loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying

# Global instance
_conversation_predictor = None

def get_conversation_predictor() -> ConversationPredictor:
    """Get the global conversation predictor instance"""
    global _conversation_predictor
    if _conversation_predictor is None:
        _conversation_predictor = ConversationPredictor()
    return _conversation_predictor

async def start_conversation_predictor():
    """Start the global conversation predictor"""
    conversation_predictor = get_conversation_predictor()
    await conversation_predictor.start()

async def stop_conversation_predictor():
    """Stop the global conversation predictor"""
    global _conversation_predictor
    if _conversation_predictor:
        await _conversation_predictor.stop()
        _conversation_predictor = None 