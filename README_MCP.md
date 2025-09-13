# OuiComply MCP Server

A Model Context Protocol (MCP) server for AI-assisted legal compliance checking using Mistral AI and the CUAD dataset.

## Overview

This MCP server provides tools and resources for legal document analysis, compliance checking, and risk assessment. It's designed to integrate with MCP-compatible clients like Claude Desktop, enabling AI assistants to perform legal compliance tasks using real-world legal contract patterns from the CUAD (Contract Understanding Atticus Dataset).

## 🆕 CUAD Dataset Integration

**NEW**: This server now integrates with the [CUAD (Contract Understanding Atticus Dataset)](https://huggingface.co/datasets/theatticusproject/cuad) from Hugging Face, providing:

- **500+ Real Legal Contracts**: Access to actual legal agreements with expert annotations
- **37 Legal Clause Categories**: Standardized taxonomy for contract analysis
- **Expert Annotations**: Professional legal analysis for accurate pattern matching
- **Enhanced Analysis**: Real-world contract patterns improve accuracy and reliability

## Features

### 🛠️ Enhanced Tools (CUAD-Powered)
- **Document Analysis**: Analyze legal documents using CUAD dataset patterns
- **CUAD Contract Analysis**: Comprehensive contract analysis with 37 clause categories
- **Clause Checking**: Verify presence of required clauses using CUAD patterns
- **Risk Assessment**: Perform risk analysis based on real contract data
- **CUAD Search**: Search 500+ contracts for specific clause examples
- **Template Generation**: Generate contract templates based on CUAD patterns

### 📚 Enhanced Resources
- **Legal Templates**: CUAD-enhanced document templates
- **Compliance Frameworks**: GDPR, CCPA, SOX, and other regulatory frameworks
- **CUAD Dataset**: Access to 500+ legal contracts and clause categories
- **Clause Categories**: 37 standardized legal clause types from CUAD
- **Regulatory Database**: Legal requirements and standards

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ouicomply

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 2. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Mistral API key
MISTRAL_KEY=your_mistral_api_key_here
```

### 3. Run the Server

```bash
# Run directly
python main.py

# Or as a module
python -m src.main

# Or using the installed command
ouicomply-mcp
```

## MCP Client Integration

### Claude Desktop

Add this server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "ouicomply": {
      "command": "python",
      "args": ["/path/to/ouicomply/main.py"],
      "env": {
        "MISTRAL_KEY": "your_mistral_api_key_here"
      }
    }
  }
}
```

### Other MCP Clients

The server implements the standard MCP protocol and should work with any MCP-compatible client.

## API Reference

### Tools

#### `analyze_document`
Analyze a legal document for compliance issues.

**Parameters:**
- `document_text` (string): The text content of the document
- `compliance_framework` (string): Framework to check against ("gdpr", "ccpa", "sox")

**Example:**
```json
{
  "document_text": "Privacy Policy content...",
  "compliance_framework": "gdpr"
}
```

#### `check_clause_presence`
Check if required clauses are present in a document.

**Parameters:**
- `document_text` (string): The text content of the document
- `required_clauses` (array): List of required clause types

**Example:**
```json
{
  "document_text": "Contract content...",
  "required_clauses": ["limitation_of_liability", "termination", "governing_law"]
}
```

#### `risk_assessment`
Perform a risk assessment on a legal document.

**Parameters:**
- `document_text` (string): The text content of the document
- `document_type` (string): Type of document ("contract", "policy", "agreement")

**Example:**
```json
{
  "document_text": "Agreement content...",
  "document_type": "contract"
}
```

### Resources

#### `resource://legal-templates`
Collection of legal document templates with required sections and compliance guidelines.

#### `resource://compliance-frameworks`
Detailed information about various compliance frameworks including GDPR, CCPA, and SOX.

## Development

### Project Structure

```
ouicomply/
├── src/
│   ├── config.py              # Configuration management
│   ├── mcp_server.py          # Main MCP server implementation
│   ├── tools/                 # Tool implementations
│   │   ├── __init__.py
│   │   └── base.py           # Base tool class
│   └── resources/            # Resource implementations
│       ├── __init__.py
│       └── base.py          # Base resource class
├── tests/                    # Test files
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── pyproject.toml           # Project configuration
└── README_MCP.md           # This file
```

### Adding New Tools

1. Create a new tool class inheriting from `BaseTool`:

```python
from src.tools.base import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description of my tool")
    
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            },
            "required": ["input"]
        }
    
    async def execute(self, arguments):
        # Tool implementation
        pass
```

2. Register the tool in `mcp_server.py`
3. Add tests in `tests/`

### Adding New Resources

1. Create a new resource class inheriting from `BaseResource`:

```python
from src.resources.base import BaseResource

class MyResource(BaseResource):
    def __init__(self):
        super().__init__(
            uri="resource://my-resource",
            name="My Resource",
            description="Description of my resource"
        )
    
    async def read(self):
        return "Resource content"
```

2. Register the resource in `mcp_server.py`

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_server.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MISTRAL_KEY` | Mistral AI API key | Yes | - |
| `MCP_SERVER_NAME` | Server name | No | `ouicomply-mcp` |
| `MCP_SERVER_VERSION` | Server version | No | `0.1.0` |
| `MCP_SERVER_PORT` | Server port | No | `3000` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `LOG_FORMAT` | Log format | No | `json` |
| `DATABASE_URL` | Database connection | No | - |

### Logging

The server uses structured logging with configurable levels and formats. Logs include:
- Request/response information
- Tool execution details
- Error tracking
- Performance metrics

## Extending the Server

This is an empty MCP server template ready for extension. To implement actual legal compliance features:

1. **Integrate Mistral AI**: Use the configured `MISTRAL_KEY` to call Mistral's API for document analysis
2. **Add Legal Logic**: Implement compliance rule engines and legal document parsing
3. **Expand Resources**: Add real legal templates, frameworks, and regulatory data
4. **Enhance Tools**: Build sophisticated analysis, checking, and assessment capabilities

## Troubleshooting

### Common Issues

1. **Configuration Error**: Ensure `.env` file exists and `MISTRAL_KEY` is set
2. **Import Errors**: Check Python path and installed dependencies
3. **MCP Connection**: Verify client configuration and server startup

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

### Logs

Check server logs for detailed error information and execution traces.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review the MCP protocol specification
