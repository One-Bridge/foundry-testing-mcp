"""
Smart Contract Testing MCP Server - Main Server Implementation (Enhanced)

This module implements the core FastMCP server for smart contract testing workflows.
The server is designed to be run locally and called from within Solidity project directories.
Enhanced with AST-based semantic analysis and proper dependency injection.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

from fastmcp import FastMCP
from .foundry_adapter import FoundryAdapter, FoundryNotFoundError, FoundryProjectError
from .project_analyzer import ProjectAnalyzer
from .ai_failure_detector import AIFailureDetector
from .ast_analyzer import ASTAnalyzer
from .testing_tools import TestingTools
from .testing_resources import TestingResources
from .testing_prompts import TestingPrompts

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestingMCPServer:
    """
    Main MCP server for smart contract testing workflows.
    
    Enhanced with AST-based semantic analysis, proper dependency injection,
    and comprehensive error handling. Provides interactive, AI-guided testing
    workflows for Solidity smart contracts using the Foundry toolchain.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Testing MCP Server with enhanced architecture.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._load_default_config()
        self.mcp = FastMCP(name="foundry-testing-agent")
        
        # Initialize core components with proper dependency injection
        try:
            self._initialize_components()
            self._register_components()
            logger.info("✅ Smart Contract Testing MCP Server initialized successfully")
            logger.info("Enhanced with AST-based semantic analysis and AI failure detection")
            
        except FoundryNotFoundError as e:
            logger.critical(f"FATAL: {e}")
            logger.critical("The server cannot start without Foundry installation.")
            logger.critical("Please install Foundry: https://getfoundry.sh/")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
    
    def _initialize_components(self) -> None:
        """Initialize all components with proper dependency injection."""
        logger.info("Initializing server components...")
        
        # Core analysis components
        logger.debug("-> Initializing FoundryAdapter...")
        self.foundry_adapter = FoundryAdapter()
        
        logger.debug("-> Initializing AST Analyzer...")
        self.ast_analyzer = ASTAnalyzer()
        
        logger.debug("-> Initializing ProjectAnalyzer with AST support...")
        self.project_analyzer = ProjectAnalyzer(self.foundry_adapter)
        
        logger.debug("-> Initializing AI Failure Detector with AST support...")
        self.ai_failure_detector = AIFailureDetector()
        
        logger.debug("-> Initializing TestingResources...")
        self.testing_resources = TestingResources()
        
        # Main service components with explicit dependency injection
        logger.debug("-> Initializing TestingTools with all dependencies...")
        self.testing_tools = TestingTools(
            foundry_adapter=self.foundry_adapter,
            project_analyzer=self.project_analyzer,
            ai_failure_detector=self.ai_failure_detector,
            testing_resources=self.testing_resources
        )
        
        logger.debug("-> Initializing TestingPrompts...")
        self.testing_prompts = TestingPrompts()
        
        logger.info("All components initialized successfully")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load enhanced default configuration from environment variables."""
        return {
            "server": {
                "host": os.getenv("MCP_SERVER_HOST", "127.0.0.1"),
                "port": int(os.getenv("MCP_SERVER_PORT", "8002")),
                "transport_mode": os.getenv("MCP_TRANSPORT_MODE", "stdio").lower()
            },
            "foundry": {
                "profile": os.getenv("FOUNDRY_PROFILE", "default"),
                "max_fuzz_runs": int(os.getenv("MAX_FUZZ_RUNS", "10000")),
                "invariant_runs": int(os.getenv("INVARIANT_RUNS", "256")),
                "enable_ast_analysis": os.getenv("ENABLE_AST_ANALYSIS", "true").lower() == "true"
            },
            "testing": {
                "coverage_target": int(os.getenv("COVERAGE_TARGET", "90")),
                "enable_gas_optimization": os.getenv("ENABLE_GAS_OPTIMIZATION", "true").lower() == "true",
                "enable_ai_failure_detection": os.getenv("ENABLE_AI_FAILURE_DETECTION", "true").lower() == "true"
            },
            "ast": {
                "solc_timeout": int(os.getenv("SOLC_TIMEOUT", "30")),
                "fallback_to_regex": os.getenv("AST_FALLBACK_TO_REGEX", "true").lower() == "true"
            },
            "workflow": {
                "default_project_path": ".",
                "auto_detect_project_type": True,
                "validate_foundry_project": True
            }
        }
    
    def _register_components(self) -> None:
        """Register all components with the MCP server with enhanced logging."""
        logger.info("Registering MCP components...")
        
        try:
            # Register testing tools with enhanced capabilities
            logger.debug("-> Registering Testing Tools...")
            self.testing_tools.register_tools(self.mcp)
            logger.info("✅ Testing Tools registered (AST-enhanced analysis)")
            
            # Register testing resources
            logger.debug("-> Registering Testing Resources...")
            self.testing_resources.register_resources(self.mcp)
            logger.info("✅ Testing Resources registered (templates, guides)")
            
            # Register testing prompts
            logger.debug("-> Registering Testing Prompts...")
            self.testing_prompts.register_prompts(self.mcp)
            logger.info("✅ Testing Prompts registered (workflow guidance)")
            
            # Register enhanced server info tool
            self._register_server_info_tool()
            logger.info("✅ Enhanced Server Info tool registered")
            
        except Exception as e:
            logger.error(f"Failed to register components: {e}")
            raise
    
    def _register_server_info_tool(self) -> None:
        """Register enhanced server info tool with AST capabilities."""
        
        @self.mcp.tool(
            name="get_server_info",
            description="""
            ℹ️ Enhanced server information and capabilities guide
            
            WHEN TO USE:
            - First time using this MCP server
            - User asks about available tools or capabilities  
            - Need to understand tool workflow and relationships
            - Checking server status and enhanced features
            - Getting quick start instructions
            
            WHAT IT DOES:
            - Provides complete overview of enhanced MCP tools
            - Explains AST-based semantic analysis capabilities
            - Shows AI failure detection features
            - Lists all available resources and templates
            - Provides workflow guidance and troubleshooting
            
            OUTPUTS:
            - Enhanced tool catalog with AST capabilities
            - Recommended workflow sequences
            - Server status and feature information
            - Quick start guide for different scenarios
            """
        )
        async def get_server_info() -> Dict[str, Any]:
            """Get enhanced server information with AST capabilities."""
            foundry_status = await self.foundry_adapter.check_foundry_installation()
            
            return {
                "server": {
                    "name": "Enhanced Smart Contract Testing MCP Server",
                    "version": "3.0.0-AST",
                    "description": "AI-powered testing workflows with AST semantic analysis",
                    "foundry_integration": foundry_status.get("installed", False),
                    "enhanced_capabilities": [
                        "🧠 AST-based semantic analysis",
                        "🔍 AI failure detection with context awareness", 
                        "🛡️ Professional security methodologies",
                        "📊 Enhanced coverage analysis with semantic gaps",
                        "🎯 Context-aware testing workflows",
                        "🔧 Dependency injection architecture"
                    ]
                },
                "ast_features": {
                    "solidity_ast_analysis": "Deep contract structure understanding via solc --ast-json",
                    "semantic_pattern_detection": "Security patterns detected by code semantics vs regex",
                    "enhanced_risk_scoring": "Risk assessment based on actual contract behavior",
                    "contextual_failure_detection": "AI failure detection with code structure context",
                    "fallback_support": "Graceful degradation to regex when AST unavailable"
                },
                "recommended_workflow": {
                    "step_1": {
                        "tool": "initialize_protocol_testing_agent",
                        "purpose": "🚀 START HERE - Enhanced project analysis with AST",
                        "when": "Beginning any testing work, first interaction with project"
                    },
                    "step_2_option_a": {
                        "tool": "analyze_project_context", 
                        "purpose": "🔍 Deep AST analysis with AI failure detection",
                        "when": "Existing tests need quality assessment or detailed planning"
                    },
                    "step_2_option_b": {
                        "tool": "execute_testing_workflow",
                        "purpose": "⚡ Direct implementation with AST-informed guidance", 
                        "when": "Clear on objectives and ready to implement"
                    },
                    "step_3": {
                        "tool": "analyze_current_test_coverage",
                        "purpose": "📊 Enhanced coverage analysis with semantic gap detection",
                        "when": "During or after test implementation"
                    }
                },
                "enhanced_tools": {
                    "initialize_protocol_testing_agent": "🚀 Enhanced project analysis with AST semantic understanding",
                    "analyze_project_context": "🔍 Deep AST analysis with AI failure detection and security patterns", 
                    "execute_testing_workflow": "⚡ AST-informed testing workflows with semantic guidance",
                    "analyze_current_test_coverage": "📊 Semantic coverage analysis with AST-based gap identification",
                    "validate_current_project": "✅ Enhanced project validation with dependency analysis", 
                    "debug_directory_detection": "🐛 Advanced troubleshooting with environment analysis"
                },
                "ai_failure_detection": {
                    "semantic_analysis": "Understands actual test logic vs surface patterns",
                    "context_awareness": "Uses AST to validate pattern matches and reduce false positives",
                    "enhanced_patterns": [
                        "Circular logic detection with semantic validation",
                        "Mock cheating detection via AST contract analysis", 
                        "Always-passing test detection with context awareness",
                        "Insufficient edge case detection via semantic analysis"
                    ]
                },
                "troubleshooting": {
                    "ast_analysis_fails": "Server gracefully falls back to regex-based analysis",
                    "solc_not_found": "AST features disabled, regex analysis continues to work",
                    "project_detection_issues": "Use debug_directory_detection for environment analysis",
                    "dependency_injection_errors": "Check component initialization logs for details"
                },
                "requirements": [
                    "Navigate to your Solidity project root directory", 
                    "Foundry must be installed and accessible",
                    "Project should have foundry.toml (or run 'forge init --force')",
                    "Contracts should be in src/ directory",
                    "Optional: solc installed for enhanced AST analysis"
                ],
                "foundry_installation": foundry_status,
                "config": {
                    "ast_analysis_enabled": self.config.get("foundry", {}).get("enable_ast_analysis", True),
                    "ai_failure_detection_enabled": self.config.get("testing", {}).get("enable_ai_failure_detection", True),
                    "coverage_target": self.config.get("testing", {}).get("coverage_target", 90)
                }
            }
    
    async def run_server(self) -> None:
        """
        Run the enhanced MCP server with comprehensive error handling.
        """
        try:
            transport_mode = self.config["server"]["transport_mode"]
            
            if transport_mode == "stdio":
                logger.info("🚀 Starting Enhanced MCP server in STDIO mode")
                logger.info("   AST-based semantic analysis: ENABLED")
                logger.info("   AI failure detection: ENABLED") 
                await self.mcp.run_async(transport="stdio")
            
            elif transport_mode == "http":
                host = self.config["server"]["host"]
                port = self.config["server"]["port"]
                logger.info(f"🚀 Starting Enhanced MCP server in HTTP mode at {host}:{port}")
                logger.info("   AST-based semantic analysis: ENABLED")
                logger.info("   AI failure detection: ENABLED")
                await self.mcp.run_async(transport="http", host=host, port=port)
            
            else:
                raise ValueError(f"Unsupported transport mode: {transport_mode}")
                
        except KeyboardInterrupt:
            # Handle shutdown gracefully without logging if I/O is closed
            try:
                logger.info("🛑 Server stopped by user")
            except (ValueError, OSError):
                pass
        except FoundryNotFoundError:
            try:
                logger.critical("❌ Cannot start server: Foundry not found")
                logger.critical("   Please install Foundry: https://getfoundry.sh/")
            except (ValueError, OSError):
                pass
            raise
        except Exception as e:
            try:
                logger.error(f"❌ Server error: {e}")
            except (ValueError, OSError):
                pass
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Enhanced cleanup of server resources."""
        try:
            # Try to log cleanup start, but handle I/O errors gracefully
            try:
                logger.info("🧹 Cleaning up server resources...")
            except (ValueError, OSError):
                # I/O streams may be closed during shutdown
                pass
            
            # Cleanup foundry adapter
            await self.foundry_adapter.cleanup()
            
            # Clear active sessions if any
            if hasattr(self.testing_tools, 'active_sessions'):
                self.testing_tools.active_sessions.clear()
            
            # Try to log completion, but handle I/O errors gracefully
            try:
                logger.info("✅ Server cleanup completed successfully")
            except (ValueError, OSError):
                # I/O streams may be closed during shutdown
                pass
            
        except Exception as e:
            # Try to log error, but handle I/O errors gracefully
            try:
                logger.error(f"❌ Cleanup error: {e}")
            except (ValueError, OSError):
                # I/O streams may be closed during shutdown
                pass

# Enhanced main server instance
async def main():
    """Enhanced main entry point for the server."""
    try:
        logger.info("🚀 Initializing Enhanced Smart Contract Testing MCP Server...")
        server = TestingMCPServer()
        await server.run_server()
        
    except FoundryNotFoundError:
        logger.critical("❌ STARTUP FAILED: Foundry not found")
        logger.critical("   Install Foundry: curl -L https://foundry.paradigm.xyz | bash")
        logger.critical("   Then run: foundryup")
        return 1
        
    except Exception as e:
        logger.critical(f"❌ STARTUP FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 