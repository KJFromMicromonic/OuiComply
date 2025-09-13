#!/usr/bin/env python3
"""
Test script for contract document analysis.
Tests the MCP server with contract documents in the docs folder.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer

async def test_contract_documents():
    """Test contract document analysis."""
    print("Testing OuiComply MCP Server with Contract Documents...")
    print("=" * 60)
    
    # Initialize the MCP server
    mcp_server = OuiComplyMCPServer()
    
    # Check if docs folder exists and has files
    docs_folder = Path("docs")
    if not docs_folder.exists():
        print("❌ docs folder not found. Creating it...")
        docs_folder.mkdir()
        print("✅ Created docs folder. Please add contract documents to test.")
        return
    
    # List available documents
    doc_files = list(docs_folder.glob("*.pdf")) + list(docs_folder.glob("*.docx")) + list(docs_folder.glob("*.txt"))
    
    if not doc_files:
        print("❌ No contract documents found in docs folder.")
        print("Please add PDF, DOCX, or TXT files to the docs folder to test.")
        return
    
    print(f"📁 Found {len(doc_files)} document(s) in docs folder:")
    for doc in doc_files:
        print(f"   - {doc.name}")
    
    print("\n" + "=" * 60)
    print("Testing Document Analysis...")
    
    # Test with the first document
    test_doc = doc_files[0]
    print(f"\n🔍 Analyzing: {test_doc.name}")
    
    try:
        # Simulate document analysis
        arguments = {
            "document_path": str(test_doc),
            "frameworks": ["GDPR", "SOX", "CCPA"],
            "analysis_type": "comprehensive"
        }
        
        result = await mcp_server._handle_analyze_document_compliance(arguments)
        
        print("✅ Analysis completed successfully!")
        print(f"📊 Result: {result[0].text[:200]}...")
        
        # Test compliance history
        print("\n📈 Testing compliance history...")
        history_result = await mcp_server._handle_get_compliance_history({})
        print(f"📋 History: {history_result[0].text[:200]}...")
        
        # Test risk trends
        print("\n📊 Testing risk trends...")
        trends_result = await mcp_server._handle_analyze_risk_trends({})
        print(f"📈 Trends: {trends_result[0].text[:200]}...")
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\nThe MCP server is ready to analyze contract documents.")
        print("You can now connect Le Chat or other MCP clients to use the server.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("This might be due to missing Mistral API key or other configuration issues.")

if __name__ == "__main__":
    print("OuiComply Contract Document Test")
    print("Make sure you have:")
    print("1. Set MISTRAL_KEY in your .env file")
    print("2. Added contract documents to the docs/ folder")
    print("3. Installed all requirements: pip install -r requirements.txt")
    print("\nPress Enter to start testing...")
    input()
    asyncio.run(test_contract_documents())
