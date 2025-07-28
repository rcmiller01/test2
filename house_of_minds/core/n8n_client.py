"""
N8N Client - Interface for workflow automation

This module provides an interface to n8n workflows for handling
utility tasks like sending emails, scheduling, file operations, etc.
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class N8NClient:
    """
    Client for interacting with n8n workflow automation.
    
    Handles execution of utility tasks through n8n webhooks
    and provides feedback on workflow completion.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the n8n client."""
        self.config = config
        self.base_url = config.get('base_url', 'http://localhost:5678')
        self.webhook_base = config.get('webhook_base', f"{self.base_url}/webhook")
        self.api_base = config.get('api_base', f"{self.base_url}/api/v1")
        self.auth_token = config.get('auth_token', os.getenv('N8N_AUTH_TOKEN'))
        
        # Workflow mappings for different task types
        self.workflow_mappings = {
            'send_email': 'email-sender',
            'send_sms': 'sms-sender',
            'schedule_reminder': 'reminder-scheduler',
            'file_operation': 'file-manager',
            'web_search': 'web-searcher',
            'weather_check': 'weather-api',
            'news_fetch': 'news-aggregator',
            'calendar_action': 'calendar-integration',
            'data_export': 'data-exporter',
            'notification': 'notification-sender'
        }
        
        # Request timeout and retry settings
        self.timeout = config.get('timeout', 30.0)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1.0)
        
        logger.info("🔧 N8N Client initialized")
    
    async def execute_workflow(self, user_input: str, task_type: str, 
                             context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute an n8n workflow based on user input and task type.
        
        Args:
            user_input: The user's request
            task_type: Type of task to execute
            context: Additional context for the workflow
            
        Returns:
            Result message from the workflow execution
        """
        try:
            # Parse the user input to extract workflow parameters
            workflow_params = await self._parse_workflow_parameters(user_input, task_type, context)
            
            # Determine the appropriate workflow
            workflow_name = self._get_workflow_for_task(task_type, workflow_params)
            
            # Execute the workflow
            result = await self._execute_webhook(workflow_name, workflow_params)
            
            # Format the response
            response = self._format_workflow_response(result, workflow_name, task_type)
            
            logger.info(f"✅ Executed n8n workflow: {workflow_name}")
            return response
            
        except Exception as e:
            logger.error(f"❌ N8N workflow execution failed: {e}")
            return f"I encountered an issue executing that task: {str(e)}. Please try again or provide more specific details."
    
    async def _parse_workflow_parameters(self, user_input: str, task_type: str, 
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse user input to extract parameters for workflow execution."""
        
        params = {
            'user_input': user_input,
            'task_type': task_type,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        # Task-specific parameter extraction
        if task_type == 'send_email':
            params.update(self._extract_email_params(user_input))
        elif task_type == 'send_sms':
            params.update(self._extract_sms_params(user_input))
        elif task_type == 'schedule_reminder':
            params.update(self._extract_reminder_params(user_input))
        elif task_type == 'file_operation':
            params.update(self._extract_file_params(user_input))
        elif task_type == 'web_search':
            params.update(self._extract_search_params(user_input))
        else:
            # Generic parameters for other workflows
            params.update(self._extract_generic_params(user_input))
        
        return params
    
    def _extract_email_params(self, user_input: str) -> Dict[str, Any]:
        """Extract email parameters from user input."""
        import re
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_input)
        
        # Extract subject from common patterns
        subject_patterns = [
            r'about\s+(.+?)(?:\s|$)',
            r'regarding\s+(.+?)(?:\s|$)',
            r'subject:\s*(.+?)(?:\s|$)'
        ]
        
        subject = "Message from AI Assistant"
        for pattern in subject_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                subject = match.group(1).strip()
                break
        
        return {
            'recipients': emails,
            'subject': subject,
            'body': user_input,
            'sender': 'ai-assistant@house-of-minds.local'
        }
    
    def _extract_sms_params(self, user_input: str) -> Dict[str, Any]:
        """Extract SMS parameters from user input."""
        import re
        
        # Extract phone numbers
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, user_input)
        formatted_phones = [f"({match[0]}) {match[1]}-{match[2]}" for match in phones]
        
        return {
            'recipients': formatted_phones,
            'message': user_input,
            'sender': 'House of Minds AI'
        }
    
    def _extract_reminder_params(self, user_input: str) -> Dict[str, Any]:
        """Extract reminder parameters from user input."""
        import re
        from dateutil import parser
        
        # Try to extract date/time information
        time_patterns = [
            r'in\s+(\d+)\s+(minutes?|hours?|days?)',
            r'at\s+(\d{1,2}:\d{2})',
            r'tomorrow',
            r'next\s+(week|month|year)',
            r'on\s+(\w+day)'
        ]
        
        reminder_time = "1 hour"  # default
        for pattern in time_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                reminder_time = match.group(0)
                break
        
        return {
            'reminder_text': user_input,
            'reminder_time': reminder_time,
            'user_id': 'default_user'
        }
    
    def _extract_file_params(self, user_input: str) -> Dict[str, Any]:
        """Extract file operation parameters from user input."""
        import re
        
        # Determine operation type
        operation = 'unknown'
        if any(word in user_input.lower() for word in ['save', 'create', 'write']):
            operation = 'save'
        elif any(word in user_input.lower() for word in ['read', 'open', 'load']):
            operation = 'read'
        elif any(word in user_input.lower() for word in ['delete', 'remove']):
            operation = 'delete'
        elif any(word in user_input.lower() for word in ['copy', 'duplicate']):
            operation = 'copy'
        
        # Extract file paths/names
        file_pattern = r'[\w\-_]+\.[a-zA-Z]{2,4}'
        files = re.findall(file_pattern, user_input)
        
        return {
            'operation': operation,
            'files': files,
            'content': user_input
        }
    
    def _extract_search_params(self, user_input: str) -> Dict[str, Any]:
        """Extract search parameters from user input."""
        # Remove search keywords to get the actual query
        search_keywords = ['search', 'find', 'look up', 'google', 'check']
        query = user_input.lower()
        
        for keyword in search_keywords:
            query = query.replace(keyword, '').strip()
        
        return {
            'query': query,
            'search_type': 'web',
            'max_results': 5
        }
    
    def _extract_generic_params(self, user_input: str) -> Dict[str, Any]:
        """Extract generic parameters for any workflow."""
        return {
            'action': 'process',
            'data': user_input,
            'priority': 'normal'
        }
    
    def _get_workflow_for_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """Determine which workflow to use for a given task type."""
        
        # Direct mapping from task type
        if task_type in self.workflow_mappings:
            return self.workflow_mappings[task_type]
        
        # Fallback logic based on content
        if 'email' in params.get('user_input', '').lower():
            return self.workflow_mappings['send_email']
        elif 'reminder' in params.get('user_input', '').lower():
            return self.workflow_mappings['schedule_reminder']
        elif 'search' in params.get('user_input', '').lower():
            return self.workflow_mappings['web_search']
        else:
            return 'generic-utility'  # Default workflow
    
    async def _execute_webhook(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an n8n workflow via webhook."""
        webhook_url = f"{self.webhook_base}/{workflow_name}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook_url,
                        json=params,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            return result
                        else:
                            error_text = await response.text()
                            logger.warning(f"Webhook error {response.status}: {error_text}")
                            
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            
                            raise Exception(f"Webhook execution failed: {response.status} - {error_text}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Webhook timeout (attempt {attempt + 1})")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise Exception("Webhook request timed out")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Webhook request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
        
        raise Exception("All webhook attempts failed")
    
    def _format_workflow_response(self, result: Dict[str, Any], workflow_name: str, task_type: str) -> str:
        """Format the workflow execution result into a user-friendly response."""
        
        # Check if workflow executed successfully
        if result.get('success', False):
            
            # Task-specific response formatting
            if task_type == 'send_email':
                recipients = result.get('recipients', [])
                return f"✅ Email sent successfully to {', '.join(recipients)}"
            
            elif task_type == 'send_sms':
                recipients = result.get('recipients', [])
                return f"✅ SMS sent successfully to {', '.join(recipients)}"
            
            elif task_type == 'schedule_reminder':
                reminder_time = result.get('scheduled_time', 'soon')
                return f"✅ Reminder scheduled for {reminder_time}"
            
            elif task_type == 'file_operation':
                operation = result.get('operation', 'file operation')
                return f"✅ {operation.title()} completed successfully"
            
            elif task_type == 'web_search':
                results_count = result.get('results_count', 0)
                return f"✅ Found {results_count} search results: {result.get('summary', '')}"
            
            else:
                return f"✅ Task completed successfully via {workflow_name}"
        
        else:
            error_message = result.get('error', 'Unknown error occurred')
            return f"❌ Task failed: {error_message}"
    
    async def health_check(self) -> bool:
        """Check if n8n is accessible and healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/healthz",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"N8N health check failed: {e}")
            return False
    
    def get_available_workflows(self) -> Dict[str, str]:
        """Get mapping of available workflows."""
        return self.workflow_mappings.copy()
    
    def add_workflow_mapping(self, task_type: str, workflow_name: str):
        """Add a new workflow mapping."""
        self.workflow_mappings[task_type] = workflow_name
        logger.info(f"➕ Added workflow mapping: {task_type} -> {workflow_name}")
    
    def remove_workflow_mapping(self, task_type: str):
        """Remove a workflow mapping."""
        if task_type in self.workflow_mappings:
            del self.workflow_mappings[task_type]
            logger.info(f"➖ Removed workflow mapping: {task_type}")
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List currently active workflows in n8n."""
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/workflows",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    
                    if response.status == 200:
                        workflows = await response.json()
                        return workflows.get('data', [])
                    else:
                        logger.warning(f"Failed to list workflows: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return []
    
    async def get_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """Get the status of a specific workflow."""
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/workflows/{workflow_name}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {'error': f'Workflow not found: {workflow_name}'}
        
        except Exception as e:
            return {'error': str(e)}
