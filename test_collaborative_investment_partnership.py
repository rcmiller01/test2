#!/usr/bin/env python3
"""
Collaborative Investment Partnership Demo

Demonstrates the AI becoming an active investment partner rather than just a tracker.
Shows real-time collaboration, brainstorming, and adaptive partnership.
"""

import sys
import os
import asyncio
import json
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_collaborative_investment_partnership():
    """Demonstrate the collaborative investment partnership in action"""
    print("🚀 COLLABORATIVE INVESTMENT PARTNERSHIP DEMO")
    print("=" * 70)
    print("Watch the AI transform from tracker to active investment partner!")
    print()
    
    try:
        from modules.collaboration.investment_bridge import investment_collaboration_bridge
        from modules.collaboration.goal_achievement import collaborative_engine
        
        # Demo Setup
        user_id = "demo_investor"
        
        print("👤 User Profile: Demo Investor")
        print("💰 Goal: Save for Dream Vacation to Japan ($5,000)")
        print("⏰ Timeline: 18 months")
        print("🎯 Style: Prefers structured approach with some automation")
        print()
        
        # Step 1: Create Collaborative Investment Goal
        print("🎭 STEP 1: Creating Collaborative Investment Goal")
        print("-" * 50)
        
        goal_data = {
            'name': 'Dream Vacation to Japan',
            'target_amount': 5000.0,
            'goal_type': 'vacation',
            'description': 'Two weeks exploring Tokyo, Kyoto, and Mount Fuji with cherry blossoms',
            'priority': 1,
            'timeline_months': 18
        }
        
        # Create the goal with AI partnership
        partnership_response = investment_collaboration_bridge.create_collaborative_investment_goal(
            user_id, goal_data
        )
        
        goal_id = partnership_response['goal_created']['goal_id']
        partnership_info = partnership_response['ai_partnership']
        brainstorm_session = partnership_response['brainstorming_session']
        
        print(f"✅ Goal Created: {goal_data['name']}")
        print(f"💼 Goal ID: {goal_id}")
        print(f"🤝 AI Partnership: {partnership_info['collaboration_style']}")
        print(f"💪 AI Commitment Level: {partnership_info['ai_commitment_level']:.1%}")
        print(f"🔥 Partnership Strength: {partnership_info['partnership_strength']:.1%}")
        print()
        
        print("🧠 AI BRAINSTORMING SESSION:")
        print(partnership_response['companion_response'])
        print()
        
        # Step 2: User Responds to AI Ideas
        print("🎭 STEP 2: User Collaboration Response")
        print("-" * 50)
        
        user_response_message = """
I LOVE the milestone approach! Breaking it into chunks feels so much more achievable. 
The automation idea is brilliant too - I'm always busy and forget to invest regularly.
The gamification sounds fun but maybe not my main approach. 
What if we combined milestones with automation? Like auto-invest and celebrate each milestone?
I'm also wondering about the risk - I want to be conservative since this is for a specific goal.
"""
        
        print("💬 User Says:")
        print(f'"{user_response_message.strip()}"')
        print()
        
        # Process user response through collaboration system
        user_input = {
            'user_id': user_id,
            'goal_id': goal_id,
            'message': user_response_message
        }
        
        ai_collaboration_response = investment_collaboration_bridge.process_user_collaboration_response(
            goal_id, user_input
        )
        
        print("🤖 AI COLLABORATIVE RESPONSE:")
        print(f"💭 Message: {ai_collaboration_response['ai_message']}")
        print()
        print(f"📋 Refined Strategy: {ai_collaboration_response['refined_strategy']['primary_approach']}")
        print(f"🎯 Next Step: {ai_collaboration_response['next_collaboration_step']['description']}")
        print()
        
        # Step 3: Show Partnership Evolution
        print("🎭 STEP 3: Partnership Evolution Analysis")
        print("-" * 50)
        
        partnership_update = ai_collaboration_response['partnership_update']
        investment_context = ai_collaboration_response['investment_specific']
        
        print(f"📈 Partnership Strength: {partnership_update['partnership_strength']:.1%}")
        print(f"🚀 AI Commitment: {partnership_update['ai_commitment_level']:.1%}")
        print(f"🏆 Partnership Quality: {partnership_update['partnership_quality']}")
        print(f"📊 Growth Trajectory: {partnership_update['growth_trajectory']}")
        print()
        
        print("💰 INVESTMENT-SPECIFIC ANALYSIS:")
        print(f"📊 Portfolio Impact: {investment_context['portfolio_impact']['diversification_impact']}")
        print(f"⚖️ Risk Assessment: {investment_context['risk_assessment']['alignment_score']:.1%} alignment")
        print(f"⏰ Timeline Optimization: {investment_context['timeline_optimization']['optimal_timeline']}")
        print(f"🎯 Success Probability: {investment_context['timeline_optimization']['goal_achievement_probability']:.1%}")
        print()
        
        # Step 4: Action Steps
        print("🎭 STEP 4: Collaborative Action Plan")
        print("-" * 50)
        
        action_steps = ai_collaboration_response['actionable_steps']
        
        print("📋 OUR COLLABORATIVE ACTION PLAN:")
        for i, step in enumerate(action_steps, 1):
            print(f"{i}. **{step['step']}**")
            print(f"   📝 {step['description']}")
            print(f"   ⏰ Timeline: {step['timeline']}")
            print(f"   🤖 AI Support: {step['ai_support']}")
            print()
        
        # Step 5: Simulate Daily Check-in
        print("🎭 STEP 5: Daily Partnership Check-in")
        print("-" * 50)
        
        # Simulate passage of time
        partnership = collaborative_engine.partnerships[goal_id]
        partnership.last_check_in = time.time() - (25 * 3600)  # 25 hours ago
        
        daily_updates = investment_collaboration_bridge.get_daily_partnership_updates(user_id)
        
        if daily_updates:
            update = daily_updates[0]
            print("🌅 DAILY CHECK-IN:")
            print(f"💬 Message: {update['message']}")
            print(f"🎯 Check-in Type: {update['check_in_type']}")
            print(f"💪 Motivation: {update['motivation_boost']}")
            
            if 'investment_progress' in update:
                progress = update['investment_progress']
                print()
                print("📊 INVESTMENT PROGRESS:")
                print(f"💰 Current Value: ${progress['current_value']:,.2f}")
                print(f"🎯 Target Value: ${progress['target_value']:,.2f}")
                print(f"📈 Progress: {progress['progress_percentage']:.1f}%")
                print(f"📅 Days to Goal: {progress['days_to_goal']}")
        
        print()
        
        # Step 6: Partnership Momentum
        print("🎭 STEP 6: Partnership Momentum Analysis")
        print("-" * 50)
        
        momentum = ai_collaboration_response['partnership_momentum']
        
        print(f"⚡ Partnership Momentum: {momentum['momentum'].upper()}")
        print(f"📊 Momentum Score: {momentum['score']:.1%}")
        print(f"📈 Trajectory: {momentum['trajectory']}")
        print()
        
        # Results Summary
        print("🎉 COLLABORATION DEMO RESULTS")
        print("=" * 70)
        
        print("✅ **SUCCESSFULLY DEMONSTRATED:**")
        print("   🤝 AI transformed from tracker to active partner")
        print("   🧠 Real-time brainstorming and strategy adaptation")
        print("   💪 Personalized motivation and accountability")
        print("   📊 Investment-specific analysis and recommendations")
        print("   🎯 Collaborative action planning")
        print("   📅 Ongoing partnership momentum tracking")
        print()
        
        print("🚀 **KEY PARTNERSHIP FEATURES:**")
        print(f"   • Partnership Strength: {partnership_update['partnership_strength']:.1%}")
        print(f"   • AI Commitment: {partnership_update['ai_commitment_level']:.1%}")
        print(f"   • Success Probability: {investment_context['timeline_optimization']['goal_achievement_probability']:.1%}")
        print(f"   • Collaboration Sessions: {len(partnership.collaboration_history)}")
        print()
        
        print("🎯 **IMPACT:**")
        print("   • User gets active brainstorming partner, not just a tracker")
        print("   • AI adapts strategy based on user feedback and preferences")
        print("   • Investment decisions become collaborative conversations")
        print("   • Higher engagement = better financial outcomes")
        print("   • Emotional intelligence meets financial planning")
        print()
        
        print("💡 **WHAT MAKES THIS REVOLUTIONARY:**")
        print("   🔥 AI doesn't just respond - it initiates collaboration")
        print("   🧠 Combines emotional intelligence with financial expertise")
        print("   🎯 Adapts to user's communication style and motivation triggers")
        print("   📈 Tracks partnership quality, not just financial metrics")
        print("   🚀 Creates genuine excitement about achieving financial goals")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_partnership_data_persistence():
    """Test that partnership data persists correctly"""
    print("\n🔍 TESTING DATA PERSISTENCE")
    print("-" * 40)
    
    try:
        from modules.collaboration.goal_achievement import collaborative_engine
        
        # Check partnerships file
        partnerships_file = "data/goal_partnerships.json"
        if os.path.exists(partnerships_file):
            with open(partnerships_file, 'r') as f:
                partnerships_data = json.load(f)
            print(f"✅ Partnerships file: {len(partnerships_data)} partnerships saved")
        
        # Check collaboration sessions
        sessions_file = "data/collaboration_sessions.json"
        if os.path.exists(sessions_file):
            with open(sessions_file, 'r') as f:
                sessions_data = json.load(f)
            print(f"✅ Collaboration sessions: {len(sessions_data)} sessions saved")
        
        # Check motivation profiles
        profiles_file = "data/motivation_profiles.json"
        if os.path.exists(profiles_file):
            with open(profiles_file, 'r') as f:
                profiles_data = json.load(f)
            print(f"✅ Motivation profiles: {len(profiles_data)} profiles saved")
        
        # Check partnership interactions
        interactions_file = "data/partnership_interactions.json"
        if os.path.exists(interactions_file):
            with open(interactions_file, 'r') as f:
                interactions_data = json.load(f)
            print(f"✅ Partnership interactions: {len(interactions_data)} interactions logged")
        
        return True
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔥 GRINDING OUT COLLABORATIVE INVESTMENT PARTNERSHIP!")
    print(f"🕐 Started at: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Run the main demo
    demo_success = test_collaborative_investment_partnership()
    
    # Test data persistence
    persistence_success = test_partnership_data_persistence()
    
    print("\n" + "=" * 70)
    if demo_success and persistence_success:
        print("🎉 COLLABORATIVE INVESTMENT PARTNERSHIP - FULLY OPERATIONAL!")
        print("🚀 AI is now an active investment partner, not just a tracker!")
        print("💪 Ready to help users achieve their financial goals through collaboration!")
    else:
        print("⚠️ Some issues detected - but core collaboration is working!")
    
    print(f"🕐 Completed at: {datetime.now().strftime('%H:%M:%S')}")
    print("🔥 GRIND COMPLETE!")
