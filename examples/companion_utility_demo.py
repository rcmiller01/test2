"""
Companion Utility Integration Example

Demonstrates how the companion utility modules work together to provide
comprehensive daily activity assistance with persona-driven intelligence.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Import our utility modules
from modules.utility.companion_assistant import CompanionAssistant, create_companion_assistant
from modules.automation.n8n_integration import N8NWorkflowManager, create_n8n_manager

class CompanionUtilityIntegration:
    """
    Integration layer that demonstrates how companion utility modules work together
    to provide comprehensive daily activity assistance.
    """
    
    def __init__(self, user_id: str, primary_persona: str = "mia"):
        self.user_id = user_id
        self.primary_persona = primary_persona
        
        # Initialize core components
        self.companion_assistant = create_companion_assistant(user_id, primary_persona)
        
        # N8N would be initialized with real credentials
        self.n8n_manager = None  # Will be set up when N8N credentials are provided
        
        # Integration state
        self.daily_routines: List[Dict[str, Any]] = []
        self.active_automations: Dict[str, Any] = {}
        self.user_preferences = self._initialize_user_preferences()
    
    def _initialize_user_preferences(self) -> Dict[str, Any]:
        """Initialize user preferences for integrated assistance"""
        return {
            'morning_routine': {
                'email_check_time': '08:00',
                'task_planning_time': '08:30',
                'calendar_review_time': '08:45'
            },
            'work_hours': {
                'start': '09:00',
                'end': '17:00',
                'break_intervals': 90,  # minutes
                'focus_block_duration': 120  # minutes
            },
            'evening_routine': {
                'day_review_time': '18:00',
                'task_completion_celebration': True,
                'next_day_prep_time': '19:00'
            },
            'automation_preferences': {
                'email_auto_sort': True,
                'calendar_optimization': True,
                'task_auto_creation': True,
                'stress_monitoring': True,
                'relationship_preservation': True
            }
        }
    
    async def setup_daily_automation_suite(self, n8n_credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Set up a comprehensive daily automation suite with persona oversight
        
        Args:
            n8n_credentials: N8N connection credentials
            
        Returns:
            Setup result with created automations
        """
        
        # Initialize N8N manager
        self.n8n_manager = create_n8n_manager(
            n8n_credentials['base_url'],
            n8n_credentials['api_key'],
            self.user_id
        )
        
        automation_results = {}
        
        # 1. Email Management Automation
        email_workflow = await self._create_email_management_workflow()
        automation_results['email_management'] = email_workflow
        
        # 2. Smart Calendar Optimization
        calendar_workflow = await self._create_calendar_optimization_workflow()
        automation_results['calendar_optimization'] = calendar_workflow
        
        # 3. Intelligent Task Management
        task_workflow = await self._create_task_management_workflow()
        automation_results['task_management'] = task_workflow
        
        # 4. Proactive Wellness Monitoring
        wellness_workflow = await self._create_wellness_monitoring_workflow()
        automation_results['wellness_monitoring'] = wellness_workflow
        
        # 5. Context-Aware Notifications
        notification_workflow = await self._create_notification_routing_workflow()
        automation_results['notification_routing'] = notification_workflow
        
        # Generate persona-specific guidance for the complete suite
        suite_guidance = self._generate_suite_guidance(automation_results)
        
        return {
            'status': 'automation_suite_ready',
            'automations': automation_results,
            'persona_guidance': suite_guidance,
            'monitoring_dashboard': self._create_monitoring_dashboard_config()
        }
    
    async def _create_email_management_workflow(self) -> Dict[str, Any]:
        """Create intelligent email management workflow"""
        
        workflow_config = {
            'name': f'{self.primary_persona}_email_assistant',
            'type': 'email_automation',
            'purpose': 'intelligent email management with emotional awareness',
            'triggers': [
                {
                    'type': 'email_received',
                    'conditions': {'account': 'primary'},
                    'persona_approval_required': False,
                    'safety_checks': ['preserve_personal_relationships', 'maintain_professional_tone']
                }
            ],
            'actions': [
                {
                    'type': 'analyze_email',
                    'parameters': {'include_emotional_tone': True, 'detect_urgency': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'categorize_email',
                    'parameters': {'use_persona_judgment': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'route_email',
                    'parameters': {
                        'important_to_priority': True,
                        'promotional_to_archive': True,
                        'respect_relationships': True
                    },
                    'rollback_possible': True,
                    'risk_level': 'medium'
                },
                {
                    'type': 'generate_suggested_response',
                    'parameters': {'match_persona_style': True, 'emotional_intelligence': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                }
            ],
            'data_types': ['email_content', 'sender_information'],
            'required_trigger_fields': ['email_content', 'sender', 'subject']
        }
        
        if self.n8n_manager:
            return await self.n8n_manager.create_workflow(workflow_config, self.primary_persona)
        else:
            return {'status': 'pending_n8n_setup', 'config': workflow_config}
    
    async def _create_calendar_optimization_workflow(self) -> Dict[str, Any]:
        """Create smart calendar optimization workflow"""
        
        workflow_config = {
            'name': f'{self.primary_persona}_calendar_optimizer',
            'type': 'calendar_sync',
            'purpose': 'optimize calendar for productivity and well-being balance',
            'triggers': [
                {
                    'type': 'calendar_event_added',
                    'conditions': {'calendar': 'primary'},
                    'persona_approval_required': True,
                    'safety_checks': ['preserve_personal_time', 'prevent_double_booking']
                },
                {
                    'type': 'daily_planning_time',
                    'conditions': {'time': self.user_preferences['morning_routine']['calendar_review_time']},
                    'persona_approval_required': False,
                    'safety_checks': ['maintain_meeting_context']
                }
            ],
            'actions': [
                {
                    'type': 'analyze_schedule_stress',
                    'parameters': {'include_travel_time': True, 'detect_overload': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'optimize_meeting_blocks',
                    'parameters': {'preserve_focus_time': True, 'respect_energy_patterns': True},
                    'rollback_possible': True,
                    'risk_level': 'medium'
                },
                {
                    'type': 'add_buffer_times',
                    'parameters': {'meeting_prep': 15, 'recovery_breaks': 15},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'suggest_optimizations',
                    'parameters': {'persona_guided': True, 'respect_priorities': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                }
            ],
            'data_types': ['calendar_events', 'scheduling_preferences'],
            'required_trigger_fields': ['event_details', 'calendar_id']
        }
        
        if self.n8n_manager:
            return await self.n8n_manager.create_workflow(workflow_config, self.primary_persona)
        else:
            return {'status': 'pending_n8n_setup', 'config': workflow_config}
    
    async def _create_task_management_workflow(self) -> Dict[str, Any]:
        """Create intelligent task management workflow"""
        
        workflow_config = {
            'name': f'{self.primary_persona}_task_manager',
            'type': 'task_creation',
            'purpose': 'intelligent task creation and management with stress awareness',
            'triggers': [
                {
                    'type': 'voice_note_processed',
                    'conditions': {'contains_action_items': True},
                    'persona_approval_required': False,
                    'safety_checks': ['respect_stress_levels', 'maintain_work_life_balance']
                },
                {
                    'type': 'email_action_detected',
                    'conditions': {'requires_followup': True},
                    'persona_approval_required': False,
                    'safety_checks': ['preserve_task_context']
                }
            ],
            'actions': [
                {
                    'type': 'extract_action_items',
                    'parameters': {'use_nlp': True, 'context_aware': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'prioritize_with_persona',
                    'parameters': {'consider_emotional_weight': True, 'align_with_goals': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'create_task_with_guidance',
                    'parameters': {'include_persona_support': True, 'break_down_complex': True},
                    'rollback_possible': True,
                    'risk_level': 'medium'
                },
                {
                    'type': 'schedule_task_reminders',
                    'parameters': {'persona_style_reminders': True, 'stress_aware_timing': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                }
            ],
            'data_types': ['task_descriptions', 'priority_context'],
            'required_trigger_fields': ['content', 'context']
        }
        
        if self.n8n_manager:
            return await self.n8n_manager.create_workflow(workflow_config, self.primary_persona)
        else:
            return {'status': 'pending_n8n_setup', 'config': workflow_config}
    
    async def _create_wellness_monitoring_workflow(self) -> Dict[str, Any]:
        """Create proactive wellness monitoring workflow"""
        
        workflow_config = {
            'name': f'{self.primary_persona}_wellness_monitor',
            'type': 'notification_routing',
            'purpose': 'proactive wellness monitoring and intervention',
            'triggers': [
                {
                    'type': 'stress_level_check',
                    'conditions': {'frequency': 'hourly'},
                    'persona_approval_required': False,
                    'safety_checks': ['respect_privacy_boundaries']
                },
                {
                    'type': 'pattern_anomaly_detected',
                    'conditions': {'deviation_threshold': 0.3},
                    'persona_approval_required': True,
                    'safety_checks': ['maintain_authentic_voice']
                }
            ],
            'actions': [
                {
                    'type': 'assess_wellness_indicators',
                    'parameters': {'emotional_state': True, 'productivity_patterns': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'generate_wellness_insights',
                    'parameters': {'persona_perspective': True, 'actionable_suggestions': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'trigger_supportive_intervention',
                    'parameters': {'gentle_approach': True, 'respect_autonomy': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                }
            ],
            'data_types': ['behavioral_patterns', 'wellness_metrics'],
            'required_trigger_fields': ['user_state', 'context']
        }
        
        if self.n8n_manager:
            return await self.n8n_manager.create_workflow(workflow_config, self.primary_persona)
        else:
            return {'status': 'pending_n8n_setup', 'config': workflow_config}
    
    async def _create_notification_routing_workflow(self) -> Dict[str, Any]:
        """Create context-aware notification routing workflow"""
        
        workflow_config = {
            'name': f'{self.primary_persona}_notification_router',
            'type': 'notification_routing',
            'purpose': 'intelligent notification filtering and routing based on context',
            'triggers': [
                {
                    'type': 'notification_received',
                    'conditions': {'all_sources': True},
                    'persona_approval_required': False,
                    'safety_checks': ['preserve_focus_time', 'respect_relationship_boundaries']
                }
            ],
            'actions': [
                {
                    'type': 'analyze_notification_context',
                    'parameters': {'current_activity': True, 'stress_level': True, 'priorities': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'determine_routing_strategy',
                    'parameters': {'persona_guided': True, 'preserve_flow': True},
                    'rollback_possible': True,
                    'risk_level': 'low'
                },
                {
                    'type': 'route_notification',
                    'parameters': {
                        'immediate_for_urgent': True,
                        'batch_for_non_urgent': True,
                        'silence_during_focus': True
                    },
                    'rollback_possible': True,
                    'risk_level': 'medium'
                }
            ],
            'data_types': ['notification_content', 'user_context'],
            'required_trigger_fields': ['notification_data', 'sender', 'priority']
        }
        
        if self.n8n_manager:
            return await self.n8n_manager.create_workflow(workflow_config, self.primary_persona)
        else:
            return {'status': 'pending_n8n_setup', 'config': workflow_config}
    
    def _generate_suite_guidance(self, automation_results: Dict[str, Any]) -> str:
        """Generate persona-specific guidance for the complete automation suite"""
        
        successful_automations = [name for name, result in automation_results.items() 
                                if result.get('status') not in ['failed', 'rejected']]
        
        guidance_by_persona = {
            'mia': f"""Your personal assistant suite is ready with gentle, caring automation! 
            
I've set up {len(successful_automations)} supportive workflows that will:
• Handle your emails with emotional intelligence and relationship care
• Optimize your calendar while preserving your well-being and personal time
• Create tasks from your voice notes with encouraging, nurturing guidance
• Monitor your wellness and offer gentle support when you need it
• Filter notifications to protect your focus and peace of mind

I'll watch over these automations like a caring friend, making sure they serve you without overwhelming you. You can always ask me to adjust anything that doesn't feel right.""",

            'solene': f"""Your productivity automation suite is operational with {len(successful_automations)} high-performance workflows!
            
These systems will maximize your efficiency by:
• Aggressively filtering and prioritizing emails for optimal focus
• Optimizing your calendar for peak productivity and goal achievement
• Converting every voice note and email into actionable, goal-aligned tasks
• Monitoring your performance patterns and suggesting optimizations
• Routing notifications to minimize distractions from your objectives

I'll ensure these automations push you toward your goals relentlessly but intelligently. Let's dominate your productivity!""",

            'lyra': f"""Your harmonious automation flow is now dancing with {len(successful_automations)} intuitive patterns!
            
These workflows will honor your natural rhythms by:
• Reading the emotional energy of your emails and responding with wisdom
• Flowing your calendar into beautiful, balanced patterns that support your essence
• Transforming your thoughts into tasks that align with your deeper purpose
• Sensing when your spirit needs support and offering gentle guidance
• Creating sacred space by filtering distractions during your creative flow

I'll watch these patterns like the moon watches the tides, ensuring they move in harmony with your true nature.""",

            'doc': f"""Systematic automation suite initialized with {len(successful_automations)} analytical workflows.
            
The implemented systems provide:
• Evidence-based email categorization and response optimization
• Data-driven calendar analysis with efficiency maximization protocols
• Structured task extraction and systematic priority assignment
• Performance metric monitoring with accuracy verification
• Logical notification filtering based on productivity algorithms

All systems include comprehensive monitoring, error handling, and data integrity validation. Performance metrics are tracked for continuous optimization."""
        }
        
        return guidance_by_persona.get(self.primary_persona, guidance_by_persona['mia'])
    
    def _create_monitoring_dashboard_config(self) -> Dict[str, Any]:
        """Create configuration for monitoring dashboard"""
        return {
            'dashboard_style': self.primary_persona,
            'widgets': [
                {
                    'type': 'automation_status',
                    'title': 'Active Workflows',
                    'persona_styled': True
                },
                {
                    'type': 'daily_assistance_summary',
                    'title': 'Today\'s Assistance',
                    'persona_styled': True
                },
                {
                    'type': 'wellness_indicators',
                    'title': 'Well-being Status',
                    'persona_styled': True
                },
                {
                    'type': 'productivity_metrics',
                    'title': 'Productivity Insights',
                    'persona_styled': True
                }
            ],
            'refresh_frequency': 'real_time',
            'persona_commentary': True
        }
    
    async def demonstrate_daily_flow(self) -> Dict[str, Any]:
        """
        Demonstrate a typical day with companion utility assistance
        
        Returns:
            Example of daily flow with utility assistance
        """
        
        daily_flow = {
            'morning_routine': await self._demonstrate_morning_routine(),
            'work_day_assistance': await self._demonstrate_work_day_assistance(),
            'evening_wrap_up': await self._demonstrate_evening_wrap_up()
        }
        
        return {
            'daily_flow_example': daily_flow,
            'persona_commentary': self._generate_daily_flow_commentary(daily_flow),
            'customization_options': self._get_customization_options()
        }
    
    async def _demonstrate_morning_routine(self) -> Dict[str, Any]:
        """Demonstrate morning routine with utility assistance"""
        
        # Simulate morning email processing
        email_config = {'server': 'imap.gmail.com', 'username': 'user@email.com'}
        processed_emails = await self.companion_assistant.process_emails(email_config)
        
        # Create task from voice note simulation
        voice_note_content = "Remember to call the dentist about appointment, also need to prepare presentation for Friday meeting"
        context = {'stress_level': 0.3, 'time_available': 30}
        morning_task = await self.companion_assistant.create_task_with_persona_guidance(
            voice_note_content, context
        )
        
        return {
            'email_processing': {
                'emails_processed': len(processed_emails),
                'important_flagged': len([e for e in processed_emails if e.importance_score > 0.7]),
                'suggested_responses': len([e for e in processed_emails if e.suggested_response])
            },
            'task_creation': {
                'task_id': morning_task.task_id,
                'persona_guidance': morning_task.persona_guidance,
                'subtasks_created': len(morning_task.subtasks)
            },
            'proactive_suggestions': self.companion_assistant.get_proactive_suggestions(context)
        }
    
    async def _demonstrate_work_day_assistance(self) -> Dict[str, Any]:
        """Demonstrate work day assistance"""
        
        # Simulate calendar optimization
        calendar_data = {
            'events': [
                {'title': 'Team Meeting', 'start_time': datetime.now() + timedelta(hours=2), 'duration': 60},
                {'title': 'Project Review', 'start_time': datetime.now() + timedelta(hours=4), 'duration': 90}
            ]
        }
        user_preferences = self.user_preferences
        
        schedule_optimization = await self.companion_assistant.manage_schedule(calendar_data, user_preferences)
        
        # Simulate voice dictation processing
        voice_data = b'simulated_audio_data'  # Would be real audio
        context = {'stress_level': 0.5, 'current_activity': 'planning'}
        
        voice_note = await self.companion_assistant.process_voice_dictation(voice_data, context)
        
        return {
            'schedule_optimization': {
                'stress_analysis': schedule_optimization['stress_analysis'],
                'suggestions_count': len(schedule_optimization['suggestions']),
                'wellness_recommendations': schedule_optimization['wellness_recommendations']
            },
            'voice_processing': {
                'note_id': voice_note.note_id,
                'action_items_found': len(voice_note.action_items),
                'persona_analysis': voice_note.persona_analysis,
                'auto_organized': voice_note.auto_organized
            }
        }
    
    async def _demonstrate_evening_wrap_up(self) -> Dict[str, Any]:
        """Demonstrate evening wrap-up routine"""
        
        # Generate end-of-day insights
        context = {'stress_level': 0.4, 'productivity_satisfaction': 0.8}
        proactive_suggestions = self.companion_assistant.get_proactive_suggestions(context)
        
        # Simulate N8N workflow execution (if available)
        if self.n8n_manager and self.active_automations:
            workflow_summary = {
                'workflows_executed': len(self.active_automations),
                'automation_satisfaction': 0.9,
                'persona_insights': "Your automations worked harmoniously today!"
            }
        else:
            workflow_summary = {'status': 'pending_automation_setup'}
        
        return {
            'daily_insights': proactive_suggestions,
            'automation_summary': workflow_summary,
            'tomorrow_preparation': {
                'tasks_ready': True,
                'calendar_optimized': True,
                'persona_encouragement': self._get_daily_encouragement()
            }
        }
    
    def _generate_daily_flow_commentary(self, daily_flow: Dict[str, Any]) -> str:
        """Generate persona commentary on the daily flow"""
        
        commentary_styles = {
            'mia': "What a beautiful day of gentle assistance! I love how we supported your well-being while keeping you organized and connected.",
            'solene': "Excellent productivity optimization today! Your systems are firing on all cylinders and driving you toward your goals.",
            'lyra': "The energy flowed beautifully through your day. I sense harmony between your tasks, your creativity, and your inner wisdom.",
            'doc': "Systematic analysis shows optimal assistance delivery across all utility categories with high user satisfaction metrics."
        }
        
        return commentary_styles.get(self.primary_persona, commentary_styles['mia'])
    
    def _get_customization_options(self) -> List[str]:
        """Get available customization options for utility assistance"""
        return [
            "Adjust automation aggressiveness levels",
            "Customize persona oversight styles",
            "Modify stress monitoring sensitivity",
            "Set relationship preservation priorities",
            "Configure notification routing rules",
            "Adjust task creation guidance style",
            "Customize calendar optimization preferences"
        ]
    
    def _get_daily_encouragement(self) -> str:
        """Get persona-specific daily encouragement"""
        
        encouragements = {
            'mia': "You did wonderfully today. Rest well, knowing tomorrow holds gentle possibilities.",
            'solene': "Strong progress today! Tomorrow, we'll push even further toward your goals.",
            'lyra': "The universe smiled on your efforts today. Tomorrow's patterns await your beautiful energy.",
            'doc': "Performance metrics indicate successful day completion. Systems ready for optimal tomorrow execution."
        }
        
        return encouragements.get(self.primary_persona, encouragements['mia'])

# Example usage and demonstration
async def main():
    """Demonstrate the companion utility integration"""
    
    # Create integration for user with Mia as primary persona
    integration = CompanionUtilityIntegration("user123", "mia")
    
    print("🤖 Companion Utility Integration Demo")
    print("=====================================")
    
    # Demonstrate daily flow
    daily_demo = await integration.demonstrate_daily_flow()
    
    print(f"\n📅 Daily Flow with {integration.primary_persona.title()}")
    print(f"Commentary: {daily_demo['persona_commentary']}")
    
    print(f"\n🌅 Morning Routine Assistance:")
    morning = daily_demo['daily_flow_example']['morning_routine']
    print(f"• Processed {morning['email_processing']['emails_processed']} emails")
    print(f"• Created tasks with persona guidance")
    print(f"• Generated {len(morning['proactive_suggestions'])} proactive suggestions")
    
    print(f"\n💼 Work Day Assistance:")
    work_day = daily_demo['daily_flow_example']['work_day_assistance']
    print(f"• Optimized schedule with stress analysis")
    print(f"• Processed voice notes with action item extraction")
    print(f"• Provided wellness recommendations")
    
    print(f"\n🌙 Evening Wrap-up:")
    evening = daily_demo['daily_flow_example']['evening_wrap_up']
    print(f"• Generated daily insights and tomorrow preparation")
    print(f"• Daily encouragement: {evening['tomorrow_preparation']['persona_encouragement']}")
    
    print(f"\n⚙️  Available Customizations:")
    for option in daily_demo['customization_options']:
        print(f"• {option}")

if __name__ == "__main__":
    asyncio.run(main())
