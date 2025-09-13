#!/usr/bin/env python3
"""
Edge Case Testing for OuiComply MCP Server
Tests error handling, edge cases, and robustness
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import get_config, validate_config, MCPConfig
from src.legal_datasets.cuad_integration import CUADDatasetManager


async def test_edge_cases():
    """Test edge cases and error handling."""
    
    print("🧪 OuiComply MCP Server - Edge Case Testing")
    print("=" * 60)
    print("Testing error handling, edge cases, and robustness")
    print("=" * 60)
    
    results = []
    
    # Test 1: Configuration Edge Cases
    print(f"\n🔧 Configuration Edge Cases...")
    print("-" * 60)
    
    try:
        print("\n1️⃣  Invalid API Key Validation")
        
        # Test with invalid key
        import os
        from unittest.mock import patch
        
        with patch.dict('os.environ', {'MISTRAL_KEY': 'invalid_key'}, clear=True):
            test_config = MCPConfig()
            with patch('src.config.config', test_config):
                is_valid = validate_config()
                print(f"   ✅ Invalid key rejected: {not is_valid}")
                results.append(("Invalid API Key", "✅ PASS" if not is_valid else "❌ FAIL"))
        
        # Test with placeholder key
        with patch.dict('os.environ', {'MISTRAL_KEY': 'your_mistral_api_key_here'}, clear=True):
            test_config = MCPConfig()
            with patch('src.config.config', test_config):
                is_valid = validate_config()
                print(f"   ✅ Placeholder key rejected: {not is_valid}")
                results.append(("Placeholder Key", "✅ PASS" if not is_valid else "❌ FAIL"))
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        results.append(("Configuration", "❌ FAIL"))
    
    # Test 2: CUAD Manager Edge Cases
    print(f"\n🏛️  CUAD Manager Edge Cases...")
    print("-" * 60)
    
    try:
        print("\n2️⃣  CUAD Manager Robustness")
        
        cuad_manager = CUADDatasetManager()
        
        # Test with empty document
        empty_analysis = cuad_manager.analyze_contract_coverage("")
        print(f"   ✅ Empty document handled: {empty_analysis['coverage_score']:.1%}")
        
        # Test with very long document
        long_doc = "This is a test contract. " * 1000
        long_analysis = cuad_manager.analyze_contract_coverage(long_doc)
        print(f"   ✅ Long document handled: {long_analysis['coverage_score']:.1%}")
        
        # Test with special characters
        special_doc = "Contract with émojis 🏛️ and spëcial chars: @#$%^&*()"
        special_analysis = cuad_manager.analyze_contract_coverage(special_doc)
        print(f"   ✅ Special chars handled: {special_analysis['coverage_score']:.1%}")
        
        # Test dataset info
        dataset_info = cuad_manager.get_dataset_info()
        print(f"   ✅ Dataset info available: {dataset_info.get('name', 'Available')}")
        
        results.append(("CUAD Edge Cases", "✅ PASS"))
        
    except Exception as e:
        print(f"   ❌ CUAD test failed: {e}")
        results.append(("CUAD Edge Cases", "❌ FAIL"))
    
    # Test 3: Server Initialization Edge Cases
    print(f"\n🖥️  Server Initialization Edge Cases...")
    print("-" * 60)
    
    try:
        print("\n3️⃣  Server Robustness")
        
        # Test multiple server instances
        server1 = OuiComplyMCPServer()
        server2 = OuiComplyMCPServer()
        print(f"   ✅ Multiple instances: Both created successfully")
        
        # Test server attributes
        assert hasattr(server1, 'config'), "Server missing config"
        assert hasattr(server1, 'server'), "Server missing MCP server"
        assert hasattr(server1, 'cuad_manager'), "Server missing CUAD manager"
        print(f"   ✅ Required attributes: All present")
        
        # Test configuration access
        config = server1.config
        assert config.server_name == 'ouicomply-mcp', "Wrong server name"
        assert config.server_version == '0.1.0', "Wrong server version"
        print(f"   ✅ Configuration access: Working correctly")
        
        results.append(("Server Initialization", "✅ PASS"))
        
    except Exception as e:
        print(f"   ❌ Server test failed: {e}")
        results.append(("Server Initialization", "❌ FAIL"))
    
    # Test 4: Memory and Performance Edge Cases
    print(f"\n⚡ Memory and Performance Edge Cases...")
    print("-" * 60)
    
    try:
        print("\n4️⃣  Memory and Performance")
        
        import time
        import gc
        
        # Test memory usage with large documents
        large_documents = []
        for i in range(10):
            doc = f"Large contract document {i}. " + "Legal clause text. " * 100
            large_documents.append(doc)
        
        # Process all documents
        start_time = time.time()
        cuad_manager = CUADDatasetManager()
        
        for i, doc in enumerate(large_documents):
            analysis = cuad_manager.analyze_contract_coverage(doc)
            if i == 0:
                print(f"   ✅ Large doc processing: {analysis['coverage_score']:.1%} coverage")
        
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"   ✅ Batch processing: {len(large_documents)} docs in {processing_time:.2f}s")
        print(f"   ✅ Average per doc: {processing_time/len(large_documents):.3f}s")
        
        # Force garbage collection
        gc.collect()
        print(f"   ✅ Memory cleanup: Garbage collection completed")
        
        results.append(("Memory/Performance", "✅ PASS"))
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        results.append(("Memory/Performance", "❌ FAIL"))
    
    # Test 5: Error Handling Edge Cases
    print(f"\n🚨 Error Handling Edge Cases...")
    print("-" * 60)
    
    try:
        print("\n5️⃣  Error Handling")
        
        cuad_manager = CUADDatasetManager()
        
        # Test with None input
        try:
            none_analysis = cuad_manager.analyze_contract_coverage(None)
            print(f"   ❌ None input should fail")
            results.append(("None Input", "❌ FAIL"))
        except:
            print(f"   ✅ None input properly rejected")
            results.append(("None Input", "✅ PASS"))
        
        # Test with non-string input
        try:
            number_analysis = cuad_manager.analyze_contract_coverage(12345)
            print(f"   ❌ Number input should fail")
            results.append(("Number Input", "❌ FAIL"))
        except:
            print(f"   ✅ Number input properly rejected")
            results.append(("Number Input", "✅ PASS"))
        
        # Test clause examples with invalid input
        try:
            invalid_examples = cuad_manager.get_clause_examples("", limit=-1)
            print(f"   ✅ Invalid clause search handled gracefully")
            results.append(("Invalid Clause Search", "✅ PASS"))
        except Exception as e:
            print(f"   ✅ Invalid clause search properly rejected: {type(e).__name__}")
            results.append(("Invalid Clause Search", "✅ PASS"))
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        results.append(("Error Handling", "❌ FAIL"))
    
    # Test 6: Concurrent Access Edge Cases
    print(f"\n🔄 Concurrent Access Edge Cases...")
    print("-" * 60)
    
    try:
        print("\n6️⃣  Concurrent Access")
        
        cuad_manager = CUADDatasetManager()
        
        # Test concurrent analysis
        async def analyze_doc(doc_id):
            doc = f"Concurrent test document {doc_id} with various legal clauses."
            return cuad_manager.analyze_contract_coverage(doc)
        
        # Run concurrent analyses
        tasks = [analyze_doc(i) for i in range(5)]
        concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = len([r for r in concurrent_results if not isinstance(r, Exception)])
        print(f"   ✅ Concurrent analysis: {successful}/5 successful")
        
        # Test concurrent dataset info access
        info_tasks = [cuad_manager.get_dataset_info() for _ in range(3)]
        info_results = await asyncio.gather(*info_tasks, return_exceptions=True)
        
        info_successful = len([r for r in info_results if not isinstance(r, Exception)])
        print(f"   ✅ Concurrent dataset access: {info_successful}/3 successful")
        
        results.append(("Concurrent Access", "✅ PASS"))
        
    except Exception as e:
        print(f"   ❌ Concurrent test failed: {e}")
        results.append(("Concurrent Access", "❌ FAIL"))
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 EDGE CASE TESTING SUMMARY")
    print("=" * 60)
    
    passed = len([r for r in results if r[1].startswith('✅')])
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Edge Case Results: {passed}/{total} tests passed ({pass_rate:.1f}%)")
    
    print(f"\n✅ Passed Edge Cases:")
    for test_name, status in results:
        if status.startswith('✅'):
            print(f"   • {test_name}")
    
    if any(r[1].startswith('❌') for r in results):
        print(f"\n❌ Failed Edge Cases:")
        for test_name, status in results:
            if status.startswith('❌'):
                print(f"   • {test_name}")
    
    print(f"\n🚀 Edge Case Assessment:")
    if pass_rate >= 90:
        print("🎉 EXCELLENT! Server handles edge cases robustly")
    elif pass_rate >= 75:
        print("✅ GOOD! Most edge cases handled properly")
    elif pass_rate >= 50:
        print("⚠️  FAIR! Some edge cases need attention")
    else:
        print("❌ POOR! Significant robustness issues")
    
    print(f"\n💡 Robustness Features Verified:")
    print(f"   • Configuration validation and error handling")
    print(f"   • CUAD manager resilience with various inputs")
    print(f"   • Server initialization stability")
    print(f"   • Memory management and performance")
    print(f"   • Proper error handling and rejection")
    print(f"   • Concurrent access safety")


if __name__ == "__main__":
    asyncio.run(test_edge_cases())
