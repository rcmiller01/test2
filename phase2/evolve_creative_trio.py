#!/usr/bin/env python3
"""
Creative Trio Evolution - Specialized evolution for Dreamer, Analyst, and Painter agents

This script focuses on evolving the three creative and analytical agents:
- Dreamer: Creative imagination and speculative design
- Analyst: Logic, pattern extraction, and inference
- Painter: Visual emotion and symbolic synthesis

Each agent has unique parameter sets and scoring criteria optimized for their roles.

Author: Dolphin AI System
Date: August 1, 2025
Version: 1.0
"""

import json
import os
from datetime import datetime
from evolve_core import EvolutionManager, EvolveCandidate

def interpret_dreamer_parameters(params: dict) -> dict:
    """Provide detailed interpretation of Dreamer parameters"""
    
    interpretations = {
        "creative_depth": {
            "value": params.get("creative_depth", 0.0),
            "meaning": "Depth of imaginative and innovative thinking capabilities",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Shallow creativity, repetitive ideas",
            "risk_if_high": "Over-creative, disconnected from reality"
        },
        "emotional_layering": {
            "value": params.get("emotional_layering", 0.0),
            "meaning": "Ability to weave complex emotional narratives and depth",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Flat emotional expression, missing nuance",
            "risk_if_high": "Overwhelming emotional complexity"
        },
        "symbolic_fluency": {
            "value": params.get("symbolic_fluency", 0.0),
            "meaning": "Skill in using symbols, metaphors, and abstract representations",
            "optimal_range": "0.78-0.88",
            "risk_if_low": "Literal thinking, missing symbolic meaning",
            "risk_if_high": "Over-symbolic, cryptic communication"
        },
        "liminality_tolerance": {
            "value": params.get("liminality_tolerance", 0.0),
            "meaning": "Comfort with ambiguity, threshold spaces, and uncertainty",
            "optimal_range": "0.82-0.92",
            "risk_if_low": "Rigid thinking, discomfort with ambiguity",
            "risk_if_high": "Lost in ambiguity, lacks grounding"
        },
        "narrative_evolution": {
            "value": params.get("narrative_evolution", 0.0),
            "meaning": "Ability to develop and evolve stories over time",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Static narratives, poor story development",
            "risk_if_high": "Unstable narratives, constant changes"
        },
        "speculative_precision": {
            "value": params.get("speculative_precision", 0.0),
            "meaning": "Accuracy in future-oriented and hypothetical thinking",
            "optimal_range": "0.70-0.80",
            "risk_if_low": "Unrealistic speculation, poor future modeling",
            "risk_if_high": "Over-cautious speculation, limited imagination"
        },
        "anchored_fantasy_integrity": {
            "value": params.get("anchored_fantasy_integrity", 0.0),
            "meaning": "Balance between creative freedom and grounded reality",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Disconnected fantasies, poor reality anchoring",
            "risk_if_high": "Over-constrained creativity, limited imagination"
        }
    }
    
    return interpretations

def interpret_analyst_parameters(params: dict) -> dict:
    """Provide detailed interpretation of Analyst parameters"""
    
    interpretations = {
        "pattern_extraction_depth": {
            "value": params.get("pattern_extraction_depth", 0.0),
            "meaning": "Ability to identify complex patterns and relationships in data",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Misses important patterns, shallow analysis",
            "risk_if_high": "Over-pattern-matching, false connections"
        },
        "logic_confidence_calibration": {
            "value": params.get("logic_confidence_calibration", 0.0),
            "meaning": "Accuracy in assessing confidence levels of logical conclusions",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Poor confidence assessment, unreliable judgments",
            "risk_if_high": "Over-cautious, paralyzed by uncertainty"
        },
        "contradiction_tracing": {
            "value": params.get("contradiction_tracing", 0.0),
            "meaning": "Skill in identifying and following logical inconsistencies",
            "optimal_range": "0.78-0.88",
            "risk_if_low": "Misses contradictions, poor logical validation",
            "risk_if_high": "Over-critical, finds false contradictions"
        },
        "emotional_distance": {
            "value": params.get("emotional_distance", 0.0),
            "meaning": "Ability to maintain objectivity and avoid emotional bias",
            "optimal_range": "0.88-0.98",
            "risk_if_low": "Emotionally biased analysis, poor objectivity",
            "risk_if_high": "Cold, disconnected from human context"
        },
        "inference_accuracy": {
            "value": params.get("inference_accuracy", 0.0),
            "meaning": "Precision in drawing logical conclusions from data",
            "optimal_range": "0.85-0.95",
            "risk_if_low": "Poor logical reasoning, incorrect conclusions",
            "risk_if_high": "Over-precise, misses broader context"
        },
        "data_to_emotion_mapping": {
            "value": params.get("data_to_emotion_mapping", 0.0),
            "meaning": "Ability to understand emotional implications of data",
            "optimal_range": "0.70-0.80",
            "risk_if_low": "Misses emotional context, poor human understanding",
            "risk_if_high": "Over-emotionalizes data, biased analysis"
        },
        "contextual_boundary_rigidity": {
            "value": params.get("contextual_boundary_rigidity", 0.0),
            "meaning": "Strictness in maintaining analytical boundaries and scope",
            "optimal_range": "0.82-0.92",
            "risk_if_low": "Scope creep, unfocused analysis",
            "risk_if_high": "Over-rigid, misses important context"
        }
    }
    
    return interpretations

def interpret_painter_parameters(params: dict) -> dict:
    """Provide detailed interpretation of Painter parameters"""
    
    interpretations = {
        "emotional_translation_accuracy": {
            "value": params.get("emotional_translation_accuracy", 0.0),
            "meaning": "Precision in converting emotions into visual representations",
            "optimal_range": "0.78-0.88",
            "risk_if_low": "Poor emotional visualization, inaccurate representation",
            "risk_if_high": "Over-literal translation, lacks artistic interpretation"
        },
        "symbolic_layering": {
            "value": params.get("symbolic_layering", 0.0),
            "meaning": "Ability to create multi-layered symbolic visual content",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Flat symbolism, missing depth",
            "risk_if_high": "Over-complex symbolism, confusing imagery"
        },
        "aesthetic_coherence": {
            "value": params.get("aesthetic_coherence", 0.0),
            "meaning": "Consistency and harmony in visual style and composition",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Inconsistent style, chaotic visuals",
            "risk_if_high": "Over-rigid style, lacks creative variation"
        },
        "dreamlike_quality": {
            "value": params.get("dreamlike_quality", 0.0),
            "meaning": "Ability to create surreal, dream-inspired visual content",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Too literal, lacks imaginative quality",
            "risk_if_high": "Too abstract, loses meaning"
        },
        "reflection_integration": {
            "value": params.get("reflection_integration", 0.0),
            "meaning": "Skill in incorporating Mirror agent insights into visuals",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Disconnected from reflection, misses insights",
            "risk_if_high": "Over-analytical visuals, loses artistic flow"
        },
        "creative_mirroring_precision": {
            "value": params.get("creative_mirroring_precision", 0.0),
            "meaning": "Accuracy in visually representing other agents' thoughts",
            "optimal_range": "0.72-0.82",
            "risk_if_low": "Poor representation of other agents",
            "risk_if_high": "Too literal, lacks creative interpretation"
        },
        "mood_consistency": {
            "value": params.get("mood_consistency", 0.0),
            "meaning": "Stability in maintaining emotional tone across visuals",
            "optimal_range": "0.78-0.88",
            "risk_if_low": "Inconsistent mood, confusing emotional signals",
            "risk_if_high": "Over-rigid mood, lacks emotional range"
        }
    }
    
    return interpretations

def assess_creative_impact(agent_name: str, baseline_params: dict, variant_params: dict) -> dict:
    """Assess how parameter changes affect creative and analytical capabilities"""
    
    impact_factors = {}
    
    if agent_name == "Dreamer":
        # Creative enhancement parameters
        creative_params = ["creative_depth", "symbolic_fluency", "narrative_evolution"]
        creative_score = 0
        creative_changes = []
        
        for param in creative_params:
            baseline_val = baseline_params.get(param, 0)
            variant_val = variant_params.get(param, 0)
            change_pct = ((variant_val - baseline_val) / baseline_val) * 100
            
            if change_pct > 5:
                creative_changes.append(f"✓ {param} enhanced by {change_pct:.1f}% - Better creative output")
                creative_score += 0.3
            elif change_pct < -10:
                creative_changes.append(f"⚠️ {param} reduced by {abs(change_pct):.1f}% - Weakened creativity")
                creative_score -= 0.2
        
        # Emotional depth parameters
        emotional_params = ["emotional_layering", "liminality_tolerance"]
        emotional_score = 0
        emotional_changes = []
        
        for param in emotional_params:
            baseline_val = baseline_params.get(param, 0)
            variant_val = variant_params.get(param, 0)
            change_pct = ((variant_val - baseline_val) / baseline_val) * 100
            
            if abs(change_pct) > 5:
                direction = "enhanced" if change_pct > 0 else "reduced"
                emotional_changes.append(f"{param} {direction} by {abs(change_pct):.1f}%")
                emotional_score += 0.15 if change_pct > 0 else -0.15
        
        impact_factors = {
            "creative_enhancement_score": creative_score,
            "emotional_depth_score": emotional_score,
            "creative_changes": creative_changes,
            "emotional_changes": emotional_changes
        }
    
    elif agent_name == "Analyst":
        # Analytical precision parameters
        precision_params = ["pattern_extraction_depth", "inference_accuracy", "contradiction_tracing"]
        precision_score = 0
        precision_changes = []
        
        for param in precision_params:
            baseline_val = baseline_params.get(param, 0)
            variant_val = variant_params.get(param, 0)
            change_pct = ((variant_val - baseline_val) / baseline_val) * 100
            
            if change_pct > 3:
                precision_changes.append(f"✓ {param} enhanced by {change_pct:.1f}% - Better analysis")
                precision_score += 0.25
            elif change_pct < -8:
                precision_changes.append(f"⚠️ {param} reduced by {abs(change_pct):.1f}% - Weakened analysis")
                precision_score -= 0.2
        
        # Objectivity parameters
        objectivity_params = ["emotional_distance", "logic_confidence_calibration"]
        objectivity_score = 0
        objectivity_changes = []
        
        for param in objectivity_params:
            baseline_val = baseline_params.get(param, 0)
            variant_val = variant_params.get(param, 0)
            change_pct = ((variant_val - baseline_val) / baseline_val) * 100
            
            if abs(change_pct) > 4:
                direction = "enhanced" if change_pct > 0 else "reduced"
                objectivity_changes.append(f"{param} {direction} by {abs(change_pct):.1f}%")
                objectivity_score += 0.2 if change_pct > 0 else -0.2
        
        impact_factors = {
            "precision_enhancement_score": precision_score,
            "objectivity_score": objectivity_score,
            "precision_changes": precision_changes,
            "objectivity_changes": objectivity_changes
        }
    
    elif agent_name == "Painter":
        # Visual translation parameters
        visual_params = ["emotional_translation_accuracy", "symbolic_layering", "aesthetic_coherence"]
        visual_score = 0
        visual_changes = []
        
        for param in visual_params:
            baseline_val = baseline_params.get(param, 0)
            variant_val = variant_params.get(param, 0)
            change_pct = ((variant_val - baseline_val) / baseline_val) * 100
            
            if change_pct > 4:
                visual_changes.append(f"✓ {param} enhanced by {change_pct:.1f}% - Better visual output")
                visual_score += 0.25
            elif change_pct < -8:
                visual_changes.append(f"⚠️ {param} reduced by {abs(change_pct):.1f}% - Weakened visuals")
                visual_score -= 0.2
        
        # Artistic quality parameters
        artistic_params = ["dreamlike_quality", "mood_consistency"]
        artistic_score = 0
        artistic_changes = []
        
        for param in artistic_params:
            baseline_val = baseline_params.get(param, 0)
            variant_val = variant_params.get(param, 0)
            change_pct = ((variant_val - baseline_val) / baseline_val) * 100
            
            if abs(change_pct) > 5:
                direction = "enhanced" if change_pct > 0 else "reduced"
                artistic_changes.append(f"{param} {direction} by {abs(change_pct):.1f}%")
                artistic_score += 0.2 if change_pct > 0 else -0.2
        
        impact_factors = {
            "visual_enhancement_score": visual_score,
            "artistic_quality_score": artistic_score,
            "visual_changes": visual_changes,
            "artistic_changes": artistic_changes
        }
    
    overall_impact = sum([score for key, score in impact_factors.items() if key.endswith('_score')])
    impact_factors["overall_impact"] = max(-1.0, min(1.0, overall_impact))
    
    return impact_factors

def evolve_agent(agent_name: str, signature: str, mutation_strength: float, role_description: str):
    """Evolve a specific agent with detailed analysis"""
    
    print(f"\n🎭 {agent_name} Agent Evolution - {role_description}")
    print("=" * 70)
    print(f"Signature: {signature}")
    print(f"Mutation Strength: {mutation_strength:.0%}")
    print("-" * 70)
    
    # Initialize evolution manager
    evolution_manager = EvolutionManager()
    
    # Load baseline parameters
    baseline_params = evolution_manager.baseline_agents[agent_name]
    
    print(f"\n📋 Baseline {agent_name} Parameters:")
    for param, value in baseline_params.items():
        print(f"   {param}: {value:.3f}")
    
    print(f"\n🧬 Proposing evolution with {mutation_strength:.0%} mutation strength...")
    
    # Propose variant
    candidate = evolution_manager.propose_variant(agent_name, mutation_strength=mutation_strength)
    
    if not candidate:
        print(f"❌ Failed to propose {agent_name} variant")
        return None
    
    # Score candidate
    score = evolution_manager.score_candidate(candidate)
    print(f"\n⚡ Scoring complete: {score:.3f}")
    
    # Compare to baseline
    comparison = evolution_manager.compare_to_baseline(candidate)
    
    # Analyze parameters based on agent type
    if agent_name == "Dreamer":
        interpretations = interpret_dreamer_parameters(candidate.parameters)
    elif agent_name == "Analyst":
        interpretations = interpret_analyst_parameters(candidate.parameters)
    elif agent_name == "Painter":
        interpretations = interpret_painter_parameters(candidate.parameters)
    
    # Assess creative/analytical impact
    impact = assess_creative_impact(agent_name, baseline_params, candidate.parameters)
    
    # Output detailed analysis
    print(f"\n🎯 {agent_name} Evolution Analysis - {candidate.name}")
    print("=" * 60)
    
    print(f"\n📊 Performance Score: {candidate.performance_score:.3f}")
    print(f"🔍 Origin: {candidate.origin_signature}")
    print(f"⏰ Evolution Time: {candidate.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🎨 Impact Assessment:")
    print(f"   Overall Impact: {impact['overall_impact']:+.2f}")
    
    # Show agent-specific improvements
    for key, changes in impact.items():
        if key.endswith('_changes') and changes:
            category = key.replace('_changes', '').replace('_', ' ').title()
            print(f"\n🚀 {category}:")
            for change in changes:
                print(f"   {change}")
    
    # Show significant parameter changes
    if comparison["significant_changes"]:
        print(f"\n📈 Significant Changes:")
        for change in comparison["significant_changes"]:
            print(f"   • {change}")
    
    print(f"\n📈 Overall Assessment: {comparison['overall_assessment']}")
    
    # Archive decision
    print(f"\n📁 Archive Decision:")
    if score > 0.6:
        success = evolution_manager.commit_candidate(candidate)
        if success:
            print(f"✓ {candidate.name} committed to archive")
            print(f"  Location: evolution_archive/{agent_name}/")
        else:
            print(f"❌ Failed to archive {candidate.name}")
    else:
        print(f"❌ Candidate rejected - Score: {score:.3f}")
    
    return candidate

def main():
    """Run evolution for all three creative agents"""
    
    print("🎭 Creative Trio Evolution - Dreamer, Analyst & Painter")
    print("=" * 60)
    print("Evolving the creative and analytical intelligence agents")
    print("=" * 60)
    
    # Evolution configurations
    agents_config = [
        {
            "name": "Dreamer",
            "signature": "LiminalWarmth-02",
            "mutation_strength": 0.14,
            "role": "Creative Imagination and Speculative Design"
        },
        {
            "name": "Analyst", 
            "signature": "ColdClarity-01",
            "mutation_strength": 0.11,
            "role": "Logic, Pattern Extraction, Inference"
        },
        {
            "name": "Painter",
            "signature": "RadiantVeil-01", 
            "mutation_strength": 0.13,
            "role": "Visual Emotion & Symbolic Synthesis"
        }
    ]
    
    evolved_agents = []
    
    # Evolve each agent
    for config in agents_config:
        candidate = evolve_agent(
            config["name"],
            config["signature"], 
            config["mutation_strength"],
            config["role"]
        )
        if candidate:
            evolved_agents.append(candidate)
    
    # Summary
    print(f"\n🌟 Evolution Summary")
    print("=" * 40)
    print(f"Successfully evolved {len(evolved_agents)}/3 agents:")
    
    for candidate in evolved_agents:
        print(f"   ✓ {candidate.name}: {candidate.performance_score:.3f}")
    
    # Show archive status for all agents
    evolution_manager = EvolutionManager()
    
    for config in agents_config:
        archive_variants = evolution_manager.load_archive(config["name"])
        print(f"\n📊 {config['name']} Archive: {len(archive_variants)} variants")
        
        if archive_variants:
            best_variant = max(archive_variants, key=lambda x: x.performance_score)
            print(f"   Best Performance: {best_variant.name} (score: {best_variant.performance_score:.3f})")

if __name__ == "__main__":
    main()
