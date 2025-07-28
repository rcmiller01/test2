"""
Intent Classifier - Task type classification for House of Minds

This module analyzes user input to determine the appropriate task type
for routing to the correct AI model or service.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Classifies user intent and determines appropriate task routing.
    
    Uses rule-based pattern matching with confidence scoring.
    Future versions can incorporate ML-based classification.
    """
    
    def __init__(self):
        """Initialize the intent classifier with pattern rules."""
        
        # Define patterns for each task type
        self.intent_patterns = {
            'conversation': {
                'patterns': [
                    r'\b(hello|hi|hey|good morning|good afternoon|how are you)\b',
                    r'\b(chat|talk|discuss|conversation)\b',
                    r'\b(tell me about yourself|introduce yourself)\b',
                    r'^(what|how|why|when|where)\s+(?!.*\b(code|program|script|function)\b)',
                    r'\b(feeling|mood|emotion|happy|sad|excited)\b'
                ],
                'weight': 1.0
            },
            
            'planning': {
                'patterns': [
                    r'\b(plan|planning|schedule|organize|strategy)\b',
                    r'\b(goal|objective|target|aim|roadmap)\b',
                    r'\b(project|timeline|deadline|milestone)\b',
                    r'\b(vacation|trip|travel|itinerary)\b',
                    r'\b(budget|cost|expense|financial plan)\b',
                    r'\b(help me (plan|organize|structure))\b'
                ],
                'weight': 1.2
            },
            
            'code': {
                'patterns': [
                    r'\b(code|program|script|function|algorithm)\b',
                    r'\b(python|javascript|java|c\+\+|html|css|sql)\b',
                    r'\b(debug|fix|error|exception|bug)\b',
                    r'\b(write|create|build|develop|implement)\b.*\b(function|class|module)\b',
                    r'\b(api|database|frontend|backend|framework)\b',
                    r'\b(git|github|repository|commit|merge)\b'
                ],
                'weight': 1.5
            },
            
            'utility': {
                'patterns': [
                    r'\b(send|email|message|text|notify)\b',
                    r'\b(reminder|calendar|appointment|meeting)\b',
                    r'\b(file|document|download|upload|save)\b',
                    r'\b(search|find|lookup|google)\b',
                    r'\b(weather|news|stock|price)\b',
                    r'\b(automation|workflow|task|execute)\b'
                ],
                'weight': 1.3
            },
            
            'memory': {
                'patterns': [
                    r'\b(remember|recall|what did|previous|before|last time)\b',
                    r'\b(memory|history|past|earlier|yesterday)\b',
                    r'\b(we discussed|we talked about|you told me)\b',
                    r'\b(save|store|keep|record)\b.*\b(information|data|note)\b',
                    r'\b(retrieve|find|search)\b.*\b(conversation|discussion|topic)\b'
                ],
                'weight': 1.1
            },
            
            'analysis': {
                'patterns': [
                    r'\b(analyze|analysis|examine|evaluate|assess)\b',
                    r'\b(compare|contrast|pros and cons|advantages|disadvantages)\b',
                    r'\b(data|statistics|metrics|trends|patterns)\b',
                    r'\b(research|study|investigate|explore)\b',
                    r'\b(report|summary|overview|breakdown)\b'
                ],
                'weight': 1.2
            },
            
            'creative': {
                'patterns': [
                    r'\b(write|create|generate|compose)\b.*\b(story|poem|song|script)\b',
                    r'\b(creative|artistic|imaginative|original)\b',
                    r'\b(brainstorm|ideate|concept|design)\b',
                    r'\b(art|music|literature|creative writing)\b',
                    r'\b(marketing|slogan|tagline|copy)\b'
                ],
                'weight': 1.1
            }
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }
        
        # Default fallback task type
        self.default_task_type = 'conversation'
        
        logger.info("🎯 Intent Classifier initialized with pattern-based rules")
    
    async def classify_intent(self, user_input: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify the intent of user input.
        
        Args:
            user_input: The user's request or query
            context: Optional context from previous interactions
            
        Returns:
            Dict containing task_type, confidence, and metadata
        """
        try:
            # Normalize input for pattern matching
            normalized_input = user_input.lower().strip()
            
            # Calculate scores for each task type
            scores = {}
            pattern_matches = {}
            
            for task_type, config in self.intent_patterns.items():
                score, matches = self._calculate_task_score(normalized_input, config)
                scores[task_type] = score
                pattern_matches[task_type] = matches
            
            # Apply context-based adjustments
            if context:
                scores = self._apply_context_adjustments(scores, context)
            
            # Find the highest scoring task type
            best_task_type = max(scores, key=scores.get) if scores else self.default_task_type
            best_score = scores.get(best_task_type, 0.0)
            
            # Determine confidence level
            confidence_level = self._get_confidence_level(best_score)
            
            # If confidence is too low, default to conversation
            if best_score < self.confidence_thresholds['low']:
                best_task_type = self.default_task_type
                confidence_level = 'low'
            
            result = {
                'task_type': best_task_type,
                'confidence': best_score,
                'confidence_level': confidence_level,
                'all_scores': scores,
                'pattern_matches': pattern_matches[best_task_type],
                'timestamp': datetime.now().isoformat(),
                'input_length': len(user_input),
                'normalized_input': normalized_input[:100]  # First 100 chars for debugging
            }
            
            logger.info(f"🎯 Classified as {best_task_type} (confidence: {best_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Intent classification error: {e}")
            return {
                'task_type': self.default_task_type,
                'confidence': 0.0,
                'confidence_level': 'low',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_task_score(self, text: str, config: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate score for a specific task type based on pattern matches."""
        patterns = config['patterns']
        weight = config['weight']
        matches = []
        
        total_score = 0.0
        
        for pattern in patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)
                    # Score based on pattern specificity and weight
                    pattern_score = (1.0 / len(patterns)) * weight
                    total_score += pattern_score
            except re.error as e:
                logger.warning(f"Invalid regex pattern: {pattern} - {e}")
                continue
        
        # Normalize score to 0-1 range
        normalized_score = min(total_score, 1.0)
        
        return normalized_score, matches
    
    def _apply_context_adjustments(self, scores: Dict[str, float], 
                                 context: Dict[str, Any]) -> Dict[str, float]:
        """Apply context-based adjustments to task scores."""
        adjusted_scores = scores.copy()
        
        # Boost score if continuing previous task type
        last_intent = context.get('last_intent')
        if last_intent and last_intent in adjusted_scores:
            adjusted_scores[last_intent] *= 1.1  # 10% boost for continuation
        
        # Boost based on conversation history
        conversation_history = context.get('conversation_history', [])
        if len(conversation_history) > 2:
            # If user has been asking code questions, boost code intent
            recent_intents = [conv.get('intent', '') for conv in conversation_history[-3:]]
            if recent_intents.count('code') >= 2:
                adjusted_scores['code'] *= 1.2
        
        return adjusted_scores
    
    def _get_confidence_level(self, score: float) -> str:
        """Determine confidence level based on score."""
        if score >= self.confidence_thresholds['high']:
            return 'high'
        elif score >= self.confidence_thresholds['medium']:
            return 'medium'
        elif score >= self.confidence_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def add_pattern(self, task_type: str, pattern: str, weight: float = 1.0):
        """Add a new pattern for a task type."""
        if task_type not in self.intent_patterns:
            self.intent_patterns[task_type] = {'patterns': [], 'weight': weight}
        
        self.intent_patterns[task_type]['patterns'].append(pattern)
        logger.info(f"➕ Added pattern for {task_type}: {pattern}")
    
    def remove_pattern(self, task_type: str, pattern: str):
        """Remove a pattern from a task type."""
        if task_type in self.intent_patterns:
            patterns = self.intent_patterns[task_type]['patterns']
            if pattern in patterns:
                patterns.remove(pattern)
                logger.info(f"➖ Removed pattern from {task_type}: {pattern}")
    
    def get_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all current patterns."""
        return self.intent_patterns.copy()
    
    def update_confidence_thresholds(self, thresholds: Dict[str, float]):
        """Update confidence thresholds."""
        self.confidence_thresholds.update(thresholds)
        logger.info(f"🎯 Updated confidence thresholds: {thresholds}")
    
    async def batch_classify(self, inputs: List[str], 
                           context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Classify multiple inputs in batch."""
        results = []
        for user_input in inputs:
            result = await self.classify_intent(user_input, context)
            results.append(result)
        
        logger.info(f"📊 Batch classified {len(inputs)} inputs")
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get classification statistics and patterns info."""
        stats = {
            'total_task_types': len(self.intent_patterns),
            'total_patterns': sum(len(config['patterns']) for config in self.intent_patterns.values()),
            'task_types': list(self.intent_patterns.keys()),
            'confidence_thresholds': self.confidence_thresholds,
            'default_task_type': self.default_task_type
        }
        
        return stats
