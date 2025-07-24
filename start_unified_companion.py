"""
Unified Companion System Startup Script

Initializes and starts the unified companion system with all components.
This script handles system initialization, dependency checks, and server startup.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('unified_companion.log')
    ]
)
logger = logging.getLogger(__name__)

class UnifiedCompanionLauncher:
    """
    Launcher for the unified companion system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_default_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default system configuration"""
        return {
            "system": {
                "name": "Unified Companion",
                "version": "1.0.0",
                "environment": "development"
            },
            "mythomax": {
                "model_name": "TheBloke/MythoMax-L2-13B-GPTQ",
                "quantization": True,
                "max_length": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "device": "auto"
            },
            "database": {
                "type": "inmemory",  # Change to "mongodb" for production
                "connection_string": None,  # Set MongoDB connection string for production
                "database_name": "unified_companion"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 1,
                "reload": True
            },
            "safety": {
                "crisis_detection": True,
                "content_filtering": True,
                "rate_limiting": True
            },
            "features": {
                "emotional_support": True,
                "technical_assistance": True,
                "creative_collaboration": True,
                "memory_system": True,
                "adaptive_responses": True
            }
        }
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        logger.info("Checking system dependencies...")
        
        required_packages = [
            "fastapi",
            "uvicorn", 
            "pydantic"
        ]
        
        optional_packages = [
            ("transformers", "MythoMax LLM functionality"),
            ("torch", "Machine learning capabilities"),
            ("motor", "MongoDB database support")
        ]
        
        missing_required = []
        missing_optional = []
        
        # Check required packages
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package}")
            except ImportError:
                missing_required.append(package)
                logger.error(f"✗ {package} (REQUIRED)")
        
        # Check optional packages
        for package, description in optional_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package} - {description}")
            except ImportError:
                missing_optional.append((package, description))
                logger.warning(f"⚠ {package} - {description} (OPTIONAL)")
        
        if missing_required:
            logger.error(f"Missing required dependencies: {missing_required}")
            logger.error("Install with: pip install fastapi uvicorn pydantic")
            return False
        
        if missing_optional:
            logger.warning("Some optional features may not be available")
            logger.warning("Install full dependencies with: pip install -r requirements_unified_companion.txt")
        
        return True
    
    def validate_configuration(self) -> bool:
        """Validate system configuration"""
        logger.info("Validating configuration...")
        
        # Check MythoMax configuration
        if self.config["features"]["technical_assistance"] or self.config["features"]["creative_collaboration"]:
            try:
                import transformers
                logger.info("✓ MythoMax LLM capabilities available")
            except ImportError:
                logger.warning("⚠ MythoMax LLM not available - some features will be limited")
                # Disable LLM-dependent features
                self.config["features"]["technical_assistance"] = False
                self.config["features"]["creative_collaboration"] = False
        
        # Check database configuration
        if self.config["database"]["type"] == "mongodb":
            try:
                import motor
                if not self.config["database"]["connection_string"]:
                    logger.warning("⚠ MongoDB configured but no connection string provided")
                    logger.warning("⚠ Falling back to in-memory database")
                    self.config["database"]["type"] = "inmemory"
                else:
                    logger.info("✓ MongoDB configuration valid")
            except ImportError:
                logger.warning("⚠ MongoDB driver not available - using in-memory database")
                self.config["database"]["type"] = "inmemory"
        else:
            logger.info("✓ Using in-memory database for development")
        
        logger.info("Configuration validation complete")
        return True
    
    async def initialize_system_components(self):
        """Initialize all system components"""
        logger.info("Initializing system components...")
        
        try:
            # Initialize database
            from modules.database.database_interface import create_database_interface
            database = create_database_interface(
                connection_string=self.config["database"]["connection_string"],
                database_type=self.config["database"]["type"]
            )
            await database.initialize()
            logger.info("✓ Database initialized")
            
            # Initialize unified companion (if available)
            try:
                from modules.core.unified_companion import UnifiedCompanion
                companion = UnifiedCompanion(self.config)
                await companion.initialize()
                logger.info("✓ Unified companion initialized")
            except ImportError as e:
                logger.warning(f"⚠ Unified companion not fully available: {e}")
                companion = None
            
            return database, companion
            
        except Exception as e:
            logger.error(f"Failed to initialize system components: {e}")
            raise
    
    def start_api_server(self):
        """Start the FastAPI server"""
        logger.info("Starting Unified Companion API server...")
        
        try:
            import uvicorn
            from modules.api.unified_companion_api import app
            
            # Configure uvicorn
            config = uvicorn.Config(
                app,
                host=self.config["api"]["host"],
                port=self.config["api"]["port"],
                workers=self.config["api"]["workers"],
                reload=self.config["api"]["reload"],
                log_level="info"
            )
            
            server = uvicorn.Server(config)
            
            logger.info(f"Server starting on http://{self.config['api']['host']}:{self.config['api']['port']}")
            logger.info("API documentation available at /docs")
            
            # Run the server
            server.run()
            
        except ImportError:
            logger.error("FastAPI or uvicorn not available - cannot start API server")
            logger.error("Install with: pip install fastapi uvicorn")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            sys.exit(1)
    
    async def run_system_tests(self):
        """Run basic system tests"""
        logger.info("Running system tests...")
        
        try:
            # Import and run the test suite
            from test_unified_companion import UnifiedCompanionTester
            
            tester = UnifiedCompanionTester()
            await tester.run_all_tests()
            
            logger.info("✓ All system tests passed")
            return True
            
        except Exception as e:
            logger.error(f"System tests failed: {e}")
            return False
    
    def print_system_info(self):
        """Print system information and status"""
        print("\n" + "="*60)
        print(f"🤖 {self.config['system']['name']} v{self.config['system']['version']}")
        print("="*60)
        print(f"Environment: {self.config['system']['environment']}")
        print(f"Database: {self.config['database']['type']}")
        print(f"API Server: {self.config['api']['host']}:{self.config['api']['port']}")
        print("\nEnabled Features:")
        for feature, enabled in self.config['features'].items():
            status = "✓" if enabled else "✗"
            print(f"  {status} {feature.replace('_', ' ').title()}")
        print("\nQuick Start:")
        print(f"  API: http://localhost:{self.config['api']['port']}")
        print(f"  Docs: http://localhost:{self.config['api']['port']}/docs")
        print(f"  Health: http://localhost:{self.config['api']['port']}/api/v1/system/health")
        print("="*60 + "\n")

async def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description="Unified Companion System Launcher")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--test", action="store_true", help="Run system tests only")
    parser.add_argument("--no-server", action="store_true", help="Skip starting the API server")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize launcher
    launcher = UnifiedCompanionLauncher(args.config)
    
    # Print system information
    launcher.print_system_info()
    
    # Check dependencies
    if not launcher.check_dependencies():
        logger.error("Dependency check failed - cannot continue")
        sys.exit(1)
    
    # Validate configuration
    if not launcher.validate_configuration():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Run tests if requested
    if args.test:
        success = await launcher.run_system_tests()
        sys.exit(0 if success else 1)
    
    # Initialize system components
    try:
        database, companion = await launcher.initialize_system_components()
        logger.info("System initialization complete")
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        sys.exit(1)
    
    # Start API server (unless disabled)
    if not args.no_server:
        launcher.start_api_server()
    else:
        logger.info("API server startup skipped")
        logger.info("System is ready for programmatic use")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
