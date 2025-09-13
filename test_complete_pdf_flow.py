#!/usr/bin/env python3
"""
Complete PDF Processing Flow Test.

This demonstrates the step-by-step PDF processing flow:
1. Read PDF file
2. Extract text content using Mistral DocumentAI
3. Generate structured output
4. Provide compliance analysis
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.tools.pdf_processor import PDFProcessor

async def test_complete_pdf_flow():
    """Test the complete PDF processing flow step by step."""
    print("Complete PDF Processing Flow Test")
    print("=" * 60)
    
    try:
        # Initialize the PDF processor
        print("🔧 Initializing PDF processor...")
        processor = PDFProcessor()
        print("✅ PDF processor initialized successfully!")
        
        # Check for PDF files
        docs_folder = Path("docs")
        pdf_files = list(docs_folder.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in docs folder")
            return
        
        test_pdf = pdf_files[0]
        print(f"📄 Processing: {test_pdf.name}")
        print(f"📊 File size: {test_pdf.stat().st_size:,} bytes")
        
        # Process PDF step by step
        print("\n🚀 Starting step-by-step PDF processing...")
        results = await processor.process_pdf_step_by_step(test_pdf)
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 PROCESSING RESULTS")
        print("=" * 60)
        
        if results["overall_status"] == "success":
            print("✅ Overall Status: SUCCESS")
            
            # Show processing steps
            print("\n📊 Processing Steps:")
            for step_name, step_data in results["steps"].items():
                status_icon = "✅" if step_data["status"] == "success" else "❌"
                print(f"   {status_icon} {step_name.replace('_', ' ').title()}")
                print(f"      Timestamp: {step_data['timestamp']}")
                
                if step_name == "read_pdf":
                    print(f"      File Size: {step_data['file_size']:,} bytes")
                elif step_name == "extract_text":
                    print(f"      Text Length: {step_data['text_length']:,} characters")
                    print(f"      Page Count: {step_data['page_count']}")
                elif step_name == "structured_output":
                    print(f"      Summary Length: {step_data['summary_length']:,} characters")
                    print(f"      Key Sections: {step_data['key_sections_count']}")
                    print(f"      Confidence: {step_data['confidence_score']:.2f}")
                elif step_name == "compliance_analysis":
                    print(f"      Compliance Areas: {step_data['compliance_areas']}")
                    print(f"      Risk Indicators: {step_data['risk_indicators']}")
                    print(f"      Recommendations: {step_data['recommendations']}")
                print()
            
            # Show document summary
            doc_content = results["document_content"]
            print("📄 Document Content:")
            print(f"   Document ID: {doc_content['document_id']}")
            print(f"   Content Type: {doc_content['content_type']}")
            print(f"   Page Count: {doc_content['page_count']}")
            print(f"   Text Length: {len(doc_content['extracted_text']):,} characters")
            
            # Show structured output
            structured = results["structured_output"]
            print(f"\n📊 Structured Analysis:")
            print(f"   Summary: {structured['summary']}")
            print(f"   Key Sections: {len(structured['key_sections'])}")
            print(f"   Compliance Areas: {len(structured['compliance_areas'])}")
            print(f"   Risk Indicators: {len(structured['risk_indicators'])}")
            print(f"   Recommendations: {len(structured['recommendations'])}")
            print(f"   Confidence Score: {structured['confidence_score']:.2f}/1.0")
            
            # Show compliance analysis
            compliance = results["compliance_analysis"]
            print(f"\n🔍 Compliance Analysis:")
            print(f"   Overall Risk Score: {compliance['overall_risk_score']:.2f}/1.0")
            print(f"   Compliance Status: {compliance['compliance_status'].replace('_', ' ').title()}")
            print(f"   Critical Issues: {len(compliance['critical_issues'])}")
            print(f"   Missing Clauses: {len(compliance['missing_clauses'])}")
            
            # Show recommendations
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(structured['recommendations'], 1):
                print(f"   {i}. {rec}")
            
        else:
            print("❌ Overall Status: FAILED")
            print(f"   Error: {results.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        print("✅ Complete PDF processing flow test completed!")
        print("\nThe step-by-step PDF processing is working correctly.")
        print("You can now use this flow in your MCP server for PDF analysis.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Complete PDF Processing Flow Test")
    print("This demonstrates the step-by-step PDF processing functionality.")
    print("\nStarting test...")
    asyncio.run(test_complete_pdf_flow())
