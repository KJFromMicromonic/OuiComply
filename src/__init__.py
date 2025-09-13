"""
OuiComply MCP Server - AI Assisted Legal Compliance Checker.

This package provides a Model Context Protocol (MCP) server for legal compliance
analysis using Mistral AI. It includes tools for document analysis, compliance
checking, and risk assessment.

Main components:
- mcp_server: Main MCP server implementation
- config: Configuration management
- tools: Tool implementations for legal analysis
- resources: Resource implementations for legal data
"""

__version__ = "0.1.0"
__author__ = "OuiComply Team"
__description__ = "OuiComply MCP Server - AI Assisted Legal Compliance Checker"

from .config import get_config, validate_config

__all__ = [
    "get_config",
    "validate_config",
]
