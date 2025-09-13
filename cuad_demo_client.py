#!/usr/bin/env python3
"""
CUAD-Enhanced Demo Client for OuiComply MCP Server.
Demonstrates the new CUAD dataset integration capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer


async def cuad_enhanced_demo():
    """Run CUAD-enhanced demo showcasing new capabilities."""
    print("🏛️  OuiComply MCP Server - CUAD Dataset Integration Demo")
    print("=" * 80)
    print("📄 Contract Understanding Atticus Dataset (CUAD) Integration")
    print("🔗 Dataset: https://huggingface.co/datasets/theatticusproject/cuad")
    print("=" * 80)
    
    # Sample legal documents for testing
    sample_contract = """
    SERVICE AGREEMENT
    
    This Service Agreement ("Agreement") is entered into on January 1, 2024, between 
    Company A and Company B. This agreement shall be governed by the laws of California.
    
    TERMINATION: Either party may terminate this agreement with 30 days written notice.
    
    LIABILITY: Company A's liability under this agreement shall not exceed the total 
    amount paid by Company B in the twelve months preceding the claim.
    
    INSURANCE: Company A shall maintain professional liability insurance of at least 
    $1,000,000 during the term of this agreement.
    
    INTELLECTUAL PROPERTY: All intellectual property developed under this agreement 
    shall be owned by Company A, with Company B receiving a non-exclusive license.
    
    AUDIT RIGHTS: Company B may audit Company A's performance under this agreement 
    with reasonable notice.
    """
    
    privacy_policy = """
    PRIVACY POLICY
    
    Effective Date: January 1, 2024
    
    We collect personal information including names, email addresses, and usage data.
    This information may be shared with third-party service providers for analytics.
    
    Users have the right to request access to their data and request deletion.
    We retain personal data for as long as necessary to provide our services.
    
    This policy is governed by the General Data Protection Regulation (GDPR).
    """
    
    print("📋 Sample Documents Loaded:")
    print("   • Service Agreement (contract analysis)")
    print("   • Privacy Policy (GDPR compliance)")
    print()
    
    try:
        # Setup server
        print("🔧 Setting up CUAD-Enhanced MCP Server...")
        server = OuiComplyMCPServer()
        
        # Initialize CUAD dataset
        print("📥 Loading CUAD dataset from Hugging Face...")
        from src.legal_datasets import initialize_cuad_dataset
        cuad_loaded = await initialize_cuad_dataset()
        
        if cuad_loaded:
            print("✅ CUAD dataset loaded successfully!")
            print(f"   • 500+ legal contracts available")
            print(f"   • 37 clause categories supported")
        else:
            print("⚠️  CUAD dataset not loaded - using basic analysis")
        
        print("\n🔍 Running CUAD-Enhanced Legal Analysis...")
        print("-" * 80)
        
        # Test 1: CUAD Contract Analysis
        print("\n1️⃣  CUAD Contract Analysis")
        print("   Document: Service Agreement")
        print("   Tool: cuad_contract_analysis")
        
        # Simulate tool call
        cuad_manager = server.cuad_manager
        analysis = cuad_manager.analyze_contract_coverage(sample_contract)
        
        print("   ✅ Analysis Complete:")
        print(f"   • Coverage Score: {analysis['coverage_score']:.1%}")
        print(f"   • Detected Clauses: {len(analysis['detected_clauses'])}")
        print(f"   • Analysis Method: {analysis['analysis_method']}")
        
        for clause in analysis['detected_clauses'][:3]:  # Show top 3
            print(f"     - {clause['clause_type']} ({clause['confidence']:.1%})")
        
        # Test 2: Enhanced Document Analysis
        print("\n2️⃣  Enhanced Document Analysis (GDPR)")
        print("   Document: Privacy Policy")
        print("   Framework: GDPR")
        print("   Tool: analyze_document")
        
        gdpr_analysis = cuad_manager.analyze_contract_coverage(privacy_policy)
        print("   ✅ Analysis Complete:")
        print(f"   • CUAD Coverage: {gdpr_analysis['coverage_score']:.1%}")
        print(f"   • Detected Clauses: {len(gdpr_analysis['detected_clauses'])}")
        print("   • GDPR Compliance: Enhanced with CUAD patterns")
        
        # Test 3: CUAD Clause Search
        print("\n3️⃣  CUAD Dataset Search")
        print("   Search: 'Limitation of Liability' clauses")
        print("   Tool: search_cuad_examples")
        
        if cuad_loaded:
            examples = cuad_manager.get_clause_examples("Limitation of Liability", limit=2)
            print("   ✅ Search Complete:")
            print(f"   • Found Examples: {len(examples)}")
            
            for i, example in enumerate(examples, 1):
                print(f"     Example {i}: {example['source_contract']}")
                print(f"     Text: \"{example['example_text'][:100]}...\"")
        else:
            print("   ⚠️  Dataset not loaded - search unavailable")
        
        # Test 4: Contract Template Generation
        print("\n4️⃣  CUAD-Based Template Generation")
        print("   Contract Type: Service Agreement")
        print("   Tool: generate_contract_template")
        
        template = cuad_manager.get_contract_template("service")
        print("   ✅ Template Generated:")
        print(f"   • Essential Clauses: {len(template.get('essential_clauses', []))}")
        print(f"   • Recommended Clauses: {len(template.get('recommended_clauses', []))}")
        print(f"   • CUAD Coverage: {template.get('cuad_coverage', 'N/A')}")
        
        print("\n   📋 Essential Clauses:")
        for clause in template.get('essential_clauses', [])[:5]:
            print(f"     • {clause}")
        
        # Test 5: Enhanced Clause Presence Check
        print("\n5️⃣  Enhanced Clause Presence Check")
        print("   Document: Service Agreement")
        print("   Required: Limitation of Liability, Governing Law, Insurance")
        print("   Tool: check_clause_presence")
        
        required_clauses = ["Limitation of Liability", "Governing Law", "Insurance"]
        detected_types = [clause['clause_type'] for clause in analysis['detected_clauses']]
        
        print("   ✅ Check Complete:")
        for clause in required_clauses:
            found = any(clause.lower() in detected.lower() for detected in detected_types)
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"     • {clause}: {status}")
        
        # Test 6: Risk Assessment with CUAD
        print("\n6️⃣  CUAD-Enhanced Risk Assessment")
        print("   Document: Service Agreement")
        print("   Tool: risk_assessment")
        
        coverage_score = analysis['coverage_score']
        risk_level = "LOW" if coverage_score > 0.7 else "MEDIUM" if coverage_score > 0.4 else "HIGH"
        
        print("   ✅ Assessment Complete:")
        print(f"   • Risk Level: {risk_level}")
        print(f"   • Clause Coverage: {coverage_score:.1%}")
        print(f"   • CUAD Categories Analyzed: {len(cuad_manager.clause_categories)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 CUAD Integration Demo Summary")
        print("=" * 80)
        
        print("📊 Enhanced Capabilities:")
        print("   ✅ CUAD dataset integration")
        print("   ✅ 37 legal clause categories")
        print("   ✅ Contract pattern analysis")
        print("   ✅ Clause example search")
        print("   ✅ Template generation")
        print("   ✅ Enhanced risk assessment")
        
        print("\n🚀 New MCP Tools Available:")
        print("   • cuad_contract_analysis - Comprehensive contract analysis")
        print("   • search_cuad_examples - Search 500+ legal contracts")
        print("   • generate_contract_template - CUAD-based templates")
        print("   • Enhanced analyze_document - CUAD pattern matching")
        print("   • Enhanced check_clause_presence - CUAD clause detection")
        print("   • Enhanced risk_assessment - CUAD coverage scoring")
        
        print("\n📚 CUAD Dataset Resources:")
        print("   • resource://cuad-dataset - Dataset information")
        print("   • resource://cuad-clause-categories - 37 clause types")
        print("   • resource://legal-templates - CUAD-enhanced templates")
        
        print("\n💡 Integration Benefits:")
        print("   • Real legal contract patterns from 500+ contracts")
        print("   • Expert-annotated clause examples")
        print("   • Standardized legal clause taxonomy")
        print("   • Enhanced accuracy in contract analysis")
        print("   • Template generation based on real contracts")
        
        print(f"\n🎉 CUAD Integration Status: {'✅ ACTIVE' if cuad_loaded else '⚠️  BASIC MODE'}")
        print("🔗 Dataset Source: https://huggingface.co/datasets/theatticusproject/cuad")
        print("🏛️  Ready for legal compliance work with CUAD enhancement!")
        
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


async def main():
    """Run the CUAD integration demo."""
    await cuad_enhanced_demo()


if __name__ == "__main__":
    asyncio.run(main())
