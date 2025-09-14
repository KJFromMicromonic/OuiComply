#!/usr/bin/env python3
"""
Test the lambda_handler locally
"""

from lambda_handler import lambda_handler

# Test payload from the deployment
test_event = {
    "v20250806": {
        "message": {
            "jsonrpc": "2.0",
            "id": "test-build-id",
            "method": "oauth/metadata"
        }
    }
}

# Test invalid method
test_event_invalid = {
    "v20250806": {
        "message": {
            "jsonrpc": "2.0",
            "id": "test-build-id",
            "method": "invalid/method"
        }
    }
}

if __name__ == "__main__":
    print("Testing lambda_handler with oauth/metadata...")
    result = lambda_handler(test_event, None)
    print("Response:", result)

    print("\nTesting lambda_handler with invalid method...")
    result_invalid = lambda_handler(test_event_invalid, None)
    print("Response:", result_invalid)
