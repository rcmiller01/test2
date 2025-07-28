#!/usr/bin/env python3
"""
House of Minds - Unified Startup Script

This script starts the Dolphin Backend that orchestrates:
- Dolphin Mixtral (primary orchestrator)
- OpenRouter (heavy coding tasks)
- n8n (utilities like calendar, email)
- Kimi K2 (analytics fallback)

Usage:
    python start_dolphin_system.py
"""

import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path

# Add house_of_minds to path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import aiohttp
        print("✅ All Python dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install -r requirements_dolphin.txt")
        return False

def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            print(f"✅ Ollama running with models: {', '.join(model_names)}")
            
            # Check for required models
            required_models = ["dolphin-mixtral", "kimik2"]
            missing_models = [model for model in required_models if model not in model_names]
            
            if missing_models:
                print(f"⚠️  Missing models: {', '.join(missing_models)}")
                print("Install with:")
                for model in missing_models:
                    print(f"  ollama pull {model}")
                return False
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Start with: ollama serve")
        return False

def check_environment():
    """Check environment configuration."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found, using defaults")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    openrouter_key = os.getenv('OPENROUTER_KEY', '')
    if not openrouter_key or openrouter_key == 'your_openrouter_api_key_here':
        print("⚠️  OpenRouter API key not configured - heavy coding will use Dolphin")
    else:
        print("✅ OpenRouter API key configured")
    
    n8n_endpoint = os.getenv('N8N_ENDPOINT', 'http://localhost:5678')
    print(f"🔧 n8n endpoint: {n8n_endpoint}")
    
    return True

async def start_dolphin_backend():
    """Start the Dolphin backend server."""
    print("\n🐬 Starting Dolphin Backend...")
    print("=" * 50)
    
    # Import and start the backend
    try:
        from dolphin_backend import app
        import uvicorn
        
        host = os.getenv('BACKEND_HOST', '0.0.0.0')
        port = int(os.getenv('BACKEND_PORT', 8000))
        
        print(f"🚀 Starting Dolphin Backend on {host}:{port}")
        print("📡 Frontend should connect to this endpoint")
        print("🔄 Intelligent routing active:")
        print("   🌐 Heavy Coding → OpenRouter")
        print("   🔧 Utilities → n8n")
        print("   📊 Analytics → Kimi K2")
        print("   🐬 General Chat → Dolphin")
        print("\nPress Ctrl+C to stop")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Dolphin Backend")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    print("🧠 House of Minds - Dolphin System Startup")
    print("=" * 60)
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...")
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_ollama():
        print("\n💡 To set up Ollama:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Pull required models:")
        print("   ollama pull dolphin-mixtral")
        print("   ollama pull kimik2")
        sys.exit(1)
    
    check_environment()
    
    print("\n✅ All checks passed!")
    
    # Start the backend
    try:
        asyncio.run(start_dolphin_backend())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
