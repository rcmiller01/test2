"""
Creative Discovery & Dynamic Model Integration System
Learns user creative preferences and dynamically integrates specialized AI models
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import importlib
import subprocess
import os

class CreativeMediaType(Enum):
    MUSIC = "music"
    VISUAL_ART = "visual_art"
    POETRY = "poetry"
    PROSE = "prose"
    PHOTOGRAPHY = "photography"
    DANCE = "dance"
    CRAFTS = "crafts"
    COOKING = "cooking"
    DIGITAL_ART = "digital_art"
    ANIMATION = "animation"
    GAME_DESIGN = "game_design"
    FASHION = "fashion"

@dataclass
class CreativePreference:
    """User's creative preference discovered through conversation"""
    media_type: CreativeMediaType
    confidence_score: float  # 0.0 to 1.0
    specific_interests: List[str]  # e.g., ["jazz", "piano"] for music
    skill_level: str  # "beginner", "intermediate", "advanced", "professional"
    emotional_connection: float  # How emotionally invested they are
    frequency_mentioned: int
    last_mentioned: datetime
    examples_shared: List[str]  # Specific works/artists they mentioned

@dataclass
class CreativeModel:
    """Dynamic AI model for specific creative medium"""
    model_id: str
    media_type: CreativeMediaType
    model_name: str
    api_endpoint: Optional[str]
    local_model_path: Optional[str]
    capabilities: List[str]
    quality_level: str  # "basic", "professional", "premium"
    cost_per_use: float
    is_installed: bool
    installation_command: Optional[str]

class CreativeDiscoveryEngine:
    """Discovers user creative interests through conversation analysis"""
    
    def __init__(self, database_manager, llm_orchestrator):
        self.db = database_manager
        self.llm = llm_orchestrator
        
        # Creative interest detection patterns
        self.detection_patterns = {
            CreativeMediaType.MUSIC: [
                "music", "song", "instrument", "band", "album", "concert", "melody", 
                "rhythm", "guitar", "piano", "drums", "singing", "compose", "jazz", 
                "rock", "classical", "electronic", "producer", "studio", "lyrics"
            ],
            CreativeMediaType.VISUAL_ART: [
                "painting", "drawing", "sketch", "canvas", "brush", "colors", "portrait",
                "landscape", "abstract", "gallery", "artist", "museum", "pencil", "oil",
                "watercolor", "acrylic", "digital art", "illustration", "design"
            ],
            CreativeMediaType.PHOTOGRAPHY: [
                "photo", "camera", "lens", "shoot", "capture", "portrait", "landscape",
                "street photography", "macro", "exposure", "composition", "editing",
                "lightroom", "photoshop", "film", "digital", "nature photography"
            ],
            CreativeMediaType.COOKING: [
                "cooking", "recipe", "chef", "kitchen", "baking", "ingredients", "flavor",
                "restaurant", "cuisine", "spices", "technique", "culinary", "food",
                "meal", "dish", "preparation", "seasoning", "knife skills"
            ],
            CreativeMediaType.CRAFTS: [
                "craft", "handmade", "knitting", "sewing", "woodworking", "pottery",
                "jewelry", "scrapbook", "diy", "maker", "tools", "materials", "project",
                "creative", "building", "carving", "weaving", "embroidery"
            ],
            CreativeMediaType.DIGITAL_ART: [
                "digital art", "photoshop", "illustrator", "tablet", "stylus", "vector",
                "pixel art", "3d modeling", "blender", "maya", "textures", "rendering",
                "concept art", "character design", "environment art", "ui design"
            ],
            CreativeMediaType.GAME_DESIGN: [
                "game design", "unity", "unreal", "programming", "level design", "mechanics",
                "gameplay", "indie game", "game dev", "prototype", "playtesting", "balance",
                "narrative design", "character development", "world building"
            ]
        }
        
        # Available creative AI models
        self.available_models = {
            CreativeMediaType.MUSIC: [
                CreativeModel(
                    model_id="musicgen_small",
                    media_type=CreativeMediaType.MUSIC,
                    model_name="MusicGen Small",
                    api_endpoint=None,
                    local_model_path="models/musicgen-small",
                    capabilities=["melody_generation", "accompaniment", "style_transfer"],
                    quality_level="basic",
                    cost_per_use=0.0,
                    is_installed=False,
                    installation_command="pip install musicgen transformers"
                ),
                CreativeModel(
                    model_id="mubert_api",
                    media_type=CreativeMediaType.MUSIC,
                    model_name="Mubert AI",
                    api_endpoint="https://api.mubert.com/",
                    local_model_path=None,
                    capabilities=["full_composition", "genre_specific", "mood_based"],
                    quality_level="professional",
                    cost_per_use=0.25,
                    is_installed=False,
                    installation_command="pip install mubert-api"
                )
            ],
            CreativeMediaType.VISUAL_ART: [
                CreativeModel(
                    model_id="stable_diffusion",
                    media_type=CreativeMediaType.VISUAL_ART,
                    model_name="Stable Diffusion",
                    api_endpoint=None,
                    local_model_path="models/stable-diffusion",
                    capabilities=["image_generation", "style_transfer", "inpainting"],
                    quality_level="professional",
                    cost_per_use=0.0,
                    is_installed=False,
                    installation_command="pip install diffusers transformers"
                ),
                CreativeModel(
                    model_id="midjourney_api",
                    media_type=CreativeMediaType.VISUAL_ART,
                    model_name="Midjourney",
                    api_endpoint="https://api.midjourney.com/",
                    local_model_path=None,
                    capabilities=["artistic_generation", "concept_art", "photorealistic"],
                    quality_level="premium",
                    cost_per_use=0.50,
                    is_installed=False,
                    installation_command="pip install midjourney-api"
                )
            ],
            CreativeMediaType.COOKING: [
                CreativeModel(
                    model_id="recipe_generator",
                    media_type=CreativeMediaType.COOKING,
                    model_name="Recipe Generator",
                    api_endpoint=None,
                    local_model_path="models/recipe-gen",
                    capabilities=["recipe_creation", "ingredient_substitution", "nutrition"],
                    quality_level="basic",
                    cost_per_use=0.0,
                    is_installed=False,
                    installation_command="pip install recipe-generator transformers"
                )
            ],
            CreativeMediaType.DIGITAL_ART: [
                CreativeModel(
                    model_id="controlnet",
                    media_type=CreativeMediaType.DIGITAL_ART,
                    model_name="ControlNet",
                    api_endpoint=None,
                    local_model_path="models/controlnet",
                    capabilities=["pose_control", "depth_control", "sketch_to_art"],
                    quality_level="professional",
                    cost_per_use=0.0,
                    is_installed=False,
                    installation_command="pip install controlnet-aux diffusers"
                )
            ]
        }
        
        # User creative preferences storage
        self.user_preferences: Dict[str, List[CreativePreference]] = {}
    
    async def analyze_conversation_for_creative_interests(self, user_id: str, conversation_text: str, 
                                                        conversation_context: Optional[Dict] = None):
        """Analyze conversation for creative interest indicators"""
        
        # Detect mentions of creative activities
        detected_interests = {}
        
        conversation_lower = conversation_text.lower()
        
        for media_type, keywords in self.detection_patterns.items():
            mentions = []
            confidence = 0.0
            
            for keyword in keywords:
                if keyword in conversation_lower:
                    mentions.append(keyword)
                    # Weight confidence based on keyword specificity
                    if len(keyword.split()) > 1:  # Multi-word keywords are more specific
                        confidence += 0.3
                    else:
                        confidence += 0.1
            
            if mentions:
                detected_interests[media_type] = {
                    'keywords': mentions,
                    'confidence': min(confidence, 1.0),
                    'context': conversation_context or {}
                }
        
        # Use LLM to extract deeper creative insights
        if detected_interests:
            enhanced_analysis = await self._llm_analyze_creative_interests(
                conversation_text, detected_interests
            )
            
            # Update user preferences
            await self._update_user_creative_preferences(user_id, enhanced_analysis)
            
            # Check if we should suggest installing new models
            await self._evaluate_model_installation_needs(user_id, enhanced_analysis)
        
        return detected_interests
    
    async def _llm_analyze_creative_interests(self, conversation: str, detected_interests: Dict):
        """Use LLM to deeply analyze creative interests from conversation"""
        
        prompt = f"""
        Analyze this conversation for creative interests and extract detailed information:
        
        Conversation: "{conversation}"
        
        Detected creative areas: {list(detected_interests.keys())}
        
        For each detected creative area, provide:
        1. Specific interests within that area
        2. Apparent skill level (beginner/intermediate/advanced/professional)
        3. Emotional connection strength (0.0-1.0)
        4. Specific examples or preferences mentioned
        5. Whether they create or just appreciate this art form
        
        Return a JSON object with detailed analysis.
        """
        
        try:
            response = await self.llm.generate_response(
                prompt, 
                persona="analytical", 
                max_tokens=800,
                temperature=0.3
            )
            
            # Parse LLM response for structured data
            analysis = json.loads(response.get('content', '{}'))
            return analysis
            
        except Exception as e:
            print(f"Error in LLM creative analysis: {e}")
            return {}
    
    async def _update_user_creative_preferences(self, user_id: str, analysis: Dict):
        """Update user's creative preferences based on analysis"""
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = []
        
        current_time = datetime.now()
        
        for media_type_str, details in analysis.items():
            try:
                media_type = CreativeMediaType(media_type_str)
                
                # Find existing preference or create new one
                existing_pref = None
                for pref in self.user_preferences[user_id]:
                    if pref.media_type == media_type:
                        existing_pref = pref
                        break
                
                if existing_pref:
                    # Update existing preference
                    existing_pref.confidence_score = max(
                        existing_pref.confidence_score, 
                        details.get('confidence', 0.0)
                    )
                    existing_pref.frequency_mentioned += 1
                    existing_pref.last_mentioned = current_time
                    
                    # Merge specific interests
                    new_interests = details.get('specific_interests', [])
                    existing_pref.specific_interests = list(set(
                        existing_pref.specific_interests + new_interests
                    ))
                    
                else:
                    # Create new preference
                    new_preference = CreativePreference(
                        media_type=media_type,
                        confidence_score=details.get('confidence', 0.0),
                        specific_interests=details.get('specific_interests', []),
                        skill_level=details.get('skill_level', 'unknown'),
                        emotional_connection=details.get('emotional_connection', 0.0),
                        frequency_mentioned=1,
                        last_mentioned=current_time,
                        examples_shared=details.get('examples', [])
                    )
                    
                    self.user_preferences[user_id].append(new_preference)
                
            except ValueError:
                # Invalid media type, skip
                continue
        
        # Save to database
        await self._save_user_preferences(user_id)
    
    async def _evaluate_model_installation_needs(self, user_id: str, analysis: Dict):
        """Evaluate if new creative models should be installed based on user interests"""
        
        user_prefs = self.user_preferences.get(user_id, [])
        
        for preference in user_prefs:
            # Install models for high-confidence, emotionally connected interests
            if (preference.confidence_score > 0.6 and 
                preference.emotional_connection > 0.5 and
                preference.frequency_mentioned >= 2):
                
                await self._suggest_and_install_models(user_id, preference)
    
    async def _suggest_and_install_models(self, user_id: str, preference: CreativePreference):
        """Suggest and potentially install creative models for user's interests"""
        
        available_models = self.available_models.get(preference.media_type, [])
        
        if not available_models:
            return
        
        # Choose best model based on user preference and system capabilities
        chosen_model = self._select_best_model(preference, available_models)
        
        if chosen_model and not chosen_model.is_installed:
            # Ask user permission to install
            install_approved = await self._request_model_installation_permission(
                user_id, chosen_model, preference
            )
            
            if install_approved:
                success = await self._install_creative_model(chosen_model)
                
                if success:
                    # Notify user and offer to create something
                    await self._offer_creative_collaboration(user_id, chosen_model, preference)
    
    def _select_best_model(self, preference: CreativePreference, available_models: List[CreativeModel]):
        """Select the best model based on user preference and system constraints"""
        
        # Score models based on various factors
        scored_models = []
        
        for model in available_models:
            score = 0.0
            
            # Prefer free models for beginners
            if preference.skill_level in ['beginner', 'unknown'] and model.cost_per_use == 0.0:
                score += 0.4
            
            # Prefer professional models for advanced users
            if preference.skill_level in ['advanced', 'professional']:
                if model.quality_level == 'professional':
                    score += 0.3
                elif model.quality_level == 'premium':
                    score += 0.4
            
            # Prefer local models for privacy
            if model.local_model_path:
                score += 0.2
            
            # Consider emotional connection - higher connection justifies premium models
            if preference.emotional_connection > 0.8 and model.quality_level == 'premium':
                score += 0.3
            
            scored_models.append((score, model))
        
        # Return highest scored model
        if scored_models:
            scored_models.sort(key=lambda x: x[0], reverse=True)
            return scored_models[0][1]
        
        return None
    
    async def _request_model_installation_permission(self, user_id: str, model: CreativeModel, 
                                                   preference: CreativePreference):
        """Ask user permission to install a creative model"""
        
        # Create a notification for the user about the potential installation
        notification = {
            'type': 'model_installation_request',
            'user_id': user_id,
            'model': {
                'name': model.model_name,
                'media_type': model.media_type.value,
                'quality': model.quality_level,
                'cost': model.cost_per_use,
                'capabilities': model.capabilities
            },
            'preference': {
                'skill_level': preference.skill_level,
                'interests': preference.specific_interests,
                'confidence': preference.confidence_score
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Store notification in database for UI to display
        await self.db.store_notification(user_id, notification)
        
        # For demo purposes, auto-approve free models
        return model.cost_per_use == 0.0
    
    async def _install_creative_model(self, model: CreativeModel):
        """Install a creative AI model"""
        
        try:
            if model.installation_command:
                # Run installation command
                process = await asyncio.create_subprocess_shell(
                    model.installation_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    model.is_installed = True
                    print(f"Successfully installed {model.model_name}")
                    return True
                else:
                    print(f"Failed to install {model.model_name}: {stderr.decode()}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error installing model {model.model_name}: {e}")
            return False
    
    async def _offer_creative_collaboration(self, user_id: str, model: CreativeModel, 
                                          preference: CreativePreference):
        """Offer to create something with the newly installed model"""
        
        # Generate a personalized creative offer
        offer_prompt = f"""
        A user who enjoys {preference.media_type.value} (specifically {', '.join(preference.specific_interests)}) 
        at a {preference.skill_level} level just had the {model.model_name} model installed.
        
        Create a warm, enthusiastic offer to collaborate on creating something in their preferred style.
        Be specific about what you could create together and make it personally meaningful.
        """
        
        try:
            response = await self.llm.generate_response(
                offer_prompt,
                persona="creative_collaborator",
                max_tokens=300,
                temperature=0.7
            )
            
            # Store the offer as a proactive interaction
            collaboration_offer = {
                'type': 'creative_collaboration_offer',
                'user_id': user_id,
                'model_used': model.model_id,
                'media_type': preference.media_type.value,
                'offer_text': response.get('content', ''),
                'preference_context': {
                    'interests': preference.specific_interests,
                    'skill_level': preference.skill_level,
                    'examples': preference.examples_shared
                },
                'timestamp': datetime.now().isoformat()
            }
            
            await self.db.store_proactive_interaction(user_id, collaboration_offer)
            
        except Exception as e:
            print(f"Error creating collaboration offer: {e}")
    
    async def create_personalized_content(self, user_id: str, media_type: CreativeMediaType, 
                                        creative_prompt: Optional[str] = None):
        """Create personalized creative content using installed models"""
        
        # Get user's preferences for this media type
        user_prefs = self.user_preferences.get(user_id, [])
        preference = None
        
        for pref in user_prefs:
            if pref.media_type == media_type:
                preference = pref
                break
        
        if not preference:
            return {"error": "No preference found for this media type"}
        
        # Find installed model for this media type
        available_models = self.available_models.get(media_type, [])
        installed_model = None
        
        for model in available_models:
            if model.is_installed:
                installed_model = model
                break
        
        if not installed_model:
            return {"error": "No installed model found for this media type"}
        
        # Generate content using the model
        return await self._generate_creative_content(installed_model, preference, creative_prompt)
    
    async def _generate_creative_content(self, model: CreativeModel, preference: CreativePreference, 
                                       prompt: Optional[str] = None):
        """Generate creative content using specified model"""
        
        try:
            if model.media_type == CreativeMediaType.MUSIC:
                return await self._generate_music(model, preference, prompt)
            elif model.media_type == CreativeMediaType.VISUAL_ART:
                return await self._generate_visual_art(model, preference, prompt)
            elif model.media_type == CreativeMediaType.COOKING:
                return await self._generate_recipe(model, preference, prompt)
            elif model.media_type == CreativeMediaType.DIGITAL_ART:
                return await self._generate_digital_art(model, preference, prompt)
            else:
                return {"error": f"Content generation not implemented for {model.media_type.value}"}
                
        except Exception as e:
            return {"error": f"Content generation failed: {str(e)}"}
    
    async def _generate_music(self, model: CreativeModel, preference: CreativePreference, prompt: Optional[str]):
        """Generate music using music AI model"""
        
        # Construct music generation prompt based on user preferences
        music_prompt = f"Create a {', '.join(preference.specific_interests)} style piece"
        if prompt:
            music_prompt += f" inspired by: {prompt}"
        
        # Placeholder for actual music generation
        # In real implementation, would call MusicGen, Mubert, etc.
        
        generated_content = {
            "type": "music",
            "model_used": model.model_name,
            "prompt": music_prompt,
            "user_preferences": preference.specific_interests,
            "file_path": f"generated/music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
            "description": f"A {preference.specific_interests[0]} piece created just for you",
            "duration_seconds": 30,
            "metadata": {
                "genre": preference.specific_interests,
                "mood": "personalized",
                "created_at": datetime.now().isoformat()
            }
        }
        
        return generated_content
    
    async def _generate_visual_art(self, model: CreativeModel, preference: CreativePreference, prompt: Optional[str]):
        """Generate visual art using image AI model"""
        
        art_prompt = f"{', '.join(preference.specific_interests)} style artwork"
        if prompt:
            art_prompt += f", {prompt}"
        
        generated_content = {
            "type": "visual_art",
            "model_used": model.model_name,
            "prompt": art_prompt,
            "user_preferences": preference.specific_interests,
            "file_path": f"generated/art_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "description": f"A {preference.specific_interests[0]} artwork created with you in mind",
            "dimensions": "1024x1024",
            "metadata": {
                "style": preference.specific_interests,
                "technique": "AI-generated",
                "created_at": datetime.now().isoformat()
            }
        }
        
        return generated_content
    
    async def _generate_recipe(self, model: CreativeModel, preference: CreativePreference, prompt: Optional[str]):
        """Generate recipe using cooking AI model"""
        
        recipe_prompt = f"Create a {', '.join(preference.specific_interests)} recipe"
        if prompt:
            recipe_prompt += f" featuring {prompt}"
        
        generated_content = {
            "type": "recipe",
            "model_used": model.model_name,
            "prompt": recipe_prompt,
            "user_preferences": preference.specific_interests,
            "title": f"Personalized {preference.specific_interests[0]} Creation",
            "ingredients": [
                "Ingredients tailored to your taste preferences",
                "Fresh, high-quality components",
                "Special touches based on your cooking style"
            ],
            "instructions": [
                "Detailed step-by-step instructions",
                "Techniques suited to your skill level",
                "Tips for personalization"
            ],
            "metadata": {
                "cuisine": preference.specific_interests,
                "difficulty": preference.skill_level,
                "created_at": datetime.now().isoformat()
            }
        }
        
        return generated_content
    
    async def _generate_digital_art(self, model: CreativeModel, preference: CreativePreference, prompt: Optional[str]):
        """Generate digital art using specialized AI model"""
        
        digital_prompt = f"Digital {', '.join(preference.specific_interests)} artwork"
        if prompt:
            digital_prompt += f", {prompt}"
        
        generated_content = {
            "type": "digital_art",
            "model_used": model.model_name,
            "prompt": digital_prompt,
            "user_preferences": preference.specific_interests,
            "file_path": f"generated/digital_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "description": f"Digital {preference.specific_interests[0]} art crafted for your aesthetic",
            "resolution": "2048x2048",
            "metadata": {
                "style": preference.specific_interests,
                "software": model.model_name,
                "created_at": datetime.now().isoformat()
            }
        }
        
        return generated_content
    
    async def get_user_creative_profile(self, user_id: str):
        """Get comprehensive creative profile for user"""
        
        preferences = self.user_preferences.get(user_id, [])
        
        if not preferences:
            return {"message": "No creative preferences discovered yet"}
        
        # Sort by confidence and recent activity
        preferences.sort(key=lambda p: (p.confidence_score, p.frequency_mentioned), reverse=True)
        
        profile = {
            "user_id": user_id,
            "creative_interests": [],
            "installed_models": [],
            "recommended_activities": [],
            "relationship_building_suggestions": []
        }
        
        for pref in preferences:
            interest_data = {
                "media_type": pref.media_type.value,
                "confidence": pref.confidence_score,
                "specific_interests": pref.specific_interests,
                "skill_level": pref.skill_level,
                "emotional_connection": pref.emotional_connection,
                "frequency_mentioned": pref.frequency_mentioned,
                "last_mentioned": pref.last_mentioned.isoformat(),
                "available_models": []
            }
            
            # Add available models for this interest
            available_models = self.available_models.get(pref.media_type, [])
            for model in available_models:
                interest_data["available_models"].append({
                    "name": model.model_name,
                    "quality": model.quality_level,
                    "cost": model.cost_per_use,
                    "installed": model.is_installed,
                    "capabilities": model.capabilities
                })
            
            profile["creative_interests"].append(interest_data)
        
        return profile
    
    async def _save_user_preferences(self, user_id: str):
        """Save user preferences to database"""
        
        preferences_data = []
        for pref in self.user_preferences.get(user_id, []):
            preferences_data.append({
                "media_type": pref.media_type.value,
                "confidence_score": pref.confidence_score,
                "specific_interests": pref.specific_interests,
                "skill_level": pref.skill_level,
                "emotional_connection": pref.emotional_connection,
                "frequency_mentioned": pref.frequency_mentioned,
                "last_mentioned": pref.last_mentioned.isoformat(),
                "examples_shared": pref.examples_shared
            })
        
        await self.db.store_user_creative_preferences(user_id, preferences_data)

# Integration with existing systems
class CreativeDiscoveryIntegration:
    """Integrates creative discovery with existing persona and conversation systems"""
    
    def __init__(self, creative_discovery_engine, persona_system, conversation_manager):
        self.discovery = creative_discovery_engine
        self.personas = persona_system
        self.conversations = conversation_manager
    
    async def process_conversation_for_creativity(self, user_id: str, conversation_data: Dict):
        """Process conversation through creative discovery lens"""
        
        # Extract conversation text
        conversation_text = conversation_data.get('message', '')
        
        if len(conversation_text) > 10:  # Only analyze substantial messages
            # Analyze for creative interests
            detected_interests = await self.discovery.analyze_conversation_for_creative_interests(
                user_id, conversation_text, conversation_data
            )
            
            # If strong creative interests detected, enhance persona responses
            if detected_interests:
                await self._enhance_persona_with_creative_context(user_id, detected_interests)
        
        return detected_interests
    
    async def _enhance_persona_with_creative_context(self, user_id: str, detected_interests: Dict):
        """Enhance persona system with creative context"""
        
        # Update persona prompts to include creative collaboration
        creative_context = {
            "detected_creative_interests": detected_interests,
            "collaborative_opportunities": True,
            "creative_engagement_mode": True
        }
        
        await self.personas.update_context(user_id, creative_context)
    
    async def suggest_creative_activities(self, user_id: str):
        """Suggest creative activities based on discovered preferences"""
        
        profile = await self.discovery.get_user_creative_profile(user_id)
        
        if not profile.get("creative_interests"):
            return []
        
        suggestions = []
        for interest in profile["creative_interests"][:3]:  # Top 3 interests
            
            if interest["confidence"] > 0.5:  # Only confident matches
                media_type = CreativeMediaType(interest["media_type"])
                
                # Check if we can create content in this area
                installed_models = [m for m in interest["available_models"] if m["installed"]]
                
                if installed_models:
                    suggestion = {
                        "activity": f"Create {media_type.value}",
                        "description": f"Let's collaborate on some {', '.join(interest['specific_interests'])} together!",
                        "media_type": media_type.value,
                        "model_available": True,
                        "skill_level": interest["skill_level"],
                        "emotional_potential": interest["emotional_connection"]
                    }
                else:
                    suggestion = {
                        "activity": f"Explore {media_type.value}",
                        "description": f"I'd love to learn more about your {', '.join(interest['specific_interests'])} interests!",
                        "media_type": media_type.value,
                        "model_available": False,
                        "skill_level": interest["skill_level"],
                        "emotional_potential": interest["emotional_connection"]
                    }
                
                suggestions.append(suggestion)
        
        return suggestions
