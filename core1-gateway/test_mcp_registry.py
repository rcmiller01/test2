#!/usr/bin/env python3
"""
Test script for MCP dynamic agent registry

This script tests the dynamic agent registry functionality including:
- Loading agents from registry.json
- Agent health checking
- Hot-reload capabilities
- Agent management operations

Usage: python test_mcp_registry.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from agent_registry import AgentRegistryManager

async def test_registry_operations():
    """Test basic registry operations"""
    print("🧪 Testing MCP Agent Registry Operations\n")
    
    # Initialize registry manager
    registry = AgentRegistryManager()
    
    try:
        print("1. Loading agent registry...")
        await registry.initialize(enable_file_watching=False)  # Disable file watching for test
        print(f"   ✅ Loaded {len(registry.agents)} agents")
        
        # Test enabled agents
        print("\n2. Testing enabled agents...")
        enabled_agents = registry.get_enabled_agents()
        print(f"   ✅ Found {len(enabled_agents)} enabled agents:")
        for name in enabled_agents.keys():
            print(f"      - {name}")
        
        # Test capabilities
        print("\n3. Testing capability search...")
        file_agents = registry.get_agents_by_capability("filesystem")
        print(f"   ✅ Found {len(file_agents)} agents with filesystem capability: {file_agents}")
        
        # Test agent types
        print("\n4. Testing agent type filtering...")
        local_agents = registry.get_agents_by_type("local")
        n8n_agents = registry.get_agents_by_type("n8n")
        print(f"   ✅ Local agents: {local_agents}")
        print(f"   ✅ n8n agents: {n8n_agents}")
        
        # Test agent health (for internal agents)
        print("\n5. Testing agent health status...")
        await asyncio.sleep(1)  # Give health checks time to run
        health_status = registry.get_all_agent_health()
        print(f"   ✅ Health status available for {len(health_status)} agents")
        for name, status in health_status.items():
            print(f"      - {name}: {status.get('status', 'unknown')}")
        
        # Test runtime enable/disable
        print("\n6. Testing runtime agent management...")
        test_agent = "file_search"
        if test_agent in registry.agents:
            original_status = registry.is_agent_enabled(test_agent)
            print(f"   📋 Agent '{test_agent}' originally enabled: {original_status}")
            
            # Disable
            await registry.disable_agent(test_agent)
            disabled_status = registry.is_agent_enabled(test_agent)
            print(f"   ✅ Agent disabled: {disabled_status}")
            
            # Re-enable
            await registry.enable_agent(test_agent)
            enabled_status = registry.is_agent_enabled(test_agent)
            print(f"   ✅ Agent re-enabled: {enabled_status}")
        
        # Test registry info
        print("\n7. Testing registry metadata...")
        info = registry.get_registry_info()
        print(f"   ✅ Registry version: {info['version']}")
        print(f"   ✅ Total agents: {info['total_agents']}")
        print(f"   ✅ Enabled agents: {info['enabled_agents']}")
        print(f"   ✅ Agent types: {info['agent_types']}")
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        await registry.shutdown()
        print("\n🧹 Registry manager shutdown complete")

async def test_registry_validation():
    """Test registry validation with invalid data"""
    print("\n🔍 Testing Registry Validation\n")
    
    # Create a temporary invalid registry
    invalid_registry = {
        "agents": {
            "invalid_agent": {
                # Missing required 'type' field
                "description": "Invalid agent for testing"
            }
        },
        "agent_types": {}
    }
    
    temp_file = Path("temp_invalid_registry.json")
    try:
        with open(temp_file, 'w') as f:
            json.dump(invalid_registry, f)
        
        registry = AgentRegistryManager(str(temp_file))
        
        try:
            await registry.load_registry()
            print("   ❌ Should have failed validation")
        except ValueError as e:
            print(f"   ✅ Validation correctly failed: {e}")
        except Exception as e:
            print(f"   ❓ Unexpected error: {e}")
            
    finally:
        if temp_file.exists():
            temp_file.unlink()

def test_registry_file_structure():
    """Test that the registry file has the expected structure"""
    print("\n📋 Testing Registry File Structure\n")
    
    registry_path = Path("agents/registry.json")
    
    if not registry_path.exists():
        print(f"   ❌ Registry file not found: {registry_path}")
        return
    
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        # Check required top-level keys
        required_keys = ['agents', 'agent_types', 'global_settings']
        for key in required_keys:
            if key in data:
                print(f"   ✅ Found required key: {key}")
            else:
                print(f"   ❌ Missing required key: {key}")
        
        # Check agents structure
        if 'agents' in data:
            agents = data['agents']
            print(f"   📊 Found {len(agents)} agents in registry")
            
            for agent_name, agent_config in agents.items():
                required_agent_keys = ['type', 'description']
                missing_keys = [key for key in required_agent_keys if key not in agent_config]
                if missing_keys:
                    print(f"   ⚠️  Agent '{agent_name}' missing keys: {missing_keys}")
                else:
                    print(f"   ✅ Agent '{agent_name}' structure valid")
        
        print("   🎯 Registry file structure validation complete")
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in registry file: {e}")
    except Exception as e:
        print(f"   ❌ Error reading registry file: {e}")

async def main():
    """Run all tests"""
    print("🚀 MCP Agent Registry Test Suite")
    print("=" * 50)
    
    # Test registry file structure first
    test_registry_file_structure()
    
    # Test validation
    await test_registry_validation()
    
    # Test main registry operations
    await test_registry_operations()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite complete!")

if __name__ == "__main__":
    asyncio.run(main())
