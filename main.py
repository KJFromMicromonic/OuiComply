"""
Main entry point for the OuiComply Legal Compliance Checker.

This file provides the main entry point for running legal compliance analysis on PDF files.

Usage:
    python main.py -file:path/to/document.pdf
    python main.py --file path/to/document.pdf
    
Examples:
    python main.py -file:test_files/new.pdf
    python main.py --file test_files/contract.pdf
"""

import asyncio
import sys
import logging
import argparse
from pathlib import Path
import PyPDF2
import io

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config import validate_config, print_config_summary
from src.legal_datasets.cuad_integration import CUADDatasetManager


def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return ""


def analyze_gdpr_compliance(text: str) -> dict:
    """
    Analyze document for GDPR compliance.
    
    Args:
        text: Document text to analyze
        
    Returns:
        GDPR compliance analysis results
    """
    text_lower = text.lower()
    
    # GDPR compliance indicators
    gdpr_elements = {
        "legal_basis": ["legal basis", "article 6", "lawful basis", "legitimate interest"],
        "data_subject_rights": ["right to access", "right to rectification", "right to erasure", "data subject rights"],
        "data_protection_officer": ["data protection officer", "dpo", "dpo@", "privacy officer"],
        "data_retention": ["retention period", "data retention", "retain data", "delete data"],
        "consent": ["consent", "agree to", "opt-in", "permission"],
        "data_processing": ["process data", "processing", "collect data", "use data"],
        "third_party_sharing": ["third party", "share data", "partners", "vendors"],
        "international_transfers": ["international transfer", "third country", "adequacy decision"]
    }
    
    found_elements = []
    missing_elements = []
    
    for element, keywords in gdpr_elements.items():
        found = any(keyword in text_lower for keyword in keywords)
        if found:
            found_elements.append(element)
        else:
            missing_elements.append(element)
    
    compliance_score = len(found_elements) / len(gdpr_elements) * 100
    
    # Risk assessment
    if compliance_score >= 80:
        risk_level = "LOW"
    elif compliance_score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return {
        "framework": "GDPR",
        "compliance_score": compliance_score,
        "found_elements": found_elements,
        "missing_elements": missing_elements,
        "risk_level": risk_level,
        "total_elements": len(gdpr_elements),
        "document_length": len(text)
    }


def analyze_contract_clauses(text: str) -> dict:
    """
    Analyze document for common contract clauses.
    
    Args:
        text: Document text to analyze
        
    Returns:
        Contract clause analysis results
    """
    text_lower = text.lower()
    
    # Common contract clauses
    clauses = {
        "governing_law": ["governed by", "governing law", "laws of"],
        "limitation_of_liability": ["limitation of liability", "limited liability", "liability cap"],
        "termination": ["terminate", "termination", "end agreement"],
        "confidentiality": ["confidential", "non-disclosure", "proprietary"],
        "intellectual_property": ["intellectual property", "copyright", "trademark"],
        "indemnification": ["indemnify", "indemnification", "hold harmless"],
        "force_majeure": ["force majeure", "act of god", "unforeseeable"],
        "dispute_resolution": ["dispute resolution", "arbitration", "mediation"]
    }
    
    detected_clauses = []
    missing_clauses = []
    
    for clause, keywords in clauses.items():
        found = any(keyword in text_lower for keyword in keywords)
        if found:
            detected_clauses.append(clause)
        else:
            missing_clauses.append(clause)
    
    coverage_score = len(detected_clauses) / len(clauses) * 100
    
    return {
        "analysis_type": "Contract Clauses",
        "detected_clauses": detected_clauses,
        "missing_clauses": missing_clauses,
        "coverage_score": coverage_score,
        "total_clauses": len(clauses),
        "document_length": len(text)
    }


async def process_document(file_path: str):
    """
    Process a PDF document for legal compliance analysis.
    
    Args:
        file_path: Path to the PDF file to analyze
    """
    print("🏛️  OuiComply Legal Compliance Checker")
    print("=" * 60)
    print("AI-Assisted Legal Document Analysis")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Validate file path
    if not Path(file_path).exists():
        print(f"❌ Error: File '{file_path}' not found!")
        return
    
    if not file_path.lower().endswith('.pdf'):
        print(f"❌ Error: File '{file_path}' is not a PDF file!")
        return
    
    print(f"📄 Analyzing document: {file_path}")
    print("-" * 60)
    
    # Extract text from PDF
    print("📖 Extracting text from PDF...")
    text = extract_text_from_pdf(file_path)
    
    if not text:
        print("❌ No text could be extracted from the PDF!")
        return
    
    print(f"✅ Text extracted successfully ({len(text)} characters)")
    print("-" * 60)
    
    # Perform GDPR compliance analysis
    print("🔍 Performing GDPR Compliance Analysis...")
    gdpr_results = analyze_gdpr_compliance(text)
    
    print(f"\n📊 GDPR Compliance Results:")
    print(f"   • Compliance Score: {gdpr_results['compliance_score']:.1f}%")
    print(f"   • Risk Level: {gdpr_results['risk_level']}")
    print(f"   • Elements Found: {len(gdpr_results['found_elements'])}/{gdpr_results['total_elements']}")
    
    if gdpr_results['found_elements']:
        print(f"   ✅ Found Elements:")
        for element in gdpr_results['found_elements']:
            print(f"      - {element.replace('_', ' ').title()}")
    
    if gdpr_results['missing_elements']:
        print(f"   ❌ Missing Elements:")
        for element in gdpr_results['missing_elements'][:5]:  # Show first 5
            print(f"      - {element.replace('_', ' ').title()}")
    
    print("-" * 60)
    
    # Perform contract clause analysis
    print("🔍 Performing Contract Clause Analysis...")
    clause_results = analyze_contract_clauses(text)
    
    print(f"\n📋 Contract Clause Results:")
    print(f"   • Coverage Score: {clause_results['coverage_score']:.1f}%")
    print(f"   • Clauses Found: {len(clause_results['detected_clauses'])}/{clause_results['total_clauses']}")
    
    if clause_results['detected_clauses']:
        print(f"   ✅ Detected Clauses:")
        for clause in clause_results['detected_clauses']:
            print(f"      - {clause.replace('_', ' ').title()}")
    
    if clause_results['missing_clauses']:
        print(f"   ❌ Missing Clauses:")
        for clause in clause_results['missing_clauses'][:5]:  # Show first 5
            print(f"      - {clause.replace('_', ' ').title()}")
    
    print("-" * 60)
    
    # Initialize CUAD manager for enhanced analysis
    print("🔍 Performing Enhanced CUAD Analysis...")
    try:
        cuad_manager = CUADDatasetManager()
        await cuad_manager.load_dataset()
        
        cuad_results = cuad_manager.analyze_contract_coverage(text)
        
        print(f"\n🏛️  CUAD Enhanced Analysis:")
        print(f"   • Coverage Score: {cuad_results['coverage_score']*100:.1f}%")
        print(f"   • Analysis Method: {cuad_results['analysis_method']}")
        print(f"   • CUAD Categories: {cuad_results['total_cuad_categories']}")
        
        if cuad_results['detected_clauses']:
            print(f"   ✅ CUAD Detected Clauses:")
            for clause in cuad_results['detected_clauses'][:5]:  # Show first 5
                print(f"      - {clause['clause_type']} ({clause['confidence']*100:.1f}% confidence)")
        
    except Exception as e:
        print(f"   ⚠️  CUAD analysis unavailable: {e}")
    
    print("=" * 60)
    
    # Summary and recommendations
    overall_score = (gdpr_results['compliance_score'] + clause_results['coverage_score']) / 2
    
    print(f"🎯 Overall Analysis Summary:")
    print(f"   • Document Length: {len(text)} characters")
    print(f"   • Overall Compliance Score: {overall_score:.1f}%")
    print(f"   • GDPR Risk Level: {gdpr_results['risk_level']}")
    
    print(f"\n💡 Recommendations:")
    if overall_score < 50:
        print("   • Document needs significant compliance improvements")
        print("   • Consider legal review before use")
        print("   • Add missing GDPR elements and contract clauses")
    elif overall_score < 80:
        print("   • Document has moderate compliance coverage")
        print("   • Review and add missing elements")
        print("   • Consider legal consultation")
    else:
        print("   • Document shows good compliance coverage")
        print("   • Minor improvements may be beneficial")
        print("   • Regular compliance reviews recommended")
    
    print("\n🚀 Analysis Complete!")


def parse_arguments():
    """Parse command line arguments."""
    # Handle both -file:path and --file path formats
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith('-file:'):
            return arg[6:]  # Remove '-file:' prefix
        elif arg == '--file' and len(sys.argv) > 2:
            return sys.argv[2]
        elif arg.startswith('--file='):
            return arg[7:]  # Remove '--file=' prefix
    
    return None


def main():
    """Main entry point."""
    file_path = parse_arguments()
    
    if not file_path:
        print("🏛️  OuiComply Legal Compliance Checker")
        print("=" * 50)
        print("Usage:")
        print("  python main.py -file:path/to/document.pdf")
        print("  python main.py --file path/to/document.pdf")
        print("\nExamples:")
        print("  python main.py -file:test_files/new.pdf")
        print("  python main.py --file test_files/contract.pdf")
        print("=" * 50)
        sys.exit(1)
    
    try:
        # Validate configuration
        if not validate_config():
            print("❌ Configuration validation failed!")
            print("Please check your .env file and ensure MISTRAL_KEY is set.")
            sys.exit(1)
        
        # Process the document
        asyncio.run(process_document(file_path))
        
    except KeyboardInterrupt:
        print("\n👋 Analysis stopped by user")
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
