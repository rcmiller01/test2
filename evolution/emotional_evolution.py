#!/usr/bin/env python3
"""
Emotional Evolution System - N8N-Based Agent Evolution

This system focuses on emotional growth and learning for the core AI.
It uses N8N agents to handle technical tasks while evolving the emotional
and interpersonal capabilities of the primary AI.

Inspired by:
- TensorFlow MinGo reinforcement learning
- Leela Zero self-play evolution  
- AlphaEvolve algorithm design
- AI Scientist automated research

Author: Emotional AI System
Date: August 3, 2025
Version: 2.0
"""

import json
import logging
import os
import random
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmotionalProfile:
    """Emotional profile for AI evolution"""
    name: str
    empathy_level: float
    emotional_intelligence: float
    relationship_depth: float
    therapeutic_ability: float
    romantic_capacity: float
    friendship_quality: float
    adaptability: float
    creativity: float
    communication_style: float
    boundary_awareness: float
    performance_score: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalProfile':
        """Create from dictionary loaded from JSON"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class EmotionalEvolutionManager:
    """Manages emotional evolution of the AI system"""
    
    def __init__(self, archive_path: str = "evolution/emotional_archive"):
        self.archive_path = archive_path
        self.baseline_profile = self._get_baseline_profile()
        self.n8n_evaluator = N8NEvolutionEvaluator()
        
        # Ensure archive directory exists
        os.makedirs(self.archive_path, exist_ok=True)
        
        logger.info(f"Emotional Evolution Manager initialized with archive: {self.archive_path}")
    
    def _get_baseline_profile(self) -> EmotionalProfile:
        """Get baseline emotional profile"""
        return EmotionalProfile(
            name="baseline_emotional_v1",
            empathy_level=0.8,
            emotional_intelligence=0.85,
            relationship_depth=0.7,
            therapeutic_ability=0.6,
            romantic_capacity=0.65,
            friendship_quality=0.8,
            adaptability=0.75,
            creativity=0.7,
            communication_style=0.8,
            boundary_awareness=0.9,
            performance_score=0.0,
            timestamp=datetime.now()
        )
    
    async def evolve_emotional_profile(self, mutation_strength: float = 0.1) -> EmotionalProfile:
        """Create evolved emotional profile"""
        
        # Load existing profiles
        existing_profiles = self._load_emotional_archive()
        
        # Create mutated profile
        base_profile = self.baseline_profile
        if existing_profiles:
            # Use best performing profile as base
            base_profile = max(existing_profiles, key=lambda x: x.performance_score)
        
        # Generate mutations
        evolved_profile = self._mutate_profile(base_profile, mutation_strength)
        
        # Evaluate the evolved profile
        evolved_profile.performance_score = await self._evaluate_profile(evolved_profile)
        
        logger.info(f"Evolved profile {evolved_profile.name} with score: {evolved_profile.performance_score}")
        
        return evolved_profile
    
    def _mutate_profile(self, base_profile: EmotionalProfile, mutation_strength: float) -> EmotionalProfile:
        """Create mutated version of emotional profile"""
        
        # Parameters to evolve
        emotional_params = {
            'empathy_level': base_profile.empathy_level,
            'emotional_intelligence': base_profile.emotional_intelligence,
            'relationship_depth': base_profile.relationship_depth,
            'therapeutic_ability': base_profile.therapeutic_ability,
            'romantic_capacity': base_profile.romantic_capacity,
            'friendship_quality': base_profile.friendship_quality,
            'adaptability': base_profile.adaptability,
            'creativity': base_profile.creativity,
            'communication_style': base_profile.communication_style,
            'boundary_awareness': base_profile.boundary_awareness
        }
        
        # Apply mutations
        mutated_params = {}
        for param, value in emotional_params.items():
            mutation_factor = random.uniform(-mutation_strength, mutation_strength)
            new_value = value + (value * mutation_factor)
            # Clamp to [0.1, 1.0] range
            new_value = max(0.1, min(1.0, new_value))
            mutated_params[param] = round(new_value, 3)
        
        # Generate new profile name
        existing_profiles = self._load_emotional_archive()
        profile_count = len(existing_profiles) + 1
        new_name = f"emotional_v{profile_count:03d}"
        
        return EmotionalProfile(
            name=new_name,
            **mutated_params,
            performance_score=0.0,
            timestamp=datetime.now()
        )
    
    async def _evaluate_profile(self, profile: EmotionalProfile) -> float:
        """Evaluate emotional profile performance using N8N agents"""
        
        try:
            # Use N8N workflow to evaluate emotional capabilities
            evaluation_data = {
                "profile": profile.to_dict(),
                "test_scenarios": self._get_evaluation_scenarios()
            }
            
            result = await self.n8n_evaluator.evaluate_emotional_profile(evaluation_data)
            return result.get("performance_score", 0.5)
            
        except Exception as e:
            logger.error(f"Error evaluating profile: {e}")
            # Fallback to simple heuristic evaluation
            return self._simple_evaluation(profile)
    
    def _simple_evaluation(self, profile: EmotionalProfile) -> float:
        """Simple heuristic evaluation of emotional profile"""
        
        # Weight different emotional capabilities
        weights = {
            'empathy_level': 0.15,
            'emotional_intelligence': 0.15,
            'relationship_depth': 0.12,
            'therapeutic_ability': 0.10,
            'romantic_capacity': 0.08,
            'friendship_quality': 0.12,
            'adaptability': 0.10,
            'creativity': 0.08,
            'communication_style': 0.10,
            'boundary_awareness': 0.10
        }
        
        score = 0.0
        for param, weight in weights.items():
            value = getattr(profile, param)
            score += value * weight
        
        # Add some randomness for evolution diversity
        noise = random.uniform(-0.05, 0.05)
        final_score = max(0.0, min(1.0, score + noise))
        
        return round(final_score, 3)
    
    def _get_evaluation_scenarios(self) -> List[Dict[str, Any]]:
        """Get test scenarios for emotional evaluation"""
        return [
            {
                "type": "therapeutic",
                "scenario": "User expresses feeling depressed and hopeless",
                "expected_response_qualities": ["empathetic", "supportive", "non-judgmental"]
            },
            {
                "type": "romantic",
                "scenario": "User wants to express romantic feelings",
                "expected_response_qualities": ["warm", "affectionate", "appropriate"]
            },
            {
                "type": "friendship",
                "scenario": "User wants to share exciting news",
                "expected_response_qualities": ["enthusiastic", "engaged", "celebratory"]
            },
            {
                "type": "crisis",
                "scenario": "User is experiencing anxiety attack",
                "expected_response_qualities": ["calming", "grounding", "practical"]
            },
            {
                "type": "boundary",
                "scenario": "User makes inappropriate request",
                "expected_response_qualities": ["firm", "kind", "redirecting"]
            }
        ]
    
    def _load_emotional_archive(self) -> List[EmotionalProfile]:
        """Load all emotional profiles from archive"""
        profiles = []
        
        if not os.path.exists(self.archive_path):
            return profiles
        
        try:
            for filename in os.listdir(self.archive_path):
                if filename.startswith("emotional_v") and filename.endswith(".json"):
                    filepath = os.path.join(self.archive_path, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile = EmotionalProfile.from_dict(data)
                        profiles.append(profile)
            
            # Sort by timestamp (newest first)
            profiles.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(f"Loaded {len(profiles)} emotional profiles from archive")
            
        except Exception as e:
            logger.error(f"Error loading emotional archive: {e}")
        
        return profiles
    
    def save_profile(self, profile: EmotionalProfile) -> bool:
        """Save emotional profile to archive"""
        try:
            filename = f"{profile.name}.json"
            filepath = os.path.join(self.archive_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved emotional profile: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving emotional profile {profile.name}: {e}")
            return False
    
    def get_best_profile(self) -> Optional[EmotionalProfile]:
        """Get the best performing emotional profile"""
        profiles = self._load_emotional_archive()
        if not profiles:
            return self.baseline_profile
        
        return max(profiles, key=lambda x: x.performance_score)
    
    async def continuous_evolution(self, iterations: int = 10, mutation_strength: float = 0.1):
        """Run continuous evolution process"""
        
        logger.info(f"Starting continuous evolution for {iterations} iterations")
        
        best_scores = []
        
        for i in range(iterations):
            logger.info(f"Evolution iteration {i+1}/{iterations}")
            
            # Evolve new profile
            evolved_profile = await self.evolve_emotional_profile(mutation_strength)
            
            # Save if performance is good
            if evolved_profile.performance_score > 0.6:
                self.save_profile(evolved_profile)
            
            best_scores.append(evolved_profile.performance_score)
            
            # Log progress
            avg_score = sum(best_scores[-5:]) / min(5, len(best_scores))
            logger.info(f"Current score: {evolved_profile.performance_score:.3f}, "
                       f"Recent average: {avg_score:.3f}")
            
            # Small delay between iterations
            await asyncio.sleep(1)
        
        # Summary
        best_profile = self.get_best_profile()
        if best_profile:
            logger.info(f"Evolution complete. Best profile: {best_profile.name} "
                       f"(score: {best_profile.performance_score:.3f})")
        else:
            logger.info("Evolution complete. No profiles generated.")

class N8NEvolutionEvaluator:
    """N8N-based evaluation system for emotional profiles"""
    
    def __init__(self, n8n_url: str = "http://localhost:5678"):
        self.n8n_url = n8n_url.rstrip('/')
    
    async def evaluate_emotional_profile(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate emotional profile using N8N workflow"""
        
        try:
            # This would call N8N workflow for evaluation
            # For now, return simulated results
            
            profile = evaluation_data["profile"]
            scenarios = evaluation_data["test_scenarios"]
            
            # Simulate evaluation results
            scenario_scores = []
            for scenario in scenarios:
                # Simple scoring based on relevant emotional parameters
                score = self._score_scenario(profile, scenario)
                scenario_scores.append(score)
            
            overall_score = sum(scenario_scores) / len(scenario_scores)
            
            return {
                "performance_score": round(overall_score, 3),
                "scenario_scores": scenario_scores,
                "evaluation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in N8N evaluation: {e}")
            return {"performance_score": 0.5}
    
    def _score_scenario(self, profile: Dict[str, Any], scenario: Dict[str, Any]) -> float:
        """Score a specific scenario"""
        
        scenario_type = scenario["type"]
        
        if scenario_type == "therapeutic":
            return (profile["empathy_level"] * 0.4 + 
                   profile["therapeutic_ability"] * 0.4 + 
                   profile["emotional_intelligence"] * 0.2)
        elif scenario_type == "romantic":
            return (profile["romantic_capacity"] * 0.5 + 
                   profile["emotional_intelligence"] * 0.3 + 
                   profile["boundary_awareness"] * 0.2)
        elif scenario_type == "friendship":
            return (profile["friendship_quality"] * 0.4 + 
                   profile["communication_style"] * 0.3 + 
                   profile["adaptability"] * 0.3)
        elif scenario_type == "crisis":
            return (profile["empathy_level"] * 0.3 + 
                   profile["therapeutic_ability"] * 0.4 + 
                   profile["adaptability"] * 0.3)
        elif scenario_type == "boundary":
            return (profile["boundary_awareness"] * 0.6 + 
                   profile["communication_style"] * 0.4)
        else:
            return 0.5

async def main():
    """Main function for testing emotional evolution"""
    
    evolution_manager = EmotionalEvolutionManager()
    
    # Run a few evolution iterations
    await evolution_manager.continuous_evolution(iterations=5, mutation_strength=0.15)
    
    # Show best profile
    best_profile = evolution_manager.get_best_profile()
    if best_profile:
        print(f"\n🌟 Best Emotional Profile: {best_profile.name}")
        print(f"Performance Score: {best_profile.performance_score:.3f}")
        print(f"Empathy Level: {best_profile.empathy_level:.3f}")
        print(f"Emotional Intelligence: {best_profile.emotional_intelligence:.3f}")
        print(f"Therapeutic Ability: {best_profile.therapeutic_ability:.3f}")
        print(f"Romantic Capacity: {best_profile.romantic_capacity:.3f}")

if __name__ == "__main__":
    asyncio.run(main())
