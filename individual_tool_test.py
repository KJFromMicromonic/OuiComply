#!/usr/bin/env python3
"""
Individual Tool Testing for OuiComply MCP Server
Tests each MCP tool function directly
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import get_config


async def test_individual_tools():
    """Test each MCP tool individually."""
    
    print("🛠️  OuiComply MCP Server - Individual Tool Testing")
    print("=" * 60)
    print("Testing each legal compliance tool directly")
    print("=" * 60)
    
    # Initialize server
    config = get_config()
    server = OuiComplyMCPServer()
    
    print(f"\n🔧 Server Configuration:")
    print(f"   • Mistral API Key: {'✓ Set' if config.mistral_api_key else '✗ Missing'}")
    print(f"   • CUAD Manager: {'✓ Loaded' if server.cuad_manager else '✗ Missing'}")
    
    # Test documents
    sample_contract = """
    Service Agreement
    
    This agreement governs the provision of services between Company and Client.
    
    1. Termination: Either party may terminate with 30 days notice.
    2. Limitation of Liability: Company's liability is limited to fees paid.
    3. Governing Law: This agreement is governed by California law.
    4. Insurance: Company maintains professional liability insurance.
    5. Confidentiality: Both parties agree to maintain confidentiality.
    """
    
    sample_privacy_policy = """
    Privacy Policy
    
    We collect personal data including names, emails, and usage data.
    Data is processed for service improvement and marketing.
    You have the right to access, rectify, and delete your data.
    Data is stored securely and may be transferred internationally.
    Contact our Data Protection Officer at dpo@company.com.
    """
    
    # Test cases for each tool
    test_cases = [
        {
            "tool": "analyze_document",
            "name": "Document Analysis (GDPR)",
            "args": {
                "document_text": sample_privacy_policy,
                "compliance_framework": "gdpr"
            }
        },
        {
            "tool": "analyze_document", 
            "name": "Document Analysis (CCPA)",
            "args": {
                "document_text": sample_privacy_policy,
                "compliance_framework": "ccpa"
            }
        },
        {
            "tool": "check_clause_presence",
            "name": "Clause Presence Check",
            "args": {
                "document_text": sample_contract,
                "required_clauses": ["termination", "limitation_of_liability", "governing_law"]
            }
        },
        {
            "tool": "risk_assessment",
            "name": "Risk Assessment",
            "args": {
                "document_text": sample_contract,
                "document_type": "contract"
            }
        },
        {
            "tool": "cuad_contract_analysis",
            "name": "CUAD Contract Analysis",
            "args": {
                "contract_text": sample_contract
            }
        },
        {
            "tool": "search_cuad_examples",
            "name": "CUAD Examples Search",
            "args": {
                "clause_type": "Limitation of Liability",
                "limit": 2
            }
        },
        {
            "tool": "generate_contract_template",
            "name": "Contract Template Generation",
            "args": {
                "contract_type": "service"
            }
        }
    ]
    
    print(f"\n🧪 Testing {len(test_cases)} tools...")
    print("-" * 60)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣  {test_case['name']}")
        print(f"   Tool: {test_case['tool']}")
        print(f"   Arguments: {len(test_case['args'])} parameters")
        
        try:
            # Get the call_tool handler
            handlers = server.server.request_handlers
            if "tools/call" in handlers:
                handler = handlers["tools/call"]
                result = await handler(test_case['tool'], test_case['args'])
                
                print("   ✅ Success:")
                print(f"   • Response Type: {type(result).__name__}")
                print(f"   • Response Length: {len(result)} items")
                if result and hasattr(result[0], 'text'):
                    preview = result[0].text[:150].replace('\n', ' ')
                    print(f"   • Preview: {preview}...")
                
                results.append({
                    "tool": test_case['tool'],
                    "name": test_case['name'],
                    "status": "✅ PASS",
                    "result_length": len(result)
                })
                
            else:
                print("   ❌ Failed: No tools/call handler found")
                results.append({
                    "tool": test_case['tool'],
                    "name": test_case['name'],
                    "status": "❌ FAIL",
                    "error": "No handler"
                })
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                "tool": test_case['tool'],
                "name": test_case['name'],
                "status": "❌ FAIL",
                "error": str(e)
            })
    
    # Test Resources
    print(f"\n📚 Testing Resources...")
    print("-" * 60)
    
    resource_tests = [
        "resource://legal-templates",
        "resource://compliance-frameworks", 
        "resource://cuad-dataset",
        "resource://cuad-clause-categories"
    ]
    
    for resource_uri in resource_tests:
        print(f"\n📄 {resource_uri}")
        try:
            handlers = server.server.request_handlers
            if "resources/read" in handlers:
                handler = handlers["resources/read"]
                content = await handler(resource_uri)
                
                print("   ✅ Success:")
                print(f"   • Content Type: {type(content).__name__}")
                print(f"   • Content Length: {len(content)} characters")
                
                results.append({
                    "resource": resource_uri,
                    "status": "✅ PASS",
                    "content_length": len(content)
                })
            else:
                print("   ❌ Failed: No resources/read handler found")
                results.append({
                    "resource": resource_uri,
                    "status": "❌ FAIL",
                    "error": "No handler"
                })
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                "resource": resource_uri,
                "status": "❌ FAIL", 
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Individual Tool Testing Summary")
    print("=" * 60)
    
    tool_results = [r for r in results if 'tool' in r]
    resource_results = [r for r in results if 'resource' in r]
    
    tool_passed = len([r for r in tool_results if r['status'].startswith('✅')])
    resource_passed = len([r for r in resource_results if r['status'].startswith('✅')])
    
    print(f"📊 Tool Tests: {tool_passed}/{len(tool_results)} passed ({tool_passed/len(tool_results)*100:.1f}%)")
    print(f"📊 Resource Tests: {resource_passed}/{len(resource_results)} passed ({resource_passed/len(resource_results)*100:.1f}%)")
    
    print(f"\n✅ Successful Tools:")
    for result in tool_results:
        if result['status'].startswith('✅'):
            print(f"   • {result['name']}")
    
    print(f"\n✅ Successful Resources:")
    for result in resource_results:
        if result['status'].startswith('✅'):
            print(f"   • {result['resource']}")
    
    if any(r['status'].startswith('❌') for r in results):
        print(f"\n❌ Failed Items:")
        for result in results:
            if result['status'].startswith('❌'):
                item_name = result.get('name', result.get('resource', 'Unknown'))
                error = result.get('error', 'Unknown error')
                print(f"   • {item_name}: {error}")
    
    overall_passed = tool_passed + resource_passed
    overall_total = len(tool_results) + len(resource_results)
    
    print(f"\n🚀 Overall Status: {overall_passed}/{overall_total} tests passed ({overall_passed/overall_total*100:.1f}%)")
    
    if overall_passed == overall_total:
        print("🎉 All individual tools and resources working perfectly!")
    elif overall_passed >= overall_total * 0.8:
        print("✅ Most functionality working - minor issues to address")
    else:
        print("⚠️  Significant issues found - needs attention")


if __name__ == "__main__":
    asyncio.run(test_individual_tools())
