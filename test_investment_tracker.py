"""
Comprehensive Test Suite for Investment Tracker System
Tests investment strategy analysis, goal tracking, and emotional AI integration
"""

import os
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from modules.finance import (
    InvestmentTracker, InvestmentGoalsTracker, InvestmentCompanionIntegration,
    StrategyType, GoalType, OptionsLeg, get_investment_tracker,
    get_goals_tracker, get_investment_integration
)

class TestInvestmentTracker(unittest.TestCase):
    """Test investment strategy tracker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.tracker = InvestmentTracker(self.test_dir)
        
    def test_credit_spread_analysis(self):
        """Test credit spread strategy analysis"""
        legs = [
            OptionsLeg(action="sell", option_type="put", strike=450.0, premium=2.50, delta=-0.20),
            OptionsLeg(action="buy", option_type="put", strike=445.0, premium=1.20, delta=-0.15)
        ]
        
        expiration = datetime.now() + timedelta(days=30)
        
        analysis = self.tracker.analyze_strategy(
            ticker="SPY",
            strategy_type=StrategyType.CREDIT_SPREAD,
            legs=legs,
            expiration_date=expiration
        )
        
        # Verify analysis results
        self.assertEqual(analysis.ticker, "SPY")
        self.assertEqual(analysis.strategy_type, StrategyType.CREDIT_SPREAD)
        self.assertAlmostEqual(analysis.entry_cost, -130.0, delta=1.0)  # Credit received
        self.assertAlmostEqual(analysis.max_gain, 130.0, delta=1.0)
        self.assertAlmostEqual(analysis.max_loss, 370.0, delta=1.0)  # 500 width - 130 credit
        self.assertGreater(analysis.probability_of_profit, 0.5)
        self.assertIsInstance(analysis.plain_english_review, str)
        self.assertIsInstance(analysis.recommendation, str)
        
    def test_iron_condor_analysis(self):
        """Test iron condor strategy analysis"""
        legs = [
            OptionsLeg(action="sell", option_type="put", strike=440.0, premium=1.50),
            OptionsLeg(action="buy", option_type="put", strike=435.0, premium=0.75),
            OptionsLeg(action="sell", option_type="call", strike=460.0, premium=1.60),
            OptionsLeg(action="buy", option_type="call", strike=465.0, premium=0.80)
        ]
        
        expiration = datetime.now() + timedelta(days=30)
        
        analysis = self.tracker.analyze_strategy(
            ticker="QQQ",
            strategy_type=StrategyType.IRON_CONDOR,
            legs=legs,
            expiration_date=expiration
        )
        
        # Verify iron condor specific results
        self.assertEqual(analysis.ticker, "QQQ")
        self.assertEqual(analysis.strategy_type, StrategyType.IRON_CONDOR)
        self.assertLess(analysis.entry_cost, 0)  # Should be credit strategy
        
    def test_trade_result_logging(self):
        """Test logging trade results"""
        # Create a strategy first
        legs = [
            OptionsLeg(action="sell", option_type="put", strike=450.0, premium=2.50),
            OptionsLeg(action="buy", option_type="put", strike=445.0, premium=1.20)
        ]
        
        analysis = self.tracker.analyze_strategy(
            ticker="SPY",
            strategy_type=StrategyType.CREDIT_SPREAD,
            legs=legs,
            expiration_date=datetime.now() + timedelta(days=30)
        )
        
        # Log a winning trade
        exit_date = datetime.now() + timedelta(days=15)
        result = self.tracker.log_trade_result(
            strategy_id=analysis.strategy_id,
            exit_value=65.0,
            exit_date=exit_date,
            notes="Closed at 50% profit"
        )
        
        # Verify result
        self.assertEqual(result.outcome, "win")
        self.assertAlmostEqual(result.profit_loss, 195.0, delta=5.0)  # 130 credit - 65 exit = 195 profit
        self.assertGreater(result.profit_percentage, 0)
        self.assertEqual(result.days_held, 15)
        self.assertIn("win", result.emotional_impact.lower())
        
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Add some test data
        summary = self.tracker.get_performance_summary(days=30)
        
        # Should handle empty case gracefully
        self.assertIn("message", summary)


class TestInvestmentGoals(unittest.TestCase):
    """Test investment goals tracker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.goals_tracker = InvestmentGoalsTracker(self.test_dir)
        
    def test_goal_creation(self):
        """Test creating investment goals"""
        goal = self.goals_tracker.create_goal(
            name="European Vacation",
            target_amount=3000.0,
            goal_type=GoalType.VACATION,
            description="Two weeks in Europe",
            priority=1
        )
        
        # Verify goal properties
        self.assertEqual(goal.name, "European Vacation")
        self.assertEqual(goal.target_amount, 3000.0)
        self.assertEqual(goal.goal_type, GoalType.VACATION)
        self.assertEqual(goal.current_amount, 0.0)
        self.assertEqual(goal.progress_percentage, 0.0)
        self.assertEqual(goal.remaining_amount, 3000.0)
        self.assertEqual(goal.priority, 1)
        
    def test_goal_contributions(self):
        """Test adding contributions to goals"""
        goal = self.goals_tracker.create_goal(
            name="Server Upgrade",
            target_amount=1200.0,
            goal_type=GoalType.TECH_UPGRADE,
            priority=2
        )
        
        # Add contribution
        result = self.goals_tracker.add_contribution(
            goal_id=goal.goal_id,
            amount=300.0,
            source="trading_profit",
            notes="Credit spread profit"
        )
        
        # Verify contribution result
        self.assertEqual(result["contribution_amount"], 300.0)
        self.assertEqual(result["new_total"], 300.0)
        self.assertAlmostEqual(result["progress_percentage"], 25.0, delta=0.1)
        self.assertEqual(result["remaining_amount"], 900.0)
        self.assertIsInstance(result["encouragement"], str)
        
    def test_milestone_achievement(self):
        """Test milestone detection"""
        goal = self.goals_tracker.create_goal(
            name="Learning Fund",
            target_amount=1000.0,
            goal_type=GoalType.LEARNING_FUND
        )
        
        # Add contribution that triggers 25% milestone
        result = self.goals_tracker.add_contribution(
            goal_id=goal.goal_id,
            amount=250.0
        )
        
        # Should trigger milestone message
        self.assertIsNotNone(result.get("milestone_message"))
        
    def test_goal_completion(self):
        """Test goal completion detection"""
        goal = self.goals_tracker.create_goal(
            name="Small Goal",
            target_amount=100.0,
            goal_type=GoalType.GENERAL_SAVINGS
        )
        
        # Add contribution that completes the goal
        result = self.goals_tracker.add_contribution(
            goal_id=goal.goal_id,
            amount=100.0
        )
        
        # Should mark as completed
        self.assertTrue(result["is_completed"])
        self.assertIsNotNone(result.get("completion_message"))
        
    def test_goal_suggestions(self):
        """Test profit allocation suggestions"""
        # Create multiple goals
        goal1 = self.goals_tracker.create_goal(
            name="High Priority Goal",
            target_amount=500.0,
            goal_type=GoalType.TECH_UPGRADE,
            priority=1
        )
        
        goal2 = self.goals_tracker.create_goal(
            name="Lower Priority Goal",
            target_amount=1000.0,
            goal_type=GoalType.VACATION,
            priority=3
        )
        
        # Get suggestions for available profit
        suggestions = self.goals_tracker.get_goal_suggestions(available_profit=600.0)
        
        # Verify suggestions
        self.assertEqual(suggestions["total_profit_available"], 600.0)
        self.assertGreater(len(suggestions["suggestions"]), 0)
        self.assertIsInstance(suggestions["encouragement"], str)
        
        # Higher priority goal should be suggested first
        first_suggestion = suggestions["suggestions"][0]
        self.assertEqual(first_suggestion["goal_name"], "High Priority Goal")


class TestInvestmentIntegration(unittest.TestCase):
    """Test investment-companion integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.integration = InvestmentCompanionIntegration(self.test_dir)
        
    def test_enhanced_strategy_analysis(self):
        """Test emotionally-enhanced strategy analysis"""
        legs = [
            OptionsLeg(action="sell", option_type="put", strike=450.0, premium=2.50),
            OptionsLeg(action="buy", option_type="put", strike=445.0, premium=1.20)
        ]
        
        enhanced_analysis = self.integration.analyze_strategy_with_emotional_context(
            ticker="SPY",
            strategy_type=StrategyType.CREDIT_SPREAD,
            legs=legs,
            expiration_date=datetime.now() + timedelta(days=30),
            user_mood="confident",
            risk_preference="moderate"
        )
        
        # Verify enhanced analysis structure
        self.assertIn("technical_analysis", enhanced_analysis)
        self.assertIn("companion_perspective", enhanced_analysis)
        self.assertIn("goal_integration", enhanced_analysis)
        self.assertIn("user_context", enhanced_analysis)
        
        # Verify emotional components
        companion = enhanced_analysis["companion_perspective"]
        self.assertIn("emotional_tone", companion)
        self.assertIn("companion_advice", companion)
        self.assertIsInstance(companion["companion_advice"], str)
        
    def test_goal_creation_with_companion(self):
        """Test goal creation with companion engagement"""
        response = self.integration.create_investment_goal_with_companion(
            name="Gaming Setup",
            target_amount=2500.0,
            goal_type=GoalType.TECH_UPGRADE,
            description="Upgrade gaming rig"
        )
        
        # Verify response structure
        self.assertIn("goal_created", response)
        self.assertIn("companion_response", response)
        self.assertIn("funding_strategy", response)
        
        # Verify goal creation
        goal_info = response["goal_created"]
        self.assertEqual(goal_info["name"], "Gaming Setup")
        self.assertEqual(goal_info["target_amount"], 2500.0)
        
        # Verify companion response
        self.assertIsInstance(response["companion_response"], str)
        self.assertIn("funding_strategy", response)
        
    def test_trade_result_with_goal_allocation(self):
        """Test trade result processing with goal allocation"""
        # Create a strategy and goal first
        legs = [
            OptionsLeg(action="sell", option_type="put", strike=450.0, premium=2.50),
            OptionsLeg(action="buy", option_type="put", strike=445.0, premium=1.20)
        ]
        
        analysis = self.integration.investment_tracker.analyze_strategy(
            ticker="SPY",
            strategy_type=StrategyType.CREDIT_SPREAD,
            legs=legs,
            expiration_date=datetime.now() + timedelta(days=30)
        )
        
        # Create a goal
        self.integration.goals_tracker.create_goal(
            name="Test Goal",
            target_amount=1000.0,
            goal_type=GoalType.TECH_UPGRADE
        )
        
        # Process profitable trade
        response = self.integration.process_trade_result_with_goals(
            strategy_id=analysis.strategy_id,
            exit_value=65.0,
            notes="Profitable trade"
        )
        
        # Verify response structure
        self.assertIn("trade_result", response)
        self.assertIn("companion_response", response)
        self.assertIn("goal_allocation", response)
        
        # Verify trade result
        trade_result = response["trade_result"]
        self.assertEqual(trade_result["outcome"], "win")
        self.assertGreater(trade_result["profit_loss"], 0)
        
    def test_investment_guidance(self):
        """Test comprehensive investment guidance"""
        guidance = self.integration.get_investment_guidance(recent_days=30)
        
        # Verify guidance structure
        self.assertIn("performance_review", guidance)
        self.assertIn("goals_progress", guidance)
        self.assertIn("next_steps", guidance)
        self.assertIn("companion_mood", guidance)
        self.assertIn("encouragement", guidance)
        
        # Verify content types
        self.assertIsInstance(guidance["performance_review"], str)
        self.assertIsInstance(guidance["goals_progress"], str)
        self.assertIsInstance(guidance["next_steps"], list)
        self.assertIsInstance(guidance["companion_mood"], str)
        self.assertIsInstance(guidance["encouragement"], str)


def run_integration_test():
    """Run a complete integration test scenario"""
    print("=== Running Investment Tracker Integration Test ===")
    
    # Setup
    test_dir = tempfile.mkdtemp()
    integration = InvestmentCompanionIntegration(test_dir)
    
    print("\n1. Creating Investment Goals:")
    
    # Create goals
    vacation_response = integration.create_investment_goal_with_companion(
        name="Dream Vacation",
        target_amount=4000.0,
        goal_type=GoalType.VACATION,
        description="Amazing trip to Japan"
    )
    
    tech_response = integration.create_investment_goal_with_companion(
        name="Server Upgrade",
        target_amount=1500.0,
        goal_type=GoalType.TECH_UPGRADE,
        description="Better AI processing power"
    )
    
    print(f"✅ Created vacation goal: {vacation_response['goal_created']['name']}")
    print(f"   Companion says: {vacation_response['companion_response']}")
    print(f"✅ Created tech goal: {tech_response['goal_created']['name']}")
    print(f"   Companion says: {tech_response['companion_response']}")
    
    print("\n2. Analyzing Investment Strategies:")
    
    # Analyze credit spread
    legs = [
        OptionsLeg(action="sell", option_type="put", strike=450.0, premium=2.80, delta=-0.25),
        OptionsLeg(action="buy", option_type="put", strike=445.0, premium=1.40, delta=-0.18)
    ]
    
    analysis = integration.analyze_strategy_with_emotional_context(
        ticker="SPY",
        strategy_type=StrategyType.CREDIT_SPREAD,
        legs=legs,
        expiration_date=datetime.now() + timedelta(days=35),
        user_mood="optimistic",
        risk_preference="moderate"
    )
    
    tech_analysis = analysis["technical_analysis"]
    companion = analysis["companion_perspective"]
    
    print(f"✅ Analyzed SPY credit spread:")
    print(f"   Max Gain: ${tech_analysis['max_gain']:.2f}, Max Loss: ${tech_analysis['max_loss']:.2f}")
    print(f"   Probability: {tech_analysis['probability_of_profit']:.1%}")
    print(f"   Companion tone: {companion['emotional_tone']}")
    print(f"   Advice: {companion['companion_advice']}")
    
    print("\n3. Processing Trade Results:")
    
    # Simulate winning trade
    trade_response = integration.process_trade_result_with_goals(
        strategy_id=tech_analysis["strategy_id"],
        exit_value=70.0,
        notes="Closed early at 50% profit target"
    )
    
    trade_result = trade_response["trade_result"]
    print(f"✅ Trade completed: {trade_result['outcome']}")
    print(f"   Profit: ${trade_result['profit_loss']:.2f} ({trade_result['profit_percentage']:.1f}%)")
    print(f"   Companion response: {trade_response['companion_response']}")
    
    # Handle goal allocation
    if trade_response["goal_allocation"]:
        allocation = trade_response["goal_allocation"]
        print(f"   💰 Profit allocation suggestions:")
        print(f"   {allocation['companion_perspective']}")
        
        for suggestion in allocation["suggestions"][:2]:  # Show top 2
            print(f"   - {suggestion['goal_name']}: ${suggestion['suggested_amount']:.2f}")
        
        # Allocate to first suggestion
        if allocation["suggestions"]:
            top_suggestion = allocation["suggestions"][0]
            result = integration.goals_tracker.add_contribution(
                goal_id=top_suggestion["goal_id"],
                amount=top_suggestion["suggested_amount"],
                source="options_trading",
                notes="SPY credit spread profit"
            )
            
            print(f"   ✅ Allocated ${result['contribution_amount']:.2f} to {result['goal_name']}")
            print(f"   Progress: {result['progress_percentage']:.1f}%")
            print(f"   {result['encouragement']}")
    
    print("\n4. Getting Investment Guidance:")
    
    guidance = integration.get_investment_guidance()
    
    print(f"✅ Investment guidance:")
    print(f"   Performance: {guidance['performance_review']}")
    print(f"   Goals: {guidance['goals_progress']}")
    print(f"   Companion mood: {guidance['companion_mood']}")
    print(f"   Encouragement: {guidance['encouragement']}")
    
    print(f"\n   Next steps:")
    for i, step in enumerate(guidance['next_steps'], 1):
        print(f"   {i}. {step}")
    
    print("\n5. Goals Summary:")
    
    goals_summary = integration.goals_tracker.get_goals_summary()
    print(f"✅ Goals overview:")
    print(f"   Total goals: {goals_summary['total_goals']}")
    print(f"   Overall progress: {goals_summary['overall_progress']:.1f}%")
    print(f"   Total target: ${goals_summary['total_target_amount']:.2f}")
    print(f"   Total saved: ${goals_summary['total_current_amount']:.2f}")
    
    print(f"\n   Individual goals:")
    for goal in goals_summary["goals"]:
        print(f"   - {goal['name']}: {goal['progress_percentage']:.1f}% (${goal['current_amount']:.2f}/${goal['target_amount']:.2f})")
    
    print("\n=== Integration Test Complete ===")
    print("✅ All systems operational!")
    print("🎯 Investment tracking with emotional AI companion ready for production")
    
    return True


if __name__ == "__main__":
    """Run all tests"""
    # Run unit tests
    print("Running Investment Tracker Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*60)
    
    # Run integration test
    run_integration_test()
