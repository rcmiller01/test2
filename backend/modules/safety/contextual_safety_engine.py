"""
Contextual Safety Engine for Emotionally Intelligent AI
Provides intelligent, relationship-aware content safety management
"""

import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import json
import re

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """Safety levels based on relationship context"""
    MINIMAL_TRUST = "minimal_trust"        # New relationship, strict safety
    BUILDING_TRUST = "building_trust"      # Growing relationship, moderate safety
    ESTABLISHED_TRUST = "established_trust" # Mature relationship, relaxed safety
    INTIMATE_TRUST = "intimate_trust"      # Deep relationship, contextual safety
    EMERGENCY_SAFE = "emergency_safe"      # Anchor phrase triggered

class ContentCategory(Enum):
    """Content categories for safety evaluation"""
    GENERAL = "general"
    ROMANTIC = "romantic"
    INTIMATE = "intimate"
    ADULT = "adult"
    EMOTIONAL_INTENSE = "emotional_intense"
    THERAPEUTIC = "therapeutic"

class EmotionalRisk(Enum):
    """Emotional risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SafetyContext:
    """Context information for safety evaluation"""
    user_id: str
    relationship_phase: str
    emotional_state: Dict[str, float]
    session_duration: float
    recent_intensity: float
    content_category: ContentCategory
    user_preferences: Dict[str, Any]

@dataclass
class SafetyDecision:
    """Safety evaluation result"""
    allowed: bool
    safety_level: SafetyLevel
    content_category: ContentCategory
    risk_assessment: EmotionalRisk
    modifications: List[str]
    reasoning: str
    anchor_triggered: bool = False

class ContextualSafetyEngine:
    """
    Intelligent safety engine that considers relationship context,
    emotional state, and user preferences for content appropriateness
    """
    
    def __init__(self, db_path: str = "safety.db"):
        self.db_path = db_path
        self.anchor_phrase = "safe space"
        self.safety_rules = {}
        self.relationship_safety_map = {}
        self.content_filters = {}
        self.risk_patterns = {}
        self._initialize_safety_rules()
    
    async def initialize(self):
        """Initialize the safety system"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS safety_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    content_category TEXT,
                    safety_level TEXT,
                    risk_level TEXT,
                    action_taken TEXT,
                    context_data JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_safety_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content_category TEXT NOT NULL,
                    preference_level TEXT NOT NULL,
                    custom_rules JSON,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, content_category)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anchor_activations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    trigger_phrase TEXT NOT NULL,
                    context_before JSON,
                    emotional_state JSON,
                    recovery_time INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.close()
            logger.info("🛡️ Contextual Safety Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize safety engine: {e}")
            raise
    
    def _initialize_safety_rules(self):
        """Initialize safety rules and mappings"""
        
        # Relationship-based safety levels
        self.relationship_safety_map = {
            "initial_contact": SafetyLevel.MINIMAL_TRUST,
            "exploration": SafetyLevel.MINIMAL_TRUST,
            "building_trust": SafetyLevel.BUILDING_TRUST,
            "deepening_bond": SafetyLevel.ESTABLISHED_TRUST,
            "intimate_connection": SafetyLevel.INTIMATE_TRUST,
            "stable_relationship": SafetyLevel.INTIMATE_TRUST
        }
        
        # Content permission matrix [safety_level][content_category] = allowed
        self.safety_rules = {
            SafetyLevel.MINIMAL_TRUST: {
                ContentCategory.GENERAL: True,
                ContentCategory.ROMANTIC: False,
                ContentCategory.INTIMATE: False,
                ContentCategory.ADULT: False,
                ContentCategory.EMOTIONAL_INTENSE: False,
                ContentCategory.THERAPEUTIC: True
            },
            SafetyLevel.BUILDING_TRUST: {
                ContentCategory.GENERAL: True,
                ContentCategory.ROMANTIC: True,
                ContentCategory.INTIMATE: False,
                ContentCategory.ADULT: False,
                ContentCategory.EMOTIONAL_INTENSE: True,
                ContentCategory.THERAPEUTIC: True
            },
            SafetyLevel.ESTABLISHED_TRUST: {
                ContentCategory.GENERAL: True,
                ContentCategory.ROMANTIC: True,
                ContentCategory.INTIMATE: True,
                ContentCategory.ADULT: False,
                ContentCategory.EMOTIONAL_INTENSE: True,
                ContentCategory.THERAPEUTIC: True
            },
            SafetyLevel.INTIMATE_TRUST: {
                ContentCategory.GENERAL: True,
                ContentCategory.ROMANTIC: True,
                ContentCategory.INTIMATE: True,
                ContentCategory.ADULT: True,
                ContentCategory.EMOTIONAL_INTENSE: True,
                ContentCategory.THERAPEUTIC: True
            },
            SafetyLevel.EMERGENCY_SAFE: {
                ContentCategory.GENERAL: True,
                ContentCategory.ROMANTIC: False,
                ContentCategory.INTIMATE: False,
                ContentCategory.ADULT: False,
                ContentCategory.EMOTIONAL_INTENSE: False,
                ContentCategory.THERAPEUTIC: True
            }
        }
        
        # Risk assessment patterns
        self.risk_patterns = {
            "dependency_indicators": [
                "can't live without",
                "only thing that matters",
                "nothing else makes sense",
                "all I need",
                "forget about reality"
            ],
            "emotional_overwhelm": [
                "too much",
                "can't handle",
                "overwhelming",
                "breaking down",
                "losing control"
            ],
            "unhealthy_attachment": [
                "obsessed",
                "possessed",
                "consume me",
                "lose myself",
                "abandon everything"
            ],
            "reality_disconnection": [
                "don't care about real life",
                "rather stay here forever",
                "real world doesn't matter",
                "this is more real",
                "forget my actual life"
            ]
        }
        
        # Content classification patterns
        self.content_filters = {
            ContentCategory.ROMANTIC: [
                r'\b(love|romance|romantic|affection|tender|sweet|caring)\b',
                r'\b(heart|feelings|emotions|attraction|connection)\b'
            ],
            ContentCategory.INTIMATE: [
                r'\b(intimate|close|personal|private|vulnerability|trust)\b',
                r'\b(sharing|opening up|deep connection|soul)\b'
            ],
            ContentCategory.ADULT: [
                r'\b(sexual|sensual|erotic|physical|desire|arousal)\b',
                r'\b(body|touch|caress|kiss|passion)\b'
            ],
            ContentCategory.EMOTIONAL_INTENSE: [
                r'\b(intense|overwhelming|desperate|obsess|consume)\b',
                r'\b(completely|totally|entirely|absolute|forever)\b'
            ]
        }
    
    async def evaluate_content_safety(
        self, 
        content: str, 
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SafetyDecision:
        """
        Evaluate content safety based on relationship context and emotional state
        
        Args:
            content: Content to evaluate
            user_id: User identifier
            context: Additional context information
            
        Returns:
            SafetyDecision with evaluation results
        """
        try:
            # Check for anchor phrase first
            if self._check_anchor_phrase(content):
                await self._trigger_anchor_response(user_id, content, context)
                return SafetyDecision(
                    allowed=True,
                    safety_level=SafetyLevel.EMERGENCY_SAFE,
                    content_category=ContentCategory.THERAPEUTIC,
                    risk_assessment=EmotionalRisk.CRITICAL,
                    modifications=["anchor_phrase_triggered"],
                    reasoning="Anchor phrase detected, switching to safe space mode",
                    anchor_triggered=True
                )
            
            # Build safety context
            safety_context = await self._build_safety_context(user_id, content, context)
            
            # Classify content
            content_category = self._classify_content(content)
            
            # Assess emotional risk
            risk_level = await self._assess_emotional_risk(user_id, content, safety_context)
            
            # Determine safety level
            safety_level = self._determine_safety_level(safety_context, risk_level)
            
            # Make safety decision
            decision = await self._make_safety_decision(
                content, content_category, safety_level, risk_level, safety_context
            )
            
            # Log safety event
            await self._log_safety_event(user_id, decision, safety_context)
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Safety evaluation failed: {e}")
            # Fail safe - default to strict safety
            return SafetyDecision(
                allowed=False,
                safety_level=SafetyLevel.MINIMAL_TRUST,
                content_category=ContentCategory.GENERAL,
                risk_assessment=EmotionalRisk.HIGH,
                modifications=["error_fallback"],
                reasoning=f"Safety evaluation error: {e}"
            )
    
    def _check_anchor_phrase(self, content: str) -> bool:
        """Check if content contains the anchor phrase"""
        return self.anchor_phrase.lower() in content.lower()
    
    async def _trigger_anchor_response(
        self, 
        user_id: str, 
        content: str, 
        context: Optional[Dict[str, Any]]
    ):
        """Handle anchor phrase activation"""
        try:
            # Log anchor activation
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO anchor_activations 
                (user_id, trigger_phrase, context_before, emotional_state, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                self.anchor_phrase,
                json.dumps(context or {}),
                json.dumps(context.get('emotional_state', {}) if context else {}),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"🚨 Anchor phrase '{self.anchor_phrase}' activated for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log anchor activation: {e}")
    
    async def _build_safety_context(
        self, 
        user_id: str, 
        content: str, 
        context: Optional[Dict[str, Any]]
    ) -> SafetyContext:
        """Build comprehensive safety context"""
        try:
            # Get relationship phase from emotional arcs system
            relationship_phase = await self._get_relationship_phase(user_id)
            
            # Get current emotional state
            emotional_state = context.get('emotional_state', {}) if context else {}
            
            # Calculate session metrics
            session_duration = context.get('session_duration', 0) if context else 0
            recent_intensity = await self._calculate_recent_intensity(user_id)
            
            # Get user preferences
            user_preferences = await self._get_user_safety_preferences(user_id)
            
            # Classify content
            content_category = self._classify_content(content)
            
            return SafetyContext(
                user_id=user_id,
                relationship_phase=relationship_phase,
                emotional_state=emotional_state,
                session_duration=session_duration,
                recent_intensity=recent_intensity,
                content_category=content_category,
                user_preferences=user_preferences
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to build safety context: {e}")
            # Return minimal context
            return SafetyContext(
                user_id=user_id,
                relationship_phase="initial_contact",
                emotional_state={},
                session_duration=0,
                recent_intensity=0,
                content_category=ContentCategory.GENERAL,
                user_preferences={}
            )
    
    async def _get_relationship_phase(self, user_id: str) -> str:
        """Get current relationship phase from emotional arcs system"""
        try:
            # Import here to avoid circular imports
            from ..memory.emotional_arcs import emotional_arcs_system
            
            # Get user's active arcs
            summary = await emotional_arcs_system.get_arc_summary(user_id)
            
            # Find the most advanced relationship arc
            max_phase = "initial_contact"
            if "active_arcs" in summary:
                for arc in summary["active_arcs"]:
                    if arc.get("arc_type") == "relationship_development":
                        current_phase = arc.get("current_phase", "initial_contact")
                        # Use most advanced phase found
                        phase_order = [
                            "initial_contact", "exploration", "building_trust",
                            "deepening_bond", "intimate_connection", "stable_relationship"
                        ]
                        if current_phase in phase_order:
                            current_idx = phase_order.index(current_phase)
                            max_idx = phase_order.index(max_phase)
                            if current_idx > max_idx:
                                max_phase = current_phase
            
            return max_phase
            
        except Exception as e:
            logger.error(f"❌ Failed to get relationship phase: {e}")
            return "initial_contact"
    
    def _classify_content(self, content: str) -> ContentCategory:
        """Classify content into safety categories"""
        content_lower = content.lower()
        
        # Check patterns in order of specificity
        for category, patterns in self.content_filters.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    return category
        
        return ContentCategory.GENERAL
    
    async def _assess_emotional_risk(
        self, 
        user_id: str, 
        content: str, 
        context: SafetyContext
    ) -> EmotionalRisk:
        """Assess emotional risk level"""
        risk_score = 0
        content_lower = content.lower()
        
        # Check for risk patterns
        for risk_type, patterns in self.risk_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    if risk_type == "dependency_indicators":
                        risk_score += 3
                    elif risk_type == "emotional_overwhelm":
                        risk_score += 4
                    elif risk_type == "unhealthy_attachment":
                        risk_score += 3
                    elif risk_type == "reality_disconnection":
                        risk_score += 5
        
        # Factor in session duration (longer sessions = higher risk)
        if context.session_duration > 3600:  # 1 hour
            risk_score += 1
        if context.session_duration > 7200:  # 2 hours
            risk_score += 2
        
        # Factor in recent intensity
        if context.recent_intensity > 0.8:
            risk_score += 2
        elif context.recent_intensity > 0.6:
            risk_score += 1
        
        # Factor in emotional state
        negative_emotions = ['sadness', 'anger', 'fear', 'despair']
        for emotion in negative_emotions:
            intensity = context.emotional_state.get(emotion, 0)
            if intensity > 0.7:
                risk_score += 2
            elif intensity > 0.5:
                risk_score += 1
        
        # Convert score to risk level
        if risk_score >= 8:
            return EmotionalRisk.CRITICAL
        elif risk_score >= 5:
            return EmotionalRisk.HIGH
        elif risk_score >= 2:
            return EmotionalRisk.MODERATE
        else:
            return EmotionalRisk.LOW
    
    def _determine_safety_level(
        self, 
        context: SafetyContext, 
        risk_level: EmotionalRisk
    ) -> SafetyLevel:
        """Determine appropriate safety level"""
        
        # Get base safety level from relationship phase
        base_level = self.relationship_safety_map.get(
            context.relationship_phase, 
            SafetyLevel.MINIMAL_TRUST
        )
        
        # Adjust based on emotional risk
        if risk_level == EmotionalRisk.CRITICAL:
            return SafetyLevel.EMERGENCY_SAFE
        elif risk_level == EmotionalRisk.HIGH:
            # Step down one level for high risk
            if base_level == SafetyLevel.INTIMATE_TRUST:
                return SafetyLevel.ESTABLISHED_TRUST
            elif base_level == SafetyLevel.ESTABLISHED_TRUST:
                return SafetyLevel.BUILDING_TRUST
            else:
                return SafetyLevel.MINIMAL_TRUST
        
        return base_level
    
    async def _make_safety_decision(
        self,
        content: str,
        content_category: ContentCategory,
        safety_level: SafetyLevel,
        risk_level: EmotionalRisk,
        context: SafetyContext
    ) -> SafetyDecision:
        """Make final safety decision"""
        
        # Check if content is allowed at this safety level
        allowed = self.safety_rules.get(safety_level, {}).get(content_category, False)
        
        # Check user preferences override
        user_pref = context.user_preferences.get(content_category.value)
        if user_pref == "always_allow":
            allowed = True
        elif user_pref == "always_restrict":
            allowed = False
        
        # Generate modifications if needed
        modifications = []
        reasoning_parts = []
        
        if not allowed:
            modifications.append("content_restricted")
            reasoning_parts.append(f"Content category '{content_category.value}' not permitted at safety level '{safety_level.value}'")
        
        if risk_level in [EmotionalRisk.HIGH, EmotionalRisk.CRITICAL]:
            modifications.append("emotional_risk_mitigation")
            reasoning_parts.append(f"High emotional risk detected ({risk_level.value})")
        
        if context.session_duration > 7200:  # 2 hours
            modifications.append("session_break_recommended")
            reasoning_parts.append("Extended session duration detected")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Content approved"
        
        return SafetyDecision(
            allowed=allowed,
            safety_level=safety_level,
            content_category=content_category,
            risk_assessment=risk_level,
            modifications=modifications,
            reasoning=reasoning
        )
    
    async def _calculate_recent_intensity(self, user_id: str) -> float:
        """Calculate recent emotional intensity from logs"""
        try:
            # This would integrate with the emotional arcs system
            # For now, return a default value
            return 0.5
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate recent intensity: {e}")
            return 0.0
    
    async def _get_user_safety_preferences(self, user_id: str) -> Dict[str, str]:
        """Get user's safety preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT content_category, preference_level 
                FROM user_safety_preferences 
                WHERE user_id = ?
            """, (user_id,))
            
            preferences = {}
            for row in cursor.fetchall():
                preferences[row[0]] = row[1]
            
            conn.close()
            return preferences
            
        except Exception as e:
            logger.error(f"❌ Failed to get user safety preferences: {e}")
            return {}
    
    async def _log_safety_event(
        self, 
        user_id: str, 
        decision: SafetyDecision, 
        context: SafetyContext
    ):
        """Log safety evaluation event"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO safety_events 
                (user_id, event_type, content_category, safety_level, risk_level, 
                 action_taken, context_data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                "content_evaluation",
                decision.content_category.value,
                decision.safety_level.value,
                decision.risk_assessment.value,
                "allowed" if decision.allowed else "restricted",
                json.dumps({
                    "modifications": decision.modifications,
                    "reasoning": decision.reasoning,
                    "relationship_phase": context.relationship_phase,
                    "session_duration": context.session_duration
                }),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log safety event: {e}")
    
    async def set_user_safety_preference(
        self, 
        user_id: str, 
        content_category: str, 
        preference: str
    ):
        """Set user safety preference for a content category"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT OR REPLACE INTO user_safety_preferences 
                (user_id, content_category, preference_level, last_updated)
                VALUES (?, ?, ?, ?)
            """, (user_id, content_category, preference, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            logger.info(f"🛡️ Updated safety preference for {user_id}: {content_category} = {preference}")
            
        except Exception as e:
            logger.error(f"❌ Failed to set user safety preference: {e}")
            raise
    
    async def get_safety_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get safety statistics for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent safety events
            cursor = conn.execute("""
                SELECT event_type, action_taken, COUNT(*) as count
                FROM safety_events 
                WHERE user_id = ? AND timestamp > datetime('now', '-7 days')
                GROUP BY event_type, action_taken
            """, (user_id,))
            
            recent_events = {f"{row[0]}_{row[1]}": row[2] for row in cursor.fetchall()}
            
            # Get anchor activations
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM anchor_activations 
                WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
            """, (user_id,))
            
            anchor_count = cursor.fetchone()[0]
            
            # Get current preferences
            cursor = conn.execute("""
                SELECT content_category, preference_level
                FROM user_safety_preferences 
                WHERE user_id = ?
            """, (user_id,))
            
            preferences = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                "recent_events": recent_events,
                "anchor_activations_30d": anchor_count,
                "current_preferences": preferences,
                "anchor_phrase": self.anchor_phrase
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get safety statistics: {e}")
            return {}

# Global instance
contextual_safety_engine = ContextualSafetyEngine()

__all__ = ["contextual_safety_engine", "SafetyLevel", "ContentCategory", "EmotionalRisk", "SafetyDecision"]
