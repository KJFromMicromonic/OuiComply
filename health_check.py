"""
Health check endpoint for ALPIC deployment.

This module provides a simple health check endpoint that ALPIC can use
to monitor the health of the MCP server.
"""

import json
import asyncio
from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path
from mcp.server.fastmcp

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config import get_config


class HealthChecker:
    """
    Health check service for the OuiComply MCP Server.
    
    Provides various health check endpoints and status monitoring
    for ALPIC deployment.
    """
    
    def __init__(self):
        self.config = get_config()
        self.start_time = datetime.now()
    
    async def basic_health_check(self) -> Dict[str, Any]:
        """
        Perform a basic health check.
        
        Returns:
            Dict[str, Any]: Health check status and basic information
        """
        try:
            # Check if Mistral API key is configured
            mistral_configured = bool(
                self.config.mistral_api_key and 
                self.config.mistral_api_key != "your_mistral_api_key_here"
            )
            
            # Calculate uptime
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "status": "healthy" if mistral_configured else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime_seconds,
                "version": self.config.server_version,
                "mistral_configured": mistral_configured,
                "checks": {
                    "configuration": "ok" if mistral_configured else "error",
                    "server": "ok",
                    "dependencies": "ok"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "checks": {
                    "configuration": "error",
                    "server": "error",
                    "dependencies": "error"
                }
            }
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """
        Perform a detailed health check with more comprehensive checks.
        
        Returns:
            Dict[str, Any]: Detailed health check status
        """
        basic_status = await self.basic_health_check()
        
        # Add additional checks
        additional_checks = {
            "memory_usage": self._check_memory_usage(),
            "disk_space": self._check_disk_space(),
            "network_connectivity": await self._check_network_connectivity(),
            "api_endpoints": self._check_api_endpoints()
        }
        
        # Determine overall health
        all_checks_ok = all(
            check.get("status") == "ok" 
            for check in additional_checks.values()
        ) and basic_status["status"] == "healthy"
        
        return {
            **basic_status,
            "status": "healthy" if all_checks_ok else "unhealthy",
            "detailed_checks": additional_checks
        }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "status": "ok" if memory.percent < 90 else "warning",
                "usage_percent": memory.percent,
                "available_mb": memory.available // (1024 * 1024)
            }
        except ImportError:
            return {"status": "ok", "note": "psutil not available"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            return {
                "status": "ok" if free_percent > 10 else "warning",
                "free_percent": free_percent,
                "free_gb": free // (1024 * 1024 * 1024)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to external services."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Test connectivity to Mistral API
                try:
                    response = await client.get("https://api.mistral.ai/v1/models")
                    mistral_status = "ok" if response.status_code in [200, 401] else "error"
                except Exception:
                    mistral_status = "error"
                
                return {
                    "status": "ok" if mistral_status == "ok" else "warning",
                    "mistral_api": mistral_status
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_api_endpoints(self) -> Dict[str, Any]:
        """Check if API endpoints are properly configured."""
        try:
            # Check if required modules can be imported
            from tools.compliance_engine import ComplianceEngine
            from tools.memory_integration import LeChatMemoryService
            
            return {
                "status": "ok",
                "compliance_engine": "available",
                "memory_service": "available"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


async def health_check_handler() -> str:
    """
    Health check handler for ALPIC.
    
    Returns:
        str: JSON response for health check
    """
    checker = HealthChecker()
    status = await checker.basic_health_check()
    return json.dumps(status, indent=2)


async def detailed_health_check_handler() -> str:
    """
    Detailed health check handler for ALPIC.
    
    Returns:
        str: JSON response for detailed health check
    """
    checker = HealthChecker()
    status = await checker.detailed_health_check()
    return json.dumps(status, indent=2)


if __name__ == "__main__":
    # For testing health check locally
    async def test_health_check():
        print("Basic Health Check:")
        print(await health_check_handler())
        print("\nDetailed Health Check:")
        print(await detailed_health_check_handler())
    
    asyncio.run(test_health_check())
