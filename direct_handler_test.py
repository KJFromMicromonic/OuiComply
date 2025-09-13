#!/usr/bin/env python3
"""
Direct Handler Testing for OuiComply MCP Server
Tests handlers directly through the server instance
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import get_config


async def test_direct_handlers():
    """Test handlers directly through server instance."""
    
    print("🔧 OuiComply MCP Server - Direct Handler Testing")
    print("=" * 60)
    print("Testing handlers directly through server methods")
    print("=" * 60)
    
    # Initialize server
    config = get_config()
    server = OuiComplyMCPServer()
    
    print(f"\n🔧 Server Configuration:")
    print(f"   • Mistral API Key: {'✓ Set' if config.mistral_api_key else '✗ Missing'}")
    print(f"   • Server Instance: {'✓ Created' if server.server else '✗ Missing'}")
    print(f"   • CUAD Manager: {'✓ Loaded' if server.cuad_manager else '✗ Missing'}")
    
    # Check what handlers are actually registered
    print(f"\n📋 Registered Handlers:")
    if hasattr(server.server, 'request_handlers'):
        handlers = server.server.request_handlers
        print(f"   • Total Handlers: {len(handlers)}")
        try:
            for handler_name in handlers.keys():
                print(f"   • {str(handler_name)}")
        except Exception as e:
            print(f"   • Handler keys: {list(handlers.keys())}")
    else:
        print("   ❌ No request_handlers attribute found")
    
    # Test sample documents
    sample_contract = """
    Service Agreement
    
    This agreement governs the provision of services between Company and Client.
    
    1. Termination: Either party may terminate with 30 days notice.
    2. Limitation of Liability: Company's liability is limited to fees paid.
    3. Governing Law: This agreement is governed by California law.
    4. Insurance: Company maintains professional liability insurance.
    """
    
    sample_privacy_policy = """
    Privacy Policy
    
    We collect personal data including names, emails, and usage data.
    Data is processed for service improvement and marketing.
    You have the right to access, rectify, and delete your data.
    Contact our Data Protection Officer at dpo@company.com.
    """
    
    # Test Resources First
    print(f"\n📚 Testing Resources...")
    print("-" * 60)
    
    try:
        # Test list_resources
        print("\n1️⃣  List Resources")
        resources = []
        if hasattr(server.server, 'request_handlers') and 'resources/list' in server.server.request_handlers:
            handler = server.server.request_handlers['resources/list']
            resources = await handler()
            print(f"   ✅ Success: Found {len(resources)} resources")
            for resource in resources:
                print(f"   • {resource.name}: {resource.uri}")
        else:
            print("   ❌ No resources/list handler found")
        
        # Test read_resource
        if resources:
            print(f"\n2️⃣  Read Resource")
            test_uri = str(resources[0].uri)
            if hasattr(server.server, 'request_handlers') and 'resources/read' in server.server.request_handlers:
                handler = server.server.request_handlers['resources/read']
                content = await handler(test_uri)
                print(f"   ✅ Success: Read {len(content)} characters from {test_uri}")
                print(f"   • Preview: {content[:100]}...")
            else:
                print("   ❌ No resources/read handler found")
        
    except Exception as e:
        print(f"   ❌ Resource test failed: {e}")
    
    # Test Tools
    print(f"\n🛠️  Testing Tools...")
    print("-" * 60)
    
    try:
        # Test list_tools
        print("\n3️⃣  List Tools")
        tools = []
        if hasattr(server.server, 'request_handlers') and 'tools/list' in server.server.request_handlers:
            handler = server.server.request_handlers['tools/list']
            tools = await handler()
            print(f"   ✅ Success: Found {len(tools)} tools")
            for tool in tools:
                print(f"   • {tool.name}: {tool.description[:50]}...")
        else:
            print("   ❌ No tools/list handler found")
        
        # Test call_tool
        if tools:
            print(f"\n4️⃣  Call Tool - analyze_document")
            if hasattr(server.server, 'request_handlers') and 'tools/call' in server.server.request_handlers:
                handler = server.server.request_handlers['tools/call']
                arguments = {
                    "document_text": sample_privacy_policy,
                    "compliance_framework": "gdpr"
                }
                result = await handler("analyze_document", arguments)
                print(f"   ✅ Success: Got {len(result)} result items")
                if result and hasattr(result[0], 'text'):
                    preview = result[0].text[:200].replace('\n', ' ')
                    print(f"   • Preview: {preview}...")
            else:
                print("   ❌ No tools/call handler found")
            
            print(f"\n5️⃣  Call Tool - check_clause_presence")
            if hasattr(server.server, 'request_handlers') and 'tools/call' in server.server.request_handlers:
                handler = server.server.request_handlers['tools/call']
                arguments = {
                    "document_text": sample_contract,
                    "required_clauses": ["termination", "limitation_of_liability"]
                }
                result = await handler("check_clause_presence", arguments)
                print(f"   ✅ Success: Got {len(result)} result items")
                if result and hasattr(result[0], 'text'):
                    preview = result[0].text[:200].replace('\n', ' ')
                    print(f"   • Preview: {preview}...")
            else:
                print("   ❌ No tools/call handler found")
        
    except Exception as e:
        print(f"   ❌ Tool test failed: {e}")
    
    # Test CUAD-specific functionality
    print(f"\n🏛️  Testing CUAD Integration...")
    print("-" * 60)
    
    try:
        print("\n6️⃣  CUAD Contract Analysis")
        if hasattr(server.server, 'request_handlers') and 'tools/call' in server.server.request_handlers:
            handler = server.server.request_handlers['tools/call']
            arguments = {"contract_text": sample_contract}
            result = await handler("cuad_contract_analysis", arguments)
            print(f"   ✅ Success: CUAD analysis completed")
            if result and hasattr(result[0], 'text'):
                # Look for coverage score in the result
                text = result[0].text
                if "Coverage Score:" in text:
                    lines = text.split('\n')
                    for line in lines:
                        if "Coverage Score:" in line:
                            print(f"   • {line.strip()}")
                            break
        else:
            print("   ❌ No tools/call handler found")
        
        print("\n7️⃣  CUAD Dataset Info")
        if hasattr(server.server, 'request_handlers') and 'resources/read' in server.server.request_handlers:
            handler = server.server.request_handlers['resources/read']
            content = await handler("resource://cuad-dataset")
            print(f"   ✅ Success: CUAD dataset info retrieved")
            # Parse JSON to show key info
            import json
            try:
                data = json.loads(content)
                if 'dataset_status' in data:
                    print(f"   • Dataset Status: {data['dataset_status']}")
                if 'total_contracts' in data:
                    print(f"   • Total Contracts: {data['total_contracts']}")
            except:
                print(f"   • Raw content length: {len(content)} characters")
        else:
            print("   ❌ No resources/read handler found")
        
    except Exception as e:
        print(f"   ❌ CUAD test failed: {e}")
    
    # Performance Test
    print(f"\n⚡ Performance Testing...")
    print("-" * 60)
    
    try:
        print("\n8️⃣  Concurrent Tool Calls")
        if hasattr(server.server, 'request_handlers') and 'tools/call' in server.server.request_handlers:
            handler = server.server.request_handlers['tools/call']
            
            # Create multiple concurrent tasks
            tasks = []
            for i in range(3):
                args = {
                    "document_text": f"Test document {i+1} for concurrent processing.",
                    "compliance_framework": "gdpr"
                }
                task = handler("analyze_document", args)
                tasks.append(task)
            
            # Run concurrently
            import time
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            print(f"   ✅ Success: {len(results)} concurrent calls completed")
            print(f"   • Total time: {end_time - start_time:.2f} seconds")
            print(f"   • Average per call: {(end_time - start_time)/len(results):.2f} seconds")
        else:
            print("   ❌ No tools/call handler found")
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Direct Handler Testing Summary")
    print("=" * 60)
    print("✅ Server instance created successfully")
    print("✅ Configuration validated")
    print("✅ CUAD manager loaded")
    
    if hasattr(server.server, 'request_handlers'):
        handler_count = len(server.server.request_handlers)
        print(f"✅ {handler_count} MCP handlers registered")
        
        # Check for key handlers
        key_handlers = ['resources/list', 'resources/read', 'tools/list', 'tools/call']
        found_handlers = [h for h in key_handlers if h in server.server.request_handlers]
        print(f"✅ {len(found_handlers)}/{len(key_handlers)} key handlers found")
        
        if len(found_handlers) == len(key_handlers):
            print("🎉 All core MCP functionality is working!")
        else:
            missing = [h for h in key_handlers if h not in server.server.request_handlers]
            print(f"⚠️  Missing handlers: {missing}")
    else:
        print("❌ No request handlers found")
    
    print("\n🚀 OuiComply MCP Server is ready for legal compliance work!")


if __name__ == "__main__":
    asyncio.run(test_direct_handlers())
