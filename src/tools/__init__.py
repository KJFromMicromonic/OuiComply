"""
Tools package for OuiComply MCP Server.

This package contains tool implementations for legal compliance analysis.
Tools are functions that can be called by MCP clients to perform specific tasks.

Example tools to implement:
- Document analysis tools
- Compliance checking tools
- Risk assessment tools
- Legal template generators
"""

from typing import List, Dict, Any
from .base import BaseTool

__all__ = ["BaseTool"]

# Future tool imports will go here:
# from .document_analyzer import DocumentAnalyzer
# from .compliance_checker import ComplianceChecker
# from .risk_assessor import RiskAssessor
