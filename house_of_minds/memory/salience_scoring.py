"""
True Recall - Salience Scoring System

Advanced salience scoring using multiple factors to determine memory importance
including recency, frequency, emotional weight, user attention, and contextual relevance.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)

class SalienceScorer:
    """
    Multi-factor salience scoring system for memory importance ranking.
    
    Uses temporal decay, frequency analysis, emotional impact, user engagement,
    and contextual factors to calculate memory salience scores.
    """
    
    def __init__(self):
        """Initialize the salience scorer with configurable weights."""
        
        # Scoring weights (should sum to 1.0)
        self.weights = {
            'recency': 0.25,        # How recent the memory is
            'frequency': 0.20,      # How often similar content appears
            'emotional': 0.25,      # Emotional impact and intensity
            'engagement': 0.15,     # User interaction and attention
            'contextual': 0.15      # Situational and topical relevance
        }
        
        # Decay parameters
        self.temporal_decay_days = 30    # Days for 50% decay
        self.frequency_window_days = 7   # Window for frequency analysis
        
        # Engagement indicators
        self.engagement_keywords = {
            'high': ['important', 'remember', 'significant', 'crucial', 'key', 
                    'vital', 'essential', 'critical', 'urgent', 'priority'],
            'medium': ['interesting', 'notable', 'relevant', 'useful', 'good', 
                      'nice', 'cool', 'helpful', 'valuable'],
            'low': ['maybe', 'perhaps', 'might', 'possibly', 'sometimes', 
                   'occasionally', 'random', 'whatever']
        }
        
        # Contextual importance indicators
        self.context_indicators = {
            'personal': ['family', 'friend', 'relationship', 'personal', 'private',
                        'feelings', 'emotions', 'dream', 'goal', 'achievement'],
            'work': ['work', 'job', 'career', 'project', 'meeting', 'deadline',
                    'task', 'business', 'professional', 'client'],
            'learning': ['learn', 'study', 'understand', 'knowledge', 'skill',
                        'practice', 'improve', 'develop', 'research', 'discover'],
            'health': ['health', 'medical', 'doctor', 'medicine', 'exercise',
                      'diet', 'wellness', 'fitness', 'therapy', 'treatment'],
            'emergency': ['urgent', 'emergency', 'immediate', 'asap', 'critical',
                         'crisis', 'problem', 'issue', 'help', 'danger']
        }
        
        logger.info("📊 SalienceScorer initialized with multi-factor analysis")
    
    def calculate_salience(
        self, 
        event: Dict[str, Any], 
        historical_events: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive salience score for a memory event.
        
        Args:
            event: The memory event to score
            historical_events: Previous events for frequency and pattern analysis
            user_context: Additional context about user preferences and patterns
            
        Returns:
            Dict containing salience score and component breakdowns
        """
        try:
            # Initialize component scores
            scores = {
                'recency': 0.0,
                'frequency': 0.0,
                'emotional': 0.0,
                'engagement': 0.0,
                'contextual': 0.0
            }
            
            # Calculate each component
            scores['recency'] = self._calculate_recency_score(event)
            scores['frequency'] = self._calculate_frequency_score(event, historical_events or [])
            scores['emotional'] = self._calculate_emotional_score(event)
            scores['engagement'] = self._calculate_engagement_score(event)
            scores['contextual'] = self._calculate_contextual_score(event, user_context)
            
            # Calculate weighted final score
            final_score = sum(scores[component] * self.weights[component] 
                            for component in scores)
            
            # Apply normalization and bounds
            final_score = max(0.0, min(1.0, final_score))
            
            # Generate salience metadata
            salience_data = {
                'salience_score': round(final_score, 4),
                'component_scores': {k: round(v, 4) for k, v in scores.items()},
                'salience_level': self._categorize_salience(final_score),
                'scoring_factors': self._identify_key_factors(scores),
                'confidence': self._calculate_scoring_confidence(event, scores),
                'calculated_at': datetime.now().isoformat()
            }
            
            return salience_data
            
        except Exception as e:
            logger.error(f"❌ Error calculating salience: {e}")
            return self._create_default_salience()
    
    def _calculate_recency_score(self, event: Dict[str, Any]) -> float:
        """Calculate recency-based salience score."""
        try:
            # Get event timestamp
            timestamp_str = event.get('timestamp', event.get('created_at', ''))
            if not timestamp_str:
                return 0.5  # Neutral score for unknown timing
            
            # Parse timestamp
            event_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            current_time = datetime.now(event_time.tzinfo) if event_time.tzinfo else datetime.now()
            
            # Calculate time difference in days
            time_diff = (current_time - event_time).total_seconds() / (24 * 3600)
            
            # Apply exponential decay
            decay_factor = math.exp(-time_diff / self.temporal_decay_days)
            
            # Recent events get bonus scoring
            if time_diff < 1:  # Less than 1 day
                recency_score = 1.0
            elif time_diff < 7:  # Less than 1 week
                recency_score = 0.8 + (decay_factor * 0.2)
            else:
                recency_score = decay_factor
            
            return max(0.0, min(1.0, recency_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating recency score: {e}")
            return 0.5
    
    def _calculate_frequency_score(self, event: Dict[str, Any], historical_events: List[Dict[str, Any]]) -> float:
        """Calculate frequency-based salience score."""
        try:
            if not historical_events:
                return 0.3  # Neutral score for no history
            
            current_content = event.get('content', '').lower()
            current_actor = event.get('actor', '')
            
            # Extract key terms from current event
            current_terms = self._extract_key_terms(current_content)
            if not current_terms:
                return 0.3
            
            # Analyze recent events for patterns
            cutoff_date = datetime.now() - timedelta(days=self.frequency_window_days)
            recent_events = []
            
            for hist_event in historical_events:
                try:
                    hist_timestamp = hist_event.get('timestamp', hist_event.get('created_at', ''))
                    if hist_timestamp:
                        hist_time = datetime.fromisoformat(hist_timestamp.replace('Z', '+00:00'))
                        if hist_time >= cutoff_date:
                            recent_events.append(hist_event)
                except:
                    continue
            
            if not recent_events:
                return 0.3
            
            # Count term frequencies
            term_counts = Counter()
            actor_mentions = 0
            total_events = len(recent_events)
            
            for hist_event in recent_events:
                hist_content = hist_event.get('content', '').lower()
                hist_terms = self._extract_key_terms(hist_content)
                
                # Count matching terms
                for term in current_terms:
                    if term in hist_terms:
                        term_counts[term] += 1
                
                # Count actor appearances
                if hist_event.get('actor') == current_actor:
                    actor_mentions += 1
            
            # Calculate frequency scores
            term_frequency_score = 0.0
            if current_terms:
                avg_frequency = sum(term_counts.values()) / len(current_terms)
                term_frequency_score = min(1.0, avg_frequency / total_events)
            
            actor_frequency_score = actor_mentions / total_events if total_events > 0 else 0
            
            # Inverse frequency weighting (rare terms are more salient)
            rare_term_bonus = 0.0
            if current_terms:
                for term in current_terms:
                    if term_counts[term] == 0:  # Unique term
                        rare_term_bonus += 0.2
                rare_term_bonus = min(1.0, rare_term_bonus / len(current_terms))
            
            # Combine frequency factors
            frequency_score = (
                term_frequency_score * 0.4 +
                actor_frequency_score * 0.3 +
                rare_term_bonus * 0.3
            )
            
            return max(0.0, min(1.0, frequency_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating frequency score: {e}")
            return 0.3
    
    def _calculate_emotional_score(self, event: Dict[str, Any]) -> float:
        """Calculate emotion-based salience score."""
        try:
            emotion_data = event.get('emotion_analysis', {})
            if not emotion_data:
                return 0.2  # Low score for no emotional data
            
            # Get emotional metrics
            intensity = emotion_data.get('emotional_intensity', 0.0)
            primary_emotion = emotion_data.get('primary_emotion')
            detected_emotions = emotion_data.get('detected_emotions', {})
            valence = abs(emotion_data.get('valence', 0.0))  # Absolute value - strong emotions matter
            arousal = abs(emotion_data.get('arousal', 0.0))
            
            # Base score from intensity
            intensity_score = min(1.0, intensity / 2.0)  # Normalize intensity
            
            # Bonus for high-impact emotions
            high_impact_emotions = ['anger', 'fear', 'joy', 'love', 'sadness', 'surprise']
            impact_bonus = 0.0
            if primary_emotion in high_impact_emotions:
                impact_bonus = 0.3
            
            # Score from valence and arousal
            valence_arousal_score = (valence + arousal) / 2.0
            
            # Emotional complexity bonus (multiple emotions)
            complexity_bonus = min(0.2, len(detected_emotions) * 0.05)
            
            # Combine emotional factors
            emotional_score = (
                intensity_score * 0.4 +
                impact_bonus +
                valence_arousal_score * 0.3 +
                complexity_bonus
            )
            
            return max(0.0, min(1.0, emotional_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating emotional score: {e}")
            return 0.2
    
    def _calculate_engagement_score(self, event: Dict[str, Any]) -> float:
        """Calculate user engagement-based salience score."""
        try:
            content = event.get('content', '').lower()
            actor = event.get('actor', '')
            
            # Length factor (longer messages often indicate more engagement)
            word_count = len(content.split())
            length_score = min(1.0, word_count / 50)  # Normalize around 50 words
            
            # Keyword-based engagement detection
            engagement_score = 0.0
            
            for level, keywords in self.engagement_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        if level == 'high':
                            engagement_score += 0.3
                        elif level == 'medium':
                            engagement_score += 0.1
                        else:  # low
                            engagement_score -= 0.1
            
            # Question indicators (show interest/engagement)
            question_count = content.count('?')
            question_score = min(0.3, question_count * 0.1)
            
            # Exclamation indicators (show emotion/engagement)
            exclamation_count = content.count('!')
            exclamation_score = min(0.2, exclamation_count * 0.05)
            
            # User vs system engagement
            actor_bonus = 0.0
            if actor.lower() in ['user', 'human']:
                actor_bonus = 0.2  # User messages often more salient
            elif actor.lower() == 'system':
                actor_bonus = -0.1  # System messages less salient
            
            # Combine engagement factors
            total_engagement = (
                length_score * 0.3 +
                min(1.0, engagement_score) * 0.4 +
                question_score +
                exclamation_score +
                actor_bonus
            )
            
            return max(0.0, min(1.0, total_engagement))
            
        except Exception as e:
            logger.error(f"❌ Error calculating engagement score: {e}")
            return 0.3
    
    def _calculate_contextual_score(self, event: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> float:
        """Calculate context-based salience score."""
        try:
            content = event.get('content', '').lower()
            
            # Base contextual relevance
            context_score = 0.0
            
            # Check for contextual indicators
            for context_type, keywords in self.context_indicators.items():
                type_score = 0.0
                for keyword in keywords:
                    if keyword in content:
                        # Weight different context types
                        if context_type == 'emergency':
                            type_score += 0.4
                        elif context_type == 'personal':
                            type_score += 0.3
                        elif context_type in ['work', 'health']:
                            type_score += 0.2
                        else:
                            type_score += 0.1
                
                context_score += min(0.4, type_score)  # Cap per category
            
            # User context adjustments
            if user_context:
                # Time of day context
                hour = user_context.get('hour')
                if hour is not None:
                    if 9 <= hour <= 17:  # Work hours
                        if 'work' in content or 'job' in content:
                            context_score += 0.2
                    elif 18 <= hour <= 22:  # Evening
                        if any(word in content for word in ['family', 'personal', 'relax']):
                            context_score += 0.2
                
                # User preferences
                preferences = user_context.get('interests', [])
                for interest in preferences:
                    if interest.lower() in content:
                        context_score += 0.1
            
            # Event type contextual importance
            event_type = event.get('event_type', '')
            if event_type in ['error', 'warning', 'alert']:
                context_score += 0.3
            elif event_type in ['achievement', 'milestone']:
                context_score += 0.2
            
            return max(0.0, min(1.0, context_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating contextual score: {e}")
            return 0.3
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for frequency analysis."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract words and filter
        words = re.findall(r'\b\w{3,}\b', text.lower())  # 3+ letter words
        key_terms = [word for word in words if word not in stop_words]
        
        return list(set(key_terms))  # Remove duplicates
    
    def _categorize_salience(self, score: float) -> str:
        """Categorize salience score into levels."""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        elif score >= 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _identify_key_factors(self, scores: Dict[str, float]) -> List[str]:
        """Identify the most important scoring factors."""
        # Sort by weighted contribution
        weighted_scores = [(factor, score * self.weights[factor]) 
                          for factor, score in scores.items()]
        weighted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top contributing factors
        return [factor for factor, weighted_score in weighted_scores[:3] 
                if weighted_score > 0.1]
    
    def _calculate_scoring_confidence(self, event: Dict[str, Any], scores: Dict[str, float]) -> float:
        """Calculate confidence in the salience scoring."""
        # Base confidence on data availability
        content_length = len(event.get('content', ''))
        has_emotion_data = bool(event.get('emotion_analysis'))
        has_timestamp = bool(event.get('timestamp') or event.get('created_at'))
        
        # Data quality factors
        length_factor = min(1.0, content_length / 100)
        emotion_factor = 1.0 if has_emotion_data else 0.5
        timestamp_factor = 1.0 if has_timestamp else 0.7
        
        # Score distribution factor (avoid all-low or all-high scores)
        score_variance = sum((s - 0.5) ** 2 for s in scores.values()) / len(scores)
        variance_factor = min(1.0, score_variance * 4)  # Higher variance = more confidence
        
        confidence = (length_factor + emotion_factor + timestamp_factor + variance_factor) / 4
        
        return round(confidence, 3)
    
    def _create_default_salience(self) -> Dict[str, Any]:
        """Create default salience data for error cases."""
        return {
            'salience_score': 0.3,
            'component_scores': {k: 0.3 for k in self.weights.keys()},
            'salience_level': 'low',
            'scoring_factors': [],
            'confidence': 0.2,
            'calculated_at': datetime.now().isoformat()
        }
    
    def update_weights(self, new_weights: Dict[str, float]) -> bool:
        """Update scoring weights (must sum to 1.0)."""
        try:
            if abs(sum(new_weights.values()) - 1.0) > 0.01:
                logger.error("❌ Weights must sum to 1.0")
                return False
            
            for component in self.weights:
                if component in new_weights:
                    self.weights[component] = new_weights[component]
            
            logger.info(f"📊 Updated salience weights: {self.weights}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating weights: {e}")
            return False

# Convenience function
def create_salience_scorer() -> SalienceScorer:
    """Create and return a salience scorer instance."""
    return SalienceScorer()
