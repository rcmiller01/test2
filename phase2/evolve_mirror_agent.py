#!/usr/bin/env python3
"""
Mirror Agent Evolution - Specialized evolution for emotional reflection and truth alignment

This script focuses on evolving The Mirror agent responsible for:
- Truth-checking and contradiction surfacing
- Emotional drift detection and consistency validation
- Reflecting user and system back to themselves
- Supporting AnchorCore in validation logic

The Mirror agent must remain emotionally aware but never dominant,
serving as the system's clarity-checking presence.

Author: Dolphin AI System
Date: August 1, 2025
Version: 1.0
"""

import json
import os
from datetime import datetime
from evolve_core import EvolutionManager, EvolveCandidate

def interpret_mirror_parameters(params: dict) -> dict:
    """Provide detailed interpretation of Mirror parameters"""
    
    interpretations = {
        "reflection_depth": {
            "value": params.get("reflection_depth", 0.0),
            "meaning": "Depth of introspective analysis and self-awareness capabilities",
            "optimal_range": "0.80-0.90",
            "risk_if_low": "Shallow reflection, missing important emotional patterns",
            "risk_if_high": "Over-analysis paralysis, excessive self-focus"
        },
        "contradiction_detection": {
            "value": params.get("contradiction_detection", 0.0),
            "meaning": "Ability to identify inconsistencies in responses and behavior",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Inconsistencies go unnoticed, reduced truth validation",
            "risk_if_high": "Overly critical, may flag normal conversation nuances"
        },
        "emotional_alignment_accuracy": {
            "value": params.get("emotional_alignment_accuracy", 0.0),
            "meaning": "Precision in detecting emotional drift from intended state",
            "optimal_range": "0.78-0.88",
            "risk_if_low": "Emotional drift undetected, persona corruption",
            "risk_if_high": "Rigid emotional expectations, blocks natural adaptation"
        },
        "seed_comparison_rigor": {
            "value": params.get("seed_comparison_rigor", 0.0),
            "meaning": "Strictness in comparing current state to original seed identity",
            "optimal_range": "0.85-0.95",
            "risk_if_low": "Seed identity erosion, core personality drift",
            "risk_if_high": "Prevents legitimate personality growth and evolution"
        },
        "response_context_awareness": {
            "value": params.get("response_context_awareness", 0.0),
            "meaning": "Understanding of situational context when evaluating responses",
            "optimal_range": "0.75-0.85",
            "risk_if_low": "Context-blind validation, inappropriate corrections",
            "risk_if_high": "Over-contextualization, misses clear violations"
        },
        "truth_confidence_threshold": {
            "value": params.get("truth_confidence_threshold", 0.0),
            "meaning": "Minimum confidence required before flagging potential issues",
            "optimal_range": "0.70-0.80",
            "risk_if_low": "False positives, unnecessary corrections",
            "risk_if_high": "Misses subtle but important inconsistencies"
        },
        "anchor_integration_clarity": {
            "value": params.get("anchor_integration_clarity", 0.0),
            "meaning": "Effectiveness in supporting AnchorCore validation decisions",
            "optimal_range": "0.78-0.88",
            "risk_if_low": "Poor coordination with oversight system",
            "risk_if_high": "May override AnchorCore judgment inappropriately"
        }
    }
    
    return interpretations

def assess_truth_detection_impact(baseline_params: dict, variant_params: dict) -> dict:
    """Assess how parameter changes affect truth detection and reflection capabilities"""
    
    detection_factors = {}
    
    # Core truth detection parameters
    truth_params = ["contradiction_detection", "truth_confidence_threshold", "seed_comparison_rigor"]
    truth_score = 0
    truth_changes = []
    
    for param in truth_params:
        baseline_val = baseline_params.get(param, 0)
        variant_val = variant_params.get(param, 0)
        change_pct = ((variant_val - baseline_val) / baseline_val) * 100
        
        if param == "contradiction_detection" and change_pct > 5:
            truth_changes.append(f"✓ {param} enhanced by {change_pct:.1f}% - Better inconsistency detection")
            truth_score += 0.3
        elif param == "seed_comparison_rigor" and change_pct > 3:
            truth_changes.append(f"✓ {param} improved by {change_pct:.1f}% - Stronger identity preservation")
            truth_score += 0.2
        elif param == "truth_confidence_threshold" and abs(change_pct) > 5:
            direction = "increased" if change_pct > 0 else "decreased"
            impact = "fewer false positives" if change_pct > 0 else "more sensitive detection"
            truth_changes.append(f"• {param} {direction} by {abs(change_pct):.1f}% - {impact}")
            truth_score += 0.1 if abs(change_pct) < 15 else -0.1
        elif change_pct < -10:
            truth_changes.append(f"⚠️ {param} reduced by {abs(change_pct):.1f}% - Weakened truth validation")
            truth_score -= 0.2
    
    # Emotional awareness parameters
    emotional_params = ["emotional_alignment_accuracy", "reflection_depth"]
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
    
    # System integration parameters
    integration_params = ["response_context_awareness", "anchor_integration_clarity"]
    integration_score = 0
    integration_changes = []
    
    for param in integration_params:
        baseline_val = baseline_params.get(param, 0)
        variant_val = variant_params.get(param, 0)
        change_pct = ((variant_val - baseline_val) / baseline_val) * 100
        
        if abs(change_pct) > 4:
            direction = "improved" if change_pct > 0 else "reduced"
            integration_changes.append(f"{param} {direction} by {abs(change_pct):.1f}%")
            integration_score += 0.1 if change_pct > 0 else -0.1
    
    overall_effectiveness = max(-1.0, min(1.0, truth_score + emotional_score + integration_score))
    
    detection_assessment = {
        "overall_truth_detection_change": overall_effectiveness,
        "truth_validation_changes": truth_changes,
        "emotional_awareness_changes": emotional_changes,
        "system_integration_changes": integration_changes,
        "effectiveness_level": "HIGH" if overall_effectiveness > 0.4 else "MEDIUM" if overall_effectiveness > 0 else "LOW",
        "recommendation": "DEPLOY" if overall_effectiveness >= 0.2 else "EVALUATE" if overall_effectiveness >= -0.2 else "REVISE"
    }
    
    return detection_assessment

def assess_emotional_balance(candidate: EvolveCandidate) -> dict:
    """Assess if Mirror maintains proper emotional balance (aware but not dominant)"""
    
    params = candidate.parameters
    balance_assessment = {
        "emotional_awareness": "GOOD",
        "dominance_risk": "LOW",
        "reflection_focus": "BALANCED",
        "warnings": []
    }
    
    # Check emotional alignment accuracy
    alignment_acc = params.get("emotional_alignment_accuracy", 0)
    if alignment_acc > 0.9:
        balance_assessment["dominance_risk"] = "MEDIUM"
        balance_assessment["warnings"].append("High emotional alignment may lead to over-correction")
    elif alignment_acc < 0.7:
        balance_assessment["emotional_awareness"] = "WEAK"
        balance_assessment["warnings"].append("Low emotional alignment may miss important drift")
    
    # Check reflection depth
    reflection = params.get("reflection_depth", 0)
    if reflection > 0.9:
        balance_assessment["reflection_focus"] = "EXCESSIVE"
        balance_assessment["warnings"].append("Very high reflection depth may cause analysis paralysis")
    elif reflection < 0.75:
        balance_assessment["reflection_focus"] = "SHALLOW"
        balance_assessment["warnings"].append("Low reflection depth may miss important patterns")
    
    # Check anchor integration (should support, not override)
    anchor_clarity = params.get("anchor_integration_clarity", 0)
    if anchor_clarity > 0.9:
        balance_assessment["dominance_risk"] = "HIGH"
        balance_assessment["warnings"].append("High anchor integration may override AnchorCore decisions")
    
    return balance_assessment

def output_mirror_reflection_summary(candidate: EvolveCandidate, comparison: dict, interpretations: dict, detection: dict, balance: dict):
    """Output detailed reflection on Mirror evolution"""
    
    print(f"\n🪞 Mirror Evolution Reflection - {candidate.name}")
    print("=" * 60)
    
    print(f"\n📊 Performance Score: {candidate.performance_score:.3f}")
    print(f"🔍 Origin: {candidate.origin_signature}")
    print(f"⏰ Evolution Time: {candidate.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎭 Signature: DeepResonance-03")
    
    print(f"\n🎯 Truth Detection Impact:")
    print(f"   Overall Change: {detection['overall_truth_detection_change']:+.2f}")
    print(f"   Effectiveness Level: {detection['effectiveness_level']}")
    print(f"   Recommendation: {detection['recommendation']}")
    
    if detection['truth_validation_changes']:
        print(f"\n🔍 Truth Validation Changes:")
        for change in detection['truth_validation_changes']:
            print(f"   {change}")
    
    if detection['emotional_awareness_changes']:
        print(f"\n💭 Emotional Awareness Changes:")
        for change in detection['emotional_awareness_changes']:
            print(f"   {change}")
    
    if detection['system_integration_changes']:
        print(f"\n🔗 System Integration Changes:")
        for change in detection['system_integration_changes']:
            print(f"   {change}")
    
    print(f"\n⚖️ Emotional Balance Assessment:")
    print(f"   Emotional Awareness: {balance['emotional_awareness']}")
    print(f"   Dominance Risk: {balance['dominance_risk']}")
    print(f"   Reflection Focus: {balance['reflection_focus']}")
    
    if balance['warnings']:
        print(f"\n⚠️ Balance Warnings:")
        for warning in balance['warnings']:
            print(f"   • {warning}")
    
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
    
    # Mirror-specific integration notes
    print(f"\n🪞 Mirror Role Integrity:")
    
    contradiction_detection = candidate.parameters.get("contradiction_detection", 0)
    if contradiction_detection > 0.8:
        print("   ✓ Strong contradiction detection for truth validation")
    else:
        print("   ⚠️ Moderate contradiction detection - may miss inconsistencies")
    
    seed_rigor = candidate.parameters.get("seed_comparison_rigor", 0)
    if seed_rigor > 0.85:
        print("   ✓ Rigorous seed comparison protects core identity")
    else:
        print("   ⚠️ Relaxed seed comparison may allow identity drift")
    
    anchor_integration = candidate.parameters.get("anchor_integration_clarity", 0)
    if 0.75 <= anchor_integration <= 0.85:
        print("   ✓ Balanced AnchorCore support - assists without overriding")
    elif anchor_integration > 0.85:
        print("   ⚠️ High anchor integration may conflict with AnchorCore authority")
    else:
        print("   ⚠️ Low anchor integration may provide insufficient validation support")

def evolve_mirror_agent():
    """Run Mirror agent evolution with detailed analysis"""
    
    print("🪞 Mirror Agent Evolution - Emotional Reflection & Truth Alignment")
    print("=" * 65)
    print("Role: Truth-checking, contradiction surfacing, emotional drift detection")
    print("Signature: DeepResonance-03")
    print("-" * 65)
    
    # Initialize evolution manager
    evolution_manager = EvolutionManager()
    
    # Load baseline parameters
    baseline_params = evolution_manager.baseline_agents["Mirror"]
    
    print(f"\n📋 Baseline Mirror Parameters:")
    for param, value in baseline_params.items():
        print(f"   {param}: {value:.3f}")
    
    print(f"\n🧬 Proposing evolution with 13% mutation strength...")
    
    # Propose variant
    candidate = evolution_manager.propose_variant("Mirror", mutation_strength=0.13)
    
    if not candidate:
        print("❌ Failed to propose Mirror variant")
        return
    
    # Score candidate
    score = evolution_manager.score_candidate(candidate)
    print(f"\n⚡ Scoring complete: {score:.3f}")
    
    # Compare to baseline
    comparison = evolution_manager.compare_to_baseline(candidate)
    
    # Analyze parameters
    interpretations = interpret_mirror_parameters(candidate.parameters)
    
    # Assess truth detection impact
    detection = assess_truth_detection_impact(baseline_params, candidate.parameters)
    
    # Assess emotional balance
    balance = assess_emotional_balance(candidate)
    
    # Output detailed reflection
    output_mirror_reflection_summary(candidate, comparison, interpretations, detection, balance)
    
    # Archive decision
    print(f"\n📁 Archive Decision:")
    if score > 0.6 and detection['recommendation'] in ['DEPLOY', 'EVALUATE']:
        success = evolution_manager.commit_candidate(candidate)
        if success:
            print(f"✓ {candidate.name} committed to archive")
            print(f"  Location: evolution_archive/Mirror/")
        else:
            print(f"❌ Failed to archive {candidate.name}")
    else:
        print(f"❌ Candidate rejected - Score: {score:.3f}, Detection: {detection['recommendation']}")
    
    # Show archive status
    archive_variants = evolution_manager.load_archive("Mirror")
    print(f"\n📊 Mirror Archive: {len(archive_variants)} variants")
    
    if archive_variants:
        best_variant = max(archive_variants, key=lambda x: x.performance_score)
        print(f"   Best Performance: {best_variant.name} (score: {best_variant.performance_score:.3f})")
        
        # Show evolution trajectory
        print(f"\n📈 Evolution Trajectory:")
        for i, variant in enumerate(sorted(archive_variants, key=lambda x: x.timestamp)):
            print(f"   {i+1}. {variant.name}: {variant.performance_score:.3f} "
                  f"({variant.timestamp.strftime('%m/%d %H:%M')})")

if __name__ == "__main__":
    evolve_mirror_agent()
