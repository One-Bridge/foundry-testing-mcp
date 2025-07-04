"""
Smart Contract Testing MCP Server

An interactive, AI-powered MCP (Model Context Protocol) server that revolutionizes
smart contract testing by providing guided, agentic workflows for designing, reviewing,
and implementing comprehensive test suites using the Foundry toolchain.

Key Features:
- Interactive Protocol Testing Agent with guided workflows
- Deep Foundry integration for test execution and coverage analysis
- Comprehensive test generation (unit, integration, invariant, fuzz)
- Professional test templates and best practices
- AI-powered testing strategy and recommendations
- Real-time coverage analysis and gap identification

Usage:
    from components import TestingMCPServer
    
    # Initialize and start the server
    server = TestingMCPServer()
    await server.start()

Author: AI Engineering Team
License: MIT
Version: 1.0.0
"""

from .components import (
    TestingMCPServer,
    FoundryAdapter,
    TestingTools,
    TestingResources,
    TestingPrompts
)

__version__ = "1.0.0"
__author__ = "AI Engineering Team"
__license__ = "MIT"
__title__ = "Smart Contract Testing MCP Server"
__description__ = "Interactive AI-powered smart contract testing workflows using Foundry"

__all__ = [
    "TestingMCPServer",
    "FoundryAdapter", 
    "TestingTools",
    "TestingResources",
    "TestingPrompts",
    "__version__",
    "__author__",
    "__license__",
    "__title__",
    "__description__"
]

# Package metadata
PACKAGE_NAME = "smart-contract-testing-mcp"
GITHUB_URL = "https://github.com/your-org/smart-contract-testing-mcp"
DOCUMENTATION_URL = "https://your-org.github.io/smart-contract-testing-mcp/"

# Feature flags
FEATURES = {
    "foundry_integration": True,
    "ai_guided_workflows": True,
    "comprehensive_coverage": True,
    "security_testing": True,
    "performance_optimization": True,
    "ci_cd_integration": True
}

def get_version():
    """Get the current package version."""
    return __version__

def get_server_info():
    """Get comprehensive server information."""
    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "github": GITHUB_URL,
        "docs": DOCUMENTATION_URL,
        "features": FEATURES
    } 