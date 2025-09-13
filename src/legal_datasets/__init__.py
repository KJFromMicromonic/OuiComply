"""
Datasets module for OuiComply MCP Server.

This module provides integration with legal datasets including:
- CUAD (Contract Understanding Atticus Dataset)
- Legal document templates
- Compliance frameworks
"""

from .cuad_integration import (
    CUADDatasetManager,
    cuad_manager,
    initialize_cuad_dataset,
    get_cuad_manager
)

__all__ = [
    'CUADDatasetManager',
    'cuad_manager', 
    'initialize_cuad_dataset',
    'get_cuad_manager'
]
