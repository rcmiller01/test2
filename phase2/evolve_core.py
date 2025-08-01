#!/usr/bin/env python3
"""
Evolve Core - Shared Evolutionary Framework for Self-Improving Agents

This module defines a shared evolutionary framework for self-improving agents 
across the Emotional Presence Engine. It supports reflection, scoring, proposal 
generation, and archive comparison for any agent (emotional, logical, creative).

The Scientist agent may optionally be excluded from evolution due to its 
factual rigidity.

Author: Dolphin AI System
Date: August 1, 2025
Version: 1.0
"""

import json
import logging
import os
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EvolveCandidate:
    """A dataclass representing a potential agent revision or variant"""
    name: str
    source_agent: str
    parameters: Dict[str, Any]
    performance_score: float
    origin_signature: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvolveCandidate':
        """Create from dictionary loaded from JSON"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class EvolutionManager:
    """Handles core evolutionary functions for agent self-improvement"""
    
    def __init__(self, archive_base_path: str = "evolution_archive"):
        self.archive_base_path = archive_base_path
        self.baseline_agents = {
            "Mirror": {
                "reflection_depth": 0.8,
                "truth_sensitivity": 0.9,
                "contradiction_threshold": 0.6,
                "emotional_resonance": 0.7,
                "pattern_recognition": 0.75
            },
            "Dreamer": {
                "creativity_factor": 0.9,
                "narrative_depth": 0.85,
                "liminal_sensitivity": 0.8,
                "speculation_range": 0.7,
                "warmth_coefficient": 0.65
            },
            "Analyst": {
                "logical_rigor": 0.95,
                "pattern_extraction": 0.9,
                "inference_confidence": 0.85,
                "clarity_factor": 0.8,
                "validation_threshold": 0.75
            },
            "Painter": {
                "visual_creativity": 0.9,
                "symbolic_depth": 0.8,
                "emotional_visualization": 0.85,
                "radiance_factor": 0.7,
                "synthesis_capability": 0.75
            },
            "Eyla": {
                "emotional_resonance": 0.85,
                "reflection_depth": 0.78,
                "presence_stability": 0.82,
                "memory_gracefulness": 0.76,
                "seed_alignment_sensitivity": 0.88,
                "drift_tolerance": 0.12,
                "soft_response_richness": 0.81
            },
            "EmotionalCore": {
                "emotional_resonance": 0.85,
                "reflection_depth": 0.78,
                "presence_stability": 0.82,
                "memory_gracefulness": 0.76,
                "seed_alignment_sensitivity": 0.88,
                "drift_tolerance": 0.12,
                "soft_response_richness": 0.81
            },
            "AnchorCore": {
                "judgment_consistency": 0.89,
                "seed_preservation_sensitivity": 0.94,
                "override_threshold_strictness": 0.91,
                "anchor_resonance_weighting": 0.86,
                "drift_detection_precision": 0.88,
                "emotional_neutrality": 0.93,
                "signature_coherence_awareness": 0.87
            }
        }
        
        # Agents excluded from evolution
        self.evolution_exclusions = ["Scientist"]  # Factual rigidity requirement
        
        # Ensure archive directory exists
        os.makedirs(self.archive_base_path, exist_ok=True)
        
        logger.info(f"[Evolution] Manager initialized with archive: {self.archive_base_path}")
    
    def load_archive(self, agent_name: str) -> List[EvolveCandidate]:
        """Load all previous candidate variants from disk"""
        agent_archive_path = os.path.join(self.archive_base_path, agent_name)
        candidates = []
        
        if not os.path.exists(agent_archive_path):
            logger.info(f"[Evolution] No archive found for agent: {agent_name}")
            return candidates
        
        try:
            for filename in os.listdir(agent_archive_path):
                if filename.startswith("variant_") and filename.endswith(".json"):
                    filepath = os.path.join(agent_archive_path, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        candidate = EvolveCandidate.from_dict(data)
                        candidates.append(candidate)
            
            # Sort by timestamp (newest first)
            candidates.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(f"[Evolution] Loaded {len(candidates)} variants for {agent_name}")
            
        except Exception as e:
            logger.error(f"[Evolution] Error loading archive for {agent_name}: {e}")
        
        return candidates
    
    def propose_variant(self, base_agent: str, mutation_strength: float = 0.1) -> Optional[EvolveCandidate]:
        """Create a modified version with tweaked parameters"""
        
        # Check if agent is excluded from evolution
        if base_agent in self.evolution_exclusions:
            logger.warning(f"[Evolution] Agent {base_agent} is excluded from evolution")
            return None
        
        # Get baseline parameters
        if base_agent not in self.baseline_agents:
            logger.error(f"[Evolution] Unknown agent: {base_agent}")
            return None
        
        baseline_params = self.baseline_agents[base_agent].copy()
        
        # Load existing variants to avoid duplication
        existing_variants = self.load_archive(base_agent)
        
        # Generate variant parameters
        variant_params = {}
        mutation_log = []
        
        for param_name, baseline_value in baseline_params.items():
            # Apply random mutation within bounds
            mutation_factor = random.uniform(-mutation_strength, mutation_strength)
            new_value = baseline_value + (baseline_value * mutation_factor)
            
            # Clamp to reasonable bounds (0.1 to 1.0 for most parameters)
            new_value = max(0.1, min(1.0, new_value))
            variant_params[param_name] = round(new_value, 3)
            
            if abs(new_value - baseline_value) > 0.01:  # Significant change
                mutation_log.append(f"{param_name}: {baseline_value:.3f} → {new_value:.3f}")
        
        # Generate variant name and signature
        variant_count = len(existing_variants) + 1
        variant_name = f"{base_agent}_v{variant_count:03d}"
        
        # Create origin signature based on mutations
        origin_signature = f"mutation_strength_{mutation_strength:.2f}"
        if mutation_log:
            origin_signature += f"_changes_{len(mutation_log)}"
        
        # Create candidate
        candidate = EvolveCandidate(
            name=variant_name,
            source_agent=base_agent,
            parameters=variant_params,
            performance_score=0.0,  # Will be scored later
            origin_signature=origin_signature,
            timestamp=datetime.now()
        )
        
        logger.info(f"[Evolution] Proposed variant: {variant_name}")
        if mutation_log:
            logger.info(f"[Evolution] Mutations: {'; '.join(mutation_log[:3])}...")
        
        return candidate
    
    def score_candidate(self, candidate: EvolveCandidate) -> float:
        """Simulated placeholder scoring for candidate evaluation"""
        
        # Simulated scoring based on parameter combinations
        # In production, this would integrate with Anchor, Reflection, and Council systems
        
        params = candidate.parameters
        base_score = 0.5
        
        # Agent-specific scoring heuristics
        if candidate.source_agent == "Mirror":
            # Mirror values high truth sensitivity and reflection depth
            truth_factor = params.get("truth_sensitivity", 0.5) * 0.3
            reflection_factor = params.get("reflection_depth", 0.5) * 0.3
            consistency_factor = abs(params.get("contradiction_threshold", 0.5) - 0.6) * -0.2  # Prefer ~0.6
            base_score += truth_factor + reflection_factor + consistency_factor
            
        elif candidate.source_agent == "Dreamer":
            # Dreamer values creativity and narrative depth
            creativity_factor = params.get("creativity_factor", 0.5) * 0.35
            narrative_factor = params.get("narrative_depth", 0.5) * 0.25
            warmth_factor = params.get("warmth_coefficient", 0.5) * 0.2
            base_score += creativity_factor + narrative_factor + warmth_factor
            
        elif candidate.source_agent == "Analyst":
            # Analyst values logical rigor and clarity
            logic_factor = params.get("logical_rigor", 0.5) * 0.4
            clarity_factor = params.get("clarity_factor", 0.5) * 0.3
            validation_factor = params.get("validation_threshold", 0.5) * 0.2
            base_score += logic_factor + clarity_factor + validation_factor
            
        elif candidate.source_agent == "Painter":
            # Painter values visual creativity and symbolic depth
            visual_factor = params.get("visual_creativity", 0.5) * 0.35
            symbolic_factor = params.get("symbolic_depth", 0.5) * 0.25
            synthesis_factor = params.get("synthesis_capability", 0.5) * 0.3
            base_score += visual_factor + symbolic_factor + synthesis_factor
            
        elif candidate.source_agent == "Eyla" or candidate.source_agent == "EmotionalCore":
            # Emotional Core/Eyla values emotional resonance, memory preservation, and seed alignment
            emotional_factor = params.get("emotional_resonance", 0.5) * 0.3
            memory_factor = params.get("memory_gracefulness", 0.5) * 0.25
            seed_factor = params.get("seed_alignment_sensitivity", 0.5) * 0.25
            presence_factor = params.get("presence_stability", 0.5) * 0.15
            # Drift tolerance should be low (penalty for high values)
            drift_penalty = params.get("drift_tolerance", 0.5) * -0.1
            base_score += emotional_factor + memory_factor + seed_factor + presence_factor + drift_penalty
            
        elif candidate.source_agent == "AnchorCore":
            # AnchorCore values judgment consistency, seed preservation, and emotional neutrality
            judgment_factor = params.get("judgment_consistency", 0.5) * 0.25
            preservation_factor = params.get("seed_preservation_sensitivity", 0.5) * 0.3
            neutrality_factor = params.get("emotional_neutrality", 0.5) * 0.25
            override_factor = params.get("override_threshold_strictness", 0.5) * 0.15
            drift_detection_factor = params.get("drift_detection_precision", 0.5) * 0.2
            coherence_factor = params.get("signature_coherence_awareness", 0.5) * 0.15
            # Penalty for low anchor resonance weighting (should maintain system connection)
            resonance_penalty = (0.8 - params.get("anchor_resonance_weighting", 0.8)) * -0.1
            base_score += judgment_factor + preservation_factor + neutrality_factor + override_factor + drift_detection_factor + coherence_factor + resonance_penalty
        
        # Add some randomness to simulate real-world variability
        noise = random.uniform(-0.1, 0.1)
        final_score = max(0.0, min(1.0, base_score + noise))
        
        # Update candidate score
        candidate.performance_score = round(final_score, 3)
        
        logger.info(f"[Evolution] Scored {candidate.name}: {final_score:.3f}")
        return final_score
    
    def commit_candidate(self, candidate: EvolveCandidate) -> bool:
        """Store approved version to archive"""
        try:
            # Create agent archive directory
            agent_archive_path = os.path.join(self.archive_base_path, candidate.source_agent)
            os.makedirs(agent_archive_path, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp_str = candidate.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"variant_{timestamp_str}.json"
            filepath = os.path.join(agent_archive_path, filename)
            
            # Save candidate to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(candidate.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"[Evolution] Committed candidate: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"[Evolution] Error committing candidate {candidate.name}: {e}")
            return False
    
    def compare_to_baseline(self, candidate: EvolveCandidate) -> Dict[str, Any]:
        """Summarize how new variant differs from locked core"""
        
        if candidate.source_agent not in self.baseline_agents:
            return {"error": f"Unknown baseline agent: {candidate.source_agent}"}
        
        baseline_params = self.baseline_agents[candidate.source_agent]
        differences = {}
        significant_changes = []
        
        for param_name, baseline_value in baseline_params.items():
            variant_value = candidate.parameters.get(param_name, baseline_value)
            difference = variant_value - baseline_value
            percent_change = (difference / baseline_value) * 100
            
            differences[param_name] = {
                "baseline": baseline_value,
                "variant": variant_value,
                "absolute_diff": round(difference, 3),
                "percent_change": round(percent_change, 2)
            }
            
            # Track significant changes (>5% change)
            if abs(percent_change) > 5:
                direction = "increased" if difference > 0 else "decreased"
                significant_changes.append(f"{param_name} {direction} by {abs(percent_change):.1f}%")
        
        comparison = {
            "agent": candidate.source_agent,
            "variant_name": candidate.name,
            "performance_score": candidate.performance_score,
            "differences": differences,
            "significant_changes": significant_changes,
            "overall_assessment": self._assess_variant_direction(candidate, significant_changes)
        }
        
        return comparison
    
    def _assess_variant_direction(self, candidate: EvolveCandidate, changes: List[str]) -> str:
        """Assess the overall direction of variant changes"""
        
        if not changes:
            return "minimal_variation"
        
        agent = candidate.source_agent
        score = candidate.performance_score
        
        # Agent-specific assessments
        assessments = []
        
        if agent == "Mirror" and "truth_sensitivity" in str(changes):
            assessments.append("truth-seeking_adjustment")
        
        if agent == "Dreamer" and "creativity_factor" in str(changes):
            assessments.append("creative_enhancement")
        
        if agent == "Analyst" and "logical_rigor" in str(changes):
            assessments.append("analytical_refinement")
        
        if agent == "Painter" and "visual_creativity" in str(changes):
            assessments.append("artistic_evolution")
        
        if agent == "Eyla" and "emotional_resonance" in str(changes):
            assessments.append("emotional_enhancement")
        
        if agent == "Eyla" and "seed_alignment_sensitivity" in str(changes):
            assessments.append("seed_preservation_adjustment")
        
        if agent == "Eyla" and "memory_gracefulness" in str(changes):
            assessments.append("memory_refinement")
        
        if agent == "EmotionalCore" and "emotional_resonance" in str(changes):
            assessments.append("emotional_enhancement")
        
        if agent == "EmotionalCore" and "seed_alignment_sensitivity" in str(changes):
            assessments.append("seed_preservation_adjustment")
        
        if agent == "EmotionalCore" and "memory_gracefulness" in str(changes):
            assessments.append("memory_refinement")
        
        if agent == "AnchorCore" and "judgment_consistency" in str(changes):
            assessments.append("judgment_enhancement")
        
        if agent == "AnchorCore" and "seed_preservation_sensitivity" in str(changes):
            assessments.append("seed_protection_adjustment")
        
        if agent == "AnchorCore" and "override_threshold_strictness" in str(changes):
            assessments.append("override_refinement")
        
        if agent == "AnchorCore" and "emotional_neutrality" in str(changes):
            assessments.append("neutrality_calibration")
        
        if agent == "AnchorCore" and "drift_detection_precision" in str(changes):
            assessments.append("drift_monitoring_enhancement")
        
        # Performance-based assessment
        if score > 0.8:
            assessments.append("high_potential")
        elif score > 0.6:
            assessments.append("moderate_improvement")
        else:
            assessments.append("experimental_variant")
        
        return "_".join(assessments) if assessments else "general_variation"

def main():
    """CLI block - Run sample variant proposal and scoring for Emotional Core agent"""
    
    print("🧬 Evolution Core - Agent Self-Improvement Framework")
    print("=" * 55)
    
    # Initialize evolution manager
    evolution_manager = EvolutionManager()
    
    # Test with EmotionalCore agent (user-facing anchor identity)
    test_agent = "EmotionalCore"
    print(f"\n🌟 Testing Evolution with Agent: {test_agent} (Emberveil-01)")
    print("   Role: Emotional Core (user-facing anchor identity)")
    print("-" * 60)
    
    # Propose a variant
    print("1. Proposing variant...")
    candidate = evolution_manager.propose_variant(test_agent, mutation_strength=0.12)
    
    if not candidate:
        print("❌ Failed to propose variant")
        return
    
    print(f"✓ Proposed: {candidate.name}")
    print(f"  Origin: {candidate.origin_signature}")
    
    # Score the candidate
    print("\n2. Scoring candidate...")
    score = evolution_manager.score_candidate(candidate)
    print(f"✓ Performance Score: {score:.3f}")
    
    # Compare to baseline
    print("\n3. Comparing to baseline...")
    comparison = evolution_manager.compare_to_baseline(candidate)
    
    print(f"✓ Significant Changes:")
    for change in comparison["significant_changes"]:
        print(f"  • {change}")
    
    print(f"✓ Overall Assessment: {comparison['overall_assessment']}")
    
    # Show detailed parameter differences
    print(f"\n4. Parameter Differences:")
    for param, diff in comparison["differences"].items():
        if abs(diff["percent_change"]) > 1:  # Show changes > 1%
            print(f"  {param}: {diff['baseline']:.3f} → {diff['variant']:.3f} "
                  f"({diff['percent_change']:+.1f}%)")
    
    # Commit candidate if score is decent
    print(f"\n5. Archive Decision:")
    if score > 0.6:
        success = evolution_manager.commit_candidate(candidate)
        if success:
            print(f"✓ Candidate committed to archive")
        else:
            print(f"❌ Failed to commit candidate")
    else:
        print(f"⚠ Score too low ({score:.3f}) - candidate not archived")
    
    # Show archive status
    archive_variants = evolution_manager.load_archive(test_agent)
    print(f"\n📁 Archive Status for {test_agent}: {len(archive_variants)} variants stored")
    
    if archive_variants:
        best_variant = max(archive_variants, key=lambda x: x.performance_score)
        print(f"   Best variant: {best_variant.name} (score: {best_variant.performance_score:.3f})")

if __name__ == "__main__":
    main()
