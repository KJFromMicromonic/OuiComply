"""
Setup script for OuiComply MCP Server.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="ouicomply-mcp",
    version="0.1.0",
    author="OuiComply Team",
    description="OuiComply MCP Server - AI Assisted Legal Compliance Checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ouicomply",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "mistralai>=0.4.0",
        "httpx>=0.25.0",
        "structlog>=23.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ouicomply-mcp=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
