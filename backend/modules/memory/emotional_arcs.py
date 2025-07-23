"""
Emotional Arcs System
Tracks long-term emotional progression and relationship development
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class ArcType(Enum):
    """Types of emotional arcs"""
    RELATIONSHIP_DEVELOPMENT = "relationship_development"
    MOOD_PROGRESSION = "mood_progression"
    TRUST_BUILDING = "trust_building"
    INTIMACY_GROWTH = "intimacy_growth"
    ATTACHMENT_FORMATION = "attachment_formation"
    EMOTIONAL_HEALING = "emotional_healing"
    PERSONAL_GROWTH = "personal_growth"

class EmotionalPhase(Enum):
    """Phases in emotional development"""
    INITIAL_CONTACT = "initial_contact"
    EXPLORATION = "exploration"
    BUILDING_TRUST = "building_trust"
    DEEPENING_BOND = "deepening_bond"
    INTIMATE_CONNECTION = "intimate_connection"
    STABLE_RELATIONSHIP = "stable_relationship"
    CRISIS_RESOLUTION = "crisis_resolution"
    RENEWED_CONNECTION = "renewed_connection"

@dataclass
class EmotionalDataPoint:
    """Individual emotional measurement"""
    timestamp: datetime
    emotion_type: str
    intensity: float  # 0.0 to 1.0
    valence: float    # -1.0 (negative) to 1.0 (positive)
    context: Dict[str, Any]
    trigger_event: Optional[str] = None

@dataclass
class EmotionalArc:
    """Complete emotional arc tracking"""
    id: str
    user_id: str
    arc_type: ArcType
    current_phase: EmotionalPhase
    start_date: datetime
    last_updated: datetime
    data_points: List[EmotionalDataPoint]
    milestones: Dict[str, datetime]
    progression_score: float  # 0.0 to 1.0
    trend_direction: float    # -1.0 (declining) to 1.0 (improving)
    metadata: Dict[str, Any]

class EmotionalArcsSystem:
    """System for tracking long-term emotional development"""
    
    def __init__(self, db_path: str = "data/emotional_arcs.db"):
        self.db_path = db_path
        self.connection = None
        self.active_arcs = {}
        self.phase_transitions = {}
        
    async def initialize(self):
        """Initialize the emotional arcs system"""
        try:
            # Create database connection
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            
            # Load active arcs
            await self._load_active_arcs()
            
            # Initialize phase transition rules
            self._initialize_phase_transitions()
            
            logger.info("✅ Emotional Arcs System initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize emotional arcs: {e}")
            raise e
    
    async def _create_tables(self):
        """Create database tables for emotional arcs"""
        cursor = self.connection.cursor()
        
        # Emotional arcs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotional_arcs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                arc_type TEXT NOT NULL,
                current_phase TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                progression_score REAL NOT NULL,
                trend_direction REAL NOT NULL,
                milestones TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        
        # Emotional data points table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotional_data_points (
                id TEXT PRIMARY KEY,
                arc_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                emotion_type TEXT NOT NULL,
                intensity REAL NOT NULL,
                valence REAL NOT NULL,
                context TEXT NOT NULL,
                trigger_event TEXT,
                FOREIGN KEY (arc_id) REFERENCES emotional_arcs (id)
            )
        """)
        
        # Phase transitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phase_transitions (
                id TEXT PRIMARY KEY,
                arc_id TEXT NOT NULL,
                from_phase TEXT NOT NULL,
                to_phase TEXT NOT NULL,
                transition_date TIMESTAMP NOT NULL,
                trigger_reason TEXT,
                confidence_score REAL NOT NULL,
                FOREIGN KEY (arc_id) REFERENCES emotional_arcs (id)
            )
        """)
        
        # Arc milestones table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arc_milestones (
                id TEXT PRIMARY KEY,
                arc_id TEXT NOT NULL,
                milestone_type TEXT NOT NULL,
                achieved_date TIMESTAMP NOT NULL,
                description TEXT,
                significance_score REAL NOT NULL,
                FOREIGN KEY (arc_id) REFERENCES emotional_arcs (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arc_user ON emotional_arcs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arc_type ON emotional_arcs(arc_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_arc ON emotional_data_points(arc_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_timestamp ON emotional_data_points(timestamp)")
        
        self.connection.commit()
        logger.info("📊 Emotional arcs database tables created")
    
    async def _load_active_arcs(self):
        """Load active emotional arcs into memory"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM emotional_arcs 
            WHERE last_updated > datetime('now', '-30 days')
        """)
        
        for row in cursor.fetchall():
            arc_id = row['id']
            
            # Load data points for this arc
            cursor.execute("""
                SELECT * FROM emotional_data_points 
                WHERE arc_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            """, (arc_id,))
            
            data_points = []
            for dp_row in cursor.fetchall():
                data_point = EmotionalDataPoint(
                    timestamp=datetime.fromisoformat(dp_row['timestamp']),
                    emotion_type=dp_row['emotion_type'],
                    intensity=dp_row['intensity'],
                    valence=dp_row['valence'],
                    context=json.loads(dp_row['context']),
                    trigger_event=dp_row['trigger_event']
                )
                data_points.append(data_point)
            
            # Create arc object
            arc = EmotionalArc(
                id=row['id'],
                user_id=row['user_id'],
                arc_type=ArcType(row['arc_type']),
                current_phase=EmotionalPhase(row['current_phase']),
                start_date=datetime.fromisoformat(row['start_date']),
                last_updated=datetime.fromisoformat(row['last_updated']),
                data_points=data_points,
                milestones=json.loads(row['milestones']),
                progression_score=row['progression_score'],
                trend_direction=row['trend_direction'],
                metadata=json.loads(row['metadata'])
            )
            
            self.active_arcs[arc_id] = arc
        
        logger.info(f"📈 Loaded {len(self.active_arcs)} active emotional arcs")
    
    def _initialize_phase_transitions(self):
        """Initialize rules for phase transitions"""
        self.phase_transitions = {
            EmotionalPhase.INITIAL_CONTACT: {
                "next_phases": [EmotionalPhase.EXPLORATION],
                "requirements": {"min_interactions": 3, "min_positive_valence": 0.2}
            },
            EmotionalPhase.EXPLORATION: {
                "next_phases": [EmotionalPhase.BUILDING_TRUST, EmotionalPhase.INITIAL_CONTACT],
                "requirements": {"min_trust_score": 0.4, "consistency_days": 7}
            },
            EmotionalPhase.BUILDING_TRUST: {
                "next_phases": [EmotionalPhase.DEEPENING_BOND, EmotionalPhase.EXPLORATION],
                "requirements": {"min_trust_score": 0.7, "emotional_consistency": 0.6}
            },
            EmotionalPhase.DEEPENING_BOND: {
                "next_phases": [EmotionalPhase.INTIMATE_CONNECTION, EmotionalPhase.BUILDING_TRUST],
                "requirements": {"min_intimacy_score": 0.6, "vulnerability_shared": True}
            },
            EmotionalPhase.INTIMATE_CONNECTION: {
                "next_phases": [EmotionalPhase.STABLE_RELATIONSHIP, EmotionalPhase.CRISIS_RESOLUTION],
                "requirements": {"min_attachment_score": 0.8, "mutual_support": True}
            },
            EmotionalPhase.STABLE_RELATIONSHIP: {
                "next_phases": [EmotionalPhase.CRISIS_RESOLUTION, EmotionalPhase.RENEWED_CONNECTION],
                "requirements": {"stability_duration": timedelta(days=30)}
            }
        }
    
    async def start_new_arc(self, 
                           user_id: str, 
                           arc_type: ArcType,
                           initial_context: Dict[str, Any] = None) -> str:
        """Start tracking a new emotional arc"""
        try:
            arc_id = f"{user_id}_{arc_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            now = datetime.now()
            
            arc = EmotionalArc(
                id=arc_id,
                user_id=user_id,
                arc_type=arc_type,
                current_phase=EmotionalPhase.INITIAL_CONTACT,
                start_date=now,
                last_updated=now,
                data_points=[],
                milestones={},
                progression_score=0.0,
                trend_direction=0.0,
                metadata=initial_context or {}
            )
            
            # Store in database
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO emotional_arcs 
                (id, user_id, arc_type, current_phase, start_date, last_updated, 
                 progression_score, trend_direction, milestones, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                arc.id, arc.user_id, arc.arc_type.value, arc.current_phase.value,
                arc.start_date, arc.last_updated, arc.progression_score,
                arc.trend_direction, json.dumps(arc.milestones), 
                json.dumps(arc.metadata)
            ))
            
            self.connection.commit()
            
            # Add to active arcs
            self.active_arcs[arc_id] = arc
            
            logger.info(f"🌱 Started new emotional arc: {arc_id} ({arc_type.value})")
            return arc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start new arc: {e}")
            raise e
    
    async def record_emotional_data(self, 
                                   user_id: str,
                                   emotion_type: str,
                                   intensity: float,
                                   valence: float,
                                   context: Dict[str, Any],
                                   trigger_event: Optional[str] = None):
        """Record new emotional data point"""
        try:
            # Find active arcs for this user
            user_arcs = [arc for arc in self.active_arcs.values() if arc.user_id == user_id]
            
            if not user_arcs:
                # Start a default relationship development arc
                await self.start_new_arc(user_id, ArcType.RELATIONSHIP_DEVELOPMENT)
                user_arcs = [arc for arc in self.active_arcs.values() if arc.user_id == user_id]
            
            now = datetime.now()
            data_point = EmotionalDataPoint(
                timestamp=now,
                emotion_type=emotion_type,
                intensity=intensity,
                valence=valence,
                context=context,
                trigger_event=trigger_event
            )
            
            # Record data point for all relevant arcs
            for arc in user_arcs:
                # Add to arc data points
                arc.data_points.append(data_point)
                arc.last_updated = now
                
                # Keep only recent data points in memory
                if len(arc.data_points) > 100:
                    arc.data_points = arc.data_points[-100:]
                
                # Store in database
                cursor = self.connection.cursor()
                dp_id = f"{arc.id}_{now.strftime('%Y%m%d_%H%M%S')}"
                cursor.execute("""
                    INSERT INTO emotional_data_points 
                    (id, arc_id, timestamp, emotion_type, intensity, valence, context, trigger_event)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dp_id, arc.id, data_point.timestamp, data_point.emotion_type,
                    data_point.intensity, data_point.valence, 
                    json.dumps(data_point.context), data_point.trigger_event
                ))
                
                # Update arc progression
                await self._update_arc_progression(arc)
                
                # Check for phase transitions
                await self._check_phase_transition(arc)
            
            self.connection.commit()
            logger.info(f"📊 Recorded emotional data: {emotion_type} ({intensity:.2f}, {valence:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Failed to record emotional data: {e}")
            raise e
    
    async def _update_arc_progression(self, arc: EmotionalArc):
        """Update arc progression score and trend"""
        if len(arc.data_points) < 2:
            return
        
        # Calculate progression score based on recent data
        recent_points = arc.data_points[-10:]  # Last 10 data points
        
        # Progression factors
        positive_trend = sum(1 for dp in recent_points if dp.valence > 0) / len(recent_points)
        intensity_growth = self._calculate_intensity_trend(recent_points)
        consistency_score = self._calculate_emotional_consistency(recent_points)
        
        # Update progression score
        arc.progression_score = min(1.0, (positive_trend * 0.4 + 
                                         intensity_growth * 0.3 + 
                                         consistency_score * 0.3))
        
        # Update trend direction
        if len(recent_points) >= 5:
            early_avg = np.mean([dp.valence for dp in recent_points[:3]])
            late_avg = np.mean([dp.valence for dp in recent_points[-3:]])
            arc.trend_direction = max(-1.0, min(1.0, (late_avg - early_avg) * 2))
        
        # Update in database
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE emotional_arcs 
            SET progression_score = ?, trend_direction = ?, last_updated = ?
            WHERE id = ?
        """, (arc.progression_score, arc.trend_direction, arc.last_updated, arc.id))
    
    def _calculate_intensity_trend(self, data_points: List[EmotionalDataPoint]) -> float:
        """Calculate if emotional intensity is growing over time"""
        if len(data_points) < 3:
            return 0.0
        
        intensities = [dp.intensity for dp in data_points]
        # Simple linear trend calculation
        x = list(range(len(intensities)))
        slope = np.polyfit(x, intensities, 1)[0]
        return max(0.0, min(1.0, slope * 5))  # Normalize to 0-1
    
    def _calculate_emotional_consistency(self, data_points: List[EmotionalDataPoint]) -> float:
        """Calculate emotional consistency/stability"""
        if len(data_points) < 3:
            return 0.0
        
        valences = [dp.valence for dp in data_points]
        std_dev = np.std(valences)
        # Lower standard deviation = higher consistency
        consistency = max(0.0, 1.0 - std_dev)
        return consistency
    
    async def _check_phase_transition(self, arc: EmotionalArc):
        """Check if arc should transition to next phase"""
        current_phase = arc.current_phase
        
        if current_phase not in self.phase_transitions:
            return
        
        transition_rules = self.phase_transitions[current_phase]
        
        # Check if requirements are met for transition
        if await self._evaluate_transition_requirements(arc, transition_rules["requirements"]):
            # Determine next phase
            next_phases = transition_rules["next_phases"]
            next_phase = self._determine_next_phase(arc, next_phases)
            
            if next_phase != current_phase:
                await self._transition_to_phase(arc, next_phase)
    
    async def _evaluate_transition_requirements(self, arc: EmotionalArc, requirements: Dict) -> bool:
        """Evaluate if transition requirements are met"""
        # This would implement specific requirement checking
        # For now, use simple progression-based logic
        return arc.progression_score > 0.6 and arc.trend_direction > 0.2
    
    def _determine_next_phase(self, arc: EmotionalArc, possible_phases: List[EmotionalPhase]) -> EmotionalPhase:
        """Determine which phase to transition to next"""
        # Use progression score and trend to determine direction
        if arc.trend_direction > 0.5 and arc.progression_score > 0.7:
            # Positive progression - move forward
            return possible_phases[0] if possible_phases else arc.current_phase
        elif arc.trend_direction < -0.3:
            # Negative trend - potentially move backward
            return possible_phases[-1] if len(possible_phases) > 1 else arc.current_phase
        else:
            # Stay in current phase
            return arc.current_phase
    
    async def _transition_to_phase(self, arc: EmotionalArc, new_phase: EmotionalPhase):
        """Transition arc to new phase"""
        old_phase = arc.current_phase
        arc.current_phase = new_phase
        arc.last_updated = datetime.now()
        
        # Record transition
        cursor = self.connection.cursor()
        transition_id = f"{arc.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute("""
            INSERT INTO phase_transitions 
            (id, arc_id, from_phase, to_phase, transition_date, trigger_reason, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transition_id, arc.id, old_phase.value, new_phase.value,
            arc.last_updated, "automatic_progression", arc.progression_score
        ))
        
        # Update arc in database
        cursor.execute("""
            UPDATE emotional_arcs 
            SET current_phase = ?, last_updated = ?
            WHERE id = ?
        """, (new_phase.value, arc.last_updated, arc.id))
        
        self.connection.commit()
        
        logger.info(f"🔄 Arc {arc.id} transitioned: {old_phase.value} → {new_phase.value}")
    
    async def get_arc_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's emotional arcs"""
        try:
            user_arcs = [arc for arc in self.active_arcs.values() if arc.user_id == user_id]
            
            if not user_arcs:
                return {"message": "No active emotional arcs found"}
            
            summary = {
                "total_arcs": len(user_arcs),
                "arcs": []
            }
            
            for arc in user_arcs:
                arc_summary = {
                    "id": arc.id,
                    "type": arc.arc_type.value,
                    "current_phase": arc.current_phase.value,
                    "progression_score": arc.progression_score,
                    "trend_direction": arc.trend_direction,
                    "days_active": (datetime.now() - arc.start_date).days,
                    "total_data_points": len(arc.data_points),
                    "recent_emotions": [dp.emotion_type for dp in arc.data_points[-5:]]
                }
                summary["arcs"].append(arc_summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get arc summary: {e}")
            return {"error": str(e)}

# Global instance
emotional_arcs_system = EmotionalArcsSystem()
