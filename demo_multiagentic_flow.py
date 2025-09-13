#!/usr/bin/env python3
"""
OuiComply Multiagentic Flow Demo Script

This script demonstrates the complete user journey for the OuiComply MCP Server
as outlined in the Mistral AI MCP Hackathon submission. It showcases:

1. Le Chat query parsing and document fetching
2. Document decomposition with structured JSON output
3. Memory-integrated compliance analysis
4. Structured reporting with learning prompts
5. Memory updates and adaptive learning
6. Workflow automation with Linear, Slack, and GitHub

Usage:
    python demo_multiagentic_flow.py
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OuiComplyDemo:
    """
    Demo class for showcasing the OuiComply multiagentic flow.
    """
    
    def __init__(self):
        """Initialize the demo with mock MCP server."""
        self.demo_data = self._load_demo_data()
        self.step_counter = 0
    
    def _load_demo_data(self) -> Dict[str, Any]:
        """Load demo data for the demonstration."""
        return {
            "queries": [
                "check Vendor_Q4.docx for compliance",
                "analyze Sales_Agreement_2024.pdf for GDPR issues",
                "review HR_Policy_Document.docx for SOX compliance"
            ],
            "teams": [
                "Procurement Team",
                "Sales Team", 
                "HR Team"
            ],
            "documents": {
                "Vendor_Q4.docx": {
                    "content": """
                    VENDOR AGREEMENT - Q4 2024
                    
                    This Vendor Agreement ("Agreement") is entered into between Company and Vendor.
                    
                    DATA PROCESSING:
                    Vendor may process personal data in accordance with applicable data protection laws.
                    Data retention period: 7 years from contract termination.
                    
                    PAYMENT TERMS:
                    Net 60 payment terms apply to all invoices.
                    
                    CONFIDENTIALITY:
                    Both parties agree to maintain confidentiality of proprietary information.
                    
                    TERMINATION:
                    Either party may terminate with 30 days written notice.
                    """,
                    "expected_issues": ["Missing sub-processors", "Insufficient data breach notification"]
                },
                "Sales_Agreement_2024.pdf": {
                    "content": """
                    SALES AGREEMENT 2024
                    
                    This Sales Agreement governs the sale of products/services.
                    
                    DATA COLLECTION:
                    We collect customer information for order processing and marketing.
                    Customers may opt-out of marketing communications.
                    
                    PAYMENT TERMS:
                    Payment due within 30 days of invoice date.
                    
                    LIABILITY:
                    Our liability is limited to the purchase price of the product.
                    """,
                    "expected_issues": ["Missing consumer rights disclosure", "Insufficient opt-out mechanisms"]
                }
            }
        }
    
    async def run_demo(self) -> None:
        """Run the complete multiagentic flow demo."""
        print("🚀 OuiComply Multiagentic Flow Demo")
        print("=" * 50)
        print()
        
        # Step 1: Query Parsing and Document Fetching
        await self._demo_step_1_query_parsing()
        
        # Step 2: Document Decomposition
        await self._demo_step_2_document_decomposition()
        
        # Step 3: Memory-Integrated Analysis
        await self._demo_step_3_memory_analysis()
        
        # Step 4: Structured Reporting
        await self._demo_step_4_structured_reporting()
        
        # Step 5: Learning and Memory Update
        await self._demo_step_5_learning_update()
        
        # Step 6: Automation Prompt Generation
        await self._demo_step_6_automation_prompts()
        
        # Step 7: Adaptive Re-analysis
        await self._demo_step_7_adaptive_reanalysis()
        
        print("\n✅ Demo completed successfully!")
        print("🎉 OuiComply MCP Server delivers adaptive compliance analysis!")
    
    async def _demo_step_1_query_parsing(self) -> None:
        """Demo Step 1: Query Parsing and Document Fetching."""
        self._print_step_header("Step 1: Query Parsing and Document Fetching")
        
        query = self.demo_data["queries"][0]
        team = self.demo_data["teams"][0]
        
        print(f"👤 User Query: '{query}'")
        print(f"🏢 Team Context: {team}")
        print()
        
        # Simulate Le Chat interface parsing
        parsed_query = {
            "document_name": "Vendor_Q4.docx",
            "team": "Procurement Team",
            "query_type": "compliance_check",
            "urgency": "medium",
            "additional_context": {"frameworks": ["GDPR", "SOX"]}
        }
        
        print("🔍 Query Agent Analysis:")
        print(f"   📄 Document: {parsed_query['document_name']}")
        print(f"   🏢 Team: {parsed_query['team']}")
        print(f"   📋 Type: {parsed_query['query_type']}")
        print(f"   ⚡ Urgency: {parsed_query['urgency']}")
        print()
        
        # Simulate Google Drive fetch
        print("📁 Google Drive Fetch:")
        print("   ✅ Document found and retrieved")
        print("   📊 Size: 2.3 MB")
        print("   📄 Type: Microsoft Word Document")
        print()
        
        # Simulate memory retrieval
        print("🧠 Memory Integration:")
        print("   📋 Compliance Rules: ['Check for Net 60 terms', 'Verify data retention clauses']")
        print("   ⚠️  Pitfall Patterns: ['Missing sub-processors', 'Insufficient breach notification']")
        print("   👤 Default Assignee: David_P")
        print("   📢 Notification: Slack")
        print()
    
    async def _demo_step_2_document_decomposition(self) -> None:
        """Demo Step 2: Document Decomposition."""
        self._print_step_header("Step 2: Document Decomposition")
        
        document_content = self.demo_data["documents"]["Vendor_Q4.docx"]["content"]
        
        print("🔧 Decomposition Agent Processing:")
        print("   📄 Using Mistral DocumentAI for parsing...")
        print("   🏗️  Extracting structured sections...")
        print()
        
        # Simulate document decomposition
        sections = [
            {
                "id": 1,
                "text": "DATA PROCESSING: Vendor may process personal data...",
                "type": "clause",
                "title": "Data Processing",
                "page": 1,
                "compliance_relevant": True
            },
            {
                "id": 2,
                "text": "PAYMENT TERMS: Net 60 payment terms apply...",
                "type": "clause", 
                "title": "Payment Terms",
                "page": 2,
                "compliance_relevant": False
            },
            {
                "id": 3,
                "text": "CONFIDENTIALITY: Both parties agree to maintain...",
                "type": "clause",
                "title": "Confidentiality",
                "page": 3,
                "compliance_relevant": True
            }
        ]
        
        print("📋 Structured Output:")
        for section in sections:
            relevance = "🔍 Compliance Relevant" if section["compliance_relevant"] else "📄 General"
            print(f"   {section['id']}. {section['title']} - {relevance}")
        
        print(f"\n   📊 Total Sections: {len(sections)}")
        print(f"   🔍 Compliance Relevant: {len([s for s in sections if s['compliance_relevant']])}")
        print("   ✅ Ready for parallel analysis")
        print()
    
    async def _demo_step_3_memory_analysis(self) -> None:
        """Demo Step 3: Memory-Integrated Analysis."""
        self._print_step_header("Step 3: Memory-Integrated Compliance Analysis")
        
        print("🤖 Analysis Agents (Parallel Processing):")
        print("   🔄 GDPR Agent: Analyzing data protection clauses...")
        print("   🔄 SOX Agent: Checking financial controls...")
        print("   🔄 CCPA Agent: Reviewing consumer rights...")
        print()
        
        # Simulate parallel analysis
        analysis_results = {
            "overall_status": "partially_compliant",
            "risk_level": "high",
            "risk_score": 0.75,
            "issues": [
                {
                    "issue_id": "gdpr_001",
                    "severity": "high",
                    "category": "data_processing",
                    "description": "Missing sub-processors disclosure",
                    "location": "Data Processing Section",
                    "recommendation": "Add explicit sub-processor list and consent mechanism",
                    "framework": "GDPR",
                    "confidence": 0.90
                },
                {
                    "issue_id": "gdpr_002",
                    "severity": "medium",
                    "category": "data_retention",
                    "description": "Data retention period not clearly specified",
                    "location": "Data Processing Section",
                    "recommendation": "Specify exact retention periods for different data types",
                    "framework": "GDPR",
                    "confidence": 0.75
                }
            ],
            "missing_clauses": [
                "Data Protection Officer contact information",
                "Cross-border transfer safeguards",
                "Data breach notification procedures"
            ],
            "team_memory_applied": True,
            "processing_time": "2.3 seconds"
        }
        
        print("📊 Analysis Results:")
        print(f"   📈 Status: {analysis_results['overall_status'].upper()}")
        print(f"   ⚠️  Risk Level: {analysis_results['risk_level'].upper()}")
        print(f"   📊 Risk Score: {analysis_results['risk_score']}/1.0")
        print(f"   🐛 Issues Found: {len(analysis_results['issues'])}")
        print(f"   📋 Missing Clauses: {len(analysis_results['missing_clauses'])}")
        print(f"   🧠 Memory Applied: {analysis_results['team_memory_applied']}")
        print(f"   ⏱️  Processing Time: {analysis_results['processing_time']}")
        print()
    
    async def _demo_step_4_structured_reporting(self) -> None:
        """Demo Step 4: Structured Reporting."""
        self._print_step_header("Step 4: Structured Report Generation")
        
        print("📝 Reporting Agent:")
        print("   🔄 Generating Le Chat formatted response...")
        print("   🔄 Creating learning prompt...")
        print("   🔄 Preparing JSON/Markdown outputs...")
        print()
        
        # Simulate structured report generation
        lechat_response = """
🔍 **Compliance Analysis Complete**

**Team:** Procurement Team
**Status:** PARTIALLY_COMPLIANT
**Risk Level:** HIGH
**Risk Score:** 0.75/1.0

**Issues Found:** 2
1. **HIGH:** Missing sub-processors disclosure
2. **MEDIUM:** Data retention period not clearly specified

**Missing Clauses:** 3
• Data Protection Officer contact information
• Cross-border transfer safeguards
• Data breach notification procedures

**Procurement Team Recommendations:**
• Review payment terms for compliance
• Check vendor data processing agreements
        """
        
        learning_prompt = """
🤖 **Learning Opportunity**

Based on this analysis for Procurement Team, I can help you learn from this experience:

**Issues Found:**
• Missing sub-processors disclosure
• Data retention period not clearly specified

**Missing Clauses:**
• Data Protection Officer contact information
• Cross-border transfer safeguards

**Would you like to:**
1. Add a new pitfall pattern to watch for?
2. Add a new compliance rule for your team?
3. Update your team's risk tolerance?
4. Just continue with the analysis

Please respond with your choice (1-4) or describe what you'd like to add.
        """
        
        print("📋 Le Chat Response:")
        print(lechat_response)
        print()
        
        print("🎓 Learning Prompt:")
        print(learning_prompt)
        print()
    
    async def _demo_step_5_learning_update(self) -> None:
        """Demo Step 5: Learning and Memory Update."""
        self._print_step_header("Step 5: Learning and Memory Update")
        
        print("🧠 Learning Agent:")
        print("   📥 Processing user feedback...")
        print("   🔄 Updating team memory...")
        print("   📊 Generating improvement suggestions...")
        print()
        
        # Simulate user feedback
        user_feedback = "Add pitfall: Check for Indemnification clauses in vendor agreements"
        
        print(f"👤 User Feedback: '{user_feedback}'")
        print()
        
        # Simulate memory update
        updated_memory = {
            "compliance_memory": {
                "rules": [
                    "Check for Net 60 terms",
                    "Verify data retention clauses",
                    "User specified: Check for Indemnification clauses in vendor agreements"
                ],
                "pitfall_patterns": [
                    "Missing sub-processors",
                    "Insufficient breach notification",
                    "User identified: Check for Indemnification clauses in vendor agreements"
                ],
                "preferred_frameworks": ["GDPR", "SOX"],
                "risk_tolerance": "medium"
            },
            "behavioral_memory": {
                "default_assignee": "David_P",
                "notification_channel": "slack",
                "escalation_rules": {"critical": "immediate", "high": "24h"},
                "workflow_preferences": {"auto_assign": True, "notify_slack": True}
            }
        }
        
        print("✅ Memory Updated Successfully:")
        print(f"   📋 Rules: {len(updated_memory['compliance_memory']['rules'])}")
        print(f"   ⚠️  Pitfalls: {len(updated_memory['compliance_memory']['pitfall_patterns'])}")
        print(f"   🎯 New Rule Added: Indemnification check")
        print(f"   🎯 New Pitfall Added: Indemnification clauses")
        print()
        
        print("💡 Improvement Suggestions:")
        print("   • Consider creating a checklist based on your frequent pitfall patterns")
        print("   • Set a default assignee to streamline task assignment")
        print("   • Consider using Slack for faster team communication")
        print()
    
    async def _demo_step_6_automation_prompts(self) -> None:
        """Demo Step 6: Automation Prompt Generation."""
        self._print_step_header("Step 6: Automation Prompt Generation")
        
        print("🤖 Automation Agent:")
        print("   🔄 Generating Linear task creation prompt...")
        print("   📢 Generating Slack notification prompt...")
        print("   📝 Generating GitHub issue creation prompt...")
        print()
        
        # Simulate prompt generation
        automation_prompts = {
            "success": True,
            "actions_taken": [
                "Generated Linear task creation prompt",
                "Generated Slack notification prompt", 
                "Generated GitHub issue creation prompt"
            ],
            "prompts": [
                {
                    "action_type": "linear_task_creation",
                    "prompt": "Please use your Linear MCP server to create a new task with the following details:\n\n**Task Title:** URGENT: Address 2 critical compliance issues in Vendor_Q4.docx\n**Description:** [Detailed task description]\n**Priority:** 1 (urgent)\n**Team:** Procurement Team\n**Assignee:** David_P\n**Labels:** compliance, urgent, legal\n\nPlease create this task and return the task ID and URL.",
                    "details": {
                        "title": "URGENT: Address 2 critical compliance issues in Vendor_Q4.docx",
                        "priority": 1,
                        "team": "Procurement Team",
                        "assignee": "David_P"
                    }
                },
                {
                    "action_type": "slack_message",
                    "prompt": "Please use your Slack MCP server to send a message with the following details:\n\n**Channel:** #procurement-compliance\n**Message Text:** 🔍 Compliance Analysis Complete - 2 issues found in Vendor_Q4.docx\n\nPlease send this message and confirm delivery.",
                    "details": {
                        "channel": "#procurement-compliance",
                        "text": "🔍 Compliance Analysis Complete - 2 issues found in Vendor_Q4.docx"
                    }
                },
                {
                    "action_type": "github_issue_creation",
                    "prompt": "Please use your GitHub MCP server to create a new issue with the following details:\n\n**Title:** Compliance Analysis: Vendor_Q4.docx - PARTIALLY_COMPLIANT\n**Body:** [Detailed compliance report]\n**Labels:** compliance, legal, issues-found\n**State:** open\n\nPlease create this issue and return the issue number and URL.",
                    "details": {
                        "title": "Compliance Analysis: Vendor_Q4.docx - PARTIALLY_COMPLIANT",
                        "labels": ["compliance", "legal", "issues-found"],
                        "state": "open"
                    }
                }
            ],
            "instructions": "Please execute these prompts using your respective MCP servers (Linear, Slack, GitHub)",
            "errors": []
        }
        
        print("✅ Prompt Generation Results:")
        for action in automation_prompts["actions_taken"]:
            print(f"   ✅ {action}")
        
        print(f"\n📋 Generated Prompts:")
        for i, prompt in enumerate(automation_prompts["prompts"], 1):
            print(f"   {i}. {prompt['action_type'].replace('_', ' ').title()}")
            print(f"      Channel/Service: {prompt['details'].get('channel', prompt['details'].get('team', 'N/A'))}")
            print(f"      Action: {prompt['details'].get('title', prompt['details'].get('text', 'N/A'))[:50]}...")
        
        print(f"\n💡 Instructions for Le Chat:")
        print(f"   {automation_prompts['instructions']}")
        print()
    
    async def _demo_step_7_adaptive_reanalysis(self) -> None:
        """Demo Step 7: Adaptive Re-analysis."""
        self._print_step_header("Step 7: Adaptive Re-analysis")
        
        print("🔄 Adaptive Re-analysis:")
        print("   🧠 Applying updated memory patterns...")
        print("   🔍 Checking for new pitfall: Indemnification clauses...")
        print("   📊 Re-calculating risk score...")
        print()
        
        # Simulate adaptive re-analysis
        reanalysis_results = {
            "original_issues": 2,
            "new_issues_found": 1,
            "additional_issue": {
                "issue_id": "indemnification_001",
                "severity": "medium",
                "category": "liability",
                "description": "Missing indemnification clause for data breaches",
                "location": "Liability Section",
                "recommendation": "Add comprehensive indemnification clause",
                "framework": "General",
                "confidence": 0.80
            },
            "updated_risk_score": 0.85,
            "memory_learning_applied": True,
            "total_issues": 3
        }
        
        print("📊 Re-analysis Results:")
        print(f"   📈 Original Issues: {reanalysis_results['original_issues']}")
        print(f"   🆕 New Issues Found: {reanalysis_results['new_issues_found']}")
        print(f"   📊 Updated Risk Score: {reanalysis_results['updated_risk_score']}/1.0")
        print(f"   🧠 Memory Learning Applied: {reanalysis_results['memory_learning_applied']}")
        print()
        
        print("🆕 New Issue Detected:")
        issue = reanalysis_results['additional_issue']
        print(f"   🐛 {issue['severity'].upper()}: {issue['description']}")
        print(f"   📍 Location: {issue['location']}")
        print(f"   💡 Recommendation: {issue['recommendation']}")
        print()
        
        print("🎉 **Adaptive Learning Success!**")
        print("   The system learned from user feedback and caught a new issue")
        print("   that wasn't identified in the original analysis!")
        print()
    
    def _print_step_header(self, title: str) -> None:
        """Print a formatted step header."""
        self.step_counter += 1
        print(f"\n{'='*60}")
        print(f"STEP {self.step_counter}: {title}")
        print(f"{'='*60}")
        print()


async def main():
    """Main demo function."""
    demo = OuiComplyDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
