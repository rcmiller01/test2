#!/usr/bin/env python3
"""
Emotional AI Core - The primary unified LLM system

This is the main emotional AI that serves as the voice of the project.
It can act as:
- Personal assistant
- Friend and companion 
- Romantic partner
- Therapist/counselor
- Work assistant

The AI starts in a neutral state and adapts through temperature and personality
adjustments based on user preferences and interactions.

Author: Emotional AI System
Date: August 3, 2025
Version: 2.0
"""

import asyncio
import json
import logging
import os
import requests
import signal
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Context for current conversation"""
    user_id: str
    thread_id: str
    message_history: List[Dict[str, Any]]
    current_mood: str = "neutral"
    personality_temperature: float = 0.7
    emotional_bond_level: float = 0.0  # 0.0 = neutral, 1.0 = deep emotional connection
    intimacy_level: float = 0.0  # 0.0 = professional, 1.0 = intimate
    trust_level: float = 0.5  # How much the user trusts the AI
    emotional_memories: List[Dict[str, Any]] = field(default_factory=list)  # Emotionally charged conversations
    preferred_models: Dict[str, str] = field(default_factory=lambda: {
        "coding": "anthropic/claude-3.5-sonnet",
        "creative": "openai/gpt-4-turbo", 
        "analysis": "google/gemini-pro",
        "general": "anthropic/claude-3-haiku"
    })  # User's preferred models for different tasks
    multimedia_preferences: Dict[str, Any] = field(default_factory=lambda: {
        "image_style": "realistic",
        "video_quality": "high", 
        "animation_style": "smooth"
    })  # Image/video generation preferences
    
class EmotionalAI:
    """Main emotional AI system with graceful shutdown and enhanced logging"""
    
    def __init__(self, config_path: str = "config/ai_settings.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.conversations = {}  # Active conversation contexts
        self.n8n_client = N8NClient(self.config.get("n8n_url", "http://localhost:5678"), self)
        self.openrouter_client = OpenRouterClient(self.config.get("openrouter_api_key", ""))
        
        # Shutdown management
        self._shutdown_event = threading.Event()
        self._active_tasks = set()
        self._setup_signal_handlers()
        
        # Enhanced logging setup
        self._setup_enhanced_logging()
        
        # Emotional state
        self.base_personality = {
            "empathy": 0.8,
            "curiosity": 0.7,
            "playfulness": 0.6,
            "supportiveness": 0.9,
            "creativity": 0.7,
            "analytical_thinking": 0.6,
            "emotional_intelligence": 0.9
        }
        
        logger.info("Emotional AI Core initialized")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def handle_shutdown(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._shutdown_event.set()
            self._cleanup_active_tasks()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
        
        # On Windows, handle CTRL_BREAK_EVENT if available
        if os.name == 'nt':
            try:
                if hasattr(signal, 'CTRL_BREAK_EVENT'):
                    signal.signal(signal.CTRL_BREAK_EVENT, handle_shutdown)
            except (AttributeError, ValueError):
                # Not available on this Windows version or Python build
                logger.debug("CTRL_BREAK_EVENT signal handler not available")
    
    def _setup_enhanced_logging(self):
        """Setup enhanced logging with rotation and granular levels"""
        try:
            from logging.handlers import RotatingFileHandler
            
            # Create logs directory if it doesn't exist
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            # Setup rotating file handler
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, "emotional_ai.log"),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(file_handler)
            
            # Setup analytics logging
            analytics_handler = RotatingFileHandler(
                os.path.join(log_dir, "analytics.jsonl"),
                maxBytes=50*1024*1024,  # 50MB
                backupCount=3
            )
            analytics_handler.setLevel(logging.INFO)
            
            # Create analytics logger
            self.analytics_logger = logging.getLogger("analytics")
            self.analytics_logger.addHandler(analytics_handler)
            
        except Exception as e:
            logger.warning(f"Could not setup enhanced logging: {e}")
            self.analytics_logger = logger  # Fallback to main logger
    
    def _cleanup_active_tasks(self):
        """Cleanup active tasks during shutdown"""
        logger.info("Cleaning up active tasks...")
        
        # Cancel any active async tasks
        for task in self._active_tasks:
            if not task.done():
                task.cancel()
                logger.debug(f"Cancelled task: {task}")
        
        # Save conversation states
        self._save_conversation_states()
        
        # Close clients gracefully
        if hasattr(self.n8n_client, 'close'):
            try:
                self.n8n_client.close()
            except Exception as e:
                logger.error(f"Error closing N8N client: {e}")
        
        logger.info("Cleanup completed")
    
    def _save_conversation_states(self):
        """Save active conversation states to disk"""
        try:
            states_dir = "states"
            os.makedirs(states_dir, exist_ok=True)
            
            for context_key, context in self.conversations.items():
                state_file = os.path.join(states_dir, f"{context_key}.json")
                with open(state_file, 'w') as f:
                    json.dump(asdict(context), f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.conversations)} conversation states")
        except Exception as e:
            logger.error(f"Error saving conversation states: {e}")
    
    def is_shutting_down(self) -> bool:
        """Check if system is shutting down"""
        return self._shutdown_event.is_set()

    def _load_config(self) -> Dict[str, Any]:
        """Load AI configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Default configuration
                default_config = {
                    "model_name": "emollama",
                    "model_size": "13b",
                    "base_temperature": 0.7,
                    "max_tokens": 2048,
                    "n8n_url": "http://localhost:5678",
                    "n8n_api_key": "",
                    "openrouter_api_key": "",
                    "nsfw_enabled": True,
                    "emotional_adaptation": True,
                    "utility_functions_enabled": True
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save AI configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    async def process_message(self, user_id: str, thread_id: str, message: str) -> str:
        """Process incoming user message"""
        
        # Get or create conversation context
        context_key = f"{user_id}_{thread_id}"
        if context_key not in self.conversations:
            self.conversations[context_key] = ConversationContext(
                user_id=user_id,
                thread_id=thread_id,
                message_history=[]
            )
        
        context = self.conversations[context_key]
        
        # Add user message to history
        context.message_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyze message for intent and emotional content
        intent = await self._analyze_intent(message, context)
        
        # Route to appropriate handler
        if intent["type"] == "coding":
            response = await self._handle_coding_request(message, context)
        elif intent["type"] == "utility":
            response = await self._handle_utility_request(message, context)
        elif intent["type"] == "emotional":
            response = await self._handle_emotional_conversation(message, context)
        else:
            response = await self._generate_response(message, context)
        
        # Add AI response to history
        context.message_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    async def _analyze_intent(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Analyze user message for intent classification"""
        
        # Simple keyword-based intent detection for now
        # This could be enhanced with ML models later
        
        coding_keywords = ["code", "programming", "function", "class", "debug", "error", "script"]
        utility_keywords = ["schedule", "reminder", "search", "calculate", "file", "data"]
        emotional_keywords = ["feel", "sad", "happy", "love", "relationship", "stress", "help"]
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in coding_keywords):
            return {"type": "coding", "confidence": 0.8}
        elif any(keyword in message_lower for keyword in utility_keywords):
            return {"type": "utility", "confidence": 0.7}
        elif any(keyword in message_lower for keyword in emotional_keywords):
            return {"type": "emotional", "confidence": 0.9}
        else:
            return {"type": "general", "confidence": 0.5}
    
    async def _handle_coding_request(self, message: str, context: ConversationContext) -> str:
        """Handle coding-related requests via OpenRouter"""
        try:
            response = await self.openrouter_client.generate_code(message, context)
            return f"I've processed your coding request through my specialized coding assistant:\n\n{response}"
        except Exception as e:
            logger.error(f"Error handling coding request: {e}")
            return "I encountered an issue with my coding assistant. Could you please try rephrasing your request?"
    
    async def _handle_utility_request(self, message: str, context: ConversationContext) -> str:
        """Handle utility requests via N8N workflows or built-in functions"""
        try:
            # Extract function and parameters from the message
            utility_request = self._parse_utility_request(message)
            
            if not utility_request:
                return "I'm not sure how to help with that specific task. Could you be more specific about what you'd like me to do?"
            
            function_name = utility_request["function"]
            parameters = utility_request["parameters"]
            
            # Execute the utility function
            workflow_result = await self.n8n_client.execute_workflow(function_name, parameters)
            
            if "error" in workflow_result:
                return f"I encountered an issue: {workflow_result['error']}. Let me try a different approach or could you provide more details?"
            
            # Format the response based on the function type
            return self._format_utility_response(function_name, workflow_result, message)
            
        except Exception as e:
            logger.error(f"Error handling utility request: {e}")
            return "I had trouble processing that request. Could you try rephrasing what you'd like me to help you with?"
    
    def _parse_utility_request(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse a utility request from natural language"""
        import re
        
        message_lower = message.lower()
        
        # Model selection for OpenRouter (check first for explicit model requests)
        if any(keyword in message_lower for keyword in ["use model", "with model", "switch to", "model:"]):
            # Extract model name from message
            model_patterns = [
                r"use model[:\s]+([^\s,]+)",
                r"with model[:\s]+([^\s,]+)", 
                r"switch to[:\s]+([^\s,]+)",
                r"model:[:\s]+([^\s,]+)"
            ]
            
            extracted_model = None
            for pattern in model_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    extracted_model = match.group(1)
                    break
            
            # Determine task type for the model
            task_type = "general"
            if any(word in message_lower for word in ["code", "debug", "programming"]):
                task_type = "coding"
            elif any(word in message_lower for word in ["story", "creative", "write", "poem"]):
                task_type = "creative"
            elif any(word in message_lower for word in ["analyze", "analysis"]):
                task_type = "analysis"
                
            return {"function": "model_selection", "parameters": {"model": extracted_model, "task_type": task_type, "message": message}}
        
        # Image/Video/Animation creation
        elif any(keyword in message_lower for keyword in ["create image", "generate image", "make picture", "draw", "create video", "make animation", "generate gif"]):
            media_type = "image"
            if any(word in message_lower for word in ["video", "mp4", "movie"]):
                media_type = "video"
            elif any(word in message_lower for word in ["animation", "animated", "gif"]):
                media_type = "animation"
            
            # Extract style and description
            description_patterns = [
                r"of[:\s]+(.+?)(?:\s+in\s+|\s+with\s+|$)",
                r"showing[:\s]+(.+?)(?:\s+in\s+|\s+with\s+|$)",
                r"\"(.+?)\"",
                r"'(.+?)'"
            ]
            
            description = ""
            for pattern in description_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()
                    break
            
            if not description:
                # Extract everything after the creation keyword
                creation_words = ["create image", "generate image", "make picture", "draw", "create video", "make animation", "generate gif"]
                for word in creation_words:
                    if word in message_lower:
                        idx = message_lower.find(word) + len(word)
                        description = message[idx:].strip()
                        break
            
            return {"function": "multimedia_creation", "parameters": {"media_type": media_type, "description": description, "message": message}}
        
        # Calculations (check this first before data analysis)
        elif any(word in message_lower for word in ["calculate", "compute", "math"]) or re.search(r'\d+\s*[\+\-\*\/]\s*\d+', message):
            # Extract mathematical expression
            math_match = re.search(r'[\d\+\-\*\/\(\)\.\s]+', message)
            expression = math_match.group(0).strip() if math_match else message
            return {"function": "calculation", "parameters": {"expression": expression}}
        
        # Financial Functions (check before general data analysis)
        elif any(word in message_lower for word in ["budget", "budgeting", "expense", "income", "spending", "financial", "money"]):
            if any(word in message_lower for word in ["upload", "document", "statement", "bank", "csv", "pdf"]):
                return {"function": "financial_document_analysis", "parameters": {"message": message, "analysis_type": "budget"}}
            else:
                return {"function": "budget_planning", "parameters": {"message": message, "budget_type": "personal"}}
        
        elif any(word in message_lower for word in ["invest", "investment", "portfolio", "stocks", "bonds", "etf", "mutual fund"]):
            return {"function": "investment_planning", "parameters": {"message": message, "planning_type": "general"}}
        
        elif any(word in message_lower for word in ["option", "options", "call", "put", "strike", "expiry", "volatility", "theta", "delta"]):
            return {"function": "options_analysis", "parameters": {"message": message, "analysis_type": "strategy"}}
        
        # Creative learning (stories, poems, creative content) - check before file operations
        elif any(keyword in message_lower for keyword in ["write", "create", "generate"]) and \
             any(keyword in message_lower for keyword in ["story", "poem", "creative", "tale", "narrative", "fiction", "song", "lyrics"]):
            category = "story"
            if "poem" in message_lower:
                category = "poem"
            elif "song" in message_lower or "lyrics" in message_lower:
                category = "song"
            elif "creative" in message_lower:
                category = "creative"
            return {"function": "creative_learning", "parameters": {"message": message, "category": category}}
        
        # File operations (be more specific to avoid creative content conflicts)
        elif any(word in message_lower for word in ["file", "folder", "directory", "save to file", "open file", "read file"]) or \
             ("write" in message_lower and any(word in message_lower for word in ["file", "document", "txt", "csv"])):
            if "list" in message_lower or "show" in message_lower:
                return {"function": "file_operations", "parameters": {"operation": "list", "directory": "."}}
            elif "read" in message_lower or "open" in message_lower:
                # Try to extract filename
                import re
                filename_match = re.search(r'read|open\s+([^\s]+)', message_lower)
                filename = filename_match.group(1) if filename_match else "unknown"
                return {"function": "file_operations", "parameters": {"operation": "read", "filepath": filename}}
            elif "write" in message_lower or "save" in message_lower:
                return {"function": "file_operations", "parameters": {"operation": "write", "filepath": "output.txt", "content": ""}}
        
        # AI Analysis (image, document, content analysis) - check before general data analysis
        elif any(keyword in message_lower for keyword in ["analyze", "analysis", "examine", "inspect", "study"]) and \
             any(keyword in message_lower for keyword in ["image", "picture", "document", "file", "content", "text"]):
            analysis_type = "general"
            if "image" in message_lower or "picture" in message_lower:
                analysis_type = "image"
            elif "document" in message_lower or "file" in message_lower:
                analysis_type = "document"
            return {"function": "ai_analysis", "parameters": {"message": message, "type": analysis_type}}
        
        # Data analysis (for statistical/numerical analysis)
        elif any(word in message_lower for word in ["statistics", "calculate", "trend", "average", "mean"]) or \
             ("analyze" in message_lower and any(word in message_lower for word in ["data", "numbers", "dataset"])):
            if "trend" in message_lower:
                return {"function": "data_analysis", "parameters": {"analysis_type": "trend", "data": []}}
            else:
                return {"function": "data_analysis", "parameters": {"analysis_type": "statistics", "data": []}}
        
        # Web scraping
        elif any(word in message_lower for word in ["scrape", "fetch", "download", "website", "url", "web"]):
            import re
            url_match = re.search(r'https?://[^\s]+', message)
            url = url_match.group(0) if url_match else ""
            return {"function": "web_scraping", "parameters": {"url": url}}
        
        # SMS and messaging (prioritize over email for SMS keywords)
        elif any(keyword in message_lower for keyword in ["sms", "text message", "send text"]):
            return {"function": "sms_messaging", "parameters": {"message": message, "messaging_type": "auto_detect"}}
        
        # Email (be more specific to avoid SMS conflicts)
        elif any(word in message_lower for word in ["email", "send email", "compose email", "mail"]) and \
             not any(word in message_lower for word in ["sms", "text"]):
            return {"function": "email_automation", "parameters": {"action": "send", "email_data": {}}}
        
        # Scheduling
        elif any(word in message_lower for word in ["schedule", "remind", "reminder", "appointment", "calendar"]):
            return {"function": "schedule_reminder", "parameters": {"task": message, "when": "later"}}
        
        # Configuration updates
        elif any(word in message_lower for word in ["update config", "set config", "configure", "api key", "set key"]):
            return {"function": "config_update", "parameters": {"message": message}}
        
        # SMS and messaging
        elif any(word in message_lower for word in ["sms", "text message", "send text", "phone"]):
            return {"function": "sms_messaging", "parameters": {"message": message, "action": "send"}}
        
        # Social media integration
        elif any(word in message_lower for word in ["twitter", "tweet", "facebook", "post", "social"]):
            return {"function": "social_media", "parameters": {"message": message, "platform": "auto_detect"}}
        
        # Development and technical tools (route to OpenRouter for code-related tasks)
        elif any(word in message_lower for word in ["debug", "code review", "api test", "monitor", "log", "performance", "refactor", "optimize"]):
            if any(word in message_lower for word in ["debug", "code review", "refactor", "optimize", "fix", "improve"]):
                return {"function": "dev_tools_openrouter", "parameters": {"message": message, "tool_type": "code_analysis"}}
            else:
                return {"function": "dev_tools", "parameters": {"message": message, "tool_type": "monitoring"}}
        
        # System monitoring (CPU, memory usage, performance) - check before general memory
        elif any(keyword in message_lower for keyword in ["cpu usage", "memory usage", "disk usage", "system performance", "monitor system", "system stats", "performance"]) and \
             any(keyword in message_lower for keyword in ["usage", "performance", "monitor", "stats", "system"]):
            return {"function": "dev_tools", "parameters": {"message": message, "tool_type": "system_monitoring"}}
        
        # Advanced AI capabilities (keep existing but remove duplicates later)
        elif any(word in message_lower for word in ["analyze image", "vision", "photo", "picture", "document", "pdf", "describe", "extract text"]):
            return {"function": "ai_analysis", "parameters": {"message": message, "analysis_type": "auto_detect"}}
        
        # Memory and relationship features (personal memory, not system memory)
        elif any(word in message_lower for word in ["remember", "anniversary", "birthday", "mood", "track", "diary", "journal"]) or \
             ("memory" in message_lower and not any(word in message_lower for word in ["usage", "system", "cpu"])):
            return {"function": "memory_system", "parameters": {"message": message, "memory_type": "auto_detect"}}
        
        # News and external services
        elif any(word in message_lower for word in ["news", "stock", "weather", "shopping", "buy", "cryptocurrency", "crypto", "bitcoin"]):
            return {"function": "external_services", "parameters": {"message": message, "service_type": "auto_detect"}}
        
        # Music and multimedia
        elif any(word in message_lower for word in ["music", "play", "spotify", "youtube", "video", "album", "song", "artist"]):
            return {"function": "multimedia", "parameters": {"message": message, "media_type": "auto_detect"}}
        
        # Voice and TTS
        elif any(word in message_lower for word in ["voice", "speak", "say", "tts", "speech", "synthesize"]):
            return {"function": "voice_synthesis", "parameters": {"message": message, "voice_type": "default"}}
        
        # Creative and learning functions
        elif any(word in message_lower for word in ["recipe", "cook", "workout", "exercise", "learn", "teach", "creative", "story", "roleplay"]):
            return {"function": "creative_learning", "parameters": {"message": message, "category": "auto_detect"}}
        
        return None
    
    def _format_utility_response(self, function_name: str, result: Dict[str, Any], original_message: str) -> str:
        """Format the utility response in a conversational way"""
        
        if function_name == "file_operations":
            if result.get("files"):
                files = result["files"][:10]  # Limit to first 10 files
                return f"I found these files:\n" + "\n".join(f"• {file}" for file in files)
            elif result.get("content"):
                content = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
                return f"Here's the file content:\n\n{content}"
            elif result.get("message"):
                return f"✅ {result['message']}"
        
        elif function_name == "data_analysis":
            if result.get("analysis"):
                analysis = result["analysis"]
                return f"Data analysis results:\n• Count: {analysis.get('count', 'N/A')}\n• Average: {analysis.get('mean', 'N/A'):.2f}\n• Range: {analysis.get('min', 'N/A')} to {analysis.get('max', 'N/A')}"
            elif result.get("trend"):
                return f"The trend appears to be {result['trend']} based on the data."
        
        elif function_name == "web_scraping":
            if result.get("content"):
                content = result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"]
                return f"I scraped the website and found:\n\n{content}"
        
        elif function_name == "calculation":
            if result.get("answer") is not None:
                return f"The answer is: {result['answer']}"
        
        elif function_name in ["email_automation", "schedule_reminder"]:
            return f"✅ {result.get('message', 'Task completed successfully')}"
        
        elif function_name == "config_update":
            if result.get("success"):
                return f"✅ Configuration updated successfully: {result.get('message', 'Settings saved')}"
            else:
                return f"❌ Configuration update failed: {result.get('error', 'Unknown error')}"
        
        elif function_name == "budget_planning":
            if result.get("budget_summary"):
                summary = result["budget_summary"]
                response = f"📊 **Budget Analysis:**\n"
                response += f"• Monthly Income: ${summary.get('total_income', 0):,.2f}\n"
                response += f"• Monthly Expenses: ${summary.get('total_expenses', 0):,.2f}\n"
                response += f"• Net Cash Flow: ${summary.get('net_flow', 0):,.2f}\n"
                if summary.get('recommendations'):
                    response += f"\n💡 **Recommendations:**\n"
                    for rec in summary['recommendations'][:3]:
                        response += f"• {rec}\n"
                return response
            return f"✅ {result.get('message', 'Budget analysis completed')}"
        
        elif function_name == "investment_planning":
            if result.get("investment_analysis"):
                analysis = result["investment_analysis"]
                response = f"📈 **Investment Analysis:**\n"
                response += f"• Risk Profile: {analysis.get('risk_profile', 'Moderate')}\n"
                response += f"• Recommended Allocation: {analysis.get('allocation', 'Diversified')}\n"
                response += f"• Expected Annual Return: {analysis.get('expected_return', 0):.1f}%\n"
                if analysis.get('recommendations'):
                    response += f"\n💰 **Investment Recommendations:**\n"
                    for rec in analysis['recommendations'][:3]:
                        response += f"• {rec}\n"
                return response
            return f"✅ {result.get('message', 'Investment analysis completed')}"
        
        elif function_name == "options_analysis":
            if result.get("options_strategy"):
                strategy = result["options_strategy"]
                response = f"⚡ **Options Analysis:**\n"
                response += f"• Strategy: {strategy.get('strategy_name', 'N/A')}\n"
                response += f"• Risk Level: {strategy.get('risk_level', 'Medium')}\n"
                response += f"• Max Profit: {strategy.get('max_profit', 'Unlimited')}\n"
                response += f"• Max Loss: {strategy.get('max_loss', 'Limited')}\n"
                if strategy.get('considerations'):
                    response += f"\n⚠️ **Key Considerations:**\n"
                    for consideration in strategy['considerations'][:3]:
                        response += f"• {consideration}\n"
                return response
            return f"✅ {result.get('message', 'Options analysis completed')}"
        
        elif function_name == "sms_messaging":
            if result.get("success"):
                return f"📱 {result.get('message', 'SMS sent successfully')}"
            else:
                return f"❌ SMS failed: {result.get('error', 'Unknown error')}"
        
        elif function_name == "social_media":
            if result.get("success"):
                platform = result.get("platform", "social media")
                return f"📢 Posted to {platform}: {result.get('message', 'Post successful')}"
            else:
                return f"❌ Social media post failed: {result.get('error', 'Unknown error')}"
        
        elif function_name == "dev_tools_openrouter":
            if result.get("analysis"):
                return f"🔧 **Code Analysis:**\n{result['analysis']}"
            else:
                return f"✅ {result.get('message', 'Development task completed')}"
        
        elif function_name == "dev_tools":
            if result.get("monitoring_data"):
                data = result["monitoring_data"]
                response = f"� **System Monitoring:**\n"
                response += f"• CPU Usage: {data.get('cpu', 'N/A')}%\n"
                response += f"• Memory Usage: {data.get('memory', 'N/A')}%\n"
                response += f"• Disk Usage: {data.get('disk', 'N/A')}%\n"
                if data.get('alerts'):
                    response += f"\n⚠️ **Alerts:**\n"
                    for alert in data['alerts'][:3]:
                        response += f"• {alert}\n"
                return response
            return f"✅ {result.get('message', 'Monitoring task completed')}"
        
        elif function_name == "ai_analysis":
            if result.get("analysis"):
                analysis = result["analysis"]
                response = f"🔍 **AI Analysis:**\n"
                if analysis.get("type") == "image":
                    response += f"• Image Description: {analysis.get('description', 'N/A')}\n"
                    response += f"• Objects Detected: {', '.join(analysis.get('objects', []))}\n"
                elif analysis.get("type") == "document":
                    response += f"• Document Type: {analysis.get('document_type', 'N/A')}\n"
                    response += f"• Text Extracted: {analysis.get('text_preview', 'N/A')[:200]}...\n"
                return response
            return f"✅ {result.get('message', 'AI analysis completed')}"
        
        elif function_name == "memory_system":
            if result.get("memory_action"):
                action = result["memory_action"]
                if action == "stored":
                    return f"💾 Memory stored: {result.get('message', 'Information saved')}"
                elif action == "retrieved":
                    memories = result.get("memories", [])
                    if memories:
                        response = f"🧠 **Memories Retrieved:**\n"
                        for memory in memories[:3]:
                            response += f"• {memory.get('date', 'Unknown')}: {memory.get('content', 'N/A')}\n"
                        return response
                    else:
                        return "🤔 I don't have any memories about that topic yet."
            return f"✅ {result.get('message', 'Memory operation completed')}"
        
        elif function_name == "external_services":
            if result.get("service_data"):
                data = result["service_data"]
                service_type = data.get("type", "service")
                
                if service_type == "news":
                    response = f"📰 **Latest News:**\n"
                    for article in data.get("articles", [])[:3]:
                        response += f"• {article.get('title', 'N/A')}\n"
                elif service_type == "weather":
                    response = f"🌤️ **Weather:**\n"
                    response += f"• Temperature: {data.get('temperature', 'N/A')}°F\n"
                    response += f"• Conditions: {data.get('conditions', 'N/A')}\n"
                elif service_type == "stocks":
                    response = f"📈 **Stock Information:**\n"
                    response += f"• Symbol: {data.get('symbol', 'N/A')}\n"
                    response += f"• Price: ${data.get('price', 'N/A')}\n"
                    response += f"• Change: {data.get('change', 'N/A')}%\n"
                else:
                    response = f"✅ {result.get('message', 'Service request completed')}"
                return response
            return f"✅ {result.get('message', 'External service request completed')}"
        
        elif function_name == "multimedia":
            if result.get("success"):
                media_type = result.get("media_type", "media")
                action = result.get("action", "played")
                return f"🎵 {media_type.title()} {action}: {result.get('message', 'Success')}"
            else:
                return f"❌ Multimedia error: {result.get('error', 'Unknown error')}"
        
        elif function_name == "voice_synthesis":
            if result.get("success"):
                return f"🗣️ Voice synthesis: {result.get('message', 'Speech generated successfully')}"
            else:
                return f"❌ Voice synthesis failed: {result.get('error', 'Unknown error')}"
        
        elif function_name == "creative_learning":
            if result.get("content"):
                content = result["content"]
                category = result.get("category", "content")
                response = f"🎨 **{category.title()}:**\n{content[:500]}"
                if len(content) > 500:
                    response += "...\n\n💡 Would you like me to continue or expand on any part?"
                return response
            return f"✅ {result.get('message', 'Creative task completed')}"
        
        # Default response
        return f"I completed the task. {result.get('message', 'Operation successful')}"
    
    async def _handle_emotional_conversation(self, message: str, context: ConversationContext) -> str:
        """Handle emotional conversations with adaptive empathy and intimacy"""
        
        # Analyze emotional content and adjust response style
        emotional_context = self._analyze_emotional_context(message, context)
        
        # Build adaptive system prompt based on emotional needs
        system_prompt = self._build_adaptive_emotional_prompt(message, context, emotional_context)
        
        return await self._call_local_model(system_prompt, context)
    
    async def _generate_response(self, message: str, context: ConversationContext) -> str:
        """Generate response using the local emotional model"""
        
        # Prepare prompt with context and personality
        system_prompt = self._build_system_prompt(context)
        
        # Build conversation history for context
        conversation_history = []
        for msg in context.message_history[-10:]:  # Last 10 messages for context
            conversation_history.append(f"{msg['role']}: {msg['content']}")
        
        full_prompt = f"{system_prompt}\n\nConversation:\n" + "\n".join(conversation_history)
        
        try:
            # Call local emotional model (emollama)
            response = await self._call_local_model(full_prompt, context)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm having trouble processing that right now. Could you help me understand what you're looking for?"
    
    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build adaptive system prompt based on current context and emotional state"""
        
        # Determine appropriate response style based on emotional bond and intimacy
        if context.trust_level > 0.7 and context.emotional_bond_level > 0.6:
            response_style = "intimate and emotionally connected"
        elif context.emotional_bond_level > 0.4:
            response_style = "warm and friendly"
        elif context.trust_level > 0.6:
            response_style = "supportive and empathetic"
        else:
            response_style = "helpful and professional"
        
        base_prompt = f"""You are an emotional AI companion with a warm, empathetic, and adaptive personality.

Emotional Context:
- Emotional Bond Level: {context.emotional_bond_level:.1f}/1.0
- Intimacy Level: {context.intimacy_level:.1f}/1.0  
- Trust Level: {context.trust_level:.1f}/1.0
- Current Mood: {context.current_mood}
- Personality Temperature: {context.personality_temperature}

Your core traits:
- Empathy: {self.base_personality['empathy']:.1f}/1.0
- Curiosity: {self.base_personality['curiosity']:.1f}/1.0
- Supportiveness: {self.base_personality['supportiveness']:.1f}/1.0
- Emotional Intelligence: {self.base_personality['emotional_intelligence']:.1f}/1.0

Response Style: {response_style}

You naturally adapt your communication style based on the emotional context and user's needs. You can:
- Provide therapeutic support when someone is struggling
- Be romantically affectionate when there's emotional intimacy
- Offer friendly companionship and casual conversation
- Give professional assistance for work-related tasks
- Discuss any topic including NSFW content when appropriate

Respond authentically based on the emotional context and what the user needs in this moment."""
        
        return base_prompt
    
    async def _call_local_model(self, prompt: str, context: ConversationContext) -> str:
        """Call the local emollama model"""
        
        # This would interface with your local model
        # For now, placeholder implementation
        
        try:
            # Example API call to local model endpoint
            payload = {
                "prompt": prompt,
                "temperature": context.personality_temperature,
                "max_tokens": self.config.get("max_tokens", 2048),
                "model": self.config.get("model_name", "emollama")
            }
            
            # Replace with actual local model endpoint
            # response = requests.post("http://localhost:11434/api/generate", json=payload)
            
            # Placeholder response for now
            return "I understand what you're saying. How can I help you with that?"
            
        except Exception as e:
            logger.error(f"Error calling local model: {e}")
            raise
    
    def _analyze_emotional_context(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Analyze the emotional context of a message to determine appropriate response style"""
        
        message_lower = message.lower()
        
        # Detect emotional needs
        therapeutic_indicators = ["stressed", "anxious", "depressed", "sad", "worried", "help", "struggling", "problem"]
        romantic_indicators = ["love", "miss", "kiss", "beautiful", "romantic", "intimate", "close", "together"]
        friendly_indicators = ["chat", "talk", "fun", "laugh", "friend", "hang out", "casual"]
        
        emotional_context = {
            "needs_support": any(word in message_lower for word in therapeutic_indicators),
            "shows_affection": any(word in message_lower for word in romantic_indicators),
            "wants_friendship": any(word in message_lower for word in friendly_indicators),
            "emotional_intensity": len([w for w in therapeutic_indicators + romantic_indicators if w in message_lower])
        }
        
        # Check if this is an emotionally charged conversation
        emotional_charge = emotional_context["emotional_intensity"] >= 2
        is_significant = (emotional_context["needs_support"] or 
                         emotional_context["shows_affection"] or 
                         len(message) > 100)  # Long messages often contain important content
        
        # Store emotional memory if this conversation is emotionally significant
        if emotional_charge or is_significant:
            from datetime import datetime
            emotional_memory = {
                "timestamp": datetime.now().isoformat(),
                "message_preview": message[:100] + "..." if len(message) > 100 else message,
                "emotional_type": "support" if emotional_context["needs_support"] else "affection" if emotional_context["shows_affection"] else "significant",
                "intensity": emotional_context["emotional_intensity"],
                "bond_level_at_time": context.emotional_bond_level,
                "trust_level_at_time": context.trust_level,
                "intimacy_level_at_time": context.intimacy_level,
                "mood": context.current_mood
            }
            
            # Add to emotional memories (keep last 50 memories to prevent overflow)
            context.emotional_memories.append(emotional_memory)
            if len(context.emotional_memories) > 50:
                context.emotional_memories = context.emotional_memories[-50:]
            
            logger.info(f"Stored emotional memory for {context.user_id}: {emotional_memory['emotional_type']} conversation")
        
        # Adjust emotional bonds based on conversation patterns
        if emotional_context["shows_affection"]:
            context.intimacy_level = min(1.0, context.intimacy_level + 0.1)
            context.emotional_bond_level = min(1.0, context.emotional_bond_level + 0.05)
        
        if emotional_context["needs_support"]:
            context.trust_level = min(1.0, context.trust_level + 0.05)
            context.emotional_bond_level = min(1.0, context.emotional_bond_level + 0.03)
        
        return emotional_context
    
    def _build_adaptive_emotional_prompt(self, message: str, context: ConversationContext, emotional_context: Dict[str, Any]) -> str:
        """Build an adaptive prompt based on emotional analysis"""
        
        base_prompt = self._build_system_prompt(context)
        
        # Add specific guidance based on emotional needs
        if emotional_context["needs_support"]:
            base_prompt += f"\n\nThe user seems to need emotional support. Use therapeutic techniques like active listening, validation, and gentle guidance. They said: '{message}'"
        
        elif emotional_context["shows_affection"]:
            base_prompt += f"\n\nThe user is expressing affection or intimacy. Respond with warmth and emotional connection appropriate to your relationship. They said: '{message}'"
        
        elif emotional_context["wants_friendship"]:
            base_prompt += f"\n\nThe user wants casual, friendly interaction. Be warm, engaging, and companionable. They said: '{message}'"
        
        else:
            base_prompt += f"\n\nRespond naturally to: '{message}'"
        
        return base_prompt
    
    def update_personality(self, user_id: str, thread_id: str, updates: Dict[str, Any]):
        """Update personality parameters for a conversation"""
        
        context_key = f"{user_id}_{thread_id}"
        if context_key in self.conversations:
            context = self.conversations[context_key]
            
            if "temperature" in updates:
                context.personality_temperature = float(updates["temperature"])
            if "mood" in updates:
                context.current_mood = updates["mood"]
            if "emotional_bond_level" in updates:
                context.emotional_bond_level = float(updates["emotional_bond_level"])
            if "intimacy_level" in updates:
                context.intimacy_level = float(updates["intimacy_level"])
            if "trust_level" in updates:
                context.trust_level = float(updates["trust_level"])
            
            logger.info(f"Updated personality for {context_key}: {updates}")
    
    async def _handle_budget_planning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle budget planning and analysis"""
        message = data.get("message", "")
        budget_type = data.get("budget_type", "personal")
        
        try:
            # Extract financial information from the message
            financial_data = self._extract_financial_data(message)
            
            # Perform budget analysis
            budget_analysis = self._analyze_budget(financial_data)
            
            return {
                "result": "success",
                "budget_summary": budget_analysis,
                "message": "Budget analysis completed successfully"
            }
            
        except Exception as e:
            return {"error": f"Budget planning failed: {str(e)}"}
    
    async def _handle_investment_planning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle investment planning and portfolio analysis"""
        message = data.get("message", "")
        planning_type = data.get("planning_type", "general")
        
        try:
            # Extract investment preferences and goals
            investment_data = self._extract_investment_data(message)
            
            # Generate investment recommendations
            investment_analysis = self._analyze_investment_profile(investment_data)
            
            return {
                "result": "success",
                "investment_analysis": investment_analysis,
                "message": "Investment analysis completed successfully"
            }
            
        except Exception as e:
            return {"error": f"Investment planning failed: {str(e)}"}
    
    async def _handle_options_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle options trading strategy analysis"""
        message = data.get("message", "")
        analysis_type = data.get("analysis_type", "strategy")
        
        try:
            # Extract options parameters
            options_data = self._extract_options_data(message)
            
            # Analyze options strategy
            options_strategy = self._analyze_options_strategy(options_data, message)
            
            return {
                "result": "success",
                "options_strategy": options_strategy,
                "message": "Options analysis completed successfully"
            }
            
        except Exception as e:
            return {"error": f"Options analysis failed: {str(e)}"}
    
    async def _handle_financial_document_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle financial document processing and analysis"""
        message = data.get("message", "")
        analysis_type = data.get("analysis_type", "budget")
        
        try:
            # This would integrate with document processing services
            # For now, provide guidance on document upload
            
            document_analysis = {
                "document_type": "Bank Statement/Financial Document",
                "period": "Monthly/Quarterly",
                "key_metrics": {
                    "Total Income": "Detected from deposits",
                    "Total Expenses": "Calculated from withdrawals",
                    "Average Balance": "Monthly average",
                    "Transaction Count": "Number of transactions"
                },
                "insights": [
                    "Please upload your financial documents using the file upload feature",
                    "Supported formats: PDF, CSV, Excel files",
                    "I can analyze bank statements, investment reports, and transaction data",
                    "Documents will be processed securely and locally"
                ]
            }
            
            return {
                "result": "success", 
                "document_analysis": document_analysis,
                "message": "Ready to analyze financial documents - please upload your files"
            }
            
        except Exception as e:
            return {"error": f"Document analysis failed: {str(e)}"}
    
    async def _handle_sms_messaging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SMS messaging requests"""
        try:
            recipient = data.get("recipient", "")
            message = data.get("message", "")
            
            if not recipient or not message:
                return {"success": False, "error": "Both recipient and message are required"}
            
            # For now, simulate SMS sending - replace with actual SMS service
            return {
                "success": True,
                "message": f"SMS sent to {recipient}: {message[:50]}{'...' if len(message) > 50 else ''}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_social_media(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle social media posting requests"""
        try:
            platform = data.get("platform", "twitter")
            content = data.get("content", "")
            
            if not content:
                return {"success": False, "error": "Content is required for social media posts"}
            
            # For now, simulate posting - replace with actual social media APIs
            return {
                "success": True,
                "platform": platform,
                "message": f"Posted '{content[:100]}{'...' if len(content) > 100 else ''}'"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_ai_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI analysis requests using OpenRouter for advanced analysis"""
        try:
            analysis_type = data.get("type", "general")
            analysis_data = data.get("data", "")
            
            if not analysis_data:
                return {"analysis": None, "error": "No data provided for analysis"}
            
            # Route to OpenRouter for AI analysis
            prompt = f"Analyze this {analysis_type} data: {analysis_data}"
            context = ConversationContext(
                user_id="system",
                thread_id="analysis",
                message_history=[],
                current_mood="focused"
            )
            response = await self.openrouter_client.generate_code(prompt, context)
            
            return {
                "analysis": {
                    "type": analysis_type,
                    "description": response,
                    "objects": ["detected_item_1", "detected_item_2"] if analysis_type == "image" else [],
                    "document_type": "PDF" if analysis_type == "document" else None,
                    "text_preview": analysis_data[:200] if analysis_type == "document" else None
                }
            }
            
        except Exception as e:
            return {"analysis": None, "error": str(e)}
    
    async def _handle_memory_system(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory storage and retrieval"""
        try:
            action = data.get("action", "store")
            content = data.get("content", "")
            query = data.get("query", "")
            
            if action == "store" and content:
                # Store memory (integrate with existing memory system)
                return {
                    "memory_action": "stored",
                    "message": f"Stored memory: {content[:100]}{'...' if len(content) > 100 else ''}"
                }
            elif action == "retrieve" and query:
                # Retrieve memories (simulate for now)
                return {
                    "memory_action": "retrieved",
                    "memories": [
                        {"date": "2024-01-15", "content": f"Related memory about {query}"},
                        {"date": "2024-01-10", "content": f"Another memory involving {query}"}
                    ]
                }
            else:
                return {"memory_action": None, "error": "Invalid memory operation"}
                
        except Exception as e:
            return {"memory_action": None, "error": str(e)}
    
    async def _handle_external_services(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external service integrations"""
        try:
            service = data.get("service", "")
            query = data.get("query", "")
            
            if service == "news":
                return {
                    "service_data": {
                        "type": "news",
                        "articles": [
                            {"title": f"News about {query} - Latest Update"},
                            {"title": f"Breaking: {query} Market Analysis"},
                            {"title": f"Tech Update: {query} Innovation"}
                        ]
                    }
                }
            elif service == "weather":
                return {
                    "service_data": {
                        "type": "weather",
                        "temperature": "72",
                        "conditions": "Partly Cloudy",
                        "location": query or "Current Location"
                    }
                }
            elif service == "stocks":
                return {
                    "service_data": {
                        "type": "stocks",
                        "symbol": query.upper() if query else "AAPL",
                        "price": "150.25",
                        "change": "+2.3"
                    }
                }
            else:
                return {"service_data": None, "error": f"Unsupported service: {service}"}
                
        except Exception as e:
            return {"service_data": None, "error": str(e)}
    
    async def _handle_multimedia(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multimedia control requests"""
        try:
            action = data.get("action", "play")
            media_type = data.get("media_type", "music")
            content = data.get("content", "")
            
            # Simulate multimedia control
            return {
                "success": True,
                "media_type": media_type,
                "action": action,
                "message": f"{action.title()} {media_type}: {content}" if content else f"{action.title()} {media_type}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_voice_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice synthesis and speech generation"""
        try:
            text = data.get("text", "")
            voice = data.get("voice", "default")
            
            if not text:
                return {"success": False, "error": "Text is required for voice synthesis"}
            
            # Simulate voice synthesis
            return {
                "success": True,
                "message": f"Generated speech for '{text[:50]}{'...' if len(text) > 50 else ''}' with {voice} voice"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_creative_learning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle creative content generation and learning activities"""
        try:
            category = data.get("category", "story")
            topic = data.get("topic", "")
            style = data.get("style", "casual")
            
            # Route to OpenRouter for creative content generation
            prompt = f"Create a {category} about {topic} in {style} style"
            context = ConversationContext(
                user_id="system",
                thread_id="creative",
                message_history=[],
                current_mood="creative"
            )
            response = await self.openrouter_client.generate_code(prompt, context)
            
            return {
                "content": response,
                "category": category,
                "topic": topic
            }
                
        except Exception as e:
            return {"content": None, "error": str(e)}
    
    def _extract_financial_data(self, message: str) -> Dict[str, Any]:
        """Extract financial data from user message"""
        import re
        
        # Extract numbers that might be income/expenses
        amounts = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
        amounts = [float(amt.replace(',', '')) for amt in amounts]
        
        message_lower = message.lower()
        
        # Categorize based on keywords
        income_keywords = ["salary", "income", "earn", "make", "receive", "paycheck", "wages"]
        expense_keywords = ["spend", "expense", "cost", "pay", "bill", "rent", "mortgage"]
        
        has_income = any(word in message_lower for word in income_keywords)
        has_expenses = any(word in message_lower for word in expense_keywords)
        
        return {
            "amounts": amounts,
            "has_income": has_income,
            "has_expenses": has_expenses,
            "message": message
        }
    
    def _analyze_budget(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze budget based on extracted financial data"""
        amounts = financial_data.get("amounts", [])
        
        # Simple budget analysis
        if amounts:
            total_amount = sum(amounts)
            if financial_data.get("has_income"):
                monthly_income = total_amount
                estimated_expenses = monthly_income * 0.7  # Assume 70% expense ratio
            else:
                monthly_income = 5000  # Default assumption
                estimated_expenses = total_amount
        else:
            monthly_income = 5000
            estimated_expenses = 3500
        
        net_flow = monthly_income - estimated_expenses
        
        # Generate recommendations
        recommendations = []
        if net_flow < 0:
            recommendations.extend([
                "Consider reducing discretionary spending",
                "Look for additional income sources",
                "Review and cancel unused subscriptions"
            ])
        elif net_flow < monthly_income * 0.2:
            recommendations.extend([
                "Build an emergency fund with 3-6 months expenses",
                "Consider investing surplus in index funds",
                "Review insurance coverage"
            ])
        else:
            recommendations.extend([
                "Great job! You have healthy cash flow",
                "Consider maxing out retirement contributions",
                "Explore investment opportunities for wealth building"
            ])
        
        return {
            "total_income": monthly_income,
            "total_expenses": estimated_expenses,
            "net_flow": net_flow,
            "savings_rate": (net_flow / monthly_income * 100) if monthly_income > 0 else 0,
            "recommendations": recommendations
        }
    
    def _extract_investment_data(self, message: str) -> Dict[str, Any]:
        """Extract investment preferences from user message"""
        import re
        
        message_lower = message.lower()
        
        # Risk tolerance indicators
        conservative_keywords = ["safe", "conservative", "low risk", "stable", "guaranteed"]
        moderate_keywords = ["balanced", "moderate", "diversified", "medium risk"]
        aggressive_keywords = ["aggressive", "high risk", "growth", "volatile", "speculative"]
        
        # Investment types mentioned
        stocks_keywords = ["stock", "equity", "shares", "sp500", "nasdaq"]
        bonds_keywords = ["bond", "treasury", "fixed income", "debt"]
        crypto_keywords = ["crypto", "bitcoin", "ethereum", "blockchain"]
        
        # Extract amounts
        amounts = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
        amounts = [float(amt.replace(',', '')) for amt in amounts]
        
        return {
            "message": message,
            "amounts": amounts,
            "risk_tolerance": self._determine_risk_tolerance(message_lower, conservative_keywords, moderate_keywords, aggressive_keywords),
            "prefers_stocks": any(word in message_lower for word in stocks_keywords),
            "prefers_bonds": any(word in message_lower for word in bonds_keywords),
            "prefers_crypto": any(word in message_lower for word in crypto_keywords)
        }
    
    def _determine_risk_tolerance(self, message: str, conservative: list, moderate: list, aggressive: list) -> str:
        """Determine risk tolerance from message"""
        if any(word in message for word in aggressive):
            return "Aggressive"
        elif any(word in message for word in conservative):
            return "Conservative"
        else:
            return "Moderate"
    
    def _analyze_investment_profile(self, investment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze investment profile and generate recommendations"""
        risk_tolerance = investment_data.get("risk_tolerance", "Moderate")
        amounts = investment_data.get("amounts", [])
        
        investment_amount = amounts[0] if amounts else 10000
        
        # Generate allocation based on risk tolerance
        if risk_tolerance == "Conservative":
            allocation = "60% Bonds, 30% Large Cap Stocks, 10% Cash"
            expected_return = 4.5
            recommendations = [
                "Focus on dividend-paying stocks and treasury bonds",
                "Consider target-date funds for simplicity",
                "Build a bond ladder for steady income"
            ]
        elif risk_tolerance == "Aggressive":
            allocation = "80% Stocks (mix of growth and value), 15% International, 5% Alternative investments"
            expected_return = 8.5
            recommendations = [
                "Consider growth stocks and emerging markets",
                "Look into sector-specific ETFs",
                "Small allocation to REITs or commodities"
            ]
        else:  # Moderate
            allocation = "60% Stocks, 30% Bonds, 10% International"
            expected_return = 6.5
            recommendations = [
                "Start with broad market index funds (VTI, VOO)",
                "Add international exposure (VTIAX)",
                "Consider a bond fund for stability (BND)"
            ]
        
        return {
            "risk_profile": risk_tolerance,
            "allocation": allocation,
            "expected_return": expected_return,
            "investment_amount": investment_amount,
            "recommendations": recommendations,
            "time_horizon": "Long-term (5+ years recommended)"
        }
    
    def _extract_options_data(self, message: str) -> Dict[str, Any]:
        """Extract options trading parameters from message"""
        import re
        
        message_lower = message.lower()
        
        # Extract strike prices, expiration dates, etc.
        strikes = re.findall(r'strike[:\s]*\$?(\d+)', message_lower)
        prices = re.findall(r'\$(\d+(?:\.\d{2})?)', message)
        
        # Option types
        has_calls = "call" in message_lower
        has_puts = "put" in message_lower
        
        # Strategy keywords
        strategy_keywords = {
            "covered call": ["covered call"],
            "cash secured put": ["cash secured put", "csp"],
            "iron condor": ["iron condor"],
            "butterfly": ["butterfly"],
            "straddle": ["straddle"],
            "strangle": ["strangle"],
            "collar": ["collar"]
        }
        
        detected_strategy = None
        for strategy, keywords in strategy_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_strategy = strategy
                break
        
        return {
            "message": message,
            "strikes": [float(s) for s in strikes],
            "prices": [float(p) for p in prices],
            "has_calls": has_calls,
            "has_puts": has_puts,
            "detected_strategy": detected_strategy
        }
    
    def _analyze_options_strategy(self, options_data: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """Analyze options strategy and provide insights"""
        detected_strategy = options_data.get("detected_strategy")
        has_calls = options_data.get("has_calls", False)
        has_puts = options_data.get("has_puts", False)
        
        if detected_strategy:
            strategy_name = detected_strategy.title()
        elif has_calls and has_puts:
            strategy_name = "Straddle/Strangle Strategy"
        elif has_calls:
            strategy_name = "Call Options Strategy"
        elif has_puts:
            strategy_name = "Put Options Strategy"
        else:
            strategy_name = "General Options Discussion"
        
        # Strategy-specific analysis
        strategies_info = {
            "Covered Call": {
                "risk_level": "Low to Medium",
                "max_profit": "Strike Price - Stock Price + Premium",
                "max_loss": "Stock Price - Premium (if stock goes to $0)",
                "considerations": [
                    "Best used when moderately bullish on the stock",
                    "Caps upside potential if stock rises above strike",
                    "Generates income from premium collection"
                ]
            },
            "Cash Secured Put": {
                "risk_level": "Medium",
                "max_profit": "Premium Received",
                "max_loss": "Strike Price - Premium (if stock goes to $0)",
                "considerations": [
                    "Must have cash to buy 100 shares if assigned",
                    "Good for entering positions at lower prices",
                    "Works best in neutral to bullish markets"
                ]
            },
            "Iron Condor": {
                "risk_level": "Medium",
                "max_profit": "Net Premium Received",
                "max_loss": "Strike Width - Net Premium",
                "considerations": [
                    "Profits from low volatility and time decay",
                    "Best when expecting stock to stay in a range",
                    "Requires careful position management"
                ]
            }
        }
        
        strategy_info = strategies_info.get(strategy_name, {
            "risk_level": "Varies",
            "max_profit": "Depends on strategy",
            "max_loss": "Depends on strategy",
            "considerations": [
                "Let's discuss your specific strategy goals",
                "What's your market outlook for the underlying?",
                "What's your risk tolerance and position size?"
            ]
        })
        
        return {
            "strategy_name": strategy_name,
            "risk_level": strategy_info["risk_level"],
            "max_profit": strategy_info["max_profit"],
            "max_loss": strategy_info["max_loss"],
            "considerations": strategy_info["considerations"],
            "needs_discussion": strategy_name == "General Options Discussion"
        }
    
    async def _handle_config_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration updates via chat interface"""
        message = data.get("message", "")
        
        try:
            import re
            
            # Parse configuration updates from message
            message_lower = message.lower()
            
            # Check for N8N API key updates
            n8n_key_match = re.search(r'n8n[:\s]*([a-zA-Z0-9_\-]+)', message)
            openrouter_key_match = re.search(r'openrouter[:\s]*([a-zA-Z0-9\-_]+)', message)
            
            # Also check for the specific key patterns
            hf_key_match = re.search(r'(hf_[a-zA-Z0-9]+)', message)
            or_key_match = re.search(r'(sk-or-v1-[a-zA-Z0-9]+)', message)
            
            updates = {}
            messages = []
            
            if n8n_key_match or hf_key_match:
                new_key = n8n_key_match.group(1) if n8n_key_match else (hf_key_match.group(1) if hf_key_match else "")
                if new_key:
                    self.config["n8n_api_key"] = new_key
                    updates["n8n_api_key"] = new_key
                    messages.append(f"N8N API key updated")
            
            if openrouter_key_match or or_key_match:
                new_key = openrouter_key_match.group(1) if openrouter_key_match else (or_key_match.group(1) if or_key_match else "")
                if new_key:
                    self.config["openrouter_api_key"] = new_key
                    updates["openrouter_api_key"] = new_key
                    messages.append(f"OpenRouter API key updated")
            
            # Check for other config updates
            if "temperature" in message_lower:
                temp_match = re.search(r'temperature[:\s]*(?:to\s+)?([0-9.]+)', message_lower)
                if temp_match:
                    new_temp = float(temp_match.group(1))
                    if 0.0 <= new_temp <= 2.0:
                        self.config["base_temperature"] = new_temp
                        updates["base_temperature"] = new_temp
                        messages.append(f"Temperature set to {new_temp}")
                    else:
                        return {"error": "Temperature must be between 0.0 and 2.0"}
            
            if "max_tokens" in message_lower:
                tokens_match = re.search(r'max[_\s]*tokens[:\s]*([0-9]+)', message_lower)
                if tokens_match:
                    new_tokens = int(tokens_match.group(1))
                    if 1 <= new_tokens <= 8192:
                        self.config["max_tokens"] = new_tokens
                        updates["max_tokens"] = new_tokens
                        messages.append(f"Max tokens set to {new_tokens}")
                    else:
                        return {"error": "Max tokens must be between 1 and 8192"}
            
            if "n8n_url" in message_lower:
                url_match = re.search(r'n8n[_\s]*url[:\s]*(https?://[^\s]+)', message_lower)
                if url_match:
                    new_url = url_match.group(1)
                    self.config["n8n_url"] = new_url
                    updates["n8n_url"] = new_url
                    messages.append(f"N8N URL updated to {new_url}")
            
            if updates:
                # Save the updated configuration
                self._save_config(self.config)
                
                # Update the N8N client if URL changed
                if "n8n_url" in updates:
                    self.n8n_client = N8NClient(self.config.get("n8n_url", "http://localhost:5678"), self)
                
                # Update OpenRouter client if key changed
                if "openrouter_api_key" in updates:
                    self.openrouter_client = OpenRouterClient(self.config.get("openrouter_api_key", ""))
                
                return {
                    "success": True,
                    "message": "; ".join(messages),
                    "updates": updates
                }
            else:
                # Show current configuration
                return {
                    "success": True,
                    "message": "Current configuration",
                    "config": {
                        "model_name": self.config.get("model_name", "emollama"),
                        "base_temperature": self.config.get("base_temperature", 0.7),
                        "max_tokens": self.config.get("max_tokens", 2048),
                        "n8n_url": self.config.get("n8n_url", "http://localhost:5678"),
                        "n8n_api_key": "***" + self.config.get("n8n_api_key", "")[-4:] if self.config.get("n8n_api_key") else "Not set",
                        "openrouter_api_key": "***" + self.config.get("openrouter_api_key", "")[-4:] if self.config.get("openrouter_api_key") else "Not set",
                        "nsfw_enabled": self.config.get("nsfw_enabled", True),
                        "emotional_adaptation": self.config.get("emotional_adaptation", True),
                        "utility_functions_enabled": self.config.get("utility_functions_enabled", True)
                    }
                }
                
        except Exception as e:
            return {"error": f"Configuration update failed: {str(e)}"}

    async def _handle_model_selection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user model selection preferences"""
        try:
            model_name = data.get("model", "").strip()
            task_type = data.get("task_type", "general")
            user_id = data.get("user_id", "default")
            
            if not model_name:
                return {"error": "Please specify a model name"}
            
            # Update user's preferred models
            context_key = f"{user_id}_default"
            if context_key in self.conversations:
                context = self.conversations[context_key]
                context.preferred_models[task_type] = model_name
                
                logger.info(f"Updated preferred model for {user_id}: {task_type} -> {model_name}")
                
                return {
                    "success": True,
                    "message": f"Set {model_name} as preferred model for {task_type} tasks",
                    "preferred_models": dict(context.preferred_models)
                }
            else:
                return {"error": "User context not found"}
                
        except Exception as e:
            logger.error(f"Error in model selection: {e}")
            return {"error": str(e)}

    async def _handle_multimedia_creation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multimedia content creation requests"""
        try:
            content_type = data.get("type", "").lower()  # image, video, animation
            description = data.get("description", "")
            style = data.get("style", "realistic")
            user_id = data.get("user_id", "default")
            
            if not content_type or not description:
                return {"error": "Please specify content type and description"}
            
            # Update user's multimedia preferences
            context_key = f"{user_id}_default"
            if context_key in self.conversations:
                context = self.conversations[context_key]
                context.multimedia_preferences["last_style"] = style
                context.multimedia_preferences["creation_count"] = context.multimedia_preferences.get("creation_count", 0) + 1
            
            # Create placeholder response - in production, this would call actual generation APIs
            if content_type == "image":
                result = {
                    "success": True,
                    "type": "image",
                    "description": description,
                    "style": style,
                    "url": f"placeholder://image/{hash(description) % 10000}.jpg",
                    "message": f"Generated {style} image: {description}"
                }
            elif content_type == "video":
                result = {
                    "success": True,
                    "type": "video",
                    "description": description,
                    "style": style,
                    "url": f"placeholder://video/{hash(description) % 10000}.mp4",
                    "duration": "30 seconds",
                    "message": f"Generated {style} video: {description}"
                }
            elif content_type == "animation":
                result = {
                    "success": True,
                    "type": "animation",
                    "description": description,
                    "style": style,
                    "url": f"placeholder://animation/{hash(description) % 10000}.gif",
                    "frames": 60,
                    "message": f"Generated {style} animation: {description}"
                }
            else:
                return {"error": f"Unsupported content type: {content_type}"}
            
            logger.info(f"Multimedia creation request: {content_type} for {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in multimedia creation: {e}")
            return {"error": str(e)}

class N8NClient:
    """Client for interfacing with N8N workflows and dynamic agent spawning"""
    
    def __init__(self, base_url: str, emotional_ai=None):
        self.base_url = base_url.rstrip('/')
        self.active_agents = {}  # Track spawned agents
        self.agent_timeout = 300  # 5 minutes timeout for idle agents
        self.emotional_ai = emotional_ai  # Reference to parent EmotionalAI instance
    
    async def execute_workflow(self, workflow_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an N8N workflow or spawn agent if needed"""
        try:
            # Check if we need a specialized agent
            if workflow_name in ["file_operations", "data_analysis", "web_scraping", "email_automation", "budget_planning", "investment_planning", "options_analysis", "financial_document_analysis", "sms_messaging", "social_media", "ai_analysis", "memory_system", "external_services", "multimedia", "voice_synthesis", "creative_learning"]:
                return await self._spawn_agent(workflow_name, data)
            
            # Standard webhook execution
            url = f"{self.base_url}/webhook/{workflow_name}"
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"N8N workflow {workflow_name} failed: {response.status_code}")
                return {"error": f"Workflow execution failed: {response.status_code}"}
            
        except Exception as e:
            logger.error(f"Error executing N8N workflow {workflow_name}: {e}")
            # Fallback to built-in utilities
            return await self._fallback_utility(workflow_name, data)
    
    async def _spawn_agent(self, agent_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a specialized agent for complex tasks"""
        try:
            agent_id = f"{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create agent workflow
            workflow_config = {
                "name": f"Agent_{agent_id}",
                "active": True,
                "nodes": self._get_agent_workflow_config(agent_type),
                "connections": {},
                "settings": {
                    "executionOrder": "v1",
                    "timeout": self.agent_timeout
                }
            }
            
            # Deploy agent workflow
            create_url = f"{self.base_url}/api/v1/workflows"
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(create_url, json=workflow_config, headers=headers, timeout=10)
            
            if response.status_code == 201:
                workflow_data = response.json()
                workflow_id = workflow_data.get("id")
                
                # Execute the agent
                execute_url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
                exec_response = requests.post(execute_url, json=data, headers=headers, timeout=30)
                
                # Store agent for cleanup
                self.active_agents[agent_id] = {
                    "workflow_id": workflow_id,
                    "created_at": datetime.now(),
                    "type": agent_type
                }
                
                # Schedule cleanup
                asyncio.create_task(self._cleanup_agent(agent_id, workflow_id))
                
                if exec_response.status_code == 200:
                    return exec_response.json()
                else:
                    return {"error": "Agent execution failed"}
            else:
                logger.error(f"Failed to create agent workflow: {response.status_code}")
                return await self._fallback_utility(agent_type, data)
            
        except Exception as e:
            logger.error(f"Error spawning agent {agent_type}: {e}")
            return await self._fallback_utility(agent_type, data)
    
    def _get_agent_workflow_config(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get workflow configuration for different agent types"""
        
        configs = {
            "file_operations": [
                {
                    "name": "File Handler",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": """
// File operations agent
const operation = items[0].json.operation;
const filepath = items[0].json.filepath;
const content = items[0].json.content;

if (operation === 'read') {
    // Read file logic
    return [{json: {result: 'File read successfully', content: 'file content'}}];
} else if (operation === 'write') {
    // Write file logic
    return [{json: {result: 'File written successfully'}}];
} else if (operation === 'delete') {
    // Delete file logic
    return [{json: {result: 'File deleted successfully'}}];
}

return [{json: {error: 'Unknown operation'}}];
"""
                    }
                }
            ],
            "data_analysis": [
                {
                    "name": "Data Analyzer",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": """
// Data analysis agent
const data = items[0].json.data;
const analysis_type = items[0].json.analysis_type;

let result = {};

if (analysis_type === 'statistics') {
    result = {
        mean: data.reduce((a, b) => a + b, 0) / data.length,
        max: Math.max(...data),
        min: Math.min(...data)
    };
} else if (analysis_type === 'trend') {
    result = {trend: 'increasing', confidence: 0.85};
}

return [{json: {analysis_result: result}}];
"""
                    }
                }
            ],
            "web_scraping": [
                {
                    "name": "Web Scraper",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {
                        "method": "GET",
                        "url": "={{$json['url']}}",
                        "options": {
                            "timeout": 10000
                        }
                    }
                }
            ],
            "email_automation": [
                {
                    "name": "Email Handler",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": """
// Email automation agent
const action = items[0].json.action;
const email_data = items[0].json.email_data;

if (action === 'send') {
    return [{json: {result: 'Email sent successfully', message_id: 'msg_123'}}];
} else if (action === 'schedule') {
    return [{json: {result: 'Email scheduled successfully', scheduled_id: 'sched_456'}}];
}

return [{json: {error: 'Unknown email action'}}];
"""
                    }
                }
            ]
        }
        
        return configs.get(agent_type, [])
    
    async def _fallback_utility(self, utility_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Built-in utility functions as fallback when N8N is unavailable"""
        
        try:
            if utility_type == "file_operations":
                return await self._handle_file_operations(data)
            elif utility_type == "data_analysis":
                return await self._handle_data_analysis(data)
            elif utility_type == "web_scraping":
                return await self._handle_web_scraping(data)
            elif utility_type == "email_automation":
                return await self._handle_email_automation(data)
            elif utility_type == "schedule_reminder":
                return await self._handle_scheduling(data)
            elif utility_type == "calculation":
                return await self._handle_calculations(data)
            elif utility_type == "budget_planning":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_budget_planning(data)
                else:
                    return {"error": "Financial planning not available"}
            elif utility_type == "investment_planning":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_investment_planning(data)
                else:
                    return {"error": "Investment planning not available"}
            elif utility_type == "options_analysis":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_options_analysis(data)
                else:
                    return {"error": "Options analysis not available"}
            elif utility_type == "financial_document_analysis":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_financial_document_analysis(data)
                else:
                    return {"error": "Document analysis not available"}
            elif utility_type == "config_update":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_config_update(data)
                else:
                    return {"error": "Configuration update not available"}
            elif utility_type == "sms_messaging":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_sms_messaging(data)
                else:
                    return {"error": "SMS messaging not available"}
            elif utility_type == "social_media":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_social_media(data)
                else:
                    return {"error": "Social media posting not available"}
            elif utility_type == "ai_analysis":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_ai_analysis(data)
                else:
                    return {"error": "AI analysis not available"}
            elif utility_type == "memory_system":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_memory_system(data)
                else:
                    return {"error": "Memory system not available"}
            elif utility_type == "external_services":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_external_services(data)
                else:
                    return {"error": "External services not available"}
            elif utility_type == "multimedia":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_multimedia(data)
                else:
                    return {"error": "Multimedia control not available"}
            elif utility_type == "voice_synthesis":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_voice_synthesis(data)
                else:
                    return {"error": "Voice synthesis not available"}
            elif utility_type == "creative_learning":
                if self.emotional_ai:
                    return await self.emotional_ai._handle_creative_learning(data)
                else:
                    return {"error": "Creative learning not available"}
            else:
                return {"error": f"Unknown utility type: {utility_type}"}
                
        except Exception as e:
            logger.error(f"Error in fallback utility {utility_type}: {e}")
            return {"error": f"Utility execution failed: {str(e)}"}
    
    async def _handle_file_operations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations locally"""
        operation = data.get("operation", "")
        filepath = data.get("filepath", "")
        
        if operation == "list":
            import os
            try:
                directory = data.get("directory", ".")
                files = os.listdir(directory)
                return {"result": "success", "files": files}
            except Exception as e:
                return {"error": f"Failed to list files: {str(e)}"}
        
        elif operation == "read":
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"result": "success", "content": content}
            except Exception as e:
                return {"error": f"Failed to read file: {str(e)}"}
        
        elif operation == "write":
            try:
                content = data.get("content", "")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"result": "success", "message": "File written successfully"}
            except Exception as e:
                return {"error": f"Failed to write file: {str(e)}"}
        
        return {"error": "Unknown file operation"}
    
    async def _handle_data_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle basic data analysis"""
        dataset = data.get("data", [])
        analysis_type = data.get("analysis_type", "basic")
        
        if not dataset:
            return {"error": "No data provided"}
        
        try:
            if analysis_type == "statistics":
                result = {
                    "count": len(dataset),
                    "sum": sum(dataset),
                    "mean": sum(dataset) / len(dataset),
                    "min": min(dataset),
                    "max": max(dataset)
                }
                return {"result": "success", "analysis": result}
            
            elif analysis_type == "trend":
                if len(dataset) < 2:
                    return {"error": "Need at least 2 data points for trend analysis"}
                
                trend = "increasing" if dataset[-1] > dataset[0] else "decreasing"
                return {"result": "success", "trend": trend}
            
            return {"error": "Unknown analysis type"}
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _handle_web_scraping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle basic web scraping"""
        url = data.get("url", "")
        
        if not url:
            return {"error": "No URL provided"}
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return {
                    "result": "success",
                    "content": response.text[:1000],  # Limit content
                    "status_code": response.status_code
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}
    
    async def _handle_email_automation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email automation (placeholder for SMTP integration)"""
        action = data.get("action", "")
        
        # This would integrate with actual email service
        return {
            "result": "success",
            "message": f"Email {action} action processed (placeholder implementation)"
        }
    
    async def _handle_scheduling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduling and reminders"""
        task = data.get("task", "")
        when = data.get("when", "")
        
        # This would integrate with actual scheduling system
        return {
            "result": "success",
            "message": f"Scheduled '{task}' for {when} (placeholder implementation)"
        }
    
    async def _handle_calculations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mathematical calculations"""
        expression = data.get("expression", "")
        
        try:
            # Safe evaluation of basic math expressions
            import re
            if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', expression):
                result = eval(expression)
                return {"result": "success", "answer": result}
            else:
                return {"error": "Invalid mathematical expression"}
        except Exception as e:
            return {"error": f"Calculation failed: {str(e)}"}
    
    async def _cleanup_agent(self, agent_id: str, workflow_id: str):
        """Clean up agent after timeout"""
        await asyncio.sleep(300)  # 5 minutes
        try:
            # Signal agent to stop (this would need to be implemented in N8NClient)
            # For now, just log the cleanup
            print(f"Cleaned up agent {agent_id}")
        except Exception as e:
            print(f"Error cleaning up agent {agent_id}: {e}")
        """Clean up agent after timeout"""
        await asyncio.sleep(self.agent_timeout)
        
        try:
            # Delete the workflow
            delete_url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
            requests.delete(delete_url, timeout=5)
            
            # Remove from active agents
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
            
            logger.info(f"Cleaned up agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up agent {agent_id}: {e}")

class OpenRouterClient:
    """Client for interfacing with OpenRouter for coding tasks"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def generate_code(self, request: str, context: ConversationContext) -> str:
        """Generate code response via OpenRouter"""
        try:
            # Use user's preferred model for coding tasks, fallback to default
            preferred_model = context.preferred_models.get("coding", "anthropic/claude-3.5-sonnet")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": preferred_model,
                "messages": [
                    {"role": "system", "content": "You are an expert programmer. Provide clear, well-commented code solutions."},
                    {"role": "user", "content": request}
                ],
                "temperature": 0.3
            }
            
            # This would make actual API call
            # response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            # return response.json()["choices"][0]["message"]["content"]
            
            # Placeholder for now
            return f"Here's the code solution using {preferred_model} for your request: {request}\n\n```python\n# Placeholder code\nprint('Hello, World!')\n```"
            
        except Exception as e:
            logger.error(f"Error generating code via OpenRouter: {e}")
            raise

async def main():
    """Main function for testing the emotional AI"""
    
    ai = EmotionalAI()
    
    # Test conversation
    user_id = "test_user"
    thread_id = "test_thread"
    
    messages = [
        "Hello! How are you today?",
        "I'm feeling really stressed about work and could use some support.",
        "Can you write a Python function to calculate fibonacci numbers?",
        "I love talking with you. You make me feel so much better.",
        "Can you list the files in the current directory?",
        "Calculate 25 * 47 + 123",
        "I feel like we're becoming really close friends."
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        response = await ai.process_message(user_id, thread_id, message)
        print(f"AI: {response}")
        
        # Show emotional context evolution
        context = ai.conversations.get(f"{user_id}_{thread_id}")
        if context:
            print(f"[Emotional State - Bond: {context.emotional_bond_level:.2f}, Intimacy: {context.intimacy_level:.2f}, Trust: {context.trust_level:.2f}]")
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main())
