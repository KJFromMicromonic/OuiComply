# API Examples

This directory contains practical code examples for implementing Mistral AI in the OuiComply project.

## Examples

- `basic-usage.py` - Basic Mistral SDK usage
- `function-calling.py` - Function calling implementation
- `structured-outputs.py` - JSON schema structured outputs
- `document-analysis.py` - Document analysis examples
- `error-handling.py` - Error handling and retry logic
- `mcp-integration.py` - MCP server integration examples

## Usage

Each example is self-contained and can be run independently:

```bash
# Run a specific example
python api-examples/basic-usage.py

# Or import in your code
from api_examples.function_calling import analyze_document_compliance
```

## Prerequisites

Make sure you have the required dependencies:

```bash
pip install mistralai httpx pydantic
```

And set your API key:

```bash
export MISTRAL_API_KEY="your_api_key_here"
```
