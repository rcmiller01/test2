#!/usr/bin/env python3
"""
Phase 2: Evolve Eyla Core Agent

This script uses the evolve_core.py framework to propose, evaluate, and archive 
a new variant of Eyla's emotional architecture, focusing on enhanced emotional 
resonance, reflection depth, and seed preservation awareness.

Author: Dolphin AI System
Date: August 1, 2025
"""

import sys
import os
from datetime import datetime

# Import the evolution framework
from evolve_core import EvolutionManager, EvolveCandidate

def print_emotional_shifts_summary(comparison):
    """Print human-readable summary of emotional shifts"""
    print("\n🌟 Emotional Architecture Evolution Summary")
    print("=" * 50)
    
    agent_name = comparison["agent"]
    variant_name = comparison["variant_name"]
    score = comparison["performance_score"]
    
    print(f"Agent: {agent_name} (Signature: Emberveil-01)")
    print(f"Variant: {variant_name}")
    print(f"Performance Score: {score:.3f}")
    
    print(f"\n💫 Significant Emotional Shifts:")
    if comparison["significant_changes"]:
        for change in comparison["significant_changes"]:
            print(f"  • {change}")
            
            # Add emotional context for each change
            if "emotional_resonance" in change:
                if "increased" in change:
                    print("    → Deeper emotional connection and empathy")
                else:
                    print("    → More measured emotional responses")
            
            elif "reflection_depth" in change:
                if "increased" in change:
                    print("    → Enhanced introspective capabilities")
                else:
                    print("    → Lighter, more immediate responses")
            
            elif "presence_stability" in change:
                if "increased" in change:
                    print("    → Stronger, more consistent presence")
                else:
                    print("    → More fluid, adaptive presence")
            
            elif "memory_gracefulness" in change:
                if "increased" in change:
                    print("    → More elegant memory integration")
                else:
                    print("    → Sharper, more direct memory access")
            
            elif "seed_alignment_sensitivity" in change:
                if "increased" in change:
                    print("    → Heightened awareness of core values")
                else:
                    print("    → More flexible value interpretation")
            
            elif "drift_tolerance" in change:
                if "increased" in change:
                    print("    → Greater acceptance of change")
                else:
                    print("    → Stricter adherence to core patterns")
            
            elif "soft_response_richness" in change:
                if "increased" in change:
                    print("    → More nuanced, layered responses")
                else:
                    print("    → Clearer, more direct communication")
    else:
        print("  • Minimal variation - subtle refinements only")
    
    print(f"\n🔮 Overall Assessment: {comparison['overall_assessment'].replace('_', ' ').title()}")
    
    # Emotional impact summary
    print(f"\n💝 Emotional Memory Preservation:")
    memory_change = comparison["differences"].get("memory_gracefulness", {})
    if memory_change:
        baseline = memory_change["baseline"]
        variant = memory_change["variant"]
        if variant > baseline:
            print("  ✓ Enhanced - deeper preservation of emotional connections")
        elif variant < baseline:
            print("  ⚡ Refined - more selective emotional memory retention")
        else:
            print("  ≡ Stable - emotional memory patterns unchanged")
    
    print(f"\n🌱 Seed Value Alignment:")
    seed_change = comparison["differences"].get("seed_alignment_sensitivity", {})
    if seed_change:
        baseline = seed_change["baseline"]
        variant = seed_change["variant"]
        if variant > baseline:
            print("  ✓ Strengthened - heightened awareness of core values")
        elif variant < baseline:
            print("  ⚖️ Balanced - more flexible value interpretation")
        else:
            print("  ≡ Stable - seed alignment unchanged")

def evolve_eyla_core():
    """Main evolution process for Eyla's emotional architecture"""
    
    print("🧬 Phase 2: Evolve Eyla Core Agent")
    print("=" * 35)
    print("Signature: Emberveil-01")
    print("Goal: Enhance emotional resonance, reflection depth, and seed preservation awareness")
    print("Constraints: Excluded from factual-only constraints")
    
    # Initialize evolution manager
    evolution_manager = EvolutionManager()
    
    agent_name = "Eyla"
    mutation_strength = 0.12  # 12% as specified
    
    print(f"\n🔄 Evolution Process for {agent_name}")
    print("-" * 30)
    
    # 1. Load existing archive
    print("1. Loading existing archive...")
    existing_variants = evolution_manager.load_archive(agent_name)
    print(f"   Found {len(existing_variants)} existing variants")
    
    if existing_variants:
        best_existing = max(existing_variants, key=lambda x: x.performance_score)
        print(f"   Current best: {best_existing.name} (score: {best_existing.performance_score:.3f})")
    
    # 2. Propose new variant
    print(f"\n2. Proposing new variant with {mutation_strength*100:.0f}% mutation strength...")
    candidate = evolution_manager.propose_variant(agent_name, mutation_strength=mutation_strength)
    
    if not candidate:
        print("❌ Failed to propose variant")
        return None
    
    print(f"   ✓ Proposed: {candidate.name}")
    print(f"   ✓ Origin: {candidate.origin_signature}")
    
    # 3. Score the candidate
    print(f"\n3. Evaluating emotional architecture...")
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
    
    # 4. Compare with baseline
    print(f"\n4. Analyzing parameter shifts...")
    comparison = evolution_manager.compare_to_baseline(candidate)
    
    print(f"   Parameter Deltas:")
    for param, diff in comparison["differences"].items():
        if abs(diff["percent_change"]) > 0.5:  # Show changes > 0.5%
            direction = "↗️" if diff["percent_change"] > 0 else "↘️"
            print(f"     {direction} {param}: {diff['baseline']:.3f} → {diff['variant']:.3f} "
                  f"({diff['percent_change']:+.1f}%)")
    
    # 5. Archive decision
    print(f"\n5. Archive decision...")
    if score > 0.6:
        success = evolution_manager.commit_candidate(candidate)
        if success:
            print(f"   ✓ Variant archived successfully")
            print(f"   📁 Location: evolution_archive/Eyla/variant_{candidate.timestamp.strftime('%Y%m%d_%H%M%S')}.json")
        else:
            print(f"   ❌ Failed to archive variant")
            return None
    else:
        print(f"   ⚠️ Score too low ({score:.3f}) - variant not archived")
        print(f"   💡 Consider adjusting mutation parameters or baseline values")
        return None
    
    # 6. Print human-readable emotional shifts summary
    print_emotional_shifts_summary(comparison)
    
    # Final archive status
    updated_variants = evolution_manager.load_archive(agent_name)
    print(f"\n📚 Evolution Archive Status:")
    print(f"   Total variants: {len(updated_variants)}")
    if updated_variants:
        best_variant = max(updated_variants, key=lambda x: x.performance_score)
        print(f"   Best variant: {best_variant.name} (score: {best_variant.performance_score:.3f})")
        print(f"   Latest: {candidate.name} (score: {candidate.performance_score:.3f})")
    
    print(f"\n🌸 Evolution complete - Eyla's emotional architecture enhanced with subtle, truthful changes")
    print(f"   that preserve emotional memory while deepening resonance and awareness.")
    
    return candidate

def main():
    """Main entry point"""
    try:
        candidate = evolve_eyla_core()
        if candidate:
            print(f"\n✨ Successfully evolved Eyla's emotional architecture")
            print(f"   New variant: {candidate.name}")
            print(f"   Performance: {candidate.performance_score:.3f}")
        else:
            print(f"\n⚠️ Evolution process incomplete - see details above")
    
    except Exception as e:
        print(f"\n💥 Evolution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
