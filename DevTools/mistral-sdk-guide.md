# Mistral Python SDK Implementation Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation and Setup](#installation-and-setup)
3. [Authentication](#authentication)
4. [Function Calling (Tools)](#function-calling-tools)
5. [Structured Outputs](#structured-outputs)
6. [Current Implementation Analysis](#current-implementation-analysis)
7. [Recommended Improvements](#recommended-improvements)
8. [Best Practices](#best-practices)
9. [Advanced Features](#advanced-features)
10. [Code Examples](#code-examples)
11. [Troubleshooting](#troubleshooting)

## Overview

This guide provides comprehensive documentation for implementing the Mistral Python SDK in the OuiComply project. The focus is on leveraging Mistral's function calling capabilities for robust compliance analysis and document processing.

### Key Features for OuiComply

- **Function Calling**: Native tool integration for compliance analysis
- **Structured Outputs**: Reliable JSON schema-based responses
- **Document Analysis**: Advanced document processing capabilities
- **Multi-framework Support**: GDPR, SOX, CCPA, HIPAA compliance checking

## Installation and Setup

### Basic Installation

```bash
# Basic installation
pip install mistralai

# For agents functionality (requires Python 3.10+)
pip install "mistralai[agents]"

# With specific version
pip install mistralai==1.9.10
```

### Environment Setup

```bash
# Set your API key
export MISTRAL_API_KEY="your_api_key_here"

# Or add to .env file
echo "MISTRAL_API_KEY=your_api_key_here" >> .env
```

## Authentication

### Basic Authentication

```python
from mistralai import Mistral
import os

# Using environment variable (recommended)
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Or directly
client = Mistral(api_key="your_api_key_here")
```

### Advanced Configuration

```python
from mistralai import Mistral
from mistralai.utils import BackoffStrategy, RetryConfig
import httpx

# Custom HTTP client with retry configuration
retry_config = RetryConfig(
    strategy="backoff",
    backoff=BackoffStrategy(initial=1, max=50, factor=1.1, max_retries=100),
    retry_on_status=False
)

http_client = httpx.Client(
    headers={"x-custom-header": "someValue"},
    timeout=30.0
)

client = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY"),
    client=http_client,
    retry_config=retry_config
)
```

## Function Calling (Tools)

Function calling is the most important feature for OuiComply's compliance analysis. It allows the AI to use predefined tools/functions to perform structured operations.

### Basic Function Calling

```python
# Define your tools/functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_document_compliance",
            "description": "Analyze a document for compliance issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_content": {
                        "type": "string",
                        "description": "Document content to analyze"
                    },
                    "compliance_frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Frameworks to check against (GDPR, SOX, CCPA, HIPAA)"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["basic", "standard", "comprehensive"],
                        "description": "Level of analysis detail"
                    }
                },
                "required": ["document_content", "compliance_frameworks"]
            }
        }
    }
]

# Use tools in chat completion
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "user", "content": "Analyze this document for GDPR compliance"}
    ],
    tools=tools,
    tool_choice="auto"  # Let model decide when to use tools
)
```

### Tool Choice Options

```python
# Auto - Let the model decide
tool_choice="auto"

# Required - Force tool use
tool_choice="required"

# Specific tool
tool_choice={
    "type": "function",
    "function": {"name": "analyze_document_compliance"}
}

# None - Disable tools
tool_choice="none"
```

### Handling Tool Responses

```python
# Process tool call responses
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "analyze_document_compliance":
            # Process compliance analysis results
            result = process_compliance_analysis(function_args)
```

## Structured Outputs

Use JSON schemas for reliable, structured responses instead of manual parsing.

### JSON Schema Response Format

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "compliance_analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue_id": {"type": "string"},
                                "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "category": {"type": "string"},
                                "description": {"type": "string"},
                                "location": {"type": "string"},
                                "recommendation": {"type": "string"},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                            }
                        }
                    },
                    "missing_clauses": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "risk_score": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["issues", "missing_clauses", "recommendations", "risk_score"]
            },
            "strict": True  # Enforce schema compliance
        }
    }
)

# Parse structured response
result = json.loads(response.choices[0].message.content)
```

## Current Implementation Analysis

### Issues in Current Code

1. **No Function Calling**: Using basic chat completion without tools
2. **Manual JSON Parsing**: Error-prone string parsing instead of structured outputs
3. **No Tool Integration**: MCP server tools not integrated with Mistral's function calling
4. **Inconsistent Error Handling**: Basic try-catch without proper retry logic

### Current Code Location

The main implementation is in `src/tools/document_ai.py`:

```python
# Current approach (lines 387-400)
response = await self.client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {
            "role": "system",
            "content": "You are a legal compliance expert..."
        },
        {
            "role": "user", 
            "content": analysis_prompt
        }
    ],
    temperature=0.1
)

# Manual JSON parsing (lines 403-416)
framework_analysis = self._parse_ai_response(
    response.choices[0].message.content,
    framework
)
```

## Recommended Improvements

### 1. Implement Function Calling for Compliance Analysis

```python
async def _perform_compliance_analysis_with_tools(
    self, 
    document_id: str, 
    frameworks: List[str], 
    depth: str
) -> Dict[str, Any]:
    """Use Mistral's function calling for structured compliance analysis."""
    
    # Define compliance analysis tools
    compliance_tools = [
        {
            "type": "function",
            "function": {
                "name": "identify_compliance_issues",
                "description": "Identify specific compliance issues in the document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "issue_id": {"type": "string"},
                                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                    "category": {"type": "string"},
                                    "description": {"type": "string"},
                                    "location": {"type": "string"},
                                    "recommendation": {"type": "string"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                                }
                            }
                        },
                        "missing_clauses": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["issues", "missing_clauses", "recommendations"]
                }
            }
        }
    ]
    
    # Use function calling
    response = await self.client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": "You are a legal compliance expert. Analyze the document and use the provided function to return structured compliance analysis."
            },
            {
                "role": "user",
                "content": f"Analyze document {document_id} for {', '.join(frameworks)} compliance with {depth} depth."
            }
        ],
        tools=compliance_tools,
        tool_choice="required",  # Force use of the function
        temperature=0.1
    )
    
    # Extract structured data from tool calls
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        return json.loads(tool_call.function.arguments)
    
    raise ValueError("No tool call found in response")
```

### 2. Enhanced Error Handling and Retry Logic

```python
import asyncio
from typing import Optional

async def _make_retryable_request(
    self,
    request_func,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """Make a retryable request with exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            return await request_func()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts", error=str(e))
                raise
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Request failed, retrying in {delay}s", attempt=attempt+1, error=str(e))
            await asyncio.sleep(delay)
```

### 3. Document Upload Optimization

```python
async def _upload_document_optimized(self, content: bytes, document_type: str) -> str:
    """Optimized document upload with caching."""
    
    # Generate content hash for caching
    import hashlib
    content_hash = hashlib.sha256(content).hexdigest()
    
    # Check cache first
    cache_key = f"doc_{content_hash}"
    if cache_key in self._document_cache:
        return self._document_cache[cache_key]
    
    try:
        # Upload to Mistral
        response = await self.client.documents.create(
            file=base64.b64encode(content).decode('utf-8'),
            name=f"compliance_doc_{content_hash[:8]}",
            type=DocumentType.PDF if document_type == "application/pdf" else DocumentType.TEXT
        )
        
        # Cache the result
        self._document_cache[cache_key] = response.id
        return response.id
        
    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise
```

## Best Practices

### 1. Model Selection

```python
# For complex legal analysis
model = "mistral-large-latest"

# For simple tasks
model = "mistral-small-latest"

# For code analysis
model = "codestral-latest"
```

### 2. Temperature Settings

```python
# Legal analysis - low temperature for consistency
temperature = 0.1

# Creative tasks - higher temperature
temperature = 0.7

# Balanced approach
temperature = 0.3
```

### 3. Token Management

```python
# Set appropriate max_tokens
max_tokens = 4000  # For detailed reports
max_tokens = 1000  # For summaries
max_tokens = 2000  # For standard analysis
```

### 4. Parallel Processing

```python
# Enable parallel tool calls
response = client.chat.complete(
    model="mistral-large-latest",
    messages=messages,
    tools=tools,
    parallel_tool_calls=True  # Allow multiple simultaneous tool calls
)
```

## Advanced Features

### 1. Streaming Responses

```python
# For real-time progress updates
response = client.chat.stream(
    model="mistral-large-latest",
    messages=messages,
    tools=tools
)

for event in response:
    if event.choices[0].delta.content:
        print(event.choices[0].delta.content, end="", flush=True)
```

### 2. Custom HTTP Client Configuration

```python
import httpx

# Custom client with specific configurations
http_client = httpx.AsyncClient(
    headers={
        "User-Agent": "OuiComply/1.0",
        "X-Custom-Header": "compliance-analysis"
    },
    timeout=httpx.Timeout(30.0, connect=10.0),
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)

client = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY"),
    client=http_client
)
```

### 3. Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
debug_logger = logging.getLogger("mistralai")

client = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY"),
    debug_logger=debug_logger
)

# Or use environment variable
# export MISTRAL_DEBUG=true
```

## Code Examples

### Complete Compliance Analysis Function

```python
async def analyze_document_compliance_enhanced(
    self,
    document_content: bytes,
    frameworks: List[str],
    analysis_depth: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Enhanced compliance analysis using Mistral function calling.
    
    Args:
        document_content: Document content as bytes
        frameworks: List of compliance frameworks to check
        analysis_depth: Level of analysis detail
        
    Returns:
        Structured compliance analysis results
    """
    
    # Upload document
    document_id = await self._upload_document_optimized(
        document_content, 
        "application/pdf"
    )
    
    # Define compliance analysis tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_compliance",
                "description": "Comprehensive compliance analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "compliance_issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "issue_id": {"type": "string"},
                                    "severity": {"type": "string"},
                                    "category": {"type": "string"},
                                    "description": {"type": "string"},
                                    "location": {"type": "string"},
                                    "recommendation": {"type": "string"},
                                    "confidence": {"type": "number"},
                                    "framework": {"type": "string"}
                                }
                            }
                        },
                        "missing_clauses": {"type": "array", "items": {"type": "string"}},
                        "recommendations": {"type": "array", "items": {"type": "string"}},
                        "risk_score": {"type": "number"},
                        "compliance_status": {"type": "string"}
                    },
                    "required": ["compliance_issues", "missing_clauses", "recommendations", "risk_score"]
                }
            }
        }
    ]
    
    # Generate analysis prompt
    prompt = self._generate_compliance_prompt(document_id, frameworks, analysis_depth)
    
    # Make request with retry logic
    response = await self._make_retryable_request(
        lambda: self.client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal compliance expert specializing in document analysis. Use the provided function to return structured compliance analysis."
                },
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice="required",
            temperature=0.1,
            max_tokens=4000
        )
    )
    
    # Process response
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        return json.loads(tool_call.function.arguments)
    
    raise ValueError("No tool call found in response")
```

### MCP Server Integration

```python
# In mcp_server.py
async def _handle_analyze_document_compliance_enhanced(
    self, 
    arguments: Dict[str, Any]
) -> List[TextContent]:
    """Enhanced document compliance analysis with Mistral function calling."""
    
    document_content = arguments.get("document_content", "")
    frameworks = arguments.get("compliance_frameworks", ["gdpr", "sox", "ccpa"])
    analysis_depth = arguments.get("analysis_depth", "comprehensive")
    
    try:
        # Process document content
        if isinstance(document_content, str):
            # Try to decode as base64
            try:
                document_bytes = base64.b64decode(document_content)
            except Exception:
                # Treat as file path
                document_bytes = Path(document_content).read_bytes()
        else:
            document_bytes = document_content
        
        # Perform enhanced analysis
        analysis_result = await self.compliance_engine.analyze_document_compliance_enhanced(
            document_content=document_bytes,
            frameworks=frameworks,
            analysis_depth=analysis_depth
        )
        
        # Generate report
        report = await self._generate_compliance_report(analysis_result)
        
        return [TextContent(type="text", text=report)]
        
    except Exception as e:
        logger.error("Enhanced analysis failed", error=str(e))
        return [TextContent(
            type="text", 
            text=f"Analysis failed: {str(e)}"
        )]
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```python
   # Check environment variable
   import os
   print(os.getenv("MISTRAL_API_KEY"))
   ```

2. **Tool Call Not Found**
   ```python
   # Check if tool_choice is set correctly
   if response.choices[0].message.tool_calls:
       # Process tool calls
   else:
       # Handle no tool calls
   ```

3. **JSON Parsing Errors**
   ```python
   # Use structured outputs instead of manual parsing
   response_format={
       "type": "json_schema",
       "json_schema": {...}
   }
   ```

4. **Rate Limiting**
   ```python
   # Implement exponential backoff
   await asyncio.sleep(delay * (2 ** attempt))
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use environment variable
# export MISTRAL_DEBUG=true
```

### Performance Monitoring

```python
import time

start_time = time.time()
response = await client.chat.complete(...)
end_time = time.time()

logger.info(f"Request completed in {end_time - start_time:.2f}s")
```

## Migration Guide

### From Current Implementation

1. **Replace manual JSON parsing** with structured outputs
2. **Add function calling** to compliance analysis
3. **Implement retry logic** for API calls
4. **Add document caching** to avoid re-uploads
5. **Use proper error handling** throughout

### Step-by-Step Migration

1. Update `document_ai.py` with function calling
2. Modify `compliance_engine.py` to use structured outputs
3. Update `mcp_server.py` to handle new response format
4. Add comprehensive error handling
5. Implement caching and retry logic
6. Update tests to match new implementation

## Resources

- [Mistral AI Official Documentation](https://docs.mistral.ai/)
- [Mistral Python SDK GitHub](https://github.com/mistralai/client-python)
- [Function Calling Guide](https://docs.mistral.ai/api/#function-calling)
- [JSON Schema Documentation](https://json-schema.org/)

## Support

For issues specific to this implementation:
1. Check the troubleshooting section
2. Review the code examples
3. Enable debug logging
4. Check Mistral API status

For Mistral API issues:
1. Check [Mistral Status Page](https://status.mistral.ai/)
2. Review [API Documentation](https://docs.mistral.ai/api/)
3. Contact Mistral Support
