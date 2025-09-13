#!/usr/bin/env python3
"""
Debug test to identify where the hanging occurs.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_config, validate_config
from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest
from src.tools.compliance_engine import ComplianceEngine
from src.tools.memory_integration import MemoryIntegration


async def test_debug_hanging():
    """Debug test to find where the hanging occurs."""
    
    print("🔍 Debug Test - Finding Hanging Issue")
    print("=" * 50)
    
    # Step 1: Test DocumentAI directly
    print("\n1. Testing DocumentAI directly...")
    try:
        document_ai = DocumentAIService()
        
        request = DocumentAnalysisRequest(
            document_content="Test content",
            document_type="text/plain",
            compliance_frameworks=["gdpr"],
            analysis_depth="basic"
        )
        
        print("   Making DocumentAI call...")
        result = await document_ai.analyze_document(request)
        print(f"   ✅ DocumentAI completed: {len(result.compliance_issues)} issues")
        
    except Exception as e:
        print(f"   ❌ DocumentAI failed: {e}")
        return
    
    # Step 2: Test ComplianceEngine directly
    print("\n2. Testing ComplianceEngine directly...")
    try:
        compliance_engine = ComplianceEngine()
        
        print("   Making ComplianceEngine call...")
        report = await compliance_engine.analyze_document_compliance(
            document_content="Test content",
            document_type="text/plain",
            frameworks=["gdpr"]
        )
        print(f"   ✅ ComplianceEngine completed: {report.overall_status}")
        
    except Exception as e:
        print(f"   ❌ ComplianceEngine failed: {e}")
        return
    
    # Step 3: Test MemoryIntegration directly
    print("\n3. Testing MemoryIntegration directly...")
    try:
        memory_integration = MemoryIntegration()
        
        print("   Getting team memory...")
        memory = await memory_integration.get_team_memory("test_team")
        print(f"   ✅ Memory retrieved: {len(memory)} keys")
        
        print("   Learning from analysis...")
        analysis_data = {
            "document_type": "test",
            "frameworks": ["gdpr"],
            "issues_found": 1,
            "risk_score": 0.5
        }
        await memory_integration.learn_from_analysis("test_team", analysis_data)
        print("   ✅ Learning completed")
        
    except Exception as e:
        print(f"   ❌ MemoryIntegration failed: {e}")
        return
    
    # Step 4: Test the problematic combination
    print("\n4. Testing problematic combination...")
    try:
        print("   Testing analyze_with_memory logic...")
        
        # Simulate the MCP server logic
        team_context = "test_team"
        
        # Get team memory
        print("   - Getting team memory...")
        team_memory = await memory_integration.get_team_memory(team_context)
        print("   - Team memory retrieved")
        
        # Perform compliance analysis
        print("   - Starting compliance analysis...")
        report = await compliance_engine.analyze_document_compliance(
            document_content="Test content",
            frameworks=["gdpr"],
            analysis_depth="comprehensive"
        )
        print("   - Compliance analysis completed")
        
        # Learn from analysis
        print("   - Learning from analysis...")
        analysis_results = {
            "issues": [issue.model_dump() for issue in report.issues],
            "missing_clauses": report.missing_clauses,
            "risk_level": report.risk_level.value,
            "overall_status": report.overall_status.value,
            "document_name": "test_doc"
        }
        
        await memory_integration.learn_from_analysis(
            team_id=team_context,
            analysis_results=analysis_results
        )
        print("   - Learning completed")
        
        print("   ✅ Full combination test completed successfully!")
        
    except Exception as e:
        print(f"   ❌ Combination test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ All debug tests passed - no hanging detected!")


if __name__ == "__main__":
    asyncio.run(test_debug_hanging())
