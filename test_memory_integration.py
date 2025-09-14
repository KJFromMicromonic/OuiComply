#!/usr/bin/env python3
"""
Test script for memory integration methods.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.tools.memory_integration import MemoryIntegration


async def test_memory_integration():
    """Test the memory integration methods."""
    print("🧪 Testing Memory Integration Methods")
    print("=" * 50)
    
    # Create memory integration instance
    memory = MemoryIntegration(use_lechat_mcp=False)  # Use local storage for testing
    
    # Test store_insight
    print("\n1. Testing store_insight...")
    try:
        result = await memory.store_insight(
            team_id="test_team_123",
            insight="Test compliance insight",
            category="testing"
        )
        print(f"   ✅ store_insight result: {result}")
    except Exception as e:
        print(f"   ❌ store_insight error: {e}")
    
    # Test get_team_status
    print("\n2. Testing get_team_status...")
    try:
        result = await memory.get_team_status("test_team_123")
        print(f"   ✅ get_team_status result: {result}")
    except Exception as e:
        print(f"   ❌ get_team_status error: {e}")
    
    # Test get_team_memory
    print("\n3. Testing get_team_memory...")
    try:
        result = await memory.get_team_memory("test_team_123")
        print(f"   ✅ get_team_memory result: {result}")
    except Exception as e:
        print(f"   ❌ get_team_memory error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Memory integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_memory_integration())
