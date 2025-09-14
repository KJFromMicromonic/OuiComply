#!/usr/bin/env python3
"""
Test script for the FastMCP + Starlette server
"""

import requests
import time
import subprocess
import sys
from pathlib import Path

def test_server():
    """Test the server functionality."""
    print("Testing OuiComply FastMCP + Starlette Server...")
    
    # Start the server in the background
    print("Starting server...")
    process = subprocess.Popen([sys.executable, "start_fastmcp_server.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up
        print("Stopping server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_server()
