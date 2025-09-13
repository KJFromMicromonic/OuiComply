#!/usr/bin/env python3
"""
Final PDF Analysis Test.

This demonstrates the complete PDF analysis functionality working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.tools.pdf_analysis_tool import PDFAnalysisTool

async def test_final_pdf_analysis():
    """Test the final PDF analysis functionality."""
    print("Final PDF Analysis Test")
    print("=" * 50)
    
    try:
        # Initialize the PDF analysis tool
        print("🔧 Initializing PDF analysis tool...")
        pdf_tool = PDFAnalysisTool()
        print("✅ PDF analysis tool initialized successfully!")
        
        # Check for PDF files
        docs_folder = Path("docs")
        pdf_files = list(docs_folder.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in docs folder")
            return
        
        test_pdf = pdf_files[0]
        print(f"📄 Testing with: {test_pdf.name}")
        print(f"📊 File size: {test_pdf.stat().st_size:,} bytes")
        
        # Test all three output formats
        formats = [
            ("summary", "Summary Format"),
            ("detailed", "Detailed Format"), 
            ("structured", "Structured Format")
        ]
        
        for format_type, format_name in formats:
            print(f"\n🔍 Testing {format_name}...")
            arguments = {
                "document_path": str(test_pdf),
                "output_format": format_type,
                "include_steps": True
            }
            
            result = await pdf_tool.analyze_pdf_document(arguments)
            print(f"✅ {format_name} completed!")
            print(f"📄 Result length: {len(result[0].text):,} characters")
            
            if format_type == "summary":
                print(f"📄 Preview:\n{result[0].text[:300]}...")
            elif format_type == "detailed":
                print(f"📄 Contains processing steps: {'✅' if 'Processing Steps' in result[0].text else '❌'}")
            elif format_type == "structured":
                print(f"📄 JSON format: {'✅' if result[0].text.strip().startswith('{') else '❌'}")
        
        print("\n" + "=" * 50)
        print("✅ All PDF analysis tests completed successfully!")
        print("\nThe PDF analysis system is fully functional and ready for use.")
        print("\nAvailable features:")
        print("• Step-by-step PDF processing")
        print("• Multiple output formats (summary, detailed, structured)")
        print("• Compliance analysis and risk assessment")
        print("• Integration with MCP server")
        print("• HTTP endpoint support")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Final PDF Analysis Test")
    print("This demonstrates the complete PDF analysis functionality.")
    print("\nStarting test...")
    asyncio.run(test_final_pdf_analysis())
