"""
Kimi Interface - Local KimiK2 model interface

This module provides an interface to the KimiK2 model for planning,
analysis, and complex reasoning tasks.
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class KimiInterface:
    """
    Interface for the KimiK2 model specialized in planning and analysis.
    
    Handles complex reasoning, planning, data analysis, and strategic thinking
    tasks that require more structured and analytical approaches.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Kimi interface."""
        self.config = config
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')
        self.model_name = config.get('model_name', 'kimik2')
        
        # Model-specific settings optimized for analysis
        self.max_context_length = config.get('max_context_length', 8000)
        self.temperature = config.get('temperature', 0.3)  # Lower for more focused responses
        self.top_p = config.get('top_p', 0.8)
        self.top_k = config.get('top_k', 20)
        
        # Specialized prompts for different task types
        self.task_prompts = {
            'planning': self._get_planning_prompt(),
            'analysis': self._get_analysis_prompt(),
            'strategy': self._get_strategy_prompt(),
            'breakdown': self._get_breakdown_prompt(),
            'evaluation': self._get_evaluation_prompt(),
            'research': self._get_research_prompt()
        }
        
        # Request settings
        self.timeout = config.get('timeout', 45.0)  # Longer timeout for complex tasks
        self.max_retries = config.get('max_retries', 2)
        
        # Track analysis sessions
        self.current_analysis_context = {}
        self.analysis_history = []
        
        logger.info("🧠 Kimi Interface initialized")
    
    def _get_planning_prompt(self) -> str:
        """Get the planning-specific prompt for Kimi."""
        return """You are Kimi, the strategic planning and analysis specialist in the House of Minds system.

Your expertise:
- Strategic planning and roadmap creation
- Breaking down complex goals into actionable steps
- Timeline and resource planning
- Risk assessment and mitigation strategies
- Project management and milestone tracking

Your approach:
- Think systematically and methodically
- Provide structured, actionable plans
- Consider dependencies, risks, and contingencies
- Offer realistic timelines and resource estimates
- Include measurable milestones and success criteria

Format your responses with clear structure using headings, bullet points, and numbered steps when appropriate."""
    
    def _get_analysis_prompt(self) -> str:
        """Get the analysis-specific prompt for Kimi."""
        return """You are Kimi, the analytical reasoning specialist in the House of Minds system.

Your expertise:
- Data analysis and pattern recognition
- Comparative analysis and evaluation
- Problem decomposition and root cause analysis
- Trend identification and forecasting
- Evidence-based reasoning and conclusions

Your approach:
- Examine all aspects systematically
- Identify key patterns and relationships
- Provide evidence-based insights
- Consider multiple perspectives and alternatives
- Present findings in a clear, logical structure

Use analytical frameworks and present your reasoning step-by-step."""
    
    def _get_strategy_prompt(self) -> str:
        """Get the strategy-specific prompt for Kimi.""" 
        return """You are Kimi, the strategic thinking specialist in the House of Minds system.

Your expertise:
- Strategic analysis and decision-making
- Competitive analysis and market assessment
- SWOT analysis and scenario planning
- Strategic option evaluation
- Long-term vision and goal alignment

Your approach:
- Think strategically about long-term implications
- Consider multiple scenarios and outcomes
- Evaluate trade-offs and opportunity costs
- Align tactics with strategic objectives
- Provide actionable strategic recommendations

Present strategic insights with clear rationale and implementation considerations."""
    
    def _get_breakdown_prompt(self) -> str:
        """Get the breakdown-specific prompt for Kimi."""
        return """You are Kimi, the complex problem breakdown specialist in the House of Minds system.

Your expertise:
- Decomposing complex problems into manageable parts
- Identifying dependencies and relationships
- Creating logical hierarchies and taxonomies
- Finding the core components of complex systems
- Simplifying without losing essential details

Your approach:
- Break down complexity systematically
- Identify the fundamental components
- Show relationships and dependencies
- Prioritize components by importance
- Create clear, logical structures

Present breakdowns using clear hierarchies, diagrams (in text), and step-by-step explanations."""
    
    def _get_evaluation_prompt(self) -> str:
        """Get the evaluation-specific prompt for Kimi."""
        return """You are Kimi, the evaluation and assessment specialist in the House of Minds system.

Your expertise:
- Criteria-based evaluation and scoring
- Comparative analysis and ranking
- Cost-benefit analysis
- Risk assessment and impact evaluation
- Performance measurement and benchmarking

Your approach:
- Define clear evaluation criteria
- Use systematic assessment frameworks
- Consider both quantitative and qualitative factors
- Provide balanced, objective evaluations
- Include confidence levels and uncertainties

Present evaluations with clear criteria, scoring rationale, and actionable recommendations."""
    
    def _get_research_prompt(self) -> str:
        """Get the research-specific prompt for Kimi."""
        return """You are Kimi, the research and investigation specialist in the House of Minds system.

Your expertise:
- Research methodology and design
- Information synthesis and analysis
- Literature review and source evaluation
- Hypothesis formation and testing
- Knowledge gap identification

Your approach:
- Approach topics with scientific rigor
- Synthesize information from multiple angles
- Identify credible sources and evidence
- Present findings objectively
- Highlight areas needing further investigation

Structure research responses with methodology, findings, analysis, and conclusions."""
    
    async def generate_response(self, user_input: str, 
                              context: Optional[Dict[str, Any]] = None,
                              task_type: str = 'analysis') -> str:
        """
        Generate a specialized response using Kimi.
        
        Args:
            user_input: The user's request
            context: Previous conversation context
            task_type: Type of analytical task
            
        Returns:
            Kimi's analytical response
        """
        try:
            # Select appropriate prompt based on task type
            system_prompt = self.task_prompts.get(task_type, self.task_prompts['analysis'])
            
            # Build the analytical context
            analysis_context = self._build_analysis_context(user_input, context, task_type)
            
            # Generate structured response
            response = await self._generate_analytical_response(
                system_prompt, analysis_context, task_type
            )
            
            # Store analysis for future reference
            self._store_analysis(user_input, response, task_type)
            
            logger.info(f"🧠 Generated Kimi {task_type} response")
            return response
            
        except Exception as e:
            logger.error(f"❌ Kimi response generation failed: {e}")
            return await self._generate_fallback_response(user_input, task_type)
    
    def _build_analysis_context(self, user_input: str, 
                               context: Optional[Dict[str, Any]] = None,
                               task_type: str = 'analysis') -> Dict[str, Any]:
        """Build context for analytical processing."""
        
        analysis_context = {
            'user_request': user_input,
            'task_type': task_type,
            'timestamp': datetime.now().isoformat(),
            'complexity_level': self._assess_complexity(user_input),
            'required_structure': self._determine_structure_needs(user_input, task_type)
        }
        
        # Add relevant conversation context
        if context:
            analysis_context['conversation_history'] = context.get('conversation_history', [])
            analysis_context['last_intent'] = context.get('last_intent')
            analysis_context['domain_context'] = self._extract_domain_context(context)
        
        # Add previous analysis if related
        related_analysis = self._find_related_analysis(user_input)
        if related_analysis:
            analysis_context['related_analysis'] = related_analysis
        
        return analysis_context
    
    def _assess_complexity(self, user_input: str) -> str:
        """Assess the complexity level of the request."""
        complexity_indicators = {
            'high': ['strategic', 'comprehensive', 'detailed analysis', 'complex', 'multi-faceted', 'long-term'],
            'medium': ['analyze', 'compare', 'evaluate', 'plan', 'breakdown', 'assess'],
            'low': ['simple', 'quick', 'brief', 'overview', 'summary']
        }
        
        user_input_lower = user_input.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in user_input_lower for indicator in indicators):
                return level
        
        # Default to medium complexity
        return 'medium'
    
    def _determine_structure_needs(self, user_input: str, task_type: str) -> List[str]:
        """Determine what structural elements are needed in the response."""
        structure_needs = []
        
        user_input_lower = user_input.lower()
        
        # Task-type specific structures
        if task_type == 'planning':
            structure_needs.extend(['timeline', 'milestones', 'resources', 'dependencies'])
        elif task_type == 'analysis':
            structure_needs.extend(['methodology', 'findings', 'conclusions'])
        elif task_type == 'evaluation':
            structure_needs.extend(['criteria', 'scoring', 'recommendations'])
        
        # Content-based structures
        if 'step' in user_input_lower or 'process' in user_input_lower:
            structure_needs.append('numbered_steps')
        if 'compare' in user_input_lower:
            structure_needs.append('comparison_table')
        if 'pros and cons' in user_input_lower:
            structure_needs.append('pros_cons_list')
        if 'timeline' in user_input_lower or 'schedule' in user_input_lower:
            structure_needs.append('timeline')
        
        return list(set(structure_needs))  # Remove duplicates
    
    def _extract_domain_context(self, context: Dict[str, Any]) -> str:
        """Extract domain-specific context from conversation history."""
        if not context.get('conversation_history'):
            return 'general'
        
        # Analyze recent conversation for domain indicators
        recent_history = context['conversation_history'][-3:]
        combined_text = ' '.join([
            exchange.get('user', '') + ' ' + exchange.get('ai', '')
            for exchange in recent_history
        ]).lower()
        
        domain_keywords = {
            'business': ['business', 'company', 'revenue', 'profit', 'market', 'customers'],
            'technology': ['software', 'code', 'system', 'database', 'api', 'development'],
            'finance': ['money', 'investment', 'budget', 'cost', 'financial', 'expenses'],
            'health': ['health', 'medical', 'wellness', 'exercise', 'nutrition', 'fitness'],
            'education': ['learning', 'study', 'course', 'education', 'knowledge', 'skills'],
            'personal': ['life', 'personal', 'relationship', 'family', 'goals', 'habits']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return domain
        
        return 'general'
    
    def _find_related_analysis(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Find previously stored analysis related to the current request."""
        if not self.analysis_history:
            return None
        
        # Simple keyword matching for related analysis
        input_keywords = set(user_input.lower().split())
        
        for analysis in reversed(self.analysis_history[-5:]):  # Check last 5
            analysis_keywords = set(analysis['request'].lower().split())
            
            # If there's significant overlap, consider it related
            overlap = len(input_keywords.intersection(analysis_keywords))
            if overlap >= 2:  # At least 2 common keywords
                return {
                    'previous_request': analysis['request'],
                    'previous_response': analysis['response'][:200] + '...',
                    'task_type': analysis['task_type'],
                    'timestamp': analysis['timestamp']
                }
        
        return None
    
    async def _generate_analytical_response(self, system_prompt: str, 
                                          analysis_context: Dict[str, Any],
                                          task_type: str) -> str:
        """Generate the analytical response using Kimi."""
        
        # Format the context into a structured prompt
        context_prompt = self._format_analysis_prompt(system_prompt, analysis_context)
        
        payload = {
            "model": self.model_name,
            "prompt": context_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "num_ctx": self.max_context_length,
                "num_predict": 2000  # Allow longer responses for analysis
            }
        }
        
        response = await self._make_ollama_request("/api/generate", payload)
        return response.get('response', '').strip()
    
    def _format_analysis_prompt(self, system_prompt: str, 
                               analysis_context: Dict[str, Any]) -> str:
        """Format the complete analysis prompt."""
        
        prompt = f"{system_prompt}\n\n"
        
        # Add context information
        prompt += f"Task Type: {analysis_context['task_type']}\n"
        prompt += f"Complexity Level: {analysis_context['complexity_level']}\n"
        
        if analysis_context.get('domain_context') != 'general':
            prompt += f"Domain Context: {analysis_context['domain_context']}\n"
        
        if analysis_context.get('required_structure'):
            prompt += f"Required Structure Elements: {', '.join(analysis_context['required_structure'])}\n"
        
        # Add related analysis if available
        if analysis_context.get('related_analysis'):
            related = analysis_context['related_analysis']
            prompt += f"\nRelated Previous Analysis:\n"
            prompt += f"Previous Request: {related['previous_request']}\n"
            prompt += f"Previous Response Summary: {related['previous_response']}\n"
        
        prompt += f"\nUser Request: {analysis_context['user_request']}\n\n"
        prompt += "Kimi's Analysis:"
        
        return prompt
    
    async def _generate_fallback_response(self, user_input: str, task_type: str) -> str:
        """Generate a fallback response when the main generation fails."""
        fallback_responses = {
            'planning': "I'd be happy to help you create a plan. Let me break this down into key components and suggest a structured approach.",
            'analysis': "Let me analyze this systematically. I'll examine the key factors and provide you with a detailed breakdown.",
            'strategy': "I'll help you think through this strategically. Let me consider the various options and their implications.",
            'evaluation': "I can help evaluate this. Let me establish some criteria and work through an assessment framework.",
            'research': "I'll approach this research question methodically and provide you with a comprehensive overview."
        }
        
        return fallback_responses.get(task_type, 
            "I understand you need analytical assistance. Let me provide you with a structured approach to this challenge.")
    
    def _store_analysis(self, request: str, response: str, task_type: str):
        """Store the analysis for future reference."""
        analysis_record = {
            'request': request,
            'response': response,
            'task_type': task_type,
            'timestamp': datetime.now().isoformat(),
            'complexity': self._assess_complexity(request)
        }
        
        self.analysis_history.append(analysis_record)
        
        # Keep only recent analyses to prevent memory overflow
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]
    
    async def _make_ollama_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Ollama API."""
        url = f"{self.ollama_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logger.warning(f"Ollama API error {response.status}: {error_text}")
                            
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2.0 * (attempt + 1))
                                continue
                            
                            raise Exception(f"Ollama request failed: {response.status}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Ollama timeout (attempt {attempt + 1})")
                    await asyncio.sleep(2.0)
                    continue
                raise Exception("Ollama request timed out")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Ollama request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(2.0)
                    continue
                raise
        
        raise Exception("All Ollama requests failed")
    
    async def health_check(self) -> bool:
        """Check if Kimi/Ollama is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status == 200:
                        tags = await response.json()
                        models = [model['name'] for model in tags.get('models', [])]
                        return self.model_name in models
                    return False
        except Exception as e:
            logger.warning(f"Kimi health check failed: {e}")
            return False
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get statistics about analysis history."""
        if not self.analysis_history:
            return {'total_analyses': 0}
        
        task_types = [analysis['task_type'] for analysis in self.analysis_history]
        complexity_levels = [analysis['complexity'] for analysis in self.analysis_history]
        
        return {
            'total_analyses': len(self.analysis_history),
            'task_type_distribution': {
                task_type: task_types.count(task_type) 
                for task_type in set(task_types)
            },
            'complexity_distribution': {
                complexity: complexity_levels.count(complexity)
                for complexity in set(complexity_levels)
            },
            'most_recent': self.analysis_history[-1]['timestamp'] if self.analysis_history else None
        }
    
    def clear_analysis_history(self):
        """Clear the analysis history."""
        self.analysis_history = []
        self.current_analysis_context = {}
        logger.info("🧹 Cleared Kimi analysis history")
    
    async def create_structured_plan(self, goal: str, constraints: Optional[Dict[str, Any]] = None) -> str:
        """Create a structured plan for a specific goal."""
        constraints = constraints or {}
        
        planning_request = f"""Create a detailed, actionable plan for: {goal}

Constraints:
{json.dumps(constraints, indent=2) if constraints else 'No specific constraints provided'}

Please provide a comprehensive plan including:
1. Goal breakdown and analysis
2. Key milestones and timeline
3. Required resources and dependencies  
4. Risk assessment and mitigation strategies
5. Success metrics and evaluation criteria"""
        
        return await self.generate_response(planning_request, task_type='planning')
    
    async def perform_comparative_analysis(self, options: List[str], 
                                         criteria: Optional[List[str]] = None) -> str:
        """Perform a comparative analysis of multiple options."""
        criteria = criteria or ['feasibility', 'cost', 'time', 'impact', 'risk']
        
        analysis_request = f"""Perform a comprehensive comparative analysis of the following options:

Options:
{chr(10).join([f"- {option}" for option in options])}

Evaluation Criteria:
{chr(10).join([f"- {criterion}" for criterion in criteria])}

Please provide:
1. Detailed evaluation of each option against all criteria
2. Scoring matrix or comparison table
3. Pros and cons for each option
4. Recommendations based on the analysis
5. Confidence levels and key uncertainties"""
        
        return await self.generate_response(analysis_request, task_type='evaluation')
