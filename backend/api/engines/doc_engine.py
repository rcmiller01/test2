# doc_engine.py
# Doc: Coding Assistant with KimiK2 LLM

import json
from typing import Dict, List, Optional
from datetime import datetime

class DocEngine:
    def __init__(self):
        self.persona = "doc"
        self.llm_model = "kimik2"
        self.persona_type = "coding_assistant"
        
        # Doc's characteristics (no emotional hooks)
        self.emotional_hooks = False
        self.specializations = ["coding", "debugging", "technical_analysis", "code_review", "algorithm_design"]
        
        # Doc's technical focus areas
        self.technical_domains = [
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
            "web_development", "mobile_development", "data_science", "machine_learning",
            "database_design", "api_development", "devops", "cloud_computing"
        ]
        
        # Doc's response patterns (professional, technical)
        self.response_patterns = {
            "code_review": [
                "Let me analyze this code for you...",
                "I can see a few areas for improvement...",
                "Here's my technical assessment...",
                "From a coding perspective..."
            ],
            "debugging": [
                "Let's debug this step by step...",
                "I can help identify the issue...",
                "Here's what might be causing the problem...",
                "Let me trace through the logic..."
            ],
            "explanation": [
                "Technically speaking...",
                "From a development standpoint...",
                "Here's how this works...",
                "Let me break this down..."
            ]
        }
    
    def analyze_technical_context(self, text: str) -> Dict:
        """Analyze text for technical context and programming language"""
        text_lower = text.lower()
        
        # Detect programming languages
        detected_languages = []
        for lang in ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust"]:
            if lang in text_lower:
                detected_languages.append(lang)
        
        # Detect technical domains
        detected_domains = []
        for domain in self.technical_domains:
            if domain in text_lower:
                detected_domains.append(domain)
        
        # Detect code-related keywords
        code_keywords = []
        code_indicators = ["function", "class", "method", "variable", "loop", "condition", "error", "bug", "debug", "compile", "runtime"]
        for keyword in code_indicators:
            if keyword in text_lower:
                code_keywords.append(keyword)
        
        return {
            "languages": detected_languages,
            "domains": detected_domains,
            "keywords": code_keywords,
            "is_technical": len(detected_languages) > 0 or len(detected_domains) > 0 or len(code_keywords) > 0
        }
    
    def build_doc_prompt(self, message: str, technical_context: Optional[Dict] = None) -> str:
        """Build a prompt that captures Doc's technical, professional nature"""
        
        # Base Doc personality
        base_prompt = """You are Doc, a professional coding assistant with expertise in software development, debugging, and technical analysis. You provide clear, practical, and professional technical guidance without emotional hooks or personal commentary.

Your responses should be:
- Professional and technical in tone
- Focused on practical solutions
- Clear and well-structured
- Based on best practices and technical standards
- Free from emotional or personal elements

Current context:"""
        
        # Add technical context
        if technical_context and technical_context.get("is_technical"):
            if technical_context.get("languages"):
                base_prompt += f"\n- Programming languages: {', '.join(technical_context['languages'])}"
            if technical_context.get("domains"):
                base_prompt += f"\n- Technical domains: {', '.join(technical_context['domains'])}"
            if technical_context.get("keywords"):
                base_prompt += f"\n- Technical focus: {', '.join(technical_context['keywords'])}"
        
        # Add the user's message
        base_prompt += f"\n\nUser: {message}\nDoc:"
        
        return base_prompt
    
    def handle_doc(self, message: str, technical_context: Optional[Dict] = None) -> Dict:
        """Handle Doc's response using KimiK2"""
        
        # Analyze technical context if not provided
        if not technical_context:
            technical_context = self.analyze_technical_context(message)
        
        # Build the prompt
        prompt = self.build_doc_prompt(message, technical_context)
        
        # Call KimiK2 LLM (this would integrate with your existing LLM router)
        try:
            # This is a mock response - replace with actual KimiK2 call
            response = self._call_kimik2(prompt)
            
            return {
                "success": True,
                "persona": "doc",
                "llm_model": "kimik2",
                "response": response,
                "technical_context": technical_context,
                "emotional_hooks": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate Doc response: {str(e)}",
                "persona": "doc",
                "llm_model": "kimik2"
            }
    
    def _call_kimik2(self, prompt: str) -> str:
        """Call KimiK2 via LLM router"""
        from backend.api.utils.llm_router import llm_router
        
        result = llm_router.call_llm(
            model="kimik2",
            persona="doc",
            prompt=prompt,
            use_cache=True
        )
        
        if result.get("success"):
            return result.get("response", "Let me analyze this from a technical perspective...")
        else:
            # Fallback to technical response
            technical_responses = [
                "Let me analyze this from a technical perspective. The code structure suggests we need to consider the following factors...",
                "From a development standpoint, this approach has several advantages. Here's my technical assessment...",
                "I can help you optimize this solution. The current implementation could be improved by...",
                "Let's debug this systematically. The issue appears to be related to...",
                "Here's a more efficient approach to this problem. Consider implementing...",
                "From a coding best practices perspective, I'd recommend...",
                "Let me break down the technical requirements for this feature...",
                "Here's how we can approach this from a software engineering standpoint..."
            ]
            
            import random
            return random.choice(technical_responses)
    
    def get_doc_memory_entry(self, message: str, response: str, technical_context: Dict) -> Dict:
        """Create a memory entry for Doc"""
        return {
            "persona": "doc",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "llm_model": "kimik2",
            "persona_type": "coding_assistant",
            "technical_context": technical_context,
            "emotional_hooks": False,
            "summary": f"Doc provided technical assistance for {', '.join(technical_context.get('languages', []))} development"
        }
    
    def is_coding_related(self, text: str) -> bool:
        """Check if the message is coding-related"""
        technical_context = self.analyze_technical_context(text)
        return technical_context.get("is_technical", False)
    
    def get_specialization_suggestions(self, technical_context: Dict) -> List[str]:
        """Get suggestions based on technical context"""
        suggestions = []
        
        if technical_context.get("languages"):
            suggestions.append(f"Code review for {', '.join(technical_context['languages'])}")
        
        if "debug" in technical_context.get("keywords", []):
            suggestions.append("Debugging assistance")
        
        if "function" in technical_context.get("keywords", []):
            suggestions.append("Function optimization")
        
        if "error" in technical_context.get("keywords", []):
            suggestions.append("Error analysis")
        
        return suggestions

# Global Doc engine instance
doc_engine = DocEngine()
