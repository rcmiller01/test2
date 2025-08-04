#!/usr/bin/env python3
"""
Demo script showcasing the comprehensive financial assistant capabilities
of the Emotional AI system.
"""

import asyncio
import json
from core.emotional_ai import EmotionalAI

async def demo_financial_assistant():
    """Demonstrate the comprehensive financial planning capabilities"""
    
    print("🤖 Emotional AI Financial Assistant Demo")
    print("=" * 60)
    
    # Initialize the AI
    ai = EmotionalAI()
    user_id = "demo_user"
    thread_id = "financial_demo"
    
    # Demo scenarios
    scenarios = [
        {
            "title": "💰 Budget Analysis",
            "message": "Can you analyze my budget? I make $7500 per month salary and spend about $5200 on expenses."
        },
        {
            "title": "📈 Investment Planning", 
            "message": "I want to invest $25000 and I prefer moderate risk with some growth potential."
        },
        {
            "title": "📊 Options Strategy Analysis",
            "message": "I'm considering selling covered calls on my 200 shares of Microsoft stock. What should I know?"
        },
        {
            "title": "🏦 Document Analysis",
            "message": "Can you help me analyze my bank statements and financial documents for budgeting?"
        },
        {
            "title": "🧮 Quick Calculation",
            "message": "Calculate my annual savings if I save $850 per month for 5 years with 4% interest."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print("-" * 40)
        print(f"User: {scenario['message']}")
        print()
        
        # Process through the AI system
        response = await ai.process_message(user_id, thread_id, scenario['message'])
        
        # Also test direct utility functions for detailed results
        utility_request = ai._parse_utility_request(scenario['message'])
        if utility_request:
            function_name = utility_request["function"]
            parameters = utility_request["parameters"]
            
            # Get detailed results from utility function
            detailed_result = await ai.n8n_client.execute_workflow(function_name, parameters)
            
            print(f"💡 Detailed Analysis:")
            if function_name == "budget_planning" and "budget_summary" in detailed_result:
                budget = detailed_result["budget_summary"]
                print(f"   Monthly Income: ${budget['total_income']:,.2f}")
                print(f"   Monthly Expenses: ${budget['total_expenses']:,.2f}")
                print(f"   Net Cash Flow: ${budget['net_flow']:,.2f}")
                print(f"   Savings Rate: {budget['savings_rate']:.1f}%")
                print(f"   Recommendations:")
                for rec in budget['recommendations']:
                    print(f"   • {rec}")
                    
            elif function_name == "investment_planning" and "investment_analysis" in detailed_result:
                investment = detailed_result["investment_analysis"]
                print(f"   Risk Profile: {investment['risk_profile']}")
                print(f"   Recommended Allocation: {investment['allocation']}")
                print(f"   Expected Annual Return: {investment['expected_return']}%")
                print(f"   Investment Amount: ${investment['investment_amount']:,.2f}")
                print(f"   Recommendations:")
                for rec in investment['recommendations']:
                    print(f"   • {rec}")
                    
            elif function_name == "options_analysis" and "options_strategy" in detailed_result:
                options = detailed_result["options_strategy"]
                print(f"   Strategy: {options['strategy_name']}")
                print(f"   Risk Level: {options['risk_level']}")
                print(f"   Max Profit: {options['max_profit']}")
                print(f"   Max Loss: {options['max_loss']}")
                print(f"   Key Considerations:")
                for consideration in options['considerations']:
                    print(f"   • {consideration}")
                    
            elif function_name == "financial_document_analysis" and "document_analysis" in detailed_result:
                doc_analysis = detailed_result["document_analysis"]
                print(f"   Document Type: {doc_analysis['document_type']}")
                print(f"   Analysis Period: {doc_analysis['period']}")
                print(f"   Key Metrics:")
                for metric, description in doc_analysis['key_metrics'].items():
                    print(f"   • {metric}: {description}")
                print(f"   Getting Started:")
                for insight in doc_analysis['insights']:
                    print(f"   • {insight}")
        
        print("\n" + "=" * 60)
    
    # Show emotional context evolution
    print(f"\n🧠 Emotional Context After Financial Discussion:")
    context = ai.conversations.get(f"{user_id}_{thread_id}")
    if context:
        print(f"   Emotional Bond Level: {context.emotional_bond_level:.2f}/10")
        print(f"   Intimacy Level: {context.intimacy_level:.2f}/10") 
        print(f"   Trust Level: {context.trust_level:.2f}/10")
        print(f"   Conversation Depth: {len(context.context_history)} exchanges")

if __name__ == "__main__":
    asyncio.run(demo_financial_assistant())
