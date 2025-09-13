"""
ALPIC-specific configuration for OuiComply MCP Server.

This module provides ALPIC-specific configuration overrides and
environment variable handling for cloud deployment.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ALPICConfig:
    """
    ALPIC-specific configuration settings.
    
    This class extends the base MCP configuration with ALPIC-specific
    settings and environment variable handling.
    """
    
    def __init__(self):
        # ALPIC Environment Detection
        self.is_alpic = os.getenv("ALPIC_ENV", "false").lower() == "true"
        self.alpic_port = int(os.getenv("PORT", "3000"))
        
        # Mistral AI Configuration
        self.mistral_api_key = os.getenv("MISTRAL_KEY", "")
        
        # MCP Server Configuration
        self.server_name = os.getenv("MCP_SERVER_NAME", "ouicomply-mcp")
        self.server_version = os.getenv("MCP_SERVER_VERSION", "1.0.0")
        self.server_port = self.alpic_port if self.is_alpic else int(os.getenv("MCP_SERVER_PORT", "3000"))
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")
        
        # ALPIC-specific settings
        self.enable_health_check = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
        self.health_check_path = os.getenv("HEALTH_CHECK_PATH", "/health")
        
        # Optional Database Configuration
        self.database_url = os.getenv("DATABASE_URL")
        
        # Optional Additional API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # LeChat Memory Integration
        self.lechat_api_url = os.getenv("LECHAT_API_URL", "https://api.lechat.ai")
        self.lechat_api_key = os.getenv("LECHAT_API_KEY")
        
        # GitHub Integration (for audit trails)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repository = os.getenv("GITHUB_REPOSITORY")
        
        # Linear/Jira Integration (for issue assignment)
        self.linear_api_key = os.getenv("LINEAR_API_KEY")
        self.jira_api_key = os.getenv("JIRA_API_KEY")
        self.jira_base_url = os.getenv("JIRA_BASE_URL")
    
    def validate(self) -> bool:
        """
        Validate ALPIC-specific configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check if Mistral API key is provided
            if not self.mistral_api_key or self.mistral_api_key == "your_mistral_api_key_here":
                raise ValueError("MISTRAL_KEY is required and must be set in environment variables")
            
            # Validate port number
            if not (1 <= self.server_port <= 65535):
                raise ValueError(f"Invalid port number: {self.server_port}")
            
            return True
        except Exception as e:
            print(f"ALPIC configuration validation failed: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of the current configuration (without sensitive data)."""
        print("=== OuiComply MCP Server - ALPIC Configuration ===")
        print(f"Environment: {'ALPIC' if self.is_alpic else 'Local'}")
        print(f"Server Name: {self.server_name}")
        print(f"Server Version: {self.server_version}")
        print(f"Server Port: {self.server_port}")
        print(f"Log Level: {self.log_level}")
        print(f"Log Format: {self.log_format}")
        print(f"Health Check: {'Enabled' if self.enable_health_check else 'Disabled'}")
        print(f"Mistral API Key: {'✓ Set' if self.mistral_api_key and self.mistral_api_key != 'your_mistral_api_key_here' else '✗ Not Set'}")
        print(f"Database URL: {'✓ Set' if self.database_url else '✗ Not Set'}")
        print("================================================")


# Global ALPIC configuration instance
alpac_config = ALPICConfig()


def get_alpic_config() -> ALPICConfig:
    """Get the global ALPIC configuration instance."""
    return alpac_config


def validate_alpic_config() -> bool:
    """Validate ALPIC configuration."""
    return alpac_config.validate()


def print_alpic_config_summary():
    """Print ALPIC configuration summary."""
    alpac_config.print_summary()
