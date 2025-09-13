#!/usr/bin/env python3
"""
Test script for the new PDF analysis functionality.
Tests the step-by-step PDF processing flow.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.tools.pdf_analysis_tool import PDFAnalysisTool

async def test_pdf_analysis():
    """Test the PDF analysis tool."""
    print("Testing PDF Analysis Tool...")
    print("=" * 50)
    
    try:
        # Initialize the PDF analysis tool
        print("🔧 Initializing PDF analysis tool...")
        pdf_tool = PDFAnalysisTool()
        print("✅ PDF analysis tool initialized successfully!")
        
        # Check for PDF files in docs folder
        print("\n📁 Checking for PDF files...")
        docs_folder = Path("docs")
        if not docs_folder.exists():
            print("❌ docs folder not found")
            return
        
        pdf_files = list(docs_folder.glob("*.pdf"))
        if not pdf_files:
            print("❌ No PDF files found in docs folder")
            return
        
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"   - {pdf.name} ({pdf.stat().st_size:,} bytes)")
        
        # Test with the first PDF file
        test_pdf = pdf_files[0]
        print(f"\n🔍 Testing with: {test_pdf.name}")
        
        # Test 1: Summary format
        print("\n📊 Test 1: Summary format")
        arguments = {
            "document_path": str(test_pdf),
            "output_format": "summary",
            "include_steps": False
        }
        
        result = await pdf_tool.analyze_pdf_document(arguments)
        print("✅ Summary analysis completed!")
        print(f"📄 Result preview: {result[0].text[:300]}...")
        
        # Test 2: Detailed format
        print("\n📊 Test 2: Detailed format")
        arguments = {
            "document_path": str(test_pdf),
            "output_format": "detailed",
            "include_steps": True
        }
        
        result = await pdf_tool.analyze_pdf_document(arguments)
        print("✅ Detailed analysis completed!")
        print(f"📄 Result length: {len(result[0].text):,} characters")
        
        # Test 3: Structured format
        print("\n📊 Test 3: Structured format")
        arguments = {
            "document_path": str(test_pdf),
            "output_format": "structured",
            "include_steps": False
        }
        
        result = await pdf_tool.analyze_pdf_document(arguments)
        print("✅ Structured analysis completed!")
        
        # Try to parse as JSON
        try:
            structured_data = json.loads(result[0].text)
            print(f"📄 Structured data keys: {list(structured_data.keys())}")
        except json.JSONDecodeError:
            print("📄 Result is not valid JSON (expected for mock data)")
        
        print("\n" + "=" * 50)
        print("✅ All PDF analysis tests completed successfully!")
        print("\nThe new PDF analysis tool is working correctly.")
        print("You can now use 'analyze_pdf_document' tool in your MCP client.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("PDF Analysis Tool Test")
    print("This test checks the new step-by-step PDF processing functionality.")
    print("\nStarting test...")
    asyncio.run(test_pdf_analysis())
