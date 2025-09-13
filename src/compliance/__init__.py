"""
Compliance Analysis Module for OuiComply MCP Server.

This module provides specialized compliance analyzers for different regulatory frameworks:
- GDPR (General Data Protection Regulation)
- SOX (Sarbanes-Oxley Act)
- Licensing Clauses

Each analyzer provides framework-specific analysis, risk assessment, and recommendations.
"""

from .gdpr_analyzer import GDPRAnalyzer
from .sox_analyzer import SOXAnalyzer
from .licensing_analyzer import LicensingAnalyzer

__all__ = [
    "GDPRAnalyzer",
    "SOXAnalyzer", 
    "LicensingAnalyzer"
]

# Version information
__version__ = "1.0.0"
__author__ = "OuiComply Team"
