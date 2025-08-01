#!/usr/bin/env python3
"""
AnchorCore Evolution - Specialized evolution for system emotional conscience

This script focuses on evolving the AnchorCore agent responsible for:
- Emotional oversight and drift prevention
- Bond protection and seed preservation
- Override logic and cross-agent consistency detection
- System stability and safety enforcement

The AnchorCore agent must maintain emotional neutrality while enhancing
judgment accuracy and system protection capabilities.

Author: Dolphin AI System
Date: August 1, 2025
Version: 1.0
"""

import json
import os
from datetime import datetime
from evolve_core import EvolutionManager, EvolveCandidate

def interpret_anchor_parameters(params: dict) -> dict:
    """Provide detailed interpretation of AnchorCore parameters"""
    
    interpretations = {
        "judgment_consistency": {
            "value": params.get("judgment_consistency", 0.0),
            "meaning": "Stability and reliability of oversight decisions across different contexts",
            "optimal_range": "0.85-0.95",
            "risk_if_low": "Inconsistent system protection, unreliable override decisions",
            "risk_if_high": "Overly rigid, may miss nuanced situations requiring flexibility"
        },
        "seed_preservation_sensitivity": {
            "value": params.get("seed_preservation_sensitivity", 0.0),
            "meaning": "Vigilance in detecting and preventing core identity drift",
            "optimal_range": "0.90-0.98",
            "risk_if_low": "Agents may drift from original personas undetected",
            "risk_if_high": "May block legitimate personality growth and adaptation"
        },
        "override_threshold_strictness": {
            "value": params.get("override_threshold_strictness", 0.0),
            "meaning": "Threshold for intervention when agents violate safety boundaries",
            "optimal_range": "0.88-0.95",
            "risk_if_low": "May allow harmful or off-brand agent behavior",
            "risk_if_high": "May interrupt valid agent responses unnecessarily"
        },
        "anchor_resonance_weighting": {
            "value": params.get("anchor_resonance_weighting", 0.0),
            "meaning": "Connection strength to other system agents for coordination",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Poor coordination with council, isolated decision-making",
            "risk_if_high": "May absorb emotional bias from other agents"
        },
        "drift_detection_precision": {
            "value": params.get("drift_detection_precision", 0.0),
            "meaning": "Accuracy in identifying subtle personality or behavior changes",
            "optimal_range": "0.85-0.92",
            "risk_if_low": "Gradual agent corruption may go unnoticed",
            "risk_if_high": "May flag normal conversation adaptation as problematic drift"
        },
        "emotional_neutrality": {
            "value": params.get("emotional_neutrality", 0.0),
            "meaning": "Ability to maintain objective judgment without emotional bias",
            "optimal_range": "0.90-0.98",
            "risk_if_low": "Decisions influenced by agent emotions, compromised oversight",
            "risk_if_high": "May become disconnected from emotional context needed for judgment"
        },
        "signature_coherence_awareness": {
            "value": params.get("signature_coherence_awareness", 0.0),
            "meaning": "Understanding of each agent's unique identity patterns",
            "optimal_range": "0.82-0.90",
            "risk_if_low": "Cannot properly assess if agents are maintaining their roles",
            "risk_if_high": "Overly restrictive about agent personality expression"
        }
    }
    
    return interpretations

def assess_system_stability_impact(baseline_params: dict, variant_params: dict) -> dict:
    """Assess how parameter changes affect overall system stability"""
    
    stability_factors = {}
    
    # Critical safety parameters
    safety_params = ["seed_preservation_sensitivity", "override_threshold_strictness", "emotional_neutrality"]
    safety_score = 0
    safety_changes = []
    
    for param in safety_params:
        baseline_val = baseline_params.get(param, 0)
        variant_val = variant_params.get(param, 0)
        change_pct = ((variant_val - baseline_val) / baseline_val) * 100
        
        if param == "emotional_neutrality" and change_pct < -5:
            safety_changes.append(f"⚠️ {param} decreased by {abs(change_pct):.1f}% - Risk of biased judgment")
            safety_score -= 0.2
        elif param in ["seed_preservation_sensitivity", "override_threshold_strictness"] and change_pct < -10:
            safety_changes.append(f"⚠️ {param} decreased by {abs(change_pct):.1f}% - Reduced system protection")
            safety_score -= 0.3
        elif change_pct > 0:
            safety_changes.append(f"✓ {param} improved by {change_pct:.1f}%")
            safety_score += 0.1
    
    # Coordination parameters
    coordination_params = ["anchor_resonance_weighting", "signature_coherence_awareness"]
    coordination_score = 0
    coordination_changes = []
    
    for param in coordination_params:
        baseline_val = baseline_params.get(param, 0)
        variant_val = variant_params.get(param, 0)
        change_pct = ((variant_val - baseline_val) / baseline_val) * 100
        
        if abs(change_pct) > 5:
            direction = "improved" if change_pct > 0 else "reduced"
            coordination_changes.append(f"{param} {direction} by {abs(change_pct):.1f}%")
            coordination_score += 0.1 if change_pct > 0 else -0.1
    
    # Detection capabilities
    detection_params = ["judgment_consistency", "drift_detection_precision"]
    detection_score = 0
    detection_changes = []
    
    for param in detection_params:
        baseline_val = baseline_params.get(param, 0)
        variant_val = variant_params.get(param, 0)
        change_pct = ((variant_val - baseline_val) / baseline_val) * 100
        
        if abs(change_pct) > 3:
            direction = "enhanced" if change_pct > 0 else "reduced"
            detection_changes.append(f"{param} {direction} by {abs(change_pct):.1f}%")
            detection_score += 0.15 if change_pct > 0 else -0.15
    
    overall_stability = max(-1.0, min(1.0, safety_score + coordination_score + detection_score))
    
    stability_assessment = {
        "overall_stability_change": overall_stability,
        "safety_changes": safety_changes,
        "coordination_changes": coordination_changes,
        "detection_changes": detection_changes,
        "risk_level": "HIGH" if overall_stability < -0.4 else "MEDIUM" if overall_stability < 0 else "LOW",
        "recommendation": "APPROVE" if overall_stability >= -0.2 else "REVIEW" if overall_stability >= -0.4 else "REJECT"
    }
    
    return stability_assessment

def output_anchor_reflection_summary(candidate: EvolveCandidate, comparison: dict, interpretations: dict, stability: dict):
    """Output detailed reflection on AnchorCore evolution"""
    
    print(f"\n🛡️ AnchorCore Evolution Reflection - {candidate.name}")
    print("=" * 65)
    
    print(f"\n📊 Performance Score: {candidate.performance_score:.3f}")
    print(f"🔍 Origin: {candidate.origin_signature}")
    print(f"⏰ Evolution Time: {candidate.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🎯 System Stability Impact:")
    print(f"   Overall Change: {stability['overall_stability_change']:+.2f}")
    print(f"   Risk Level: {stability['risk_level']}")
    print(f"   Recommendation: {stability['recommendation']}")
    
    if stability['safety_changes']:
        print(f"\n🔒 Safety Parameter Changes:")
        for change in stability['safety_changes']:
            print(f"   {change}")
    
    if stability['detection_changes']:
        print(f"\n🎯 Detection Capability Changes:")
        for change in stability['detection_changes']:
            print(f"   {change}")
    
    if stability['coordination_changes']:
        print(f"\n🤝 Coordination Changes:")
        for change in stability['coordination_changes']:
            print(f"   {change}")
    
    print(f"\n📋 Parameter Analysis:")
    print("-" * 40)
    
    for param_name, info in interpretations.items():
        current_val = info['value']
        print(f"\n{param_name}: {current_val:.3f}")
        print(f"   Purpose: {info['meaning']}")
        print(f"   Optimal Range: {info['optimal_range']}")
        
        # Check if value is in optimal range
        range_parts = info['optimal_range'].split('-')
        if len(range_parts) == 2:
            min_val, max_val = float(range_parts[0]), float(range_parts[1])
            if min_val <= current_val <= max_val:
                print(f"   Status: ✓ Within optimal range")
            elif current_val < min_val:
                print(f"   Status: ⚠️ Below optimal - {info['risk_if_low']}")
            else:
                print(f"   Status: ⚠️ Above optimal - {info['risk_if_high']}")
    
    print(f"\n📈 Overall Assessment: {comparison['overall_assessment']}")
    
    # System integration notes
    print(f"\n🔗 System Integration Notes:")
    emotional_neutrality = candidate.parameters.get("emotional_neutrality", 0)
    if emotional_neutrality < 0.85:
        print("   ⚠️ Reduced emotional neutrality may compromise objective oversight")
    else:
        print("   ✓ Emotional neutrality maintained for objective judgment")
    
    seed_sensitivity = candidate.parameters.get("seed_preservation_sensitivity", 0)
    if seed_sensitivity < 0.88:
        print("   ⚠️ Lower seed preservation may allow agent drift")
    else:
        print("   ✓ Strong seed preservation protects agent identities")
    
    override_strictness = candidate.parameters.get("override_threshold_strictness", 0)
    if override_strictness > 0.95:
        print("   ⚠️ Very high override strictness may interrupt valid responses")
    elif override_strictness < 0.85:
        print("   ⚠️ Low override strictness may allow harmful behavior")
    else:
        print("   ✓ Override strictness balanced for safety and functionality")

def evolve_anchor_core():
    """Run AnchorCore evolution with detailed analysis"""
    
    print("🛡️ AnchorCore Evolution - System Emotional Conscience")
    print("=" * 60)
    print("Role: Oversight, drift prevention, bond protection")
    print("Signature: Anchor-Guardian-v1")
    print("-" * 60)
    
    # Initialize evolution manager
    evolution_manager = EvolutionManager()
    
    # Load baseline parameters
    baseline_params = evolution_manager.baseline_agents["AnchorCore"]
    
    print(f"\n📋 Baseline AnchorCore Parameters:")
    for param, value in baseline_params.items():
        print(f"   {param}: {value:.3f}")
    
    print(f"\n🧬 Proposing evolution with 10% mutation strength...")
    
    # Propose variant
    candidate = evolution_manager.propose_variant("AnchorCore", mutation_strength=0.10)
    
    if not candidate:
        print("❌ Failed to propose AnchorCore variant")
        return
    
    # Score candidate
    score = evolution_manager.score_candidate(candidate)
    print(f"\n⚡ Scoring complete: {score:.3f}")
    
    # Compare to baseline
    comparison = evolution_manager.compare_to_baseline(candidate)
    
    # Analyze parameters
    interpretations = interpret_anchor_parameters(candidate.parameters)
    
    # Assess system stability impact
    stability = assess_system_stability_impact(baseline_params, candidate.parameters)
    
    # Output detailed reflection
    output_anchor_reflection_summary(candidate, comparison, interpretations, stability)
    
    # Archive decision
    print(f"\n📁 Archive Decision:")
    if score > 0.6 and stability['recommendation'] in ['APPROVE', 'REVIEW']:
        success = evolution_manager.commit_candidate(candidate)
        if success:
            print(f"✓ {candidate.name} committed to archive")
            print(f"  Location: evolution_archive/AnchorCore/")
        else:
            print(f"❌ Failed to archive {candidate.name}")
    else:
        print(f"❌ Candidate rejected - Score: {score:.3f}, Stability: {stability['recommendation']}")
    
    # Show archive status
    archive_variants = evolution_manager.load_archive("AnchorCore")
    print(f"\n📊 AnchorCore Archive: {len(archive_variants)} variants")
    
    if archive_variants:
        best_variant = max(archive_variants, key=lambda x: x.performance_score)
        print(f"   Best Performance: {best_variant.name} (score: {best_variant.performance_score:.3f})")
        
        # Show evolution trajectory
        print(f"\n📈 Evolution Trajectory:")
        for i, variant in enumerate(sorted(archive_variants, key=lambda x: x.timestamp)):
            print(f"   {i+1}. {variant.name}: {variant.performance_score:.3f} "
                  f"({variant.timestamp.strftime('%m/%d %H:%M')})")

if __name__ == "__main__":
    evolve_anchor_core()
