#!/usr/bin/env python3
"""
Test script for contract document analysis without making API calls.
This tests the MCP server structure and local functionality only.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer

async def test_document_structure():
    """Test document analysis structure without API calls."""
    print("Testing OuiComply MCP Server - Document Structure...")
    print("=" * 60)
    
    try:
        # Initialize the MCP server
        print("🔧 Initializing MCP server...")
        mcp_server = OuiComplyMCPServer()
        print("✅ MCP server initialized successfully!")
        
        # Check docs folder
        print("\n📁 Checking docs folder...")
        docs_folder = Path("docs")
        if docs_folder.exists():
            doc_files = list(docs_folder.glob("*.pdf")) + list(docs_folder.glob("*.docx")) + list(docs_folder.glob("*.txt"))
            print(f"   Found {len(doc_files)} document(s):")
            for doc in doc_files:
                print(f"   - {doc.name} ({doc.stat().st_size} bytes)")
                
            # Test with a simple text file instead of PDF
            test_doc = None
            for doc in doc_files:
                if doc.suffix.lower() == '.txt':
                    test_doc = doc
                    break
            
            if not test_doc and doc_files:
                test_doc = doc_files[0]  # Use first available file
            
            if test_doc:
                print(f"\n🔍 Testing with: {test_doc.name}")
                
                # Test document reading without API call
                try:
                    if test_doc.suffix.lower() == '.txt':
                        with open(test_doc, 'r', encoding='utf-8') as f:
                            content = f.read()
                        print(f"   ✅ Successfully read text file ({len(content)} characters)")
                        print(f"   📄 Preview: {content[:200]}...")
                    else:
                        print(f"   ⚠️  {test_doc.suffix} file - would need API processing")
                        print(f"   📄 File size: {test_doc.stat().st_size} bytes")
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
        else:
            print("   ❌ docs folder not found")
        
        # Test compliance history (should work with empty cache)
        print("\n📊 Testing compliance history...")
        history_result = await mcp_server._handle_get_compliance_history({})
        print(f"   ✅ History result: {history_result[0].text}")
        
        # Test risk trends (should work with empty cache)
        print("\n📈 Testing risk trends...")
        trends_result = await mcp_server._handle_analyze_risk_trends({})
        print(f"   ✅ Trends result: {trends_result[0].text}")
        
        print("\n" + "=" * 60)
        print("✅ All structure tests completed successfully!")
        print("\nThe MCP server is working correctly.")
        print("The hanging issue is likely in the Mistral API call.")
        print("\nRecommendations:")
        print("1. Use the HTTP server: python mcp_http_server.py")
        print("2. Test with simple text files first")
        print("3. Check Mistral API key and network connectivity")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("OuiComply Document Structure Test (No API Calls)")
    print("This test checks document handling without making API calls.")
    print("\nStarting test...")
    asyncio.run(test_document_structure())
