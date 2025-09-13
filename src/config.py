"""
Configuration management for OuiComply MCP Server.
Loads environment variables and provides configuration settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class MCPConfig:
    """Configuration settings for the MCP server."""
    
    def __init__(self):
        # Mistral AI Configuration
        self.mistral_api_key = os.getenv("MISTRAL_KEY", "")
        
        # MCP Server Configuration
        self.server_name = os.getenv("MCP_SERVER_NAME", "ouicomply-mcp")
        self.server_version = os.getenv("MCP_SERVER_VERSION", "0.1.0")
        self.server_port = int(os.getenv("MCP_SERVER_PORT", "3000"))
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")
        
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


# Global configuration instance
config = MCPConfig()


def get_config() -> MCPConfig:
    """Get the global configuration instance."""
    return config


def validate_config() -> bool:
    """Validate that all required configuration is present."""
    try:
        # Check if Mistral API key is provided
        if not config.mistral_api_key or config.mistral_api_key == "your_mistral_api_key_here":
            raise ValueError("MISTRAL_KEY is required and must be set in .env file")
        
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False


def print_config_summary():
    """Print a summary of the current configuration (without sensitive data)."""
    print("=== OuiComply MCP Server Configuration ===")
    print(f"Server Name: {config.server_name}")
    print(f"Server Version: {config.server_version}")
    print(f"Server Port: {config.server_port}")
    print(f"Log Level: {config.log_level}")
    print(f"Log Format: {config.log_format}")
    print(f"Mistral API Key: {'✓ Set' if config.mistral_api_key and config.mistral_api_key != 'your_mistral_api_key_here' else '✗ Not Set'}")
    print(f"Database URL: {'✓ Set' if config.database_url else '✗ Not Set'}")
    print("==========================================")
