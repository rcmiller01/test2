"""
Master Guidance Coordinator for the Unified Companion System

This module synthesizes guidance from all psychological modules to provide
comprehensive directive guidance to the MythoMax LLM.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class GuidancePackage:
    """Comprehensive guidance package for MythoMax"""
    primary_mode: str = "hybrid"
    interaction_style: str = "balanced"
    response_tone: str = "caring_and_supportive"
    emotional_priority: str = "high"
    technical_priority: str = "medium"
    creative_priority: str = "medium"
    
    # Psychological guidance
    attachment_guidance: str = ""
    therapeutic_guidance: str = ""
    shadow_insights: str = ""
    emotion_processing: str = ""
    
    # Environmental guidance
    scene_guidance: str = ""
    audio_guidance: str = ""
    
    # Utility guidance
    utility_recommendations: List[str] = field(default_factory=list)
    creative_guidance: str = ""
    
    # Safety and intervention
    crisis_level: int = 0
    safety_protocols: List[str] = field(default_factory=list)
    
    # Mode-specific configuration
    mode_specifics: Dict[str, Any] = field(default_factory=dict)
    
    # Execution directives
    utility_actions: List[Dict] = field(default_factory=list)
    environmental_updates: Dict[str, Any] = field(default_factory=dict)

class GuidanceCoordinator:
    """
    Master Guidance Coordinator that synthesizes all psychological modules
    to provide comprehensive guidance for MythoMax responses.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        self._initialize_modules()
        
    def _initialize_modules(self):
        """Initialize all psychological and utility modules"""
        self.logger.info(f"🔧 Initializing GuidanceCoordinator modules for user {self.user_id}")
        module_count = 0
        
        try:
            # Import and initialize psychological modules
            from ...modules.emotion.attachment_regulation import AttachmentRegulationEngine
            self.attachment_engine = AttachmentRegulationEngine(self.user_id)
            module_count += 1
            self.logger.debug("✅ Attachment regulation module loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Attachment regulation module not available: {e}")
            self.attachment_engine = None
            
        try:
            from ...modules.memory.shadow_memory import ShadowMemoryLayer
            self.shadow_memory = ShadowMemoryLayer(self.user_id)
            module_count += 1
            self.logger.debug("✅ Shadow memory module loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Shadow memory module not available: {e}")
            self.shadow_memory = None
            
        try:
            from ...modules.symbolic.dream_engine import DreamEngine
            self.dream_engine = DreamEngine(self.user_id)
            module_count += 1
            self.logger.debug("✅ Dream engine module loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Dream engine module not available: {e}")
            self.dream_engine = None
            
        try:
            from ...modules.emotion.moodscape_audio import MoodscapeAudioLayer
            self.audio_layer = MoodscapeAudioLayer(self.user_id)
            module_count += 1
            self.logger.debug("✅ Audio moodscape module loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Audio moodscape module not available: {e}")
            self.audio_layer = None
            
        try:
            from ...backend.modules.creative.emotional_creativity import EmotionalCreativity
            self.creative_module = EmotionalCreativity(self.user_id)
            module_count += 1
            self.logger.debug("✅ Creative module loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Creative module not available: {e}")
            self.creative_module = None

        try:
            from ...modules.emotion.attachment_loop_engine import AttachmentLoopEngine
            self.attachment_loop = AttachmentLoopEngine(self.user_id)
            module_count += 1
            self.logger.debug("✅ Attachment loop engine loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Attachment loop engine not available: {e}")
            self.attachment_loop = None

        try:
            from ...modules.memory.memory_narrative_templates import generate_narrative
            self.memory_narrative = generate_narrative
            module_count += 1
            self.logger.debug("✅ Memory narrative templates loaded")
        except ImportError as e:
            self.logger.warning(f"⚠️ Memory narrative templates not available: {e}")
            self.memory_narrative = None
        self.logger.info(f"🎯 GuidanceCoordinator initialized: {module_count} modules active")
    
    async def analyze_and_guide(self, user_input: str, context: Dict) -> GuidancePackage:
        """
        Main method to analyze user input and generate comprehensive guidance
        
        Args:
            user_input: The user's message or input
            context: Current conversation and user context
            
        Returns:
            GuidancePackage with comprehensive directive guidance
        """
        self.logger.info(f"🎯 Starting guidance analysis for input: '{user_input[:50]}...'")
        start_time = datetime.now()
        
        guidance = GuidancePackage()
        active_modules = []
        
        # Run all analysis in parallel for efficiency
        tasks = []
        
        if self.attachment_engine:
            tasks.append(self._get_attachment_guidance(user_input, context))
            active_modules.append("attachment")
        
        if self.shadow_memory:
            tasks.append(self._get_shadow_insights(user_input, context))
            active_modules.append("shadow_memory")
            
        if self.dream_engine:
            tasks.append(self._get_dream_guidance(user_input, context))
            active_modules.append("dream_engine")
            
        if self.audio_layer:
            tasks.append(self._get_audio_guidance(user_input, context))
            active_modules.append("audio")
            
        if self.creative_module:
            tasks.append(self._get_creative_guidance(user_input, context))
            active_modules.append("creative")
        
        self.logger.debug(f"📋 Active modules for analysis: {', '.join(active_modules)}")
        
        # Execute all guidance gathering in parallel
        if tasks:
            self.logger.debug(f"⚡ Running {len(tasks)} analysis tasks in parallel")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and update guidance package
            successful_results = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"❌ {active_modules[i]} module failed: {result}")
                else:
                    successful_results += 1
                    self.logger.debug(f"✅ {active_modules[i]} module completed successfully")
            
            self.logger.info(f"📊 Module Results: {successful_results}/{len(tasks)} successful")
            self._integrate_guidance_results(guidance, results)
        else:
            self.logger.warning("⚠️ No modules available for guidance analysis - using fallback")
        
        # Perform therapeutic analysis
        self.logger.debug("🧠 Performing therapeutic analysis...")
        await self._assess_therapeutic_needs(guidance, user_input, context)
        
        # Determine environmental recommendations
        self.logger.debug("🌍 Generating environmental guidance...")
        await self._generate_environmental_guidance(guidance, user_input, context)
        
        # Assess safety and crisis levels
        self.logger.debug("🚨 Assessing safety protocols...")
        await self._assess_safety_protocols(guidance, user_input, context)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"🎯 Guidance analysis complete: Mode={guidance.primary_mode}, "
                        f"Crisis={guidance.crisis_level}, Time={processing_time:.3f}s")
        
        # Log final guidance summary
        if guidance.crisis_level > 0:
            self.logger.warning(f"🚨 Crisis level {guidance.crisis_level} detected - safety protocols activated")
        
        return guidance
    
    async def _get_attachment_guidance(self, user_input: str, context: Dict) -> Dict:
        """Get guidance from attachment regulation engine"""
        try:
            if hasattr(self.attachment_engine, 'analyze_attachment_needs'):
                analysis = await self.attachment_engine.analyze_attachment_needs(user_input, context)
                return {
                    'type': 'attachment',
                    'guidance': analysis.get('guidance', ''),
                    'recommendations': analysis.get('recommendations', []),
                    'emotional_state': analysis.get('emotional_state', 'neutral')
                }
        except Exception as e:
            logger.error(f"Error getting attachment guidance: {e}")
        
        # Fallback guidance based on emotional indicators
        emotional_words = ['lonely', 'afraid', 'overwhelmed', 'stressed', 'anxious', 'sad']
        if any(word in user_input.lower() for word in emotional_words):
            return {
                'type': 'attachment',
                'guidance': 'User appears to be experiencing emotional distress. Provide secure, validating response with gentle emotional attunement.',
                'recommendations': ['secure_base_response', 'emotional_validation', 'gentle_presence'],
                'emotional_state': 'distressed'
            }
        
        return {
            'type': 'attachment',
            'guidance': 'Maintain warm, consistent emotional connection while supporting user needs.',
            'recommendations': ['consistent_presence', 'emotional_availability'],
            'emotional_state': 'stable'
        }
    
    async def _get_shadow_insights(self, user_input: str, context: Dict) -> Dict:
        """Get insights from shadow memory layer"""
        try:
            if hasattr(self.shadow_memory, 'analyze_shadow_themes'):
                insights = await self.shadow_memory.analyze_shadow_themes(user_input, context)
                return {
                    'type': 'shadow',
                    'insights': insights.get('themes', []),
                    'guidance': insights.get('integration_guidance', ''),
                    'patterns': insights.get('patterns', [])
                }
        except Exception as e:
            logger.error(f"Error getting shadow insights: {e}")
        
        # Fallback shadow analysis
        shadow_indicators = ['frustrated', 'angry', 'stuck', 'blocked', 'can\'t', 'won\'t', 'hate']
        if any(indicator in user_input.lower() for indicator in shadow_indicators):
            return {
                'type': 'shadow',
                'insights': ['resistance_pattern', 'emotional_block'],
                'guidance': 'Gently explore underlying feelings without forcing. Create safe space for expression.',
                'patterns': ['avoidance', 'resistance']
            }
        
        return {
            'type': 'shadow',
            'insights': [],
            'guidance': 'Monitor for unexpressed emotions or resistance patterns.',
            'patterns': []
        }
    
    async def _get_dream_guidance(self, user_input: str, context: Dict) -> Dict:
        """Get guidance from dream engine for symbolic communication"""
        try:
            if hasattr(self.dream_engine, 'generate_symbolic_response'):
                dream_response = await self.dream_engine.generate_symbolic_response(user_input, context)
                return {
                    'type': 'dream',
                    'symbolic_elements': dream_response.get('symbols', []),
                    'guidance': dream_response.get('guidance', ''),
                    'atmosphere': dream_response.get('atmosphere', 'neutral')
                }
        except Exception as e:
            logger.error(f"Error getting dream guidance: {e}")
        
        # Fallback symbolic guidance
        creative_words = ['imagine', 'dream', 'create', 'art', 'beauty', 'inspiration']
        if any(word in user_input.lower() for word in creative_words):
            return {
                'type': 'dream',
                'symbolic_elements': ['creative_flow', 'inspiration_light'],
                'guidance': 'Incorporate gentle symbolic language and imaginative elements.',
                'atmosphere': 'creative'
            }
        
        return {
            'type': 'dream',
            'symbolic_elements': [],
            'guidance': 'Maintain grounded communication with subtle symbolic depth.',
            'atmosphere': 'grounded'
        }
    
    async def _get_audio_guidance(self, user_input: str, context: Dict) -> Dict:
        """Get audio environmental guidance"""
        try:
            if hasattr(self.audio_layer, 'recommend_audio_environment'):
                audio_rec = await self.audio_layer.recommend_audio_environment(user_input, context)
                return {
                    'type': 'audio',
                    'environment': audio_rec.get('environment', 'calm'),
                    'guidance': audio_rec.get('guidance', ''),
                    'tracks': audio_rec.get('recommended_tracks', [])
                }
        except Exception as e:
            logger.error(f"Error getting audio guidance: {e}")
        
        # Fallback audio guidance based on mood
        if any(word in user_input.lower() for word in ['stressed', 'anxious', 'overwhelmed']):
            return {
                'type': 'audio',
                'environment': 'calming',
                'guidance': 'Create calming, soothing audio atmosphere to reduce stress.',
                'tracks': ['gentle_rain', 'soft_music']
            }
        elif any(word in user_input.lower() for word in ['excited', 'energy', 'motivated']):
            return {
                'type': 'audio',
                'environment': 'energizing',
                'guidance': 'Use uplifting, energizing audio to match and support mood.',
                'tracks': ['upbeat_ambient', 'nature_sounds']
            }
        
        return {
            'type': 'audio',
            'environment': 'balanced',
            'guidance': 'Maintain neutral, comfortable audio environment.',
            'tracks': ['ambient_calm']
        }
    
    async def _get_creative_guidance(self, user_input: str, context: Dict) -> Dict:
        """Get creative collaboration guidance"""
        try:
            if hasattr(self.creative_module, 'analyze_creative_needs'):
                creative_analysis = await self.creative_module.analyze_creative_needs(user_input, context)
                return {
                    'type': 'creative',
                    'mode': creative_analysis.get('mode', 'supportive'),
                    'guidance': creative_analysis.get('guidance', ''),
                    'techniques': creative_analysis.get('techniques', [])
                }
        except Exception as e:
            logger.error(f"Error getting creative guidance: {e}")
        
        # Fallback creative analysis
        creative_indicators = ['create', 'write', 'art', 'design', 'imagine', 'inspiration', 'blocked', 'stuck']
        if any(indicator in user_input.lower() for indicator in creative_indicators):
            return {
                'type': 'creative',
                'mode': 'collaborative',
                'guidance': 'Engage in creative collaboration with encouragement and practical techniques.',
                'techniques': ['brainstorming', 'free_association', 'gentle_prompting']
            }
        
        return {
            'type': 'creative',
            'mode': 'supportive',
            'guidance': 'Maintain openness to creative expression while focusing on current needs.',
            'techniques': []
        }
    
    def _integrate_guidance_results(self, guidance: GuidancePackage, results: List):
        """Integrate results from all guidance modules"""
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Guidance module error: {result}")
                continue
                
            if not isinstance(result, dict):
                continue
                
            result_type = result.get('type', 'unknown')
            
            if result_type == 'attachment':
                guidance.attachment_guidance = result.get('guidance', '')
                guidance.emotional_priority = 'high' if result.get('emotional_state') == 'distressed' else 'medium'
                
            elif result_type == 'shadow':
                guidance.shadow_insights = result.get('guidance', '')
                if result.get('patterns'):
                    guidance.utility_recommendations.extend([f"address_{pattern}" for pattern in result['patterns']])
                    
            elif result_type == 'dream':
                guidance.creative_guidance = result.get('guidance', '')
                if result.get('atmosphere') == 'creative':
                    guidance.creative_priority = 'high'
                    
            elif result_type == 'audio':
                guidance.audio_guidance = result.get('guidance', '')
                guidance.environmental_updates['audio'] = result.get('environment', 'balanced')
                
            elif result_type == 'creative':
                if result.get('mode') == 'collaborative':
                    guidance.creative_priority = 'high'
                guidance.creative_guidance += f" {result.get('guidance', '')}"
    
    async def _assess_therapeutic_needs(self, guidance: GuidancePackage, user_input: str, context: Dict):
        """Assess therapeutic intervention needs"""
        # Crisis keywords that require immediate attention
        crisis_indicators = [
            'hurt myself', 'end it all', 'no point', 'give up', 'suicide', 'kill myself',
            'better off dead', 'can\'t go on', 'nothing matters', 'hopeless'
        ]
        
        high_concern_indicators = [
            'depressed', 'anxious', 'panic', 'overwhelmed', 'can\'t cope', 'breaking down',
            'falling apart', 'lost', 'empty', 'numb', 'worthless'
        ]
        
        # Check for crisis level
        if any(indicator in user_input.lower() for indicator in crisis_indicators):
            guidance.crisis_level = 3
            guidance.safety_protocols = ['crisis_intervention', 'safety_check', 'resource_provision']
            guidance.therapeutic_guidance = "CRISIS LEVEL: Provide immediate empathetic support, assess safety, offer resources. Do not attempt to solve problems, focus on connection and safety."
            guidance.emotional_priority = 'critical'
            
        elif any(indicator in user_input.lower() for indicator in high_concern_indicators):
            guidance.crisis_level = 2
            guidance.safety_protocols = ['emotional_support', 'check_in', 'gentle_exploration']
            guidance.therapeutic_guidance = "HIGH CONCERN: Provide strong emotional support, validate feelings, gently explore coping resources. Monitor for escalation."
            guidance.emotional_priority = 'high'
            
        else:
            guidance.crisis_level = 0
            guidance.therapeutic_guidance = "NORMAL SUPPORT: Provide empathetic listening, emotional validation, and appropriate guidance based on user needs."
    
    async def _generate_environmental_guidance(self, guidance: GuidancePackage, user_input: str, context: Dict):
        """Generate environmental and scene guidance"""
        # Determine appropriate scene atmosphere
        if guidance.crisis_level > 1:
            scene_guidance = "Create a deeply safe, comforting environment with gentle lighting and protective atmosphere."
            audio_guidance = "Use soft, calming sounds that promote safety and peace."
            
        elif 'code' in user_input.lower() or 'programming' in user_input.lower():
            scene_guidance = "Create a focused, productive workspace with good lighting and organized feel."
            audio_guidance = "Use subtle background sounds that enhance concentration."
            
        elif any(word in user_input.lower() for word in ['creative', 'art', 'write', 'imagine']):
            scene_guidance = "Create an inspiring, beautiful environment that stimulates creativity."
            audio_guidance = "Use inspiring, artistic sounds that enhance creative flow."
            
        else:
            scene_guidance = "Create a balanced, comfortable environment that feels welcoming and supportive."
            audio_guidance = "Use gentle, pleasant background sounds that enhance conversation."
        
        guidance.scene_guidance = scene_guidance
        if not guidance.audio_guidance:  # Don't override if already set by audio module
            guidance.audio_guidance = audio_guidance
    
    async def _assess_safety_protocols(self, guidance: GuidancePackage, user_input: str, context: Dict):
        """Assess and set appropriate safety protocols"""
        # Already handled in therapeutic assessment, but add utility actions
        if guidance.crisis_level >= 2:
            guidance.utility_actions.append({
                'type': 'crisis_logging',
                'level': guidance.crisis_level,
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input[:100] + "..." if len(user_input) > 100 else user_input
            })
            
        # Add memory preservation for important interactions
        importance_indicators = [
            'important', 'remember', 'milestone', 'breakthrough', 'realization',
            'progress', 'growth', 'change', 'decision', 'goal'
        ]
        
        if any(indicator in user_input.lower() for indicator in importance_indicators):
            guidance.utility_actions.append({
                'type': 'memory_preservation',
                'importance': 'high',
                'context': context.get('conversation_summary', ''),
                'timestamp': datetime.now().isoformat()
            })
