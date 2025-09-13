#!/usr/bin/env python3
"""
Demo script showing how to use downloaded CUAD contracts with OuiComply.

This script demonstrates how to analyze downloaded CUAD contracts using
the existing compliance analysis tools in the OuiComply system.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest
    from src.tools.compliance_engine import ComplianceEngine
except ImportError as e:
    print(f"Error importing OuiComply modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class CUADAnalysisDemo:
    """
    Demonstration class for analyzing CUAD contracts with OuiComply.
    
    This class provides methods to analyze downloaded CUAD contracts
    using the existing compliance analysis tools.
    """
    
    def __init__(self, contracts_folder: str = "docs/cuad_contracts"):
        """
        Initialize the CUAD analysis demo.
        
        Args:
            contracts_folder: Path to the downloaded CUAD contracts folder
        """
        self.contracts_folder = Path(contracts_folder)
        self.document_ai = DocumentAIService()
        self.compliance_engine = ComplianceEngine()
        
        # Contract type descriptions for better analysis context
        self.contract_descriptions = {
            "service": "General service agreements covering various business services",
            "affiliate_agreements": "Partnership and affiliate marketing contracts",
            "license_agreements": "Software and content licensing agreements",
            "intellectual_property": "IP licensing and protection agreements",
            "non_compete": "Non-compete and non-solicitation agreements",
            "privacy": "Privacy policy and data protection agreements"
        }
    
    def get_available_contracts(self) -> Dict[str, List[Path]]:
        """
        Get list of available contracts organized by type.
        
        Returns:
            Dictionary mapping contract types to lists of contract files
        """
        contracts = {}
        
        if not self.contracts_folder.exists():
            print(f"❌ Contracts folder not found: {self.contracts_folder}")
            print("Please run the download script first:")
            print("python download_cuad_contracts.py")
            return contracts
        
        for contract_type in self.contracts_folder.iterdir():
            if contract_type.is_dir():
                pdf_files = list(contract_type.glob("*.pdf"))
                if pdf_files:
                    contracts[contract_type.name] = pdf_files
        
        return contracts
    
    def print_contract_summary(self) -> None:
        """Print a summary of available contracts."""
        contracts = self.get_available_contracts()
        
        if not contracts:
            print("No contracts found. Please download them first.")
            return
        
        print("📋 Available CUAD Contracts")
        print("=" * 50)
        
        total_files = 0
        for contract_type, files in contracts.items():
            print(f"\n📁 {contract_type.replace('_', ' ').title()}")
            print(f"   Files: {len(files)}")
            total_files += len(files)
            
            # Show first few files as examples
            for i, file_path in enumerate(files[:3]):
                print(f"   - {file_path.name}")
            if len(files) > 3:
                print(f"   ... and {len(files) - 3} more")
        
        print(f"\n📊 Total: {total_files} contract files across {len(contracts)} categories")
    
    async def analyze_contract_sample(self, contract_type: str = "service", 
                                    max_files: int = 3) -> List[Dict[str, Any]]:
        """
        Analyze a sample of contracts from a specific category.
        
        Args:
            contract_type: Type of contracts to analyze
            max_files: Maximum number of files to analyze
            
        Returns:
            List of analysis results
        """
        contracts = self.get_available_contracts()
        
        if contract_type not in contracts:
            print(f"❌ Contract type '{contract_type}' not found")
            print(f"Available types: {list(contracts.keys())}")
            return []
        
        files_to_analyze = contracts[contract_type][:max_files]
        results = []
        
        print(f"\n🔍 Analyzing {len(files_to_analyze)} {contract_type} contracts...")
        print("-" * 50)
        
        for i, file_path in enumerate(files_to_analyze, 1):
            print(f"\n📄 Analyzing {i}/{len(files_to_analyze)}: {file_path.name}")
            
            try:
                # Create analysis request
                request = DocumentAnalysisRequest(
                    document_content=str(file_path),
                    compliance_frameworks=["gdpr", "sox", "ccpa"],
                    analysis_depth="comprehensive"
                )
                
                # Analyze document
                result = await self.document_ai.analyze_document(request)
                
                # Extract key information
                analysis_summary = {
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "contract_type": contract_type,
                    "compliance_score": result.get("compliance_score", 0),
                    "risk_level": result.get("risk_level", "unknown"),
                    "issues_found": len(result.get("issues", [])),
                    "key_clauses": result.get("key_clauses", [])[:5]  # Top 5 clauses
                }
                
                results.append(analysis_summary)
                
                # Print summary
                print(f"   ✅ Compliance Score: {analysis_summary['compliance_score']:.2f}")
                print(f"   ⚠️  Risk Level: {analysis_summary['risk_level'].upper()}")
                print(f"   📋 Issues Found: {analysis_summary['issues_found']}")
                
                if analysis_summary['key_clauses']:
                    print(f"   🔑 Key Clauses: {', '.join(analysis_summary['key_clauses'])}")
                
            except Exception as e:
                print(f"   ❌ Error analyzing {file_path.name}: {e}")
                results.append({
                    "file_name": file_path.name,
                    "error": str(e)
                })
        
        return results
    
    def generate_analysis_report(self, results: List[Dict[str, Any]]) -> None:
        """
        Generate a summary report of the analysis results.
        
        Args:
            results: List of analysis results
        """
        if not results:
            print("No results to report")
            return
        
        print("\n📊 Analysis Summary Report")
        print("=" * 50)
        
        # Calculate statistics
        successful_analyses = [r for r in results if "error" not in r]
        failed_analyses = [r for r in results if "error" in r]
        
        if successful_analyses:
            avg_compliance_score = sum(r.get("compliance_score", 0) for r in successful_analyses) / len(successful_analyses)
            total_issues = sum(r.get("issues_found", 0) for r in successful_analyses)
            
            print(f"📈 Successful Analyses: {len(successful_analyses)}")
            print(f"📉 Failed Analyses: {len(failed_analyses)}")
            print(f"🎯 Average Compliance Score: {avg_compliance_score:.2f}")
            print(f"⚠️  Total Issues Found: {total_issues}")
            
            # Risk level distribution
            risk_levels = {}
            for result in successful_analyses:
                risk = result.get("risk_level", "unknown")
                risk_levels[risk] = risk_levels.get(risk, 0) + 1
            
            print(f"\n🚨 Risk Level Distribution:")
            for risk, count in risk_levels.items():
                print(f"   {risk.upper()}: {count} contracts")
        
        if failed_analyses:
            print(f"\n❌ Failed Analyses:")
            for result in failed_analyses:
                print(f"   - {result['file_name']}: {result['error']}")

async def main():
    """Main function to run the CUAD analysis demo."""
    print("🚀 CUAD Contract Analysis Demo")
    print("=" * 50)
    
    # Initialize demo
    demo = CUADAnalysisDemo()
    
    # Show available contracts
    demo.print_contract_summary()
    
    # Check if contracts are available
    contracts = demo.get_available_contracts()
    if not contracts:
        print("\n💡 To download contracts, run:")
        print("python download_cuad_contracts.py")
        return
    
    # Analyze a sample of service contracts
    print(f"\n🔍 Analyzing sample contracts...")
    results = await demo.analyze_contract_sample("service", max_files=2)
    
    # Generate report
    demo.generate_analysis_report(results)
    
    print(f"\n✅ Demo completed!")
    print(f"💡 To analyze more contracts, modify the script or use the MCP server directly")

if __name__ == "__main__":
    asyncio.run(main())
