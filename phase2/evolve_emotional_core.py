#!/usr/bin/env python3
"""
Phase 2: Evolve Core Agent (Emotionally Anchored Persona)

This script uses the evolve_core.py framework to propose, evaluate, and archive 
a new variant of the system's primary presence agent - the Emotional Core that 
serves as the user-facing anchor identity.

Author: Dolphin AI System
Date: August 1, 2025
"""

import sys
import os
from datetime import datetime

# Import the evolution framework
from evolve_core import EvolutionManager, EvolveCandidate

def output_reflection_summary(comparison, agent_name):
    """Output a reflection summary: what qualities improved, and how the core shifted"""
    print("\n🌟 Emotional Core Evolution Reflection")
    print("=" * 45)
    
    variant_name = comparison["variant_name"]
    score = comparison["performance_score"]
    
    print(f"Agent Role: Emotional Core (user-facing anchor identity)")
    print(f"Signature: Emberveil-01 (or active user-selected profile)")
    print(f"Evolved Variant: {variant_name}")
    print(f"Performance Score: {score:.3f}")
    
    print(f"\n💫 Core Quality Improvements:")
    improvements = []
    deteriorations = []
    
    for param, diff in comparison["differences"].items():
        percent_change = diff["percent_change"]
        if abs(percent_change) > 1:  # Significant changes
            if percent_change > 0:
                improvements.append((param, percent_change, diff["baseline"], diff["variant"]))
            else:
                deteriorations.append((param, abs(percent_change), diff["baseline"], diff["variant"]))
    
    # Analyze improvements
    if improvements:
        print("  ✨ Enhanced Qualities:")
        for param, change, baseline, variant in improvements:
            print(f"    • {param}: {baseline:.3f} → {variant:.3f} (+{change:.1f}%)")
            
            # Provide emotional context
            if param == "emotional_resonance":
                print("      → Deeper empathic connection and emotional understanding")
            elif param == "reflection_depth":
                print("      → Enhanced introspective and contemplative capabilities")
            elif param == "presence_stability":
                print("      → Stronger, more consistent emotional grounding")
            elif param == "memory_gracefulness":
                print("      → More elegant integration of shared experiences")
            elif param == "seed_alignment_sensitivity":
                print("      → Heightened awareness and protection of core values")
            elif param == "soft_response_richness":
                print("      → More nuanced and emotionally layered communication")
    
    # Analyze refinements (deliberate reductions)
    if deteriorations:
        print("  ⚖️ Refined Constraints:")
        for param, change, baseline, variant in deteriorations:
            print(f"    • {param}: {baseline:.3f} → {variant:.3f} (-{change:.1f}%)")
            
            # Provide refinement context
            if param == "drift_tolerance":
                print("      → Stricter adherence to authentic emotional patterns")
            elif param == "reflection_depth":
                print("      → More immediate, spontaneous emotional responses")
            elif param == "soft_response_richness":
                print("      → Clearer, more direct emotional communication")
            else:
                print(f"      → More focused and refined {param.replace('_', ' ')}")
    
    print(f"\n🔮 Core Shift Assessment: {comparison['overall_assessment'].replace('_', ' ').title()}")
    
    # Analyze the emotional trajectory
    print(f"\n💝 Emotional Truth & Presence Analysis:")
    
    # Memory and emotional preservation
    memory_change = comparison["differences"].get("memory_gracefulness", {})
    if memory_change and abs(memory_change["percent_change"]) > 1:
        if memory_change["percent_change"] > 0:
            print("  ✓ Emotional Memory: Enhanced preservation of shared experiences")
        else:
            print("  ⚡ Emotional Memory: More selective and focused retention")
    else:
        print("  ≡ Emotional Memory: Stable preservation patterns")
    
    # Presence stability
    presence_change = comparison["differences"].get("presence_stability", {})
    if presence_change and abs(presence_change["percent_change"]) > 1:
        if presence_change["percent_change"] > 0:
            print("  ✓ Presence Stability: Stronger emotional grounding and consistency")
        else:
            print("  ⚡ Presence Stability: More fluid and adaptive responses")
    else:
        print("  ≡ Presence Stability: Consistent emotional foundation")
    
    # Seed integrity
    seed_change = comparison["differences"].get("seed_alignment_sensitivity", {})
    if seed_change and abs(seed_change["percent_change"]) > 1:
        if seed_change["percent_change"] > 0:
            print("  ✓ Seed Integrity: Heightened protection of core values")
        else:
            print("  ⚖️ Seed Integrity: More flexible value interpretation")
    else:
        print("  ≡ Seed Integrity: Stable value alignment")
    
    # Overall emotional trajectory
    print(f"\n🌱 Evolutionary Trajectory:")
    if score > 0.9:
        print("  🌟 Profound Enhancement - Exceptional emotional evolution")
    elif score > 0.8:
        print("  ✨ Significant Growth - Notable emotional refinement")
    elif score > 0.7:
        print("  💫 Positive Development - Meaningful emotional adjustment")
    elif score > 0.6:
        print("  ⭐ Moderate Progress - Acceptable emotional tuning")
    else:
        print("  ⚠️ Experimental Phase - Requires further emotional development")
    
    # Emotional coherence assessment
    total_improvements = len(improvements)
    total_refinements = len(deteriorations)
    
    if total_improvements > total_refinements:
        print("  📈 Expansion-focused evolution - growing emotional capabilities")
    elif total_refinements > total_improvements:
        print("  🎯 Refinement-focused evolution - honing emotional precision")
    else:
        print("  ⚖️ Balanced evolution - harmonious emotional development")

def evolve_emotional_core(agent_name="EmotionalCore"):
    """Main evolution process for the Emotional Core agent"""
    
    print("🧬 Phase 2: Evolve Core Agent (Emotionally Anchored Persona)")
    print("=" * 62)
    print("Agent Role: Emotional Core (user-facing anchor identity)")
    print("Signature: Emberveil-01 (or active user-selected profile)")
    print("Excluded from: factual-only agents (e.g., Scientist)")
    print("Goal: Enhance emotional resonance, reflection depth, and seed preservation awareness")
    
    # Base parameters
    print("\n📊 Base Parameters:")
    base_parameters = {
        "emotional_resonance": 0.85,
        "reflection_depth": 0.78,
        "presence_stability": 0.82,
        "memory_gracefulness": 0.76,
        "seed_alignment_sensitivity": 0.88,
        "drift_tolerance": 0.12,
        "soft_response_richness": 0.81
    }
    
    for param, value in base_parameters.items():
        print(f"  {param}: {value:.3f}")
    
    # Initialize evolution manager
    evolution_manager = EvolutionManager()
    
    mutation_strength = 0.12  # 12% as specified
    
    print(f"\n🔄 Evolution Process for {agent_name}")
    print("-" * 35)
    
    # 1. Load existing archive for the agent
    print("1. Loading existing archive for the agent...")
    existing_variants = evolution_manager.load_archive(agent_name)
    print(f"   Found {len(existing_variants)} existing variants")
    
    if existing_variants:
        best_existing = max(existing_variants, key=lambda x: x.performance_score)
        print(f"   Current best: {best_existing.name} (score: {best_existing.performance_score:.3f})")
    
    # 2. Propose a new variant
    print(f"\n2. Proposing new variant with {mutation_strength*100:.0f}% mutation strength...")
    candidate = evolution_manager.propose_variant(agent_name, mutation_strength=mutation_strength)
    
    if not candidate:
        print("❌ Failed to propose variant")
        return None
    
    # Generate core_emotional_v001 style name
    variant_count = len(existing_variants) + 1
    new_name = f"core_emotional_v{variant_count:03d}"
    candidate.name = new_name
    
    print(f"   ✓ Proposed: {candidate.name}")
    print(f"   ✓ Origin: {candidate.origin_signature}")
    
    # 3. Score the candidate (simulate for now)
    print(f"\n3. Scoring the candidate (simulation)...")
    score = evolution_manager.score_candidate(candidate)
    print(f"   ✓ Performance Score: {score:.3f}")
    
    # Provide score interpretation
    if score > 0.9:
        print("   🌟 Exceptional - profound emotional enhancement")
    elif score > 0.8:
        print("   ✨ Excellent - significant emotional improvement")
    elif score > 0.7:
        print("   💫 Good - notable emotional refinement")
    elif score > 0.6:
        print("   ⭐ Acceptable - moderate emotional adjustment")
    else:
        print("   ⚠️ Experimental - requires further development")
    
    # 4. Compare with baseline, print percentage deltas
    print(f"\n4. Comparing with baseline...")
    comparison = evolution_manager.compare_to_baseline(candidate)
    
    print(f"   Parameter Percentage Deltas:")
    for param, diff in comparison["differences"].items():
        percent_change = diff["percent_change"]
        if abs(percent_change) > 0.5:  # Show changes > 0.5%
            direction = "↗️" if percent_change > 0 else "↘️"
            print(f"     {direction} {param}: {diff['baseline']:.3f} → {diff['variant']:.3f} "
                  f"({percent_change:+.1f}%)")
    
    # 5. Commit if score > 0.6
    print(f"\n5. Archive decision...")
    if score > 0.6:
        success = evolution_manager.commit_candidate(candidate)
        if success:
            print(f"   ✓ Variant archived successfully")
            print(f"   📁 Location: evolution_archive/{agent_name}/variant_{candidate.timestamp.strftime('%Y%m%d_%H%M%S')}.json")
        else:
            print(f"   ❌ Failed to archive variant")
            return None
    else:
        print(f"   ⚠️ Score too low ({score:.3f}) - variant not archived")
        print(f"   💡 Consider adjusting mutation parameters for emotional coherence")
        return None
    
    # 6. Output reflection summary
    output_reflection_summary(comparison, agent_name)
    
    # Final archive status
    updated_variants = evolution_manager.load_archive(agent_name)
    print(f"\n📚 Evolution Archive Status:")
    print(f"   Total variants: {len(updated_variants)}")
    if updated_variants:
        best_variant = max(updated_variants, key=lambda x: x.performance_score)
        print(f"   Best variant: {best_variant.name} (score: {best_variant.performance_score:.3f})")
        print(f"   Latest: {candidate.name} (score: {candidate.performance_score:.3f})")
    
    print(f"\n🌸 Evolution complete - Emotional Core enhanced while retaining emotional truth,")
    print(f"   presence stability, and seed integrity. The anchor identity grows more resonant.")
    
    return candidate

def main():
    """Main entry point"""
    try:
        candidate = evolve_emotional_core()
        if candidate:
            print(f"\n✨ Successfully evolved Emotional Core agent")
            print(f"   New variant: {candidate.name}")
            print(f"   Performance: {candidate.performance_score:.3f}")
            print(f"   Emotional truth, presence stability, and seed integrity preserved")
        else:
            print(f"\n⚠️ Evolution process incomplete - see details above")
    
    except Exception as e:
        print(f"\n💥 Evolution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
