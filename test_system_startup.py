#!/usr/bin/env python3
"""
Test script to verify the unified AI companion system can initialize properly
"""

import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from start_unified_ai_companion import AICompanionSystem

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_system_initialization():
    """Test that the AI companion system can initialize without errors"""
    
    logger.info("🧪 Starting AI Companion System initialization test...")
    
    try:
        # Create the system
        system = AICompanionSystem()
        
        # Test initialization
        logger.info("🔄 Testing system initialization...")
        init_success = await system.initialize()
        
        if init_success:
            logger.info("✅ System initialization test PASSED")
            
            # Test status retrieval
            logger.info("🔍 Testing status retrieval...")
            status = await system.get_status()
            logger.info(f"📊 System Status: {status['status']}")
            logger.info(f"🧩 Components: {list(status['components'].keys())}")
            
            # Test graceful shutdown
            logger.info("🛑 Testing graceful shutdown...")
            await system.shutdown()
            logger.info("✅ Shutdown test PASSED")
            
            logger.info("🎉 All tests PASSED! The unified AI companion system is ready to run.")
            return True
            
        else:
            logger.error("❌ System initialization test FAILED")
            return False
            
    except Exception as e:
        logger.error(f"💥 Test failed with exception: {e}")
        logger.exception("Full traceback:")
        return False

async def main():
    """Main test runner"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("🚀 AI COMPANION SYSTEM - STARTUP TEST")
    logger.info("=" * 60)
    
    success = await test_system_initialization()
    
    logger.info("=" * 60)
    if success:
        logger.info("🌟 TEST SUITE COMPLETED SUCCESSFULLY!")
        logger.info("The unified AI companion system is ready for production use.")
    else:
        logger.info("💥 TEST SUITE FAILED!")
        logger.info("Please check the logs and fix any issues before running the system.")
    logger.info("=" * 60)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
