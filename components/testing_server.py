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
            name="smart-contract-testing"
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
                description="""
                ℹ️ Server information and quick start guide - Use when you need to understand MCP capabilities
                
                WHEN TO USE:
                - First time using this MCP server
                - User asks about available tools or capabilities
                - Need to understand tool workflow and relationships
                - Checking server status and Foundry installation
                - Getting quick start instructions
                
                WHAT IT DOES:
                - Provides complete overview of all available MCP tools
                - Explains tool relationships and recommended workflow
                - Lists all available resources (templates, documentation)
                - Shows server version and capability information
                - Provides quick start instructions for different scenarios
                
                OUTPUTS:
                - Complete tool catalog with descriptions
                - Recommended workflow sequence
                - Available resources and templates
                - Server status and version information
                - Quick start guide for common scenarios
                
                WORKFLOW: Use before other tools to understand MCP capabilities, or when users need orientation.
                """
            )
            async def get_server_info() -> Dict[str, Any]:
                """Get server information and usage instructions."""
                return {
                    "server": {
                        "name": "Smart Contract Testing MCP Server",
                        "version": "2.0.0",
                        "description": "World-class AI-powered testing workflows with context analysis and security expertise",
                        "foundry_integration": True,
                        "capabilities": [
                            "Context-aware project analysis",
                            "AI failure detection",
                            "Professional security methodologies",
                            "Adaptive testing workflows"
                        ]
                    },
                    "recommended_workflow": {
                        "step_1": {
                            "tool": "initialize_protocol_testing_agent",
                            "purpose": "Start here - analyzes project and recommends workflow",
                            "when": "Beginning any testing work, first interaction with project"
                        },
                        "step_2_option_a": {
                            "tool": "analyze_project_context", 
                            "purpose": "Deep analysis with AI failure detection",
                            "when": "Existing tests need quality assessment or detailed planning needed"
                        },
                        "step_2_option_b": {
                            "tool": "execute_testing_workflow",
                            "purpose": "Direct implementation of testing strategy", 
                            "when": "Clear on objectives and ready to implement"
                        },
                        "step_3": {
                            "tool": "analyze_current_test_coverage",
                            "purpose": "Monitor progress and validate coverage",
                            "when": "During or after test implementation"
                        }
                    },
                    "troubleshooting_tools": {
                        "validate_current_project": "Use when getting project setup errors",
                        "debug_directory_detection": "Use when MCP can't find your project files"
                    },
                    "available_tools": {
                        "initialize_protocol_testing_agent": "🚀 STEP 1: Start testing workflow - analyzes project and provides recommendations",
                        "analyze_project_context": "🔍 STEP 2: Deep analysis with AI failure detection and improvement planning", 
                        "execute_testing_workflow": "⚡ STEP 3: Execute structured testing workflow with professional methodologies",
                        "analyze_current_test_coverage": "📊 Coverage analysis and gap identification",
                        "validate_current_project": "✅ Project validation and setup troubleshooting", 
                        "debug_directory_detection": "🐛 Advanced directory/path troubleshooting"
                    },
                    "key_features": {
                        "context_awareness": "Understands current project state, doesn't restart from scratch",
                        "ai_failure_detection": "Catches problematic AI-generated tests (circular logic, mock cheating)",
                        "security_expertise": "Integrates Trail of Bits, OpenZeppelin, ConsenSys methodologies",
                        "adaptive_workflows": "Tailors guidance to project maturity and testing phase"
                    },
                    "usage_scenarios": {
                        "new_project": "initialize_protocol_testing_agent → execute_testing_workflow('create_new_suite')",
                        "enhance_existing": "initialize_protocol_testing_agent → analyze_project_context → execute_testing_workflow('evaluate_existing')",
                        "coverage_check": "analyze_current_test_coverage (standalone)",
                        "troubleshooting": "validate_current_project or debug_directory_detection"
                    },
                    "requirements": [
                        "Navigate to your Solidity project root directory", 
                        "Foundry must be installed and accessible",
                        "Project should have foundry.toml (or run 'forge init --force')",
                        "Contracts should be in src/ directory"
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
                await self.mcp.run_async(transport="stdio")
            
            elif transport_mode == "http":
                host = self.config["server"]["host"]
                port = self.config["server"]["port"]
                logger.info(f"Starting MCP server in HTTP mode at {host}:{port}")
                await self.mcp.run_async(transport="http", host=host, port=port)
            
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