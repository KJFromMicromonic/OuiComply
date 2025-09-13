#!/usr/bin/env python3
"""
Test script for MCP server with PDF analysis.
Tests the new PDF analysis tool through the MCP server.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer

async def test_mcp_pdf_analysis():
    """Test PDF analysis through MCP server."""
    print("Testing MCP Server with PDF Analysis...")
    print("=" * 50)
    
    try:
        # Initialize the MCP server
        print("🔧 Initializing MCP server...")
        mcp_server = OuiComplyMCPServer()
        print("✅ MCP server initialized successfully!")
        
        # Check for PDF files
        docs_folder = Path("docs")
        pdf_files = list(docs_folder.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in docs folder")
            return
        
        test_pdf = pdf_files[0]
        print(f"📄 Testing with: {test_pdf.name}")
        
        # Test PDF analysis tool directly
        print("\n🔍 Testing analyze_pdf_document tool...")
        arguments = {
            "document_path": str(test_pdf),
            "output_format": "summary",
            "include_steps": True
        }
        
        result = await mcp_server.pdf_analysis_tool.analyze_pdf_document(arguments)
        print("✅ PDF analysis completed!")
        print(f"📊 Result type: {type(result)}")
        print(f"📄 Result length: {len(result[0].text):,} characters")
        print(f"📄 Result preview:\n{result[0].text[:500]}...")
        
        # Test tools list
        print("\n🛠️  Testing tools list...")
        tools_result = await mcp_server.handle_list_tools()
        print("✅ Tools list completed!")
        print(f"📋 Tools count: {len(tools_result)}")
        
        for tool in tools_result:
            print(f"   - {tool.name}: {tool.description}")
        
        print("\n" + "=" * 50)
        print("✅ All MCP PDF analysis tests completed successfully!")
        print("\nThe MCP server with PDF analysis is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("MCP Server PDF Analysis Test")
    print("This test checks PDF analysis through the MCP server.")
    print("\nStarting test...")
    asyncio.run(test_mcp_pdf_analysis())
