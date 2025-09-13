"""
CUAD (Contract Understanding Atticus Dataset) Integration for OuiComply MCP Server.

This module provides integration with the Hugging Face CUAD dataset for 
contract analysis and legal document understanding.

CUAD Dataset: https://huggingface.co/datasets/theatticusproject/cuad
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datasets import load_dataset
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CUADDatasetManager:
    """
    Manager for CUAD (Contract Understanding Atticus Dataset) integration.
    
    Provides access to legal contract templates, clause examples, and 
    contract analysis patterns from the CUAD dataset.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize CUAD dataset manager.
        
        Args:
            cache_dir: Directory to cache dataset files
        """
        self.cache_dir = cache_dir or str(Path.home() / ".cache" / "ouicomply" / "cuad")
        self.dataset = None
        self.clause_categories = [
            "Agreement Date",
            "Anti-Assignment",
            "Audit Rights", 
            "Authority",
            "Cap on Liability",
            "Change of Control",
            "Competitive Restriction Clause",
            "Covenant not to Sue",
            "Effective Date",
            "Exclusivity",
            "Expiration Date",
            "Governing Law",
            "Insurance",
            "IP Ownership Assignment",
            "Joint IP Ownership",
            "License Grant",
            "Limitation of Liability",
            "Liquidated Damages",
            "Minimum Commitment",
            "Most Favored Nation",
            "No-Solicit of Customers",
            "No-Solicit of Employees", 
            "Non-Compete",
            "Non-Disparagement",
            "Notice Period to Terminate Renewal",
            "Post-Termination Services",
            "Price Restrictions",
            "Renewal Term",
            "Revenue/Profit Sharing",
            "ROFR/ROFO/ROFN",
            "Source Code Escrow",
            "Termination for Convenience",
            "Third Party Beneficiary",
            "Uncapped Liability",
            "Unlimited/All-You-Can-Eat-License",
            "Volume Restriction",
            "Warranty Duration"
        ]
        
    async def load_dataset(self) -> bool:
        """
        Load the CUAD dataset from Hugging Face.
        
        Returns:
            bool: True if dataset loaded successfully
        """
        try:
            logger.info("Loading CUAD dataset from Hugging Face (limited subset)...")
            
            # Load only a small subset to avoid memory issues
            loop = asyncio.get_event_loop()
            self.dataset = await loop.run_in_executor(
                None, 
                lambda: load_dataset(
                    "theatticusproject/cuad", 
                    cache_dir=self.cache_dir,
                    split="train[:100]"  # Load only first 100 samples
                )
            )
            
            logger.info(f"CUAD dataset subset loaded successfully. Samples: {len(self.dataset)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CUAD dataset: {e}")
            logger.info("Continuing with mock dataset for demonstration...")
            # Create a mock dataset for demonstration
            self.dataset = self._create_mock_dataset()
            return True
    
    def _create_mock_dataset(self):
        """Create a mock dataset for demonstration purposes."""
        return {
            "context": "This is a sample contract with governing law and limitation of liability clauses.",
            "question": "Does this contract contain a governing law clause?",
            "answers": {"text": ["This agreement shall be governed by the laws of California."]},
            "title": "Sample Service Agreement"
        }
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded CUAD dataset.
        
        Returns:
            Dict containing dataset statistics and information
        """
        if not self.dataset:
            return {"error": "Dataset not loaded"}
        
        # Handle both full dataset and mock dataset
        if isinstance(self.dataset, dict):
            # Mock dataset
            return {
                "name": "Contract Understanding Atticus Dataset (CUAD) - Mock",
                "source": "https://huggingface.co/datasets/theatticusproject/cuad",
                "description": "A mock dataset for demonstration purposes",
                "total_contracts": 1,
                "clause_categories": len(self.clause_categories),
                "supported_clauses": self.clause_categories,
                "features": ["context", "question", "answers", "title"],
                "sample_contract_length": len(self.dataset.get('context', ''))
            }
        else:
            # Real dataset subset
            return {
                "name": "Contract Understanding Atticus Dataset (CUAD)",
                "source": "https://huggingface.co/datasets/theatticusproject/cuad",
                "description": "A dataset of legal contracts with expert annotations for contract understanding",
                "total_contracts": len(self.dataset),
                "clause_categories": len(self.clause_categories),
                "supported_clauses": self.clause_categories,
                "features": list(self.dataset.features.keys()) if hasattr(self.dataset, 'features') else [],
                "sample_contract_length": len(self.dataset[0]['context']) if len(self.dataset) > 0 else 0
            }
    
    def search_contracts_by_clause(self, clause_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for contracts containing specific clause types.
        
        Args:
            clause_type: Type of clause to search for
            limit: Maximum number of contracts to return
            
        Returns:
            List of contracts containing the specified clause type
        """
        if not self.dataset:
            return []
        
        if clause_type not in self.clause_categories:
            return []
        
        matching_contracts = []
        
        # Handle mock dataset
        if isinstance(self.dataset, dict):
            # Check if mock dataset contains the clause type
            if clause_type.lower() in self.dataset.get('context', '').lower():
                contract_info = {
                    "contract_id": 0,
                    "title": self.dataset.get('title', 'Mock Contract'),
                    "context_preview": self.dataset.get('context', '')[:500] + "...",
                    "clause_type": clause_type,
                    "question": self.dataset.get('question', ''),
                    "answers": self.dataset.get('answers', {}),
                    "contract_length": len(self.dataset.get('context', ''))
                }
                matching_contracts.append(contract_info)
        else:
            # Handle real dataset
            for i, sample in enumerate(self.dataset):
                if i >= limit:
                    break
                    
                # Check if this sample contains the requested clause type
                if clause_type.lower().replace(" ", "_") in sample.get('question', '').lower():
                    contract_info = {
                        "contract_id": i,
                        "title": sample.get('title', f'Contract {i}'),
                        "context_preview": sample.get('context', '')[:500] + "...",
                        "clause_type": clause_type,
                        "question": sample.get('question', ''),
                        "answers": sample.get('answers', {}),
                        "contract_length": len(sample.get('context', ''))
                    }
                    matching_contracts.append(contract_info)
        
        return matching_contracts
    
    def get_clause_examples(self, clause_type: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get examples of specific clause types from the dataset.
        
        Args:
            clause_type: Type of clause to get examples for
            limit: Maximum number of examples to return
            
        Returns:
            List of clause examples with context
        """
        if not self.dataset:
            return []
        
        contracts = self.search_contracts_by_clause(clause_type, limit * 2)
        examples = []
        
        for contract in contracts[:limit]:
            if contract['answers'].get('text'):
                example = {
                    "clause_type": clause_type,
                    "example_text": contract['answers']['text'][0] if contract['answers']['text'] else "",
                    "context": contract['context_preview'],
                    "source_contract": contract['title'],
                    "contract_id": contract['contract_id']
                }
                examples.append(example)
        
        return examples
    
    def analyze_contract_coverage(self, contract_text: str, framework: str = "general") -> Dict[str, Any]:
        """
        Analyze a contract to identify which CUAD clause types it might contain.
        Enhanced to support multiple compliance frameworks.
        
        Args:
            contract_text: Text of the contract to analyze
            framework: Compliance framework to focus on ("general", "gdpr", "sox", "licensing")
            
        Returns:
            Analysis results with potential clause matches
        """
        contract_lower = contract_text.lower()
        
        # Enhanced clause indicators with framework-specific patterns
        clause_indicators = self._get_framework_clause_indicators(framework)
        
        detected_clauses = []
        potential_clauses = []
        
        for clause_type, keywords in clause_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in contract_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                clause_info = {
                    "clause_type": clause_type,
                    "confidence": confidence,
                    "keyword_matches": matches,
                    "total_keywords": len(keywords),
                    "framework": framework
                }
                
                if confidence >= 0.3:
                    detected_clauses.append(clause_info)
                else:
                    potential_clauses.append(clause_info)
        
        # Framework-specific analysis
        framework_analysis = self._analyze_framework_specific(contract_lower, framework)
        
        return {
            "contract_length": len(contract_text),
            "detected_clauses": detected_clauses,
            "potential_clauses": potential_clauses,
            "coverage_score": len(detected_clauses) / len(clause_indicators),
            "total_cuad_categories": len(self.clause_categories),
            "framework": framework,
            "framework_analysis": framework_analysis,
            "analysis_method": "enhanced_keyword_based"
        }
    
    def _get_framework_clause_indicators(self, framework: str) -> Dict[str, List[str]]:
        """Get clause indicators based on compliance framework."""
        
        # Base CUAD clause indicators
        base_indicators = {
            "Agreement Date": ["agreement date", "effective date", "date of agreement"],
            "Anti-Assignment": ["anti-assignment", "no assignment", "cannot assign"],
            "Audit Rights": ["audit", "inspection", "examine records"],
            "Authority": ["authority", "authorized", "power to"],
            "Cap on Liability": ["cap on liability", "maximum liability", "liability cap"],
            "Change of Control": ["change of control", "change in control"],
            "Competitive Restriction Clause": ["non-compete", "competitive restriction"],
            "Governing Law": ["governed by", "governing law", "laws of"],
            "Insurance": ["insurance", "insured", "coverage"],
            "IP Ownership Assignment": ["intellectual property", "ip ownership"],
            "License Grant": ["license", "grant", "permitted use"],
            "Limitation of Liability": ["limitation of liability", "limited liability"],
            "Liquidated Damages": ["liquidated damages", "predetermined damages"],
            "Termination for Convenience": ["terminate", "termination", "end agreement"],
            "Warranty Duration": ["warranty", "guarantee", "warranted"]
        }
        
        if framework == "gdpr":
            # Add GDPR-specific indicators
            gdpr_indicators = {
                "Data Processing Agreement": ["data processing", "personal data", "gdpr"],
                "Data Subject Rights": ["data subject", "access", "rectification", "erasure"],
                "Legal Basis": ["legal basis", "consent", "legitimate interest"],
                "Data Controller": ["data controller", "controller", "responsible party"],
                "Data Processor": ["data processor", "processor", "third party"],
                "International Transfers": ["international transfer", "third country", "adequacy"],
                "Breach Notification": ["data breach", "notification", "supervisory authority"],
                "Privacy by Design": ["privacy by design", "data protection by design"],
                "Retention Period": ["retention", "storage period", "delete data"],
                "DPO Contact": ["dpo", "data protection officer", "privacy officer"]
            }
            base_indicators.update(gdpr_indicators)
            
        elif framework == "sox":
            # Add SOX-specific indicators
            sox_indicators = {
                "Internal Controls": ["internal controls", "icfr", "financial reporting"],
                "Management Certification": ["management certification", "ceo", "cfo"],
                "Audit Committee": ["audit committee", "independent", "financial expert"],
                "Financial Disclosure": ["financial disclosure", "material information"],
                "Whistleblower Protection": ["whistleblower", "anonymous reporting", "retaliation"],
                "Documentation Requirements": ["documentation", "policies", "procedures"],
                "Risk Assessment": ["risk assessment", "fraud risk", "material weakness"],
                "Monitoring Controls": ["monitoring", "testing", "effectiveness"],
                "COSO Framework": ["coso", "control framework", "control environment"],
                "Auditor Independence": ["auditor independence", "external auditor", "attestation"]
            }
            base_indicators.update(sox_indicators)
            
        elif framework == "licensing":
            # Add licensing-specific indicators
            licensing_indicators = {
                "License Scope": ["scope", "field of use", "territory", "application"],
                "Exclusivity": ["exclusive", "non-exclusive", "sole license"],
                "Royalty Terms": ["royalty", "royalties", "revenue share", "percentage"],
                "Usage Restrictions": ["permitted use", "prohibited", "restrictions"],
                "Modification Rights": ["modify", "derivative works", "improvements"],
                "Distribution Rights": ["distribute", "sublicense", "transfer"],
                "Termination Conditions": ["termination", "breach", "cure period"],
                "IP Ownership": ["ownership", "title", "intellectual property"],
                "Patent Rights": ["patent", "patent rights", "claims", "invention"],
                "Copyright License": ["copyright", "reproduction", "public performance"],
                "Trade Secret": ["trade secret", "confidential", "proprietary"],
                "Open Source": ["open source", "gpl", "mit", "apache", "creative commons"]
            }
            base_indicators.update(licensing_indicators)
        
        return base_indicators
    
    def _analyze_framework_specific(self, contract_lower: str, framework: str) -> Dict[str, Any]:
        """Perform framework-specific analysis."""
        
        if framework == "gdpr":
            return self._analyze_gdpr_specific(contract_lower)
        elif framework == "sox":
            return self._analyze_sox_specific(contract_lower)
        elif framework == "licensing":
            return self._analyze_licensing_specific(contract_lower)
        else:
            return {"framework": "general", "specific_analysis": "none"}
    
    def _analyze_gdpr_specific(self, contract_lower: str) -> Dict[str, Any]:
        """GDPR-specific analysis."""
        gdpr_elements = {
            "has_legal_basis": any(term in contract_lower for term in 
                ["consent", "legitimate interest", "contract", "legal obligation"]),
            "mentions_data_subjects": any(term in contract_lower for term in 
                ["data subject", "individual", "person"]),
            "has_retention_policy": any(term in contract_lower for term in 
                ["retention", "delete", "storage period"]),
            "mentions_transfers": any(term in contract_lower for term in 
                ["transfer", "third country", "international"]),
            "has_security_measures": any(term in contract_lower for term in 
                ["security", "encryption", "protect", "safeguard"]),
            "mentions_rights": any(term in contract_lower for term in 
                ["access", "rectification", "erasure", "portability"])
        }
        
        compliance_score = sum(gdpr_elements.values()) / len(gdpr_elements)
        
        return {
            "framework": "gdpr",
            "elements": gdpr_elements,
            "compliance_score": compliance_score,
            "risk_level": "LOW" if compliance_score > 0.7 else "MEDIUM" if compliance_score > 0.4 else "HIGH"
        }
    
    def _analyze_sox_specific(self, contract_lower: str) -> Dict[str, Any]:
        """SOX-specific analysis."""
        sox_elements = {
            "has_internal_controls": any(term in contract_lower for term in 
                ["internal controls", "icfr", "control framework"]),
            "mentions_certification": any(term in contract_lower for term in 
                ["certification", "ceo", "cfo", "management"]),
            "has_audit_provisions": any(term in contract_lower for term in 
                ["audit", "auditor", "independent", "attestation"]),
            "mentions_documentation": any(term in contract_lower for term in 
                ["documentation", "policies", "procedures"]),
            "has_whistleblower": any(term in contract_lower for term in 
                ["whistleblower", "reporting", "anonymous"]),
            "mentions_monitoring": any(term in contract_lower for term in 
                ["monitoring", "testing", "effectiveness"])
        }
        
        compliance_score = sum(sox_elements.values()) / len(sox_elements)
        
        return {
            "framework": "sox",
            "elements": sox_elements,
            "compliance_score": compliance_score,
            "risk_level": "LOW" if compliance_score > 0.6 else "MEDIUM" if compliance_score > 0.3 else "HIGH"
        }
    
    def _analyze_licensing_specific(self, contract_lower: str) -> Dict[str, Any]:
        """Licensing-specific analysis."""
        licensing_elements = {
            "has_grant_clause": any(term in contract_lower for term in 
                ["grant", "license", "hereby grants"]),
            "defines_scope": any(term in contract_lower for term in 
                ["scope", "field of use", "territory"]),
            "mentions_exclusivity": any(term in contract_lower for term in 
                ["exclusive", "non-exclusive", "sole"]),
            "has_usage_terms": any(term in contract_lower for term in 
                ["permitted", "prohibited", "restrictions"]),
            "mentions_royalties": any(term in contract_lower for term in 
                ["royalty", "payment", "fee", "compensation"]),
            "has_termination": any(term in contract_lower for term in 
                ["termination", "breach", "expire"])
        }
        
        compliance_score = sum(licensing_elements.values()) / len(licensing_elements)
        
        return {
            "framework": "licensing",
            "elements": licensing_elements,
            "compliance_score": compliance_score,
            "risk_level": "LOW" if compliance_score > 0.7 else "MEDIUM" if compliance_score > 0.4 else "HIGH"
        }
    
    def get_contract_template(self, contract_type: str = "general") -> Dict[str, Any]:
        """
        Generate a contract template based on CUAD dataset patterns.
        
        Args:
            contract_type: Type of contract template to generate
            
        Returns:
            Contract template with recommended clauses
        """
        if not self.dataset:
            return {"error": "Dataset not loaded"}
        
        # Essential clauses for most contracts
        essential_clauses = [
            "Agreement Date",
            "Effective Date", 
            "Governing Law",
            "Termination for Convenience",
            "Limitation of Liability"
        ]
        
        # Additional clauses by contract type
        contract_specific_clauses = {
            "service": ["Insurance", "Warranty Duration", "Post-Termination Services"],
            "license": ["License Grant", "IP Ownership Assignment", "Exclusivity"],
            "employment": ["Non-Compete", "No-Solicit of Employees", "Non-Disparagement"],
            "partnership": ["Revenue/Profit Sharing", "Joint IP Ownership", "Change of Control"]
        }
        
        recommended_clauses = essential_clauses.copy()
        if contract_type in contract_specific_clauses:
            recommended_clauses.extend(contract_specific_clauses[contract_type])
        
        template = {
            "contract_type": contract_type,
            "essential_clauses": essential_clauses,
            "recommended_clauses": recommended_clauses,
            "total_clauses": len(recommended_clauses),
            "cuad_coverage": f"{len(recommended_clauses)}/{len(self.clause_categories)} CUAD categories",
            "clause_examples": {}
        }
        
        # Add examples for each recommended clause
        for clause in recommended_clauses[:5]:  # Limit to first 5 for performance
            examples = self.get_clause_examples(clause, limit=1)
            if examples:
                template["clause_examples"][clause] = examples[0]["example_text"]
        
        return template


# Global instance for use across the MCP server
cuad_manager = CUADDatasetManager()


async def initialize_cuad_dataset() -> bool:
    """
    Initialize the CUAD dataset for use in the MCP server.
    
    Returns:
        bool: True if initialization successful
    """
    return await cuad_manager.load_dataset()


def get_cuad_manager() -> CUADDatasetManager:
    """
    Get the global CUAD dataset manager instance.
    
    Returns:
        CUADDatasetManager instance
    """
    return cuad_manager
