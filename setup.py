"""
Smart Contract Testing MCP Server - Setup Configuration

This package provides an interactive AI-powered MCP server for smart contract testing
workflows using the Foundry toolchain.
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure we're using Python 3.8+
if sys.version_info < (3, 8):
    raise RuntimeError("This package requires Python 3.8 or later")

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Smart Contract Testing MCP Server - Interactive AI-powered testing workflows"

# Read requirements
def read_requirements(filename):
    requirements_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(requirements_path):
        return []
    
    with open(requirements_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    requirements = []
    for line in lines:
        line = line.strip()
        # Skip comments, empty lines, and section headers
        if line and not line.startswith("#") and not line.startswith("["):
            requirements.append(line)
    
    return requirements

# Version information
VERSION = "1.0.0"

# Setup configuration
setup(
    name="smart-contract-testing-mcp",
    version=VERSION,
    author="AI Engineering Team",
    author_email="engineering@example.com",
    description="Interactive AI-powered smart contract testing workflows using Foundry",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/smart-contract-testing-mcp",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    package_data={
        "components": ["py.typed"],
        "templates": ["*.sol"],
        "docs": ["**/*.md", "**/*.txt"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "black>=23.0.0",
            "isort>=5.12.0", 
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "mkdocs-mermaid2-plugin>=0.6.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-contract-testing-mcp=components.testing_server:main",
            "testing-mcp=components.testing_server:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/smart-contract-testing-mcp/issues",
        "Source": "https://github.com/your-org/smart-contract-testing-mcp",
        "Documentation": "https://your-org.github.io/smart-contract-testing-mcp/",
        "Funding": "https://github.com/sponsors/your-org",
    },
    keywords=[
        "smart-contracts",
        "testing",
        "foundry",
        "solidity",
        "mcp",
        "model-context-protocol",
        "ai-testing",
        "blockchain",
        "ethereum",
        "defi",
        "security-testing",
        "coverage-analysis",
        "fuzz-testing",
        "invariant-testing",
    ],
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    test_suite="tests",
) 