"""
Base resource class for OuiComply MCP Server resources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from mcp.types import Resource


class BaseResource(ABC):
    """
    Base class for all MCP resources in the OuiComply server.
    
    All resources should inherit from this class and implement the required methods.
    """
    
    def __init__(self, uri: str, name: str, description: str, mime_type: str = "application/json"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
    
    def to_resource(self) -> Resource:
        """
        Convert this resource to an MCP Resource object.
        
        Returns:
            Resource object for MCP protocol
        """
        return Resource(
            uri=self.uri,
            name=self.name,
            description=self.description,
            mimeType=self.mime_type
        )
    
    @abstractmethod
    async def read(self) -> str:
        """
        Read the content of this resource.
        
        Returns:
            String content of the resource
        """
        pass
    
    def validate_uri(self, uri: str) -> bool:
        """
        Validate if the given URI matches this resource.
        
        Args:
            uri: URI to validate
            
        Returns:
            True if URI matches, False otherwise
        """
        return uri == self.uri


class PlaceholderResource(BaseResource):
    """
    Placeholder resource implementation for demonstration purposes.
    Replace this with actual resource implementations.
    """
    
    def __init__(self):
        super().__init__(
            uri="resource://placeholder",
            name="Placeholder Resource",
            description="A placeholder resource for demonstration",
            mime_type="application/json"
        )
    
    async def read(self) -> str:
        return """
        {
            "type": "placeholder",
            "message": "This is a placeholder resource. Replace with actual resource data.",
            "examples": {
                "legal_templates": "Legal document templates would go here",
                "compliance_frameworks": "Compliance framework data would go here",
                "regulatory_requirements": "Regulatory requirement data would go here"
            }
        }
        """


class LegalTemplatesResource(BaseResource):
    """
    Resource containing legal document templates.
    This is a placeholder - extend with actual templates.
    """
    
    def __init__(self):
        super().__init__(
            uri="resource://legal-templates",
            name="Legal Document Templates",
            description="Collection of legal document templates for compliance checking",
            mime_type="application/json"
        )
    
    async def read(self) -> str:
        return """
        {
            "templates": {
                "privacy_policy": {
                    "name": "Privacy Policy Template",
                    "description": "GDPR-compliant privacy policy template",
                    "required_sections": [
                        "data_collection",
                        "data_usage",
                        "data_retention",
                        "user_rights",
                        "contact_information"
                    ]
                },
                "terms_of_service": {
                    "name": "Terms of Service Template",
                    "description": "Standard terms of service template",
                    "required_sections": [
                        "acceptance_of_terms",
                        "service_description",
                        "user_obligations",
                        "limitation_of_liability",
                        "termination"
                    ]
                },
                "data_processing_agreement": {
                    "name": "Data Processing Agreement Template",
                    "description": "GDPR Article 28 compliant DPA template",
                    "required_sections": [
                        "processing_purposes",
                        "data_categories",
                        "retention_periods",
                        "security_measures",
                        "subprocessor_provisions"
                    ]
                }
            }
        }
        """


class ComplianceFrameworksResource(BaseResource):
    """
    Resource containing compliance frameworks and standards.
    This is a placeholder - extend with actual frameworks.
    """
    
    def __init__(self):
        super().__init__(
            uri="resource://compliance-frameworks",
            name="Compliance Frameworks",
            description="Various legal compliance frameworks and standards",
            mime_type="application/json"
        )
    
    async def read(self) -> str:
        return """
        {
            "frameworks": {
                "gdpr": {
                    "name": "General Data Protection Regulation",
                    "jurisdiction": "European Union",
                    "key_requirements": [
                        "lawful_basis_for_processing",
                        "data_subject_rights",
                        "privacy_by_design",
                        "data_breach_notification",
                        "data_protection_officer"
                    ],
                    "penalties": "Up to 4% of annual global turnover or €20 million"
                },
                "ccpa": {
                    "name": "California Consumer Privacy Act",
                    "jurisdiction": "California, USA",
                    "key_requirements": [
                        "consumer_right_to_know",
                        "consumer_right_to_delete",
                        "consumer_right_to_opt_out",
                        "non_discrimination",
                        "privacy_policy_requirements"
                    ],
                    "penalties": "Up to $7,500 per violation"
                },
                "sox": {
                    "name": "Sarbanes-Oxley Act",
                    "jurisdiction": "United States",
                    "key_requirements": [
                        "internal_controls",
                        "financial_reporting_accuracy",
                        "audit_committee_independence",
                        "executive_certification",
                        "whistleblower_protection"
                    ],
                    "penalties": "Criminal penalties up to 25 years imprisonment"
                }
            }
        }
        """
