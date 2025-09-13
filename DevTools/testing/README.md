# Testing Utilities

This directory contains testing utilities and examples for the OuiComply project's Mistral AI integration.

## Test Files

- `test_mistral_integration.py` - Integration tests for Mistral AI
- `test_function_calling.py` - Tests for function calling functionality
- `test_structured_outputs.py` - Tests for structured output validation
- `test_error_handling.py` - Tests for error handling and retry logic
- `mock_responses.py` - Mock responses for testing without API calls

## Running Tests

```bash
# Run all tests
python -m pytest DevTools/testing/

# Run specific test file
python -m pytest DevTools/testing/test_function_calling.py

# Run with verbose output
python -m pytest DevTools/testing/ -v

# Run with coverage
python -m pytest DevTools/testing/ --cov=src
```

## Test Configuration

Create a `.env.test` file for test configuration:

```bash
# Test API key (use a test key or mock)
MISTRAL_API_KEY=test_key_here

# Test settings
MISTRAL_TEST_MODE=true
MISTRAL_MOCK_RESPONSES=true
```

## Mock Testing

For testing without making actual API calls, use the mock responses:

```python
from testing.mock_responses import MockMistralClient

# Use mock client for testing
client = MockMistralClient()
```

## Test Data

Test documents and expected responses are stored in the `test_data/` directory:

- `sample_privacy_policy.txt` - Sample privacy policy for testing
- `sample_terms_of_service.txt` - Sample terms of service
- `expected_responses.json` - Expected API responses for validation
