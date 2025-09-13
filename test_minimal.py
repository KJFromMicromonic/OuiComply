#!/usr/bin/env python3
"""
Minimal test server to verify basic FastAPI setup works.
"""

from fastapi import FastAPI
import uvicorn

# Create app with minimal configuration
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "minimal"}

if __name__ == "__main__":
    print("🚀 Starting minimal test server...")
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="info")
