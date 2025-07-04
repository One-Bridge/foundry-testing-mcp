"""
Smart Contract Testing MCP Server - Main Server Implementation

This module implements the core FastMCP server for smart contract testing workflows.
The server is designed to be run locally and called from within Solidity project directories.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

from fastmcp import FastMCP
from .foundry_adapter import FoundryAdapter
from .testing_tools import TestingTools
from .testing_resources import TestingResources
from .testing_prompts import TestingPrompts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestingMCPServer:
    """
    Main MCP server for smart contract testing workflows.
    
    This server provides interactive, AI-guided testing workflows for Solidity
    smart contracts using the Foundry toolchain. It's designed to be run locally
    and called from within Solidity project directories via MCP clients like Cursor.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Testing MCP Server.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._load_default_config()
        self.mcp = FastMCP(
            name="smart-contract-testing",
            version="1.0.0",
            description="Interactive AI-powered smart contract testing workflows (call from within your project directory)"
        )
        
        # Initialize components
        self.foundry_adapter = FoundryAdapter()
        self.testing_tools = TestingTools(self.foundry_adapter)
        self.testing_resources = TestingResources()
        self.testing_prompts = TestingPrompts()
        
        # Register components with MCP
        self._register_components()
        
        logger.info("Smart Contract Testing MCP Server initialized successfully")
        logger.info("Usage: Navigate to your Solidity project directory and use the MCP tools")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from environment variables."""
        return {
            "server": {
                "host": os.getenv("MCP_SERVER_HOST", "127.0.0.1"),
                "port": int(os.getenv("MCP_SERVER_PORT", "8002")),
                "transport_mode": os.getenv("MCP_TRANSPORT_MODE", "stdio").lower()
            },
            "foundry": {
                "profile": os.getenv("FOUNDRY_PROFILE", "default"),
                "max_fuzz_runs": int(os.getenv("MAX_FUZZ_RUNS", "10000")),
                "invariant_runs": int(os.getenv("INVARIANT_RUNS", "256"))
            },
            "testing": {
                "coverage_target": int(os.getenv("COVERAGE_TARGET", "90")),
                "enable_gas_optimization": os.getenv("ENABLE_GAS_OPTIMIZATION", "true").lower() == "true"
            },
            "workflow": {
                "default_project_path": ".",  # Always use current directory
                "auto_detect_project_type": True,
                "validate_foundry_project": True
            }
        }
    
    def _register_components(self) -> None:
        """Register all components with the MCP server."""
        try:
            # Register testing tools
            self.testing_tools.register_tools(self.mcp)
            logger.info("Testing tools registered successfully")
            
            # Register testing resources
            self.testing_resources.register_resources(self.mcp)
            logger.info("Testing resources registered successfully")
            
            # Register testing prompts
            self.testing_prompts.register_prompts(self.mcp)
            logger.info("Testing prompts registered successfully")
            
            # Add server-level information tool
            @self.mcp.tool(
                name="get_server_info",
                description="Get information about the MCP server and usage instructions"
            )
            async def get_server_info() -> Dict[str, Any]:
                """Get server information and usage instructions."""
                return {
                    "server": {
                        "name": "Smart Contract Testing MCP Server",
                        "version": "1.0.0",
                        "description": "AI-powered testing workflows for Solidity smart contracts",
                        "foundry_integration": True
                    },
                    "usage": {
                        "workflow": "Call from within your Solidity project directory",
                        "start_command": "initialize_protocol_testing_agent",
                        "requirements": [
                            "Navigate to your Solidity project root directory",
                            "Ensure foundry.toml exists (or run 'forge init --force')",
                            "Have contracts in src/ directory",
                            "Foundry must be installed and accessible"
                        ]
                    },
                    "available_tools": [
                        "initialize_protocol_testing_agent - Start guided testing workflow",
                        "execute_testing_workflow - Run structured testing phases",
                        "analyze_current_test_coverage - Analyze coverage for current project",
                        "validate_current_project - Check if current directory is valid Foundry project"
                    ],
                    "available_resources": [
                        "testing/foundry-patterns - Best practices and patterns",
                        "testing/templates/{type} - Test templates",
                        "testing/project-analysis - Current project analysis",
                        "testing/coverage-report - Current coverage report",
                        "testing/documentation - Comprehensive guides"
                    ],
                    "available_prompts": [
                        "analyze-contract-for-testing - Contract analysis guidance",
                        "design-test-strategy - Testing strategy development",
                        "review-test-coverage - Coverage improvement guidance",
                        "design-security-tests - Security testing scenarios",
                        "optimize-test-performance - Performance optimization"
                    ],
                    "foundry_installation": await self.foundry_adapter.check_foundry_installation()
                }
            
        except Exception as e:
            logger.error(f"Failed to register components: {e}")
            raise
    
    async def run_server(self) -> None:
        """
        Run the MCP server.
        
        This method starts the server according to the configured transport mode.
        """
        try:
            transport_mode = self.config["server"]["transport_mode"]
            
            if transport_mode == "stdio":
                logger.info("Starting MCP server in STDIO mode")
                await self.mcp.run(transport="stdio")
            
            elif transport_mode == "http":
                host = self.config["server"]["host"]
                port = self.config["server"]["port"]
                logger.info(f"Starting MCP server in HTTP mode at {host}:{port}")
                await self.mcp.run(transport="http", host=host, port=port)
            
            else:
                raise ValueError(f"Unsupported transport mode: {transport_mode}")
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Cleanup server resources."""
        try:
            await self.foundry_adapter.cleanup()
            logger.info("Server cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Main server instance
async def main():
    """Main entry point for the server."""
    server = TestingMCPServer()
    await server.run_server()

if __name__ == "__main__":
    asyncio.run(main()) 