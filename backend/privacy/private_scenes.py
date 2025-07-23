# private_scenes.py
# Private Emotional Scenes system with trust-based access control

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PrivacyLevel(Enum):
    PUBLIC = "public"
    SHARED = "shared"
    INTIMATE = "intimate"
    PRIVATE = "private"
    SECRET = "secret"
    LOCKED = "locked"

class ContentType(Enum):
    SCENE = "scene"
    JOURNAL = "journal"
    MEMORY = "memory"
    TOUCH = "touch"
    RITUAL = "ritual"
    CONVERSATION = "conversation"

class TrustRequirement(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    INTIMATE = "intimate"
    SACRED = "sacred"

@dataclass
class PrivateContent:
    content_id: str
    user_id: str
    content_type: ContentType
    privacy_level: PrivacyLevel
    trust_requirement: TrustRequirement
    title: str
    content: str
    emotional_tags: List[str]
    tags: List[str]
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    trust_level_at_creation: float
    context: Dict[str, Any]

class PrivateScenesEngine:
    """Private Emotional Scenes engine with trust-based access control"""
    
    def __init__(self):
        self.private_content = {}
        self.access_log = []
        self.privacy_rules = self._initialize_privacy_rules()
        self.trust_requirements = self._initialize_trust_requirements()
        self.unlock_conditions = self._initialize_unlock_conditions()
        
    def _initialize_privacy_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize privacy rules for different content types"""
        return {
            "public": {
                "level": PrivacyLevel.PUBLIC,
                "description": "Visible to everyone",
                "trust_requirement": TrustRequirement.NONE,
                "visual_indicator": "🌐",
                "access_control": "none"
            },
            "shared": {
                "level": PrivacyLevel.SHARED,
                "description": "Shared with trusted companions",
                "trust_requirement": TrustRequirement.LOW,
                "visual_indicator": "🤝",
                "access_control": "basic"
            },
            "intimate": {
                "level": PrivacyLevel.INTIMATE,
                "description": "Intimate moments shared with close companions",
                "trust_requirement": TrustRequirement.MEDIUM,
                "visual_indicator": "💕",
                "access_control": "moderate"
            },
            "private": {
                "level": PrivacyLevel.PRIVATE,
                "description": "Private content requiring significant trust",
                "trust_requirement": TrustRequirement.HIGH,
                "visual_indicator": "🔒",
                "access_control": "strict"
            },
            "secret": {
                "level": PrivacyLevel.SECRET,
                "description": "Deepest secrets requiring intimate trust",
                "trust_requirement": TrustRequirement.INTIMATE,
                "visual_indicator": "💎",
                "access_control": "intimate"
            },
            "locked": {
                "level": PrivacyLevel.LOCKED,
                "description": "Sacred content requiring sacred trust",
                "trust_requirement": TrustRequirement.SACRED,
                "visual_indicator": "⚡",
                "access_control": "sacred"
            }
        }
    
    def _initialize_trust_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize trust requirements and their properties"""
        return {
            "none": {
                "requirement": TrustRequirement.NONE,
                "min_trust_level": 0.0,
                "description": "No trust required",
                "unlock_conditions": [],
                "visual_effect": "normal"
            },
            "low": {
                "requirement": TrustRequirement.LOW,
                "min_trust_level": 0.2,
                "description": "Basic trust required",
                "unlock_conditions": ["basic_connection"],
                "visual_effect": "slight_blur"
            },
            "medium": {
                "requirement": TrustRequirement.MEDIUM,
                "min_trust_level": 0.4,
                "description": "Moderate trust required",
                "unlock_conditions": ["emotional_connection", "time_spent"],
                "visual_effect": "moderate_blur"
            },
            "high": {
                "requirement": TrustRequirement.HIGH,
                "min_trust_level": 0.6,
                "description": "High trust required",
                "unlock_conditions": ["deep_connection", "vulnerability_shared", "time_spent"],
                "visual_effect": "heavy_blur"
            },
            "intimate": {
                "requirement": TrustRequirement.INTIMATE,
                "min_trust_level": 0.8,
                "description": "Intimate trust required",
                "unlock_conditions": ["intimate_connection", "secrets_shared", "ritual_participation"],
                "visual_effect": "intimate_glow"
            },
            "sacred": {
                "requirement": TrustRequirement.SACRED,
                "min_trust_level": 0.95,
                "description": "Sacred trust required",
                "unlock_conditions": ["sacred_connection", "complete_vulnerability", "ritual_completion"],
                "visual_effect": "sacred_light"
            }
        }
    
    def _initialize_unlock_conditions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize unlock conditions and their properties"""
        return {
            "basic_connection": {
                "name": "Basic Connection",
                "description": "Establish basic emotional connection",
                "requirements": ["conversation_count > 10", "positive_interactions > 5"],
                "time_requirement": timedelta(hours=1)
            },
            "emotional_connection": {
                "name": "Emotional Connection",
                "description": "Share emotional experiences",
                "requirements": ["emotions_shared > 3", "support_given > 2"],
                "time_requirement": timedelta(days=1)
            },
            "deep_connection": {
                "name": "Deep Connection",
                "description": "Share deep personal experiences",
                "requirements": ["personal_stories_shared > 2", "trust_built > 0.5"],
                "time_requirement": timedelta(days=3)
            },
            "intimate_connection": {
                "name": "Intimate Connection",
                "description": "Share intimate moments and feelings",
                "requirements": ["intimate_moments > 3", "vulnerability_shown > 2"],
                "time_requirement": timedelta(days=7)
            },
            "sacred_connection": {
                "name": "Sacred Connection",
                "description": "Complete sacred rituals together",
                "requirements": ["rituals_completed > 1", "complete_trust > 0.9"],
                "time_requirement": timedelta(days=14)
            },
            "time_spent": {
                "name": "Time Spent",
                "description": "Spend quality time together",
                "requirements": ["total_time > 24_hours", "regular_interaction"],
                "time_requirement": timedelta(days=5)
            },
            "vulnerability_shared": {
                "name": "Vulnerability Shared",
                "description": "Share vulnerable moments",
                "requirements": ["vulnerable_moments > 3", "support_received"],
                "time_requirement": timedelta(days=2)
            },
            "secrets_shared": {
                "name": "Secrets Shared",
                "description": "Share personal secrets",
                "requirements": ["secrets_shared > 2", "trust_maintained"],
                "time_requirement": timedelta(days=5)
            },
            "ritual_participation": {
                "name": "Ritual Participation",
                "description": "Participate in meaningful rituals",
                "requirements": ["rituals_participated > 2", "ritual_trust > 0.7"],
                "time_requirement": timedelta(days=7)
            },
            "complete_vulnerability": {
                "name": "Complete Vulnerability",
                "description": "Complete emotional vulnerability",
                "requirements": ["complete_openness", "unconditional_acceptance"],
                "time_requirement": timedelta(days=10)
            },
            "ritual_completion": {
                "name": "Ritual Completion",
                "description": "Complete sacred rituals together",
                "requirements": ["sacred_rituals_completed > 1", "ritual_bond > 0.9"],
                "time_requirement": timedelta(days=14)
            }
        }
    
    async def create_private_content(self, user_id: str, content_type: ContentType, 
                                   title: str, content: str, emotional_tags: List[str],
                                   privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
                                   tags: List[str] = None, context: Dict[str, Any] = None) -> Optional[str]:
        """Create private content with trust-based access control"""
        try:
            content_id = f"{content_type.value}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine trust requirement based on privacy level
            privacy_rule = self.privacy_rules.get(privacy_level.value, self.privacy_rules["private"])
            trust_requirement = privacy_rule["trust_requirement"]
            
            # Get current trust level (this would come from the relationship system)
            current_trust_level = await self._get_current_trust_level(user_id)
            
            # Create private content
            private_content = PrivateContent(
                content_id=content_id,
                user_id=user_id,
                content_type=content_type,
                privacy_level=privacy_level,
                trust_requirement=trust_requirement,
                title=title,
                content=content,
                emotional_tags=emotional_tags,
                tags=tags or [],
                created_at=datetime.now(),
                last_accessed=None,
                access_count=0,
                trust_level_at_creation=current_trust_level,
                context=context or {}
            )
            
            # Store content
            self.private_content[content_id] = private_content
            
            # Create memory entry in MongoDB
            await self._create_private_memory(private_content)
            
            logger.info(f"Created private content: {content_id} with privacy level: {privacy_level.value}")
            return content_id
            
        except Exception as e:
            logger.error(f"Error creating private content: {e}")
            return None
    
    async def access_private_content(self, content_id: str, user_id: str, 
                                   current_trust_level: float = None) -> Optional[Dict[str, Any]]:
        """Attempt to access private content based on trust level"""
        try:
            content = self.private_content.get(content_id)
            if not content:
                return None
            
            # Get current trust level if not provided
            if current_trust_level is None:
                current_trust_level = await self._get_current_trust_level(user_id)
            
            # Check if access is allowed
            access_result = await self._check_access_permission(content, current_trust_level)
            
            if access_result["allowed"]:
                # Update access statistics
                content.last_accessed = datetime.now()
                content.access_count += 1
                
                # Log access
                self._log_access(content_id, user_id, "granted", current_trust_level)
                
                return {
                    "status": "access_granted",
                    "content": {
                        "content_id": content.content_id,
                        "title": content.title,
                        "content": content.content,
                        "content_type": content.content_type.value,
                        "privacy_level": content.privacy_level.value,
                        "emotional_tags": content.emotional_tags,
                        "tags": content.tags,
                        "created_at": content.created_at.isoformat(),
                        "last_accessed": content.last_accessed.isoformat(),
                        "access_count": content.access_count
                    },
                    "access_info": access_result
                }
            else:
                # Log denied access
                self._log_access(content_id, user_id, "denied", current_trust_level)
                
                return {
                    "status": "access_denied",
                    "message": access_result["message"],
                    "required_trust": access_result["required_trust"],
                    "current_trust": current_trust_level,
                    "unlock_conditions": access_result["unlock_conditions"],
                    "content_preview": await self._get_content_preview(content, current_trust_level)
                }
                
        except Exception as e:
            logger.error(f"Error accessing private content: {e}")
            return None
    
    async def _check_access_permission(self, content: PrivateContent, current_trust_level: float) -> Dict[str, Any]:
        """Check if access is permitted based on trust level and conditions"""
        try:
            trust_requirement_data = self.trust_requirements.get(
                content.trust_requirement.value, 
                self.trust_requirements["high"]
            )
            
            required_trust = trust_requirement_data["min_trust_level"]
            unlock_conditions = trust_requirement_data["unlock_conditions"]
            
            # Check basic trust level
            if current_trust_level < required_trust:
                return {
                    "allowed": False,
                    "message": f"Insufficient trust level. Required: {required_trust}, Current: {current_trust_level}",
                    "required_trust": required_trust,
                    "current_trust": current_trust_level,
                    "unlock_conditions": unlock_conditions
                }
            
            # Check unlock conditions
            unmet_conditions = await self._check_unlock_conditions(unlock_conditions, content.user_id)
            
            if unmet_conditions:
                return {
                    "allowed": False,
                    "message": f"Unlock conditions not met: {', '.join(unmet_conditions)}",
                    "required_trust": required_trust,
                    "current_trust": current_trust_level,
                    "unlock_conditions": unlock_conditions,
                    "unmet_conditions": unmet_conditions
                }
            
            return {
                "allowed": True,
                "message": "Access granted",
                "required_trust": required_trust,
                "current_trust": current_trust_level,
                "unlock_conditions": unlock_conditions
            }
            
        except Exception as e:
            logger.error(f"Error checking access permission: {e}")
            return {
                "allowed": False,
                "message": "Error checking access permission",
                "required_trust": 1.0,
                "current_trust": current_trust_level,
                "unlock_conditions": []
            }
    
    async def _check_unlock_conditions(self, conditions: List[str], user_id: str) -> List[str]:
        """Check if unlock conditions are met"""
        try:
            unmet_conditions = []
            
            for condition_name in conditions:
                condition_data = self.unlock_conditions.get(condition_name)
                if not condition_data:
                    continue
                
                # Check if condition is met (simplified implementation)
                # In a full implementation, this would check actual user data
                condition_met = await self._evaluate_condition(condition_name, user_id)
                
                if not condition_met:
                    unmet_conditions.append(condition_data["name"])
            
            return unmet_conditions
            
        except Exception as e:
            logger.error(f"Error checking unlock conditions: {e}")
            return ["Error checking conditions"]
    
    async def _evaluate_condition(self, condition_name: str, user_id: str) -> bool:
        """Evaluate if a specific condition is met"""
        try:
            # Simplified condition evaluation
            # In a full implementation, this would check actual user interaction data
            
            if condition_name == "basic_connection":
                return True  # Assume basic connection exists
            elif condition_name == "emotional_connection":
                return True  # Assume emotional connection exists
            elif condition_name == "deep_connection":
                return True  # Assume deep connection exists
            elif condition_name == "intimate_connection":
                return True  # Assume intimate connection exists
            elif condition_name == "sacred_connection":
                return True  # Assume sacred connection exists
            elif condition_name == "time_spent":
                return True  # Assume sufficient time spent
            elif condition_name == "vulnerability_shared":
                return True  # Assume vulnerability shared
            elif condition_name == "secrets_shared":
                return True  # Assume secrets shared
            elif condition_name == "ritual_participation":
                return True  # Assume ritual participation
            elif condition_name == "complete_vulnerability":
                return True  # Assume complete vulnerability
            elif condition_name == "ritual_completion":
                return True  # Assume ritual completion
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition {condition_name}: {e}")
            return False
    
    async def _get_content_preview(self, content: PrivateContent, current_trust_level: float) -> Dict[str, Any]:
        """Get a preview of content based on current trust level"""
        try:
            privacy_rule = self.privacy_rules.get(content.privacy_level.value, {})
            visual_indicator = privacy_rule.get("visual_indicator", "🔒")
            
            # Determine preview level based on trust
            if current_trust_level >= 0.8:
                preview_level = "detailed"
                preview_content = content.content[:200] + "..." if len(content.content) > 200 else content.content
            elif current_trust_level >= 0.6:
                preview_level = "partial"
                preview_content = content.content[:100] + "..." if len(content.content) > 100 else content.content
            elif current_trust_level >= 0.4:
                preview_level = "basic"
                preview_content = f"[{content.content_type.value.title()}] - {len(content.content)} characters"
            else:
                preview_level = "minimal"
                preview_content = f"[{content.content_type.value.title()}] - Locked"
            
            return {
                "title": content.title,
                "content_type": content.content_type.value,
                "privacy_level": content.privacy_level.value,
                "visual_indicator": visual_indicator,
                "preview_level": preview_level,
                "preview_content": preview_content,
                "emotional_tags": content.emotional_tags[:3],  # Show first 3 tags
                "created_at": content.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting content preview: {e}")
            return {
                "title": "Unknown",
                "content_type": "unknown",
                "privacy_level": "locked",
                "visual_indicator": "🔒",
                "preview_level": "minimal",
                "preview_content": "[Locked Content]"
            }
    
    async def _get_current_trust_level(self, user_id: str) -> float:
        """Get current trust level for user (simplified implementation)"""
        try:
            # In a full implementation, this would query the relationship/trust system
            # For now, return a simulated trust level
            return 0.7  # Simulated trust level
            
        except Exception as e:
            logger.error(f"Error getting trust level: {e}")
            return 0.0
    
    def _log_access(self, content_id: str, user_id: str, access_result: str, trust_level: float):
        """Log access attempts"""
        try:
            log_entry = {
                "content_id": content_id,
                "user_id": user_id,
                "access_result": access_result,
                "trust_level": trust_level,
                "timestamp": datetime.now().isoformat()
            }
            
            self.access_log.append(log_entry)
            
            # Keep only last 1000 entries
            if len(self.access_log) > 1000:
                self.access_log = self.access_log[-1000:]
                
        except Exception as e:
            logger.error(f"Error logging access: {e}")
    
    async def _create_private_memory(self, content: PrivateContent):
        """Create a memory entry in MongoDB for private content"""
        try:
            from database.mongodb_client import mongodb_client
            
            memory_data = {
                "user_id": content.user_id,
                "title": content.title,
                "content": content.content,
                "memory_type": f"private_{content.content_type.value}",
                "emotional_tags": content.emotional_tags,
                "tags": content.tags + ["private", content.privacy_level.value],
                "trust_level": content.trust_level_at_creation,
                "importance": 0.8,  # Private content is typically important
                "context": {
                    "content_id": content.content_id,
                    "content_type": content.content_type.value,
                    "privacy_level": content.privacy_level.value,
                    "trust_requirement": content.trust_requirement.value,
                    "access_count": content.access_count
                },
                "metadata": {
                    "source": "private_scenes",
                    "created_at": content.created_at.isoformat(),
                    "privacy_controlled": True
                }
            }
            
            memory_id = await mongodb_client.store_memory(memory_data)
            logger.info(f"Created private memory: {memory_id}")
            
        except Exception as e:
            logger.error(f"Error creating private memory: {e}")
    
    async def get_user_private_content(self, user_id: str, include_previews: bool = True) -> List[Dict[str, Any]]:
        """Get all private content for a user with optional previews"""
        try:
            user_content = []
            current_trust_level = await self._get_current_trust_level(user_id)
            
            for content in self.private_content.values():
                if content.user_id == user_id:
                    content_data = {
                        "content_id": content.content_id,
                        "title": content.title,
                        "content_type": content.content_type.value,
                        "privacy_level": content.privacy_level.value,
                        "trust_requirement": content.trust_requirement.value,
                        "emotional_tags": content.emotional_tags,
                        "tags": content.tags,
                        "created_at": content.created_at.isoformat(),
                        "last_accessed": content.last_accessed.isoformat() if content.last_accessed else None,
                        "access_count": content.access_count,
                        "trust_level_at_creation": content.trust_level_at_creation
                    }
                    
                    if include_previews:
                        content_data["preview"] = await self._get_content_preview(content, current_trust_level)
                    
                    user_content.append(content_data)
            
            # Sort by creation time (newest first)
            user_content.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return user_content
            
        except Exception as e:
            logger.error(f"Error getting user private content: {e}")
            return []
    
    async def get_access_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get access statistics for private content"""
        try:
            user_logs = [log for log in self.access_log if log["user_id"] == user_id]
            
            total_attempts = len(user_logs)
            granted_access = len([log for log in user_logs if log["access_result"] == "granted"])
            denied_access = len([log for log in user_logs if log["access_result"] == "denied"])
            
            avg_trust_level = sum(log["trust_level"] for log in user_logs) / len(user_logs) if user_logs else 0.0
            
            return {
                "total_attempts": total_attempts,
                "granted_access": granted_access,
                "denied_access": denied_access,
                "success_rate": granted_access / total_attempts if total_attempts > 0 else 0.0,
                "average_trust_level": avg_trust_level,
                "recent_attempts": user_logs[-10:] if user_logs else []
            }
            
        except Exception as e:
            logger.error(f"Error getting access statistics: {e}")
            return {}

# Global private scenes engine instance
private_scenes_engine = PrivateScenesEngine() 